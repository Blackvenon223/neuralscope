"""Codebase Q&A domain entities."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SourceReference:
    file_path: str
    line_start: int = 0
    line_end: int = 0
    snippet: str = ""


@dataclass
class Answer:
    question: str
    answer: str
    sources: list[SourceReference] = field(default_factory=list)
    confidence: float = 0.0

    @property
    def source_count(self) -> int:
        return len(self.sources)
