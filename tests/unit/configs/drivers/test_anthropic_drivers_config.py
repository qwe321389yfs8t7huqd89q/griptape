import pytest

from griptape.configs.drivers import AnthropicDriversConfig


class TestAnthropicDriversConfig:
    @pytest.fixture(autouse=True)
    def _mock_anthropic(self, mocker):
        mocker.patch("anthropic.Anthropic")
        mocker.patch("voyageai.Client")

    @pytest.fixture()
    def config(self):
        return AnthropicDriversConfig()

    def test_to_dict(self, config):
        assert config.to_dict() == {
            "type": "AnthropicDriversConfig",
            "prompt_driver": {
                "type": "AnthropicPromptDriver",
                "temperature": 0.1,
                "max_tokens": 1000,
                "stream": False,
                "model": "claude-3-5-sonnet-20240620",
                "top_p": 0.999,
                "top_k": 250,
                "use_native_tools": True,
            },
            "image_generation_driver": {"type": "DummyImageGenerationDriver"},
            "image_query_driver": {
                "type": "AnthropicImageQueryDriver",
                "model": "claude-3-5-sonnet-20240620",
                "max_tokens": 256,
            },
            "embedding_driver": {
                "type": "VoyageAiEmbeddingDriver",
                "model": "voyage-large-2",
                "input_type": "document",
            },
            "vector_store_driver": {
                "type": "LocalVectorStoreDriver",
                "embedding_driver": {
                    "type": "VoyageAiEmbeddingDriver",
                    "model": "voyage-large-2",
                    "input_type": "document",
                },
            },
            "conversation_memory_driver": {
                "type": "LocalConversationMemoryDriver",
                "persist_file": None,
            },
            "text_to_speech_driver": {"type": "DummyTextToSpeechDriver"},
            "audio_transcription_driver": {"type": "DummyAudioTranscriptionDriver"},
        }

    def test_from_dict(self, config):
        assert AnthropicDriversConfig.from_dict(config.to_dict()).to_dict() == config.to_dict()
