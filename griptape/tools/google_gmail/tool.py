from __future__ import annotations

import base64
import logging
from email.message import EmailMessage

from attrs import define, field
from schema import Literal, Schema

from griptape.artifacts import ErrorArtifact, InfoArtifact, ListArtifact, TextArtifact
from griptape.tools import BaseGoogleClient
from griptape.utils.decorators import activity


@define
class GoogleGmailClient(BaseGoogleClient):
    CREATE_DRAFT_EMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]

    owner_email: str = field(kw_only=True)

    @activity(
        config={
            "description": "Can be used to create a draft email in GMail",
            "schema": Schema(
                {
                    Literal("to", description="email address which to send to"): str,
                    Literal("subject", description="subject of the email"): str,
                    Literal("body", description="body of the email"): str,
                },
            ),
        },
    )
    def create_draft_email(self, params: dict) -> InfoArtifact | ErrorArtifact:
        values = params["values"]

        try:
            service = self._build_client(
                scopes=self.CREATE_DRAFT_EMAIL_SCOPES,
                service_name="gmail",
                version="v1",
                owner_email=self.owner_email,
            )

            message = EmailMessage()
            message.set_content(values["body"])
            message["To"] = values["to"]
            message["From"] = self.owner_email
            message["Subject"] = values["subject"]

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {"message": {"raw": encoded_message}}
            draft = service.users().drafts().create(userId="me", body=create_message).execute()
            return InfoArtifact(f'An email draft was successfully created (ID: {draft["id"]})')

        except Exception as error:
            logging.error(error)
            return ErrorArtifact(f"error creating draft email: {error}")

    @activity(
        config={
            "description": "Can be used to read emails from the GMail inbox",
            "schema": Schema(
                {
                    Literal("max_results", description="maximum number of emails to fetch"): int,
                    Literal("page_token", description="page token to continue from previous result"): int,
                    Literal("query", description="google query string to be passed to messages().list method"): str
                },
            ),
        }
    )
    def read_emails(self, params: dict) -> ListArtifact | ErrorArtifact:
        values = params["values"]
        max_results = values.get("max_results", 10)
        query_string = values.get("query")

        try:
            service = self._build_client(
                scopes=["https://www.googleapis.com/auth/gmail.readonly"],
                service_name="gmail",
                version="v1",
                owner_email=self.owner_email,
            )

            # Query for messages in the inbox where the user is in the To: field
            # query = "in:inbox to:me"
            query = query_string
            results = service.users().messages().list(userId="me", maxResults=max_results, q=query).execute()
            messages = results.get("messages", [])

            emails = []
            for message in messages:
                msg = service.users().messages().get(userId="me", id=message["id"]).execute()
                headers = {header["name"]: header["value"] for header in msg["payload"]["headers"]}
                email_info = {
                    "from": headers.get("From"),
                    "date": headers.get("Date"),
                    "subject": headers.get("Subject"),
                }
                emails.append(email_info)

            next_page_token = results.get("nextPageToken")
            # uh...

            return ListArtifact([TextArtifact(email) for email in emails])

        except Exception as error:
            logging.error(error)
            return ErrorArtifact(f"error reading emails: {error}")
