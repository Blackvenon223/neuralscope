"""Wide logging context for use cases (ILogContextRepository pattern from rules.md)."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any

from neuralscope.core.logging import get_logger

logger = get_logger("log_context")


class ILogContextRepository(ABC):
    """Interface for wide logging in use cases.

    Every use case must:
    1. Call emit_input() before business logic
    2. Call emit_result() before every return
    """

    @abstractmethod
    def emit_input(self, **kwargs: Any) -> None:
        """Log use case input parameters."""
        raise NotImplementedError

    @abstractmethod
    def emit_result(self, *, result: str, **kwargs: Any) -> None:
        """Log use case result (success/error/specific status)."""
        raise NotImplementedError


class LogContextRepository(ILogContextRepository):
    """Default implementation: logs to structured logger."""

    def __init__(self, use_case_name: str) -> None:
        self._use_case = use_case_name
        self._start_time: float | None = None

    def emit_input(self, **kwargs: Any) -> None:
        """Log input and start timer."""
        self._start_time = time.monotonic()
        context = " ".join(f"{k}={v}" for k, v in kwargs.items())
        logger.info("USE_CASE_INPUT | %s | %s", self._use_case, context)

    def emit_result(self, *, result: str, **kwargs: Any) -> None:
        """Log result with elapsed time."""
        elapsed = (
            f"{time.monotonic() - self._start_time:.3f}s" if self._start_time else "n/a"
        )
        context = " ".join(f"{k}={v}" for k, v in kwargs.items())
        logger.info(
            "USE_CASE_RESULT | %s | result=%s | elapsed=%s | %s",
            self._use_case,
            result,
            elapsed,
            context,
        )
