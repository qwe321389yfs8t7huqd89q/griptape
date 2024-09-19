from __future__ import annotations

from typing import Literal, Optional

import openai
from attrs import Factory, define, field

from griptape.artifacts.audio_artifact import AudioArtifact
from griptape.drivers import BaseTextToSpeechDriver


@define
class OpenAiTextToSpeechDriver(BaseTextToSpeechDriver):
    model: str = field(default="tts-1", kw_only=True, metadata={"serializable": True})
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = field(
        default="alloy",
        kw_only=True,
        metadata={"serializable": True},
    )
    format: Literal["mp3", "opus", "aac", "flac"] = field(default="mp3", kw_only=True, metadata={"serializable": True})
    speed: float = field(default=1.0, kw_only=True, metadata={"serializable": True})
    api_type: Optional[str] = field(default=openai.api_type, kw_only=True)
    api_version: Optional[str] = field(default=openai.api_version, kw_only=True, metadata={"serializable": True})
    base_url: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    api_key: Optional[str] = field(default=None, kw_only=True)
    organization: Optional[str] = field(default=openai.organization, kw_only=True, metadata={"serializable": True})
    max_characters: int = field(default=4096, kw_only=True, metadata={"serializable": True})
    client: openai.OpenAI = field(
        default=Factory(
            lambda self: openai.OpenAI(api_key=self.api_key, base_url=self.base_url, organization=self.organization),
            takes_self=True,
        ),
    )

    @speed.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_speed(self, attribute: str, value: float) -> None:
        if value < 0.25 or value > 4.0:
            raise ValueError("Speed must be between 0.5 and 4.0")

    def try_text_to_audio(self, prompt: str) -> AudioArtifact:
        response = self.client.audio.speech.create(
            input=prompt,
            model=self.model,
            voice=self.voice,
            response_format=self.format,
            speed=self.speed,
        )

        return AudioArtifact(value=response.content, format=self.format)
