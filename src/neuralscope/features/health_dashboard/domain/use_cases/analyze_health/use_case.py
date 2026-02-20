"""Analyze health use case."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from neuralscope.core.log_context import ILogContextRepository
from neuralscope.features.health_dashboard.domain.entities.health import HealthReport
from neuralscope.features.health_dashboard.domain.repository.health import IHealthRepository


@dataclass(frozen=True)
class AnalyzeHealthParams:
    path: str


@dataclass(frozen=True)
class AnalyzeHealthSuccess:
    report: HealthReport
    def is_success(self) -> bool:
        return True


@dataclass(frozen=True)
class AnalyzeHealthError:
    message: str
    def is_success(self) -> bool:
        return False


class AnalyzeHealthUseCase:
    def __init__(
        self,
        health_repo: IHealthRepository,
        log_context_repository: ILogContextRepository,
    ) -> None:
        self._health = health_repo
        self._log_context = log_context_repository

    async def __call__(
        self, params: AnalyzeHealthParams,
    ) -> AnalyzeHealthSuccess | AnalyzeHealthError:
        self._log_context.emit_input(path=params.path)

        root = Path(params.path).resolve()
        if not root.is_dir():
            self._log_context.emit_result(result="error", reason="not a directory")
            return AnalyzeHealthError(f"Path is not a directory: {params.path}")

        try:
            report = await self._health.analyze(str(root))
        except Exception as exc:
            self._log_context.emit_result(result="error", reason=str(exc))
            return AnalyzeHealthError(f"Health analysis failed: {exc}")

        self._log_context.emit_result(
            result="success",
            files=report.total_files,
            score=report.health_score,
        )
        return AnalyzeHealthSuccess(report=report)
