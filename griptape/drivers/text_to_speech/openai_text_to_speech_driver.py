from __future__ import annotations

from typing import Literal, Optional

import openai
from attrs import Factory, define, field

from griptape.artifacts.audio_artifact import AudioArtifact
from griptape.drivers import BaseTextToSpeechDriver
from griptape.tokenizers import SimpleTokenizer


@define
class OpenAiTextToSpeechDriver(BaseTextToSpeechDriver):
    model: str = field(default="tts-1", kw_only=True, metadata={"serializable": True})
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = field(
        default="alloy",
        kw_only=True,
        metadata={"serializable": True},
    )
    format: Literal["mp3", "opus", "aac", "flac"] = field(default="mp3", kw_only=True, metadata={"serializable": True})
    api_type: Optional[str] = field(default=openai.api_type, kw_only=True)
    api_version: Optional[str] = field(default=openai.api_version, kw_only=True, metadata={"serializable": True})
    base_url: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    api_key: Optional[str] = field(default=None, kw_only=True)
    organization: Optional[str] = field(default=openai.organization, kw_only=True, metadata={"serializable": True})
    client: openai.OpenAI = field(
        default=Factory(
            lambda self: openai.OpenAI(api_key=self.api_key, base_url=self.base_url, organization=self.organization),
            takes_self=True,
        ),
    )

    def try_text_to_audio(self, prompts: list[str]) -> list[AudioArtifact]:
        tokenizer = SimpleTokenizer(characters_per_token=self.max_characters)
        # treat each set of characters of length max_characters as a "token"
        prompt = self.prompt_separator.join(prompts)
        num_tokens = tokenizer.count_tokens(prompt)
        return [
            AudioArtifact(
                value=self.client.audio.speech.create(
                    input=prompt[i * self.max_characters : (i + 1) * self.max_characters],
                    voice=self.voice,
                    model=self.model,
                    response_format=self.format,
                ).content,
                format=self.format,
            )
            for i in range(0, num_tokens, 1)
        ]
