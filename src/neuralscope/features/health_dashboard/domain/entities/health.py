"""Health dashboard domain entities."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ComplexityMetric:
    file_path: str
    function_name: str
    complexity: int
    rank: str = "A"


@dataclass
class HealthReport:
    project_path: str
    total_files: int = 0
    total_lines: int = 0
    avg_complexity: float = 0.0
    test_coverage: float | None = None
    dependency_count: int = 0
    hotspots: list[ComplexityMetric] = field(default_factory=list)
    summary: str = ""

    @property
    def health_score(self) -> float:
        score = 10.0
        if self.avg_complexity > 10:
            score -= 2.0
        elif self.avg_complexity > 5:
            score -= 1.0
        if self.test_coverage is not None and self.test_coverage < 60:
            score -= 2.0
        if len(self.hotspots) > 5:
            score -= 1.0
        return max(0.0, score)
