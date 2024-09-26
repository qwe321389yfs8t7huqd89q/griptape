from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field
from schema import Literal, Schema

from griptape.artifacts import ErrorArtifact, ListArtifact, TextArtifact
from griptape.tools import BaseAwsTool
from griptape.utils.decorators import activity, lazy_property

if TYPE_CHECKING:
    from mypy_boto3_iam import IAMClient


@define
class AwsIamTool(BaseAwsTool):
    _client: IAMClient = field(default=None, kw_only=True, alias="client", metadata={"serializable": False})

    @lazy_property()
    def client(self) -> IAMClient:
        return self.session.client("iam")

    @activity(
        config={
            "description": "Can be use to get a policy for an AWS IAM user.",
            "schema": Schema(
                {
                    Literal("user_name", description="Username of the AWS IAM user."): str,
                    Literal(
                        "policy_name",
                        description="PolicyName of the AWS IAM Policy embedded in the specified IAM user.",
                    ): str,
                },
            ),
        },
    )
    def get_user_policy(self, params: dict) -> TextArtifact | ErrorArtifact:
        try:
            policy = self.client.get_user_policy(
                UserName=params["values"]["user_name"],
                PolicyName=params["values"]["policy_name"],
            )
            return TextArtifact(policy["PolicyDocument"])
        except Exception as e:
            return ErrorArtifact(f"error returning policy document: {e}")

    @activity(config={"description": "Can be used to list AWS MFA Devices"})
    def list_mfa_devices(self, _: dict) -> ListArtifact | ErrorArtifact:
        try:
            devices = self.client.list_mfa_devices()
            return ListArtifact([TextArtifact(str(d)) for d in devices["MFADevices"]])
        except Exception as e:
            return ErrorArtifact(f"error listing mfa devices: {e}")

    @activity(
        config={
            "description": "Can be used to list policies for a given IAM user.",
            "schema": Schema(
                {Literal("user_name", description="Username of the AWS IAM user for which to list policies."): str},
            ),
        },
    )
    def list_user_policies(self, params: dict) -> ListArtifact | ErrorArtifact:
        try:
            policies = self.client.list_user_policies(UserName=params["values"]["user_name"])
            policy_names = policies["PolicyNames"]

            attached_policies = self.client.list_attached_user_policies(UserName=params["values"]["user_name"])
            attached_policy_names = [
                p["PolicyName"] for p in attached_policies["AttachedPolicies"] if "PolicyName" in p
            ]

            return ListArtifact([TextArtifact(str(p)) for p in policy_names + attached_policy_names])
        except Exception as e:
            return ErrorArtifact(f"error listing iam user policies: {e}")

    @activity(config={"description": "Can be used to list AWS IAM users."})
    def list_users(self, _: dict) -> ListArtifact | ErrorArtifact:
        try:
            users = self.client.list_users()
            return ListArtifact([TextArtifact(str(u)) for u in users["Users"]])
        except Exception as e:
            return ErrorArtifact(f"error listing s3 users: {e}")
