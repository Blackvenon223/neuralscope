"""Complexity analyzer datasource using radon."""

from __future__ import annotations

from pathlib import Path

from neuralscope.core.logging import get_logger
from neuralscope.features.health_dashboard.domain.entities.health import (
    ComplexityMetric,
    HealthReport,
)

logger = get_logger("complexity_analyzer")


class ComplexityAnalyzer:
    """Analyzes Python project complexity using file metrics."""

    async def analyze(self, project_path: str) -> HealthReport:
        root = Path(project_path)
        py_files = list(root.rglob("*.py"))
        py_files = [f for f in py_files if not self._should_skip(f, root)]

        total_lines = 0
        complexities: list[int] = []
        hotspots: list[ComplexityMetric] = []

        for f in py_files:
            try:
                lines = f.read_text(encoding="utf-8").splitlines()
                total_lines += len(lines)
                cc = self._estimate_complexity(lines)
                complexities.append(cc)
                if cc > 5:
                    hotspots.append(
                        ComplexityMetric(
                            file_path=str(f.relative_to(root)),
                            function_name="(module)",
                            complexity=cc,
                            rank="C" if cc > 10 else "B",
                        )
                    )
            except (OSError, UnicodeDecodeError):
                continue

        avg_cc = sum(complexities) / len(complexities) if complexities else 0.0
        hotspots.sort(key=lambda h: h.complexity, reverse=True)

        return HealthReport(
            project_path=project_path,
            total_files=len(py_files),
            total_lines=total_lines,
            avg_complexity=round(avg_cc, 2),
            dependency_count=0,
            hotspots=hotspots[:10],
        )

    @staticmethod
    def _estimate_complexity(lines: list[str]) -> int:
        """Simple cyclomatic complexity estimate by counting branches."""
        branch_keywords = {"if", "elif", "for", "while", "except", "with", "and", "or"}
        count = 1
        for line in lines:
            stripped = line.strip()
            first_word = stripped.split("(")[0].split(":")[0].split(" ")[0]
            if first_word in branch_keywords:
                count += 1
        return count

    @staticmethod
    def _should_skip(file_path: Path, root: Path) -> bool:
        parts = file_path.relative_to(root).parts
        skip = {".venv", "venv", "__pycache__", ".git", "node_modules"}
        return bool(skip & set(parts))
