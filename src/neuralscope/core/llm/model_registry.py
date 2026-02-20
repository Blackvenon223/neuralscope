"""Multi-provider LLM Model Registry.

Direct providers: OpenAI, Anthropic, Google, Azure, Ollama.
LLM proxies:     OpenRouter (100+ models, one key), LiteLLM (self-hosted proxy).
"""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel

from neuralscope.core.llm.models import ModelConfig
from neuralscope.core.logging import get_logger
from neuralscope.core.settings import LLMProvider, Settings, get_settings

logger = get_logger("llm.registry")

PROVIDER_MODELS: dict[LLMProvider, str] = {
    LLMProvider.OPENAI: (
        "gpt-5.2, gpt-5.1, gpt-5, gpt-5-mini, gpt-5-nano, "
        "o3, o3-pro, o4-mini, "
        "gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, gpt-4o, gpt-4o-mini"
    ),
    LLMProvider.ANTHROPIC: (
        "claude-sonnet-4-6-20260217, claude-opus-4-6-20260205, "
        "claude-haiku-4-5-20251001, "
        "claude-sonnet-4-20250514, claude-opus-4-20250514, "
        "claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022"
    ),
    LLMProvider.GOOGLE: (
        "gemini-3-pro, gemini-3-flash, "
        "gemini-2.5-pro, gemini-2.5-flash, gemini-2.5-flash-lite, "
        "gemini-2.0-flash, gemini-1.5-pro"
    ),
    LLMProvider.AZURE: "(your Azure deployments)",
    LLMProvider.OLLAMA: (
        "llama4, llama4:scout, llama4:maverick, "
        "qwen3, qwen3:32b, qwen3:235b, qwen3-coder, "
        "deepseek-r1, deepseek-v3, deepseek-v3.1-terminus, "
        "gemma3, phi-4, mistral"
    ),
    LLMProvider.OPENROUTER: "any model via openrouter.ai (deepseek/r1, meta-llama/4, etc.)",
    LLMProvider.LITELLM: "any model via your LiteLLM proxy (mirrors provider APIs)",
}


class ModelRegistry:
    """Creates and caches LangChain LLM instances.

    Usage:
        registry = ModelRegistry()
        llm = registry.get("openai/gpt-5.2")
        llm = registry.get("anthropic/claude-sonnet-4-6-20260217")
        llm = registry.get("openrouter/deepseek/r1")
        llm = registry.get("litellm/gpt-5.2")
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._cache: dict[str, BaseChatModel] = {}

    def get(
        self,
        model_string: str | None = None,
        *,
        temperature: float = 0.1,
        max_tokens: int | None = None,
    ) -> BaseChatModel:
        if model_string is None:
            model_string = self._settings.get_model_string()

        cache_key = f"{model_string}:{temperature}:{max_tokens}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        config = ModelConfig.from_string(
            model_string, temperature=temperature, max_tokens=max_tokens
        )
        llm = self._create(config)
        self._cache[cache_key] = llm
        logger.info("Created LLM: %s (temp=%.1f)", model_string, temperature)
        return llm

    def _create(self, config: ModelConfig) -> BaseChatModel:
        factory = {
            LLMProvider.OPENAI: self._openai,
            LLMProvider.ANTHROPIC: self._anthropic,
            LLMProvider.GOOGLE: self._google,
            LLMProvider.AZURE: self._azure,
            LLMProvider.OLLAMA: self._ollama,
            LLMProvider.OPENROUTER: self._openrouter,
            LLMProvider.LITELLM: self._litellm,
        }
        builder = factory.get(config.provider)
        if builder is None:
            msg = f"Unsupported provider: {config.provider}"
            raise ValueError(msg)
        return builder(config)

    # ── Direct providers ──────────────────────────────────────────────────

    def _openai(self, config: ModelConfig) -> BaseChatModel:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            api_key=self._settings.openai_api_key,
        )

    def _anthropic(self, config: ModelConfig) -> BaseChatModel:
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens or 8192,
            api_key=self._settings.anthropic_api_key,
        )

    def _google(self, config: ModelConfig) -> BaseChatModel:
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=config.model_name,
            temperature=config.temperature,
            max_output_tokens=config.max_tokens,
            google_api_key=self._settings.google_api_key,
        )

    def _azure(self, config: ModelConfig) -> BaseChatModel:
        from langchain_openai import AzureChatOpenAI

        return AzureChatOpenAI(
            azure_deployment=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            api_key=self._settings.azure_openai_api_key,
            azure_endpoint=self._settings.azure_openai_endpoint or "",
        )

    def _ollama(self, config: ModelConfig) -> BaseChatModel:
        from langchain_community.chat_models import ChatOllama

        return ChatOllama(
            model=config.model_name,
            temperature=config.temperature,
            base_url=self._settings.ollama_base_url,
        )

    # ── LLM proxy services ────────────────────────────────────────────────

    def _openrouter(self, config: ModelConfig) -> BaseChatModel:
        """OpenRouter — 100+ models through openrouter.ai with a single API key.

        Model names pass through as-is (e.g. "deepseek/r1", "meta-llama/4").
        Uses OpenAI-compatible endpoint under the hood.
        """
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            api_key=self._settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    def _litellm(self, config: ModelConfig) -> BaseChatModel:
        """LiteLLM — self-hosted proxy that unifies any provider behind OpenAI API.

        Requires a running LiteLLM proxy (default: http://localhost:4000).
        Model name is forwarded to the proxy for routing.
        """
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            api_key=self._settings.litellm_api_key or "sk-litellm",
            base_url=self._settings.litellm_api_base,
        )

    # ── Info ───────────────────────────────────────────────────────────────

    def list_providers(self) -> list[dict[str, str]]:
        result = []
        for provider in LLMProvider:
            result.append({
                "provider": provider.value,
                "status": "configured" if self._has_credentials(provider) else "not configured",
                "models": PROVIDER_MODELS.get(provider, ""),
            })
        return result

    def _has_credentials(self, provider: LLMProvider) -> bool:
        checks: dict[LLMProvider, bool] = {
            LLMProvider.OPENAI: bool(self._settings.openai_api_key),
            LLMProvider.ANTHROPIC: bool(self._settings.anthropic_api_key),
            LLMProvider.GOOGLE: bool(self._settings.google_api_key),
            LLMProvider.AZURE: bool(self._settings.azure_openai_api_key),
            LLMProvider.OLLAMA: True,
            LLMProvider.OPENROUTER: bool(self._settings.openrouter_api_key),
            LLMProvider.LITELLM: True,
        }
        return checks.get(provider, False)
