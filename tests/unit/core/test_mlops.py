"""Tests for MLOps infrastructure: cache and tracing."""

import time

from neuralscope.core.cache import LLMCache
from neuralscope.core.tracing import Tracer, TraceSpan


def test_cache_key_deterministic():
    cache = LLMCache.__new__(LLMCache)
    k1 = cache.key("gpt-5.2", [{"role": "user", "content": "hello"}])
    k2 = cache.key("gpt-5.2", [{"role": "user", "content": "hello"}])
    assert k1 == k2


def test_cache_key_varies_by_model():
    cache = LLMCache.__new__(LLMCache)
    k1 = cache.key("gpt-5.2", [{"role": "user", "content": "hello"}])
    k2 = cache.key("gpt-5.1", [{"role": "user", "content": "hello"}])
    assert k1 != k2


def test_cache_crud(tmp_path):
    cache = LLMCache(cache_dir=tmp_path / "cache")
    cache.set("abc", "response text")
    assert cache.get("abc") == "response text"
    assert cache.get("nonexistent") is None
    cache.clear()
    assert cache.get("abc") is None


def test_trace_span_duration():
    span = TraceSpan(operation="review", model="gpt-5.2", start_time=time.time() - 1.0)
    span.finish(output_tokens=100)
    assert span.duration_ms > 900
    assert span.output_tokens == 100
    assert span.error is None


def test_tracer_stats():
    tracer = Tracer()
    s1 = tracer.start_span("review", "gpt-5.2")
    s1.finish()
    s2 = tracer.start_span("docs", "gpt-5.2")
    s2.finish(error="timeout")

    stats = tracer.stats
    assert stats["total_calls"] == 2
    assert stats["errors"] == 1
    assert stats["avg_latency_ms"] >= 0


def test_tracer_max_spans():
    tracer = Tracer(max_spans=5)
    for i in range(10):
        tracer.start_span(f"op_{i}", "model")
    assert len(tracer.spans) == 5
