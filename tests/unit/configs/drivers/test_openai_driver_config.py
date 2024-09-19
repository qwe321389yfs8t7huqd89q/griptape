import pytest

from griptape.configs.drivers import OpenAiDriversConfig


class TestOpenAiDriversConfig:
    @pytest.fixture(autouse=True)
    def mock_openai(self, mocker):
        return mocker.patch("openai.OpenAI")

    @pytest.fixture()
    def config(self):
        return OpenAiDriversConfig()

    def test_to_dict(self, config):
        assert config.to_dict() == {
            "type": "OpenAiDriversConfig",
            "prompt_driver": {
                "type": "OpenAiChatPromptDriver",
                "base_url": None,
                "model": "gpt-4o",
                "organization": None,
                "response_format": None,
                "seed": None,
                "temperature": 0.1,
                "max_tokens": None,
                "stream": False,
                "user": "",
                "use_native_tools": True,
            },
            "conversation_memory_driver": {
                "type": "LocalConversationMemoryDriver",
                "persist_file": None,
            },
            "embedding_driver": {
                "base_url": None,
                "model": "text-embedding-3-small",
                "organization": None,
                "type": "OpenAiEmbeddingDriver",
            },
            "image_generation_driver": {
                "api_version": None,
                "base_url": None,
                "image_size": "512x512",
                "model": "dall-e-2",
                "organization": None,
                "quality": "standard",
                "response_format": "b64_json",
                "style": None,
                "type": "OpenAiImageGenerationDriver",
            },
            "image_query_driver": {
                "api_version": None,
                "base_url": None,
                "image_quality": "auto",
                "max_tokens": 256,
                "model": "gpt-4o",
                "organization": None,
                "type": "OpenAiImageQueryDriver",
            },
            "vector_store_driver": {
                "embedding_driver": {
                    "base_url": None,
                    "model": "text-embedding-3-small",
                    "organization": None,
                    "type": "OpenAiEmbeddingDriver",
                },
                "type": "LocalVectorStoreDriver",
            },
            "text_to_speech_driver": {
                "type": "OpenAiTextToSpeechDriver",
                "api_version": None,
                "base_url": None,
                "format": "mp3",
                "model": "tts-1",
                "organization": None,
                "voice": "alloy",
                "speed": 1.0,
                "max_characters": 4096,
            },
            "audio_transcription_driver": {
                "type": "OpenAiAudioTranscriptionDriver",
                "api_version": None,
                "base_url": None,
                "model": "whisper-1",
                "organization": None,
            },
        }

    def test_from_dict(self, config):
        assert OpenAiDriversConfig.from_dict(config.to_dict()).to_dict() == config.to_dict()
