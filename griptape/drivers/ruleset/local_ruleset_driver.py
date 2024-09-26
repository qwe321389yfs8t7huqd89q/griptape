from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from attrs import define, field

from griptape.drivers import BaseRulesetDriver

if TYPE_CHECKING:
    from griptape.rules import BaseRule


@define(kw_only=True)
class LocalRulesetDriver(BaseRulesetDriver):
    persist_file: Optional[str] = field(default=None, metadata={"serializable": True})

    def load(self, name: Optional[str] = None) -> tuple[list[BaseRule], dict[str, Any]]:
        file_name = name if name is not None else self.persist_file
        if (
            file_name is not None
            and os.path.exists(file_name)
            and (loaded_str := Path(file_name).read_text()) is not None
        ):
            try:
                return self._from_ruleset_dict(json.loads(loaded_str))
            except Exception as e:
                raise ValueError(f"Unable to load data from {file_name}") from e

        return [], {}
