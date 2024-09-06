from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.configs import Defaults

if TYPE_CHECKING:
    from griptape.artifacts.audio_artifact import AudioArtifact
    from griptape.drivers import BaseTextToSpeechDriver


@define
class TextToSpeechEngine:
    max_characters: int = field(default=4096, kw_only=True, metadata={"serializable": True})
    prompt_separator: str = field(default=". ", kw_only=True, metadata={"serializable": True})
    text_to_speech_driver: BaseTextToSpeechDriver = field(
        default=Factory(lambda: Defaults.drivers_config.text_to_speech_driver), kw_only=True
    )

    def run(self, prompts: list[str], *args, **kwargs) -> list[AudioArtifact]:
        prompt = self.prompt_separator.join(prompts)
        
        return self.text_to_speech_driver.try_text_to_audio(prompts=prompts)
