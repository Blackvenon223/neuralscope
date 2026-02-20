"""Application settings."""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"
    LITELLM = "litellm"


class QdrantMode(str, Enum):
    MEMORY = "memory"
    SERVER = "server"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="NEURALSCOPE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    # LLM
    llm_provider: LLMProvider = LLMProvider.OPENAI
    llm_model: str = "gpt-5.2"

    # Direct provider keys
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    google_api_key: str | None = Field(default=None, alias="GOOGLE_API_KEY")
    azure_openai_api_key: str | None = Field(default=None, alias="AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: str | None = Field(default=None, alias="AZURE_OPENAI_ENDPOINT")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")

    # LLM proxy services
    openrouter_api_key: str | None = Field(default=None, alias="OPENROUTER_API_KEY")
    litellm_api_base: str = Field(default="http://localhost:4000", alias="LITELLM_API_BASE")
    litellm_api_key: str | None = Field(default=None, alias="LITELLM_API_KEY")

    # Qdrant
    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_mode: QdrantMode = Field(default=QdrantMode.MEMORY, alias="QDRANT_MODE")

    # MLOps
    langsmith_api_key: str | None = Field(default=None, alias="LANGSMITH_API_KEY")
    langsmith_tracing: bool = Field(default=False, alias="LANGSMITH_TRACING")

    # General
    log_level: str = "INFO"
    cache_enabled: bool = True
    profiles_dir: Path = Path.home() / ".neuralscope" / "profiles"

    def get_model_string(self) -> str:
        return f"{self.llm_provider.value}/{self.llm_model}"


def get_settings() -> Settings:
    return Settings()
