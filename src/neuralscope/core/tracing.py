"""LLM call tracing for observability and evaluation.

Captures call metadata (model, latency, tokens) for debugging,
cost tracking, and integration with LangSmith or custom backends.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from neuralscope.core.logging import get_logger

logger = get_logger("llm_tracing")


@dataclass
class TraceSpan:
    operation: str
    model: str
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    @property
    def duration_ms(self) -> float:
        if self.end_time == 0.0:
            return 0.0
        return (self.end_time - self.start_time) * 1000

    def finish(self, *, output_tokens: int = 0, error: str | None = None) -> None:
        self.end_time = time.time()
        self.output_tokens = output_tokens
        self.error = error


class Tracer:
    """In-memory trace collector. Integrates with LangSmith when configured."""

    def __init__(self, max_spans: int = 1000) -> None:
        self._spans: list[TraceSpan] = []
        self._max = max_spans

    def start_span(self, operation: str, model: str, **metadata: Any) -> TraceSpan:
        span = TraceSpan(operation=operation, model=model, metadata=metadata)
        self._spans.append(span)
        if len(self._spans) > self._max:
            self._spans = self._spans[-self._max:]
        return span

    @property
    def spans(self) -> list[TraceSpan]:
        return list(self._spans)

    @property
    def stats(self) -> dict[str, Any]:
        total = len(self._spans)
        errors = sum(1 for s in self._spans if s.error)
        avg_ms = 0.0
        finished = [s for s in self._spans if s.end_time > 0]
        if finished:
            avg_ms = sum(s.duration_ms for s in finished) / len(finished)
        return {
            "total_calls": total,
            "errors": errors,
            "avg_latency_ms": round(avg_ms, 1),
        }

    def clear(self) -> None:
        self._spans.clear()
