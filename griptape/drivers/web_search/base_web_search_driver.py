from abc import ABC, abstractmethod

from attrs import define, field

from griptape.artifacts import ListArtifact


@define
class BaseWebSearchDriver(ABC):
    results_count: int = field(default=5, kw_only=True)

    @abstractmethod
    def search(self, query: str, **kwargs) -> ListArtifact: ...
