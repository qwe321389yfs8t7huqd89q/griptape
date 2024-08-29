from __future__ import annotations

from typing import Any, Union
from attrs import define, field, Factory


@define(slots=False)
class ClientMixin:
    client: Any = field(default=Factory(lambda self: self._client_factory(), takes_self=True), kw_only=True, metadata={"serializable": False})

    # def __attrs_post_init__(self):
    #     if missing_params := self._validate_client_parameters():
    #         raise ValueError(
    #             "Missing parameters for {} client: ({})".format(
    #                 self.__class__.__name__,
    #                 ", ".join([" or ".join(missing_params_tup) for missing_params_tup in missing_params]),
    #             )
    #         )
    #     if self.client is None:
    #         self.client = self._build_client()

    def _client_factory(self) -> Any:
        if missing_params := self._validate_client_parameters():
            raise ValueError(
                "Missing parameters for {} client: ({})".format(
                    self.__class__.__name__,
                    ", ".join([" or ".join(missing_params_tup) for missing_params_tup in missing_params]),
                )
            )
        return self._build_client()

    def _build_client(self) -> Any:
        return None

    def _validate_client_parameters(self) -> list[tuple[str]]:
        return [
            req_param_tup if isinstance(req_param_tup, tuple) else (req_param_tup,)
            for req_param_tup in self._required_client_parameters()
            if all(
                [getattr(self, req_param, None) is None for req_param in req_param_tup]
                if isinstance(req_param_tup, tuple)
                else [getattr(self, req_param_tup, None)]
            )
        ]

    def _required_client_parameters(self) -> list[Union[str, tuple[str]]]:
        return []
