from __future__ import annotations

from attrs import define

from griptape.artifacts import BlobArtifact
from griptape.loaders import BaseFileLoader


@define
class BlobLoader(BaseFileLoader[BlobArtifact]):
    def parse(self, data: bytes, meta: dict) -> BlobArtifact:
        if self.encoding is None:
            return BlobArtifact(data)
        else:
            return BlobArtifact(data, encoding=self.encoding)
