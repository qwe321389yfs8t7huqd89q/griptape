from __future__ import annotations

from abc import abstractmethod
from typing import Any, Union, TypeVar, Generic
from attrs import define, field, Factory, fields


@define(slots=False)
class ClientMixin:
    client: Any = field(
        default=Factory(lambda self: self._client_factory(), takes_self=True),
        kw_only=True,
        metadata={"serializable": False},
    )

    @abstractmethod
    def _default_client(self) -> Any: ...

    def _client_factory(self) -> Any:
        if missing_params := self._validate_client_parameters():
            raise ValueError(
                "Missing parameters for {} client: ({})".format(
                    self.__class__.__name__,
                    ", ".join([" or ".join(missing_params_tup) for missing_params_tup in missing_params]),
                )
            )
        return self._default_client()

    def _validate_client_parameters(self) -> list[tuple[str]]:
        return [
            req_param_tup
            for req_param_tup in self._required_client_parameters()
            if all([getattr(self, req_param, None) is None for req_param in req_param_tup])
        ]

    def _required_client_parameters(self) -> list[tuple[str]]:
        fields_dict = {}
        for field in fields(type(self)):
            if field.metadata.get("client_required", False):
                key = field.metadata.get("client_param_group", field.name)
                if key not in fields_dict:
                    fields_dict[key] = {field.name}
                else:
                    fields_dict[key].add(field.name)
        tup = list(tuple(fields_set) for fields_set in fields_dict.values())
        print(tup)
        return tup
