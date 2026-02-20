"""Graph rendering to DOT/SVG/JSON formats."""

from __future__ import annotations

import json
from enum import Enum

import networkx as nx

from neuralscope.features.dependency_graph.domain.entities.graph import (
    DependencyGraph,
    NodeKind,
)


class OutputFormat(str, Enum):
    DOT = "dot"
    JSON = "json"
    SVG = "svg"


NODE_COLORS = {
    NodeKind.PACKAGE: "#6366f1",
    NodeKind.MODULE: "#3b82f6",
    NodeKind.CLASS: "#10b981",
    NodeKind.FUNCTION: "#f59e0b",
}


class GraphRenderer:
    """Renders a DependencyGraph to various output formats."""

    def render(self, graph: DependencyGraph, fmt: OutputFormat = OutputFormat.DOT) -> str:
        nxg = self._to_networkx(graph)
        match fmt:
            case OutputFormat.DOT:
                return self._to_dot(nxg, graph)
            case OutputFormat.JSON:
                return self._to_json(graph)
            case OutputFormat.SVG:
                return self._to_svg(nxg, graph)

    def _to_networkx(self, graph: DependencyGraph) -> nx.DiGraph:
        g = nx.DiGraph()
        for node in graph.nodes:
            g.add_node(node.id, label=node.name, kind=node.kind.value)
        for edge in graph.edges:
            g.add_edge(edge.source, edge.target, relation=edge.relation)
        return g

    def _to_dot(self, _nxg: nx.DiGraph, graph: DependencyGraph) -> str:
        lines = ["digraph DependencyGraph {"]
        lines.append("  rankdir=LR;")
        lines.append('  node [shape=box, style="rounded,filled", fontname="Inter"];')
        lines.append("")

        for node in graph.nodes:
            color = NODE_COLORS.get(node.kind, "#94a3b8")
            lines.append(
                f'  "{node.id}" [label="{node.name}", fillcolor="{color}", fontcolor="white"];'
            )

        lines.append("")
        for edge in graph.edges:
            lines.append(f'  "{edge.source}" -> "{edge.target}" [label="{edge.relation}"];')

        lines.append("}")
        return "\n".join(lines)

    def _to_json(self, graph: DependencyGraph) -> str:
        data = {
            "root": graph.root_path,
            "nodes": [
                {
                    "id": n.id,
                    "name": n.name,
                    "kind": n.kind.value,
                    "file": n.file_path,
                    "line": n.line,
                }
                for n in graph.nodes
            ],
            "edges": [
                {"source": e.source, "target": e.target, "relation": e.relation}
                for e in graph.edges
            ],
            "stats": {
                "nodes": graph.node_count,
                "edges": graph.edge_count,
            },
        }
        return json.dumps(data, indent=2)

    def _to_svg(self, nxg: nx.DiGraph, graph: DependencyGraph) -> str:
        try:
            from graphviz import Source

            dot = self._to_dot(nxg, graph)
            src = Source(dot)
            return src.pipe(format="svg").decode("utf-8")
        except ImportError:
            return self._to_dot(nxg, graph)
