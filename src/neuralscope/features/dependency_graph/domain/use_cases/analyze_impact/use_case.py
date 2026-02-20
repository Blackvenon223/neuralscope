"""Analyze change impact use case."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from neuralscope.core.log_context import ILogContextRepository
from neuralscope.features.dependency_graph.domain.repository.graph_builder import (
    IGraphBuilderRepository,
)
from neuralscope.features.dependency_graph.domain.repository.impact_analyzer import (
    IImpactAnalyzerRepository,
)
from neuralscope.features.dependency_graph.domain.use_cases.analyze_impact.results import (
    AnalyzeImpactError,
    AnalyzeImpactResult,
    AnalyzeImpactSuccess,
)


@dataclass(frozen=True)
class AnalyzeImpactParams:
    path: str
    changed_files: list[str] = field(default_factory=list)


class AnalyzeImpactUseCase:
    def __init__(
        self,
        graph_repo: IGraphBuilderRepository,
        impact_repo: IImpactAnalyzerRepository,
        log_context_repository: ILogContextRepository,
    ) -> None:
        self._graph_repo = graph_repo
        self._impact_repo = impact_repo
        self._log_context = log_context_repository

    async def __call__(self, params: AnalyzeImpactParams) -> AnalyzeImpactResult:
        self._log_context.emit_input(
            path=params.path,
            changed_files=params.changed_files,
        )

        root = Path(params.path).resolve()
        if not root.is_dir():
            self._log_context.emit_result(result="error", reason="not a directory")
            return AnalyzeImpactError(f"Path is not a directory: {params.path}")

        graph = await self._graph_repo.build(str(root))
        report = await self._impact_repo.analyze(graph, params.changed_files)

        self._log_context.emit_result(
            result="success",
            affected_count=report.affected_count,
            risk=report.risk_level.value,
        )
        return AnalyzeImpactSuccess(report=report)
