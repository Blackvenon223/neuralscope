"""Build graph use case results."""

from __future__ import annotations

from dataclasses import dataclass

from neuralscope.features.dependency_graph.domain.entities.graph import DependencyGraph


@dataclass(frozen=True)
class BuildGraphSuccess:
    graph: DependencyGraph
    rendered: str

    def is_success(self) -> bool:
        return True


@dataclass(frozen=True)
class BuildGraphError:
    message: str

    def is_success(self) -> bool:
        return False


BuildGraphResult = BuildGraphSuccess | BuildGraphError
