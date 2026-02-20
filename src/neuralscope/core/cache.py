"""LLM response caching via diskcache.

Wraps LangChain LLMs to cache completions and avoid redundant API calls
during development and CI.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import diskcache

from neuralscope.core.logging import get_logger

logger = get_logger("llm_cache")

_DEFAULT_DIR = Path.home() / ".neuralscope" / "cache"


class LLMCache:
    def __init__(self, cache_dir: Path | None = None, ttl: int = 3600) -> None:
        self._dir = cache_dir or _DEFAULT_DIR
        self._cache = diskcache.Cache(str(self._dir))
        self._ttl = ttl

    def key(self, model: str, messages: list[dict[str, str]]) -> str:
        payload = json.dumps({"model": model, "messages": messages}, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

    def get(self, cache_key: str) -> str | None:
        result = self._cache.get(cache_key)
        if result is not None:
            logger.debug("Cache hit: %s", cache_key[:12])
        return result

    def set(self, cache_key: str, value: str) -> None:
        self._cache.set(cache_key, value, expire=self._ttl)

    def clear(self) -> None:
        self._cache.clear()

    @property
    def stats(self) -> dict[str, Any]:
        return {
            "directory": str(self._dir),
            "size": len(self._cache),
        }
