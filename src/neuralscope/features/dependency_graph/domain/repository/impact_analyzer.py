"""Repository contract for impact analysis."""

from __future__ import annotations

from abc import ABC, abstractmethod

from neuralscope.features.dependency_graph.domain.entities.graph import DependencyGraph
from neuralscope.features.dependency_graph.domain.entities.impact import ImpactReport


class IImpactAnalyzerRepository(ABC):
    @abstractmethod
    async def analyze(
        self, graph: DependencyGraph, changed_files: list[str]
    ) -> ImpactReport:
        raise NotImplementedError
