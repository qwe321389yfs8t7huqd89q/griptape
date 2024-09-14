import os
import tempfile
import uuid
from unittest.mock import Mock

import pytest

from griptape.artifacts.image_artifact import ImageArtifact
from griptape.tools import PromptImageGenerationTool


class TestPromptImageGenerationTool:
    @pytest.fixture()
    def image_generation_engine(self) -> Mock:
        return Mock()

    @pytest.fixture()
    def image_generator(self, image_generation_engine) -> PromptImageGenerationTool:
        return PromptImageGenerationTool(engine=image_generation_engine)

    def test_validate_output_configs(self, image_generation_engine) -> None:
        with pytest.raises(ValueError):
            PromptImageGenerationTool(engine=image_generation_engine, output_dir="test", output_file="test")

    def test_generate_image(self, image_generator) -> None:
        image_generator.engine.run.return_value = Mock(
            value=b"image data", format="png", width=512, height=512, model="test model", prompt="test prompt"
        )

        image_artifact = image_generator.generate_image(
            params={"values": {"prompt": "test prompt", "negative_prompt": "test negative prompt"}}
        )

        assert image_artifact

    def test_generate_image_with_outfile(self, image_generation_engine) -> None:
        outfile = f"{tempfile.gettempdir()}/{str(uuid.uuid4())}.png"
        image_generator = PromptImageGenerationTool(engine=image_generation_engine, output_file=outfile)

        image_generator.engine.run.return_value = ImageArtifact(  # pyright: ignore[reportFunctionMemberAccess]
            value=b"image data", format="png", width=512, height=512
        )

        image_artifact = image_generator.generate_image(
            params={"values": {"prompt": "test prompt", "negative_prompt": "test negative prompt"}}
        )

        assert image_artifact
        assert os.path.exists(outfile)
