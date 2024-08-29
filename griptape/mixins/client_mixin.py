from __future__ import annotations

from abc import abstractmethod
from typing import Any, Union, TypeVar, Generic
from attrs import define, field, Factory

T = TypeVar("T")


@define(slots=False)
class ClientMixin(Generic[T]):
    client: T = field(
        default=Factory(lambda self: self._client_factory(), takes_self=True),
        kw_only=True,
        metadata={"serializable": False},
    )

    @abstractmethod
    def _default_client(self) -> T: ...

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
