from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional, cast

from attrs import define, field

from griptape.artifacts import TextArtifact
from griptape.loaders import BaseLoader
from griptape.utils import import_optional_dependency
from griptape.utils.hash import str_to_hash

if TYPE_CHECKING:
    from pandas import DataFrame

    from griptape.drivers import BaseEmbeddingDriver


@define
class DataFrameLoader(BaseLoader):
    embedding_driver: Optional[BaseEmbeddingDriver] = field(default=None, kw_only=True)
    formatter_fn: Callable[[dict], str] = field(
        default=lambda value: "\n".join(f"{key}: {val}" for key, val in value.items()), kw_only=True
    )

    def load(self, source: DataFrame, *args, **kwargs) -> list[TextArtifact]:
        artifacts = []

        chunks = [TextArtifact(self.formatter_fn(row)) for row in source.to_dict(orient="records")]

        if self.embedding_driver:
            for chunk in chunks:
                chunk.generate_embedding(self.embedding_driver)

        for chunk in chunks:
            artifacts.append(chunk)

        return artifacts

    def load_collection(self, sources: list[DataFrame], *args, **kwargs) -> dict[str, list[TextArtifact]]:
        return cast(dict[str, list[TextArtifact]], super().load_collection(sources, *args, **kwargs))

    def to_key(self, source: DataFrame, *args, **kwargs) -> str:
        hash_pandas_object = import_optional_dependency("pandas.core.util.hashing").hash_pandas_object

        return str_to_hash(str(hash_pandas_object(source, index=True).values))
