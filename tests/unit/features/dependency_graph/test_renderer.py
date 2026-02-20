"""Tests for graph renderer."""

import json

from neuralscope.features.dependency_graph.data.datasource.graph_renderer.implementation import (
    GraphRenderer,
    OutputFormat,
)
from neuralscope.features.dependency_graph.domain.entities.graph import (
    DependencyGraph,
    GraphEdge,
    GraphNode,
    NodeKind,
)


def _sample_graph() -> DependencyGraph:
    return DependencyGraph(
        root_path="/project",
        nodes=[
            GraphNode(id="app", name="app", kind=NodeKind.MODULE, file_path="app.py"),
            GraphNode(id="utils", name="utils", kind=NodeKind.MODULE, file_path="utils.py"),
            GraphNode(id="app.Server", name="Server", kind=NodeKind.CLASS, file_path="app.py"),
        ],
        edges=[
            GraphEdge(source="app", target="utils", relation="imports"),
        ],
    )


def test_render_dot():
    renderer = GraphRenderer()
    dot = renderer.render(_sample_graph(), OutputFormat.DOT)
    assert "digraph DependencyGraph" in dot
    assert '"app" -> "utils"' in dot
    assert '"app.Server"' in dot


def test_render_json():
    renderer = GraphRenderer()
    raw = renderer.render(_sample_graph(), OutputFormat.JSON)
    data = json.loads(raw)
    assert data["stats"]["nodes"] == 3
    assert data["stats"]["edges"] == 1
    assert len(data["nodes"]) == 3
    assert len(data["edges"]) == 1


def test_render_svg_fallback_without_graphviz():
    renderer = GraphRenderer()
    result = renderer.render(_sample_graph(), OutputFormat.SVG)
    assert "digraph" in result or "<svg" in result
