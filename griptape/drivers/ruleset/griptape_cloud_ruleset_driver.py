from __future__ import annotations

import os
import uuid
from typing import TYPE_CHECKING, Any, Optional
from urllib.parse import urljoin

import requests
from attrs import Attribute, Factory, define, field

from griptape.drivers import BaseRulesetDriver
from griptape.utils import dict_merge

if TYPE_CHECKING:
    from griptape.rules import BaseRule


@define(kw_only=True)
class GriptapeCloudRulesetDriver(BaseRulesetDriver):
    """A driver for storing conversation memory in the Griptape Cloud.

    Attributes:
        ruleset_id: The ID of the Thread to store the conversation memory in. If not provided, the driver will attempt to
            retrieve the ID from the environment variable `GT_CLOUD_THREAD_ID`. If that is not set, a new Thread will be
            created.
        base_url: The base URL of the Griptape Cloud API. Defaults to the value of the environment variable
            `GT_CLOUD_BASE_URL` or `https://cloud.griptape.ai`.
        api_key: The API key to use for authenticating with the Griptape Cloud API. If not provided, the driver will
            attempt to retrieve the API key from the environment variable `GT_CLOUD_API_KEY`.

    Raises:
        ValueError: If `api_key` is not provided.
    """

    ruleset_id: str = field(
        default=None,
        metadata={"serializable": True},
    )
    base_url: str = field(
        default=Factory(lambda: os.getenv("GT_CLOUD_BASE_URL", "https://cloud.griptape.ai")),
    )
    api_key: Optional[str] = field(default=Factory(lambda: os.getenv("GT_CLOUD_API_KEY")))
    headers: dict = field(
        default=Factory(lambda self: {"Authorization": f"Bearer {self.api_key}"}, takes_self=True),
        init=False,
    )

    def __attrs_post_init__(self) -> None:
        if self.ruleset_id is None:
            self.ruleset_id = os.getenv("GT_CLOUD_THREAD_ID", self._get_ruleset_id())

    @api_key.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_api_key(self, _: Attribute, value: Optional[str]) -> str:
        if value is None:
            raise ValueError(f"{self.__class__.__name__} requires an API key")
        return value

    # def store(self, rules: list[BaseRule], metadata: dict[str, Any]) -> None:
    #     # loop through the rules and store them
    #     rule_ids = []
    #     for rule in rules:
    #         # if the rule has an id in metadata, use that to patch the rule
    #         if rule.meta.get("rule_id"):
    #             rule_res = self._call_api(
    #                 "patch",
    #                 f"/rules/{rule.meta.pop('rule_id')}",
    #                 json.dumps({"rule": rule.value, "metadata": rule.meta}),
    #             )
    #         else:
    #             rule_res = self._call_api("post", "/rules", json.dumps({"rule": rule.value, "metadata": rule.meta}))

    #         rule_ids.append(rule_res.get("rule_id"))

    #     self._call_api(
    #         "patch",
    #         f"/rulesets/{self.ruleset_id}",
    #         json.dumps({"rule_ids": rule_ids, "metadata": metadata}),
    #     )

    def load(self, name: Optional[str] = None) -> tuple[list[BaseRule], dict[str, Any]]:
        ruleset = None
        if name is not None:
            res = self._call_api("get", f"/rulesets?alias={name}")
            if res.get("rulesets"):
                ruleset = res["rulesets"][0]
        if ruleset is None:
            ruleset = self._call_api("get", f"/rulesets/{self.ruleset_id}")

        rules = ruleset.get("rules", [])

        for rule in rules:
            rule["metadata"] = dict_merge(rule["metadata"], {"rule_id": rule["rule_id"]})

        return [self._get_rule(rule["rule"], rule["metadata"]) for rule in rules], ruleset.get("metadata", {})

    def _get_ruleset_id(self) -> str:
        ruleset_id = self._call_api("post", "/rulesets", {"alias": uuid.uuid4().hex}).get("ruleset")
        if ruleset_id is None:
            raise ValueError("Unable to create a new ruleset")
        return ruleset_id

    def _get_url(self, path: str) -> str:
        path = path.lstrip("/")
        return urljoin(self.base_url, f"/api/{path}")

    def _call_api(self, method: str, path: str, data=None) -> dict:
        res = requests.request(method, self._get_url(path), headers=self.headers, json=data)
        res.raise_for_status()
        return res.json()
