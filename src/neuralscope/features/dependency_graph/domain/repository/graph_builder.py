"""Repository contract for graph building."""

from __future__ import annotations

from abc import ABC, abstractmethod

from neuralscope.features.dependency_graph.domain.entities.graph import DependencyGraph


class IGraphBuilderRepository(ABC):
    @abstractmethod
    async def build(self, root_path: str, *, mode: str = "ast") -> DependencyGraph:
        raise NotImplementedError
