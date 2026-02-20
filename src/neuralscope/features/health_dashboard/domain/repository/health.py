"""Repository contract for health analysis."""

from __future__ import annotations

from abc import ABC, abstractmethod

from neuralscope.features.health_dashboard.domain.entities.health import HealthReport


class IHealthRepository(ABC):
    @abstractmethod
    async def analyze(self, project_path: str) -> HealthReport:
        raise NotImplementedError
