from attrs import Factory, define, field

from griptape.artifacts import AudioArtifact, TextArtifact
from griptape.configs import Defaults
from griptape.drivers import BaseAudioTranscriptionDriver


@define
class AudioTranscriptionEngine:
    audio_transcription_driver: BaseAudioTranscriptionDriver = field(
        default=Factory(lambda: Defaults.drivers_config.audio_transcription_driver), kw_only=True
    )

    def run(self, audio: AudioArtifact, *args, **kwargs) -> TextArtifact:
        return self.audio_transcription_driver.try_run(audio)
