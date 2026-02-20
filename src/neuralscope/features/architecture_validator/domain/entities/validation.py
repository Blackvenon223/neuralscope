"""Architecture validation domain entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ViolationSeverity(str, Enum):
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class ArchRule:
    name: str
    description: str
    pattern: str = ""


@dataclass(frozen=True)
class Violation:
    rule: str
    file_path: str
    message: str
    severity: ViolationSeverity = ViolationSeverity.ERROR
    line: int = 0


@dataclass
class ValidationReport:
    project_path: str
    rules_checked: int = 0
    violations: list[Violation] = field(default_factory=list)
    summary: str = ""

    @property
    def violation_count(self) -> int:
        return len(self.violations)

    @property
    def passed(self) -> bool:
        return not any(v.severity == ViolationSeverity.ERROR for v in self.violations)
