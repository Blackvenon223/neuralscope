"""Tests for settings."""

from neuralscope.core.settings import LLMProvider, QdrantMode, Settings


def test_defaults():
    settings = Settings(_env_file=None)
    assert settings.llm_provider == LLMProvider.OPENAI
    assert settings.llm_model == "gpt-5.2"
    assert settings.qdrant_mode == QdrantMode.MEMORY
    assert settings.cache_enabled is True


def test_model_string():
    settings = Settings(
        _env_file=None, llm_provider="anthropic",
        llm_model="claude-sonnet-4-6-20260217",
    )
    assert settings.get_model_string() == "anthropic/claude-sonnet-4-6-20260217"


def test_profiles_dir():
    settings = Settings(_env_file=None)
    assert settings.profiles_dir.name == "profiles"
    assert settings.profiles_dir.parent.name == ".neuralscope"


def test_proxy_defaults():
    settings = Settings(_env_file=None)
    assert settings.litellm_api_base == "http://localhost:4000"
    assert settings.openrouter_api_key is None
