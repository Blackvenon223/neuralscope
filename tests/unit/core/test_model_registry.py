"""Tests for Model Registry."""

from neuralscope.core.llm.model_registry import ModelRegistry
from neuralscope.core.llm.models import ModelConfig
from neuralscope.core.settings import LLMProvider, Settings


def test_parse_openai():
    config = ModelConfig.from_string("openai/gpt-5.2")
    assert config.provider == LLMProvider.OPENAI
    assert config.model_name == "gpt-5.2"


def test_parse_no_provider():
    config = ModelConfig.from_string("gpt-5-mini")
    assert config.provider == LLMProvider.OPENAI
    assert config.model_name == "gpt-5-mini"


def test_parse_anthropic():
    config = ModelConfig.from_string("anthropic/claude-sonnet-4-6-20260217")
    assert config.provider == LLMProvider.ANTHROPIC
    assert config.model_name == "claude-sonnet-4-6-20260217"


def test_parse_ollama():
    config = ModelConfig.from_string("ollama/qwen3")
    assert config.provider == LLMProvider.OLLAMA
    assert config.model_name == "qwen3"


def test_parse_openrouter():
    config = ModelConfig.from_string("openrouter/deepseek/r1")
    assert config.provider == LLMProvider.OPENROUTER
    assert config.model_name == "deepseek/r1"


def test_parse_litellm():
    config = ModelConfig.from_string("litellm/gpt-5.2")
    assert config.provider == LLMProvider.LITELLM
    assert config.model_name == "gpt-5.2"


def test_parse_unknown_prefix_falls_back():
    config = ModelConfig.from_string("some-unknown/model-v3")
    assert config.provider == LLMProvider.OPENAI
    assert config.model_name == "some-unknown/model-v3"


def test_list_providers_count():
    settings = Settings(_env_file=None)
    registry = ModelRegistry(settings)
    providers = registry.list_providers()
    assert len(providers) == len(LLMProvider)


def test_openai_configured():
    settings = Settings(_env_file=None, openai_api_key="sk-test")
    registry = ModelRegistry(settings)
    providers = registry.list_providers()
    openai = next(p for p in providers if p["provider"] == "openai")
    assert openai["status"] == "configured"


def test_openrouter_configured():
    settings = Settings(_env_file=None, openrouter_api_key="sk-or-test")
    registry = ModelRegistry(settings)
    providers = registry.list_providers()
    openrouter = next(p for p in providers if p["provider"] == "openrouter")
    assert openrouter["status"] == "configured"


def test_litellm_always_configured():
    settings = Settings(_env_file=None)
    registry = ModelRegistry(settings)
    providers = registry.list_providers()
    litellm = next(p for p in providers if p["provider"] == "litellm")
    assert litellm["status"] == "configured"


def test_ollama_always_configured():
    settings = Settings(_env_file=None)
    registry = ModelRegistry(settings)
    providers = registry.list_providers()
    ollama = next(p for p in providers if p["provider"] == "ollama")
    assert ollama["status"] == "configured"
