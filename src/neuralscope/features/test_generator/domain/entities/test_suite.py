"""Test generator domain entities."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TestCase:
    name: str
    body: str
    description: str = ""


@dataclass
class TestSuite:
    source_file: str
    test_cases: list[TestCase] = field(default_factory=list)
    rendered: str = ""

    @property
    def count(self) -> int:
        return len(self.test_cases)
