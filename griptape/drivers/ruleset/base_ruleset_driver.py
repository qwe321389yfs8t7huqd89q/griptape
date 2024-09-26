from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

from griptape.mixins.serializable_mixin import SerializableMixin

if TYPE_CHECKING:
    from griptape.rules import BaseRule


class BaseRulesetDriver(SerializableMixin, ABC):
    @abstractmethod
    def load(self, name: Optional[str] = None) -> tuple[list[BaseRule], dict[str, Any]]: ...

    def _from_ruleset_dict(self, params_dict: dict[str, Any]) -> tuple[list[BaseRule], dict[str, Any]]:
        return [
            self._get_rule(rule["value"], rule.get("meta", {})) for rule in params_dict.get("rules", [])
        ], params_dict.get("meta", {})

    def _get_rule(self, value: Any, meta: dict[str, Any]) -> BaseRule:
        from griptape.rules import JsonSchemaRule, Rule

        return JsonSchemaRule(value=value, meta=meta) if isinstance(value, dict) else Rule(value=str(value), meta=meta)
