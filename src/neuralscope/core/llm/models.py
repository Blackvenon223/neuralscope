"""LLM model config."""

from __future__ import annotations

from dataclasses import dataclass

from neuralscope.core.settings import LLMProvider


@dataclass(frozen=True)
class ModelConfig:
    provider: LLMProvider
    model_name: str
    temperature: float = 0.1
    max_tokens: int | None = None

    @classmethod
    def from_string(cls, model_string: str, **kwargs: object) -> ModelConfig:
        """Parse 'provider/model_name' string.

        Supports:
            "gpt-5.2"                              → openai/gpt-5.2
            "openai/gpt-5-mini"                    → openai/gpt-5-mini
            "anthropic/claude-sonnet-4-6-20260217" → anthropic/claude-sonnet-4-6-20260217
            "google/gemini-3-pro"                  → google/gemini-3-pro
            "openrouter/deepseek/r1"               → openrouter/deepseek/r1
            "litellm/gpt-5.2"                     → litellm/gpt-5.2
        """
        if "/" not in model_string:
            return cls(provider=LLMProvider.OPENAI, model_name=model_string, **kwargs)  # type: ignore[arg-type]

        provider_str, model_name = model_string.split("/", 1)
        try:
            provider = LLMProvider(provider_str.lower())
        except ValueError:
            # Unknown prefix — treat entire string as model name for OpenAI
            return cls(provider=LLMProvider.OPENAI, model_name=model_string, **kwargs)  # type: ignore[arg-type]
        return cls(provider=provider, model_name=model_name, **kwargs)  # type: ignore[arg-type]
