import base64

import pytest

from griptape.artifacts import BaseArtifact, BlobArtifact


class TestBlobArtifact:
    def test_value_type_conversion(self):
        assert BlobArtifact(1).value == b"1"

    def test_to_text(self):
        assert BlobArtifact(b"foobar", name="foobar.txt").to_text() == "foobar"

    def test_to_bytes(self):
        assert BlobArtifact(b"foo").to_bytes() == b"foo"

    def test_to_text_encoding(self):
        assert (
            BlobArtifact("ß".encode("ascii", errors="backslashreplace"), name="foobar.txt", encoding="ascii").to_text()
            == "\\xdf"
        )

    def test_to_text_encoding_error(self):
        with pytest.raises(ValueError):
            assert BlobArtifact("ß".encode(), name="foobar.txt", encoding="ascii").to_text()

    def test_to_text_encoding_error_handler(self):
        assert (
            BlobArtifact("ß".encode(), name="foobar.txt", encoding="ascii", encoding_error_handler="replace").to_text()
            == "��"
        )

    def test_to_dict(self):
        assert BlobArtifact(b"foobar", name="foobar.txt").to_dict()["name"] == "foobar.txt"

    def test_serialization(self):
        artifact = BlobArtifact(b"foobar", name="foobar.txt")
        artifact_dict = artifact.to_dict()

        assert artifact_dict["name"] == "foobar.txt"
        assert base64.b64decode(artifact_dict["value"]) == b"foobar"

    def test_deserialization(self):
        artifact = BlobArtifact(b"foobar", name="foobar.txt")
        artifact_dict = artifact.to_dict()
        deserialized_artifact = BaseArtifact.from_dict(artifact_dict)

        assert isinstance(deserialized_artifact, BlobArtifact)
        assert deserialized_artifact.name == "foobar.txt"
        assert deserialized_artifact.value == b"foobar"

    def test_name(self):
        assert BlobArtifact(b"foo", name="bar").name == "bar"

    def test_mime_type(self):
        assert BlobArtifact(b"foo").mime_type == "application/octet-stream"

    def test___add__(self):
        with pytest.raises(TypeError):
            BlobArtifact(b"foo") + BlobArtifact(b"bar")

    def test___bool__(self):
        assert not bool(BlobArtifact(b""))
        assert bool(BlobArtifact(b"foo"))
