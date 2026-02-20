"""Data repository for health analysis."""

from __future__ import annotations

from neuralscope.features.health_dashboard.data.datasource.complexity_analyzer.implementation import (
    ComplexityAnalyzer,
)
from neuralscope.features.health_dashboard.domain.entities.health import HealthReport
from neuralscope.features.health_dashboard.domain.repository.health import IHealthRepository


class HealthRepository(IHealthRepository):
    def __init__(self, analyzer: ComplexityAnalyzer | None = None) -> None:
        self._analyzer = analyzer or ComplexityAnalyzer()

    async def analyze(self, project_path: str) -> HealthReport:
        return await self._analyzer.analyze(project_path)
