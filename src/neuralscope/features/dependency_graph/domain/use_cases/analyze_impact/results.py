"""Analyze impact use case results."""

from __future__ import annotations

from dataclasses import dataclass

from neuralscope.features.dependency_graph.domain.entities.impact import ImpactReport


@dataclass(frozen=True)
class AnalyzeImpactSuccess:
    report: ImpactReport

    def is_success(self) -> bool:
        return True


@dataclass(frozen=True)
class AnalyzeImpactError:
    message: str

    def is_success(self) -> bool:
        return False


AnalyzeImpactResult = AnalyzeImpactSuccess | AnalyzeImpactError
