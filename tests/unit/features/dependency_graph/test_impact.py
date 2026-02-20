"""Tests for impact analysis."""

import pytest

from neuralscope.features.dependency_graph.data.repository.impact_analyzer import (
    ImpactAnalyzerRepository,
)
from neuralscope.features.dependency_graph.domain.entities.graph import (
    DependencyGraph,
    GraphEdge,
    GraphNode,
    NodeKind,
)
from neuralscope.features.dependency_graph.domain.entities.impact import RiskLevel


def _project_graph() -> DependencyGraph:
    return DependencyGraph(
        root_path="/project",
        nodes=[
            GraphNode(id="main", name="main", kind=NodeKind.MODULE, file_path="main.py"),
            GraphNode(id="auth", name="auth", kind=NodeKind.MODULE, file_path="auth.py"),
            GraphNode(id="db", name="db", kind=NodeKind.MODULE, file_path="db.py"),
            GraphNode(id="utils", name="utils", kind=NodeKind.MODULE, file_path="utils.py"),
        ],
        edges=[
            GraphEdge(source="main", target="auth"),
            GraphEdge(source="auth", target="db"),
            GraphEdge(source="auth", target="utils"),
            GraphEdge(source="main", target="utils"),
        ],
    )


@pytest.mark.asyncio
async def test_impact_on_utils():
    repo = ImpactAnalyzerRepository()
    report = await repo.analyze(_project_graph(), ["utils.py"])

    assert report.affected_count > 0
    affected_names = {a.name for a in report.affected}
    assert "auth" in affected_names or "main" in affected_names


@pytest.mark.asyncio
async def test_no_impact_on_leaf():
    repo = ImpactAnalyzerRepository()
    graph = DependencyGraph(
        root_path="/project",
        nodes=[
            GraphNode(id="a", name="a", kind=NodeKind.MODULE, file_path="a.py"),
        ],
        edges=[],
    )
    report = await repo.analyze(graph, ["a.py"])
    assert report.affected_count == 0
    assert report.risk_level == RiskLevel.LOW


@pytest.mark.asyncio
async def test_cascade_risk_level():
    repo = ImpactAnalyzerRepository()
    report = await repo.analyze(_project_graph(), ["db.py"])
    assert report.risk_level in {RiskLevel.HIGH, RiskLevel.MEDIUM, RiskLevel.CRITICAL}
