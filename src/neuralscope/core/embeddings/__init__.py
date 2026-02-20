"""Embeddings service for RAG (Qdrant)."""

from __future__ import annotations

from typing import Optional

from langchain_core.embeddings import Embeddings

from neuralscope.core.logging import get_logger
from neuralscope.core.settings import LLMProvider, Settings, get_settings

logger = get_logger("embeddings")


class EmbeddingsService:
    """Creates embedding models for vector search.

    Follows the LLM provider setting by default.
    OpenRouter and LiteLLM proxy through OpenAI embeddings endpoint.
    Anthropic falls back to OpenAI (no native embeddings API).
    """

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self._settings = settings or get_settings()
        self._cache: Optional[Embeddings] = None

    def get(self, provider: Optional[str] = None) -> Embeddings:
        if self._cache is not None and provider is None:
            return self._cache

        resolved = LLMProvider(provider) if provider else self._settings.llm_provider
        embeddings = self._create(resolved)

        if provider is None:
            self._cache = embeddings
        return embeddings

    def _create(self, provider: LLMProvider) -> Embeddings:
        match provider:
            case LLMProvider.OPENAI:
                return self._openai_embeddings(
                    api_key=self._settings.openai_api_key,
                )
            case LLMProvider.GOOGLE:
                from langchain_google_genai import GoogleGenerativeAIEmbeddings

                return GoogleGenerativeAIEmbeddings(
                    model="models/text-embedding-004",
                    google_api_key=self._settings.google_api_key,
                )
            case LLMProvider.OLLAMA:
                from langchain_community.embeddings import OllamaEmbeddings

                return OllamaEmbeddings(
                    model="nomic-embed-text",
                    base_url=self._settings.ollama_base_url,
                )
            case LLMProvider.AZURE:
                from langchain_openai import AzureOpenAIEmbeddings

                return AzureOpenAIEmbeddings(
                    azure_deployment="text-embedding-3-small",
                    api_key=self._settings.azure_openai_api_key,
                    azure_endpoint=self._settings.azure_openai_endpoint or "",
                )
            case LLMProvider.OPENROUTER:
                return self._openai_embeddings(
                    api_key=self._settings.openrouter_api_key,
                    base_url="https://openrouter.ai/api/v1",
                )
            case LLMProvider.LITELLM:
                return self._openai_embeddings(
                    api_key=self._settings.litellm_api_key or "sk-litellm",
                    base_url=self._settings.litellm_api_base,
                )
            case _:
                logger.warning("No native embeddings for %s, using OpenAI", provider.value)
                return self._openai_embeddings(
                    api_key=self._settings.openai_api_key,
                )

    @staticmethod
    def _openai_embeddings(
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> Embeddings:
        from langchain_openai import OpenAIEmbeddings

        kwargs: dict = {"model": "text-embedding-3-small"}
        if api_key:
            kwargs["api_key"] = api_key
        if base_url:
            kwargs["base_url"] = base_url
        return OpenAIEmbeddings(**kwargs)
