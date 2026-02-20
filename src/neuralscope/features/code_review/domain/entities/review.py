"""Code review domain entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class IssueCategory(str, Enum):
    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"
    MAINTAINABILITY = "maintainability"
    COMPLEXITY = "complexity"
    NAMING = "naming"
    DOCUMENTATION = "documentation"


@dataclass(frozen=True)
class Issue:
    line: int
    message: str
    severity: Severity
    category: IssueCategory
    suggestion: str = ""


@dataclass
class ReviewResult:
    file_path: str
    score: float
    summary: str
    issues: list[Issue] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.CRITICAL)

    @property
    def passed(self) -> bool:
        return self.score >= 7.0 and self.critical_count == 0
