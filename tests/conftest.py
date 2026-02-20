"""Test configuration and shared fixtures."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from neuralscope.core.settings import Settings


@pytest.fixture
def mock_settings() -> Settings:
    """Settings with test defaults (no real API keys)."""
    return Settings(
        llm_provider="openai",
        llm_model="gpt-4o-mini",
        openai_api_key="sk-test-fake-key",
        log_level="DEBUG",
        cache_enabled=False,
        qdrant_mode="memory",
    )


@pytest.fixture
def mock_llm() -> MagicMock:
    """Mock LangChain LLM that returns predictable responses."""
    llm = MagicMock()
    llm.ainvoke = AsyncMock(return_value=MagicMock(content="Mock LLM response"))
    llm.invoke = MagicMock(return_value=MagicMock(content="Mock LLM response"))
    return llm
