from __future__ import annotations

import imaplib
from typing import Optional, cast

from attrs import astuple, define, field

from griptape.artifacts import ListArtifact, TextArtifact
from griptape.loaders import BaseLoader
from griptape.utils import import_optional_dependency


@define
class EmailLoader(BaseLoader):
    @define(frozen=True)
    class EmailQuery:
        """An email retrieval query.

        Attributes:
            label: Label to retrieve emails from such as 'INBOX' or 'SENT'.
            key: Optional key for filtering such as 'FROM' or 'SUBJECT'.
            search_criteria: Optional search criteria to filter emails by key.
            max_count: Optional max email count.
        """

        label: str = field(kw_only=True)
        key: Optional[str] = field(default=None, kw_only=True)
        search_criteria: Optional[str] = field(default=None, kw_only=True)
        max_count: Optional[int] = field(default=None, kw_only=True)

    imap_url: str = field(kw_only=True)
    username: str = field(kw_only=True)
    password: str = field(kw_only=True)

    def load(self, source: EmailQuery, *args, **kwargs) -> ListArtifact:
        label, key, search_criteria, max_count = astuple(source)

        list_artifact = None
        with imaplib.IMAP4_SSL(self.imap_url) as client:
            client.login(self.username, self.password)

            mailbox = client.select(f'"{label}"', readonly=True)
            if mailbox[0] != "OK":
                raise Exception(mailbox[1][0].decode())

            if key and search_criteria:
                _typ, [message_numbers] = client.search(None, key, f'"{search_criteria}"')
                messages_count = self._count_messages(message_numbers)
            elif len(mailbox) > 1 and mailbox[1] and mailbox[1][0] is not None:
                messages_count = int(mailbox[1][0])
            else:
                raise Exception("unable to parse number of messages")

            top_n = max(0, messages_count - max_count) if max_count else 0
            for i in range(messages_count, top_n, -1):
                _result, data = client.fetch(str(i), "(RFC822)")

                if data is None or not data or data[0] is None:
                    continue

                list_artifact = self.load_from_bytes(
                    data[0][1],
                    *args,
                    **kwargs,
                )

            client.close()

            return list_artifact if list_artifact else ListArtifact([])

    def load_from_bytes(self, source: bytes | int, *args, **kwargs) -> ListArtifact:
        mailparser = import_optional_dependency("mailparser")

        email = mailparser.parse_from_bytes(source)
        body = []
        if email.text_plain:
            body.append(email.text_plain)
        elif email.text_html:
            body.append(email.text_html)
        elif email.text_not_managed:
            body.append(email.text_not_managed)

        return ListArtifact([TextArtifact("\n".join(body))])

    def _count_messages(self, message_numbers: bytes) -> int:
        return len(list(filter(None, message_numbers.decode().split(" "))))

    def load_collection(self, sources: list[EmailQuery], *args, **kwargs) -> dict[str, ListArtifact]:
        return cast(dict[str, ListArtifact], super().load_collection(sources, *args, **kwargs))
