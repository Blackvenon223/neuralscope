"""Dependency graph domain entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class NodeKind(str, Enum):
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    PACKAGE = "package"


@dataclass(frozen=True)
class GraphNode:
    id: str
    name: str
    kind: NodeKind
    file_path: str
    line: int = 0
    docstring: str | None = None


@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    relation: str = "imports"


@dataclass
class DependencyGraph:
    root_path: str
    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    def get_node(self, node_id: str) -> GraphNode | None:
        return next((n for n in self.nodes if n.id == node_id), None)

    def get_dependents(self, node_id: str) -> list[str]:
        return [e.source for e in self.edges if e.target == node_id]

    def get_dependencies(self, node_id: str) -> list[str]:
        return [e.target for e in self.edges if e.source == node_id]
