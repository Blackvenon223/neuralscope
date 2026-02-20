"""Build dependency graph use case."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from neuralscope.core.log_context import ILogContextRepository
from neuralscope.features.dependency_graph.data.datasource.graph_renderer.implementation import (
    GraphRenderer,
    OutputFormat,
)
from neuralscope.features.dependency_graph.domain.repository.graph_builder import (
    IGraphBuilderRepository,
)
from neuralscope.features.dependency_graph.domain.use_cases.build_graph.results import (
    BuildGraphError,
    BuildGraphResult,
    BuildGraphSuccess,
)


@dataclass(frozen=True)
class BuildGraphParams:
    path: str
    output_format: str = "json"
    mode: str = "ast"


class BuildGraphUseCase:
    def __init__(
        self,
        graph_repo: IGraphBuilderRepository,
        log_context_repository: ILogContextRepository,
    ) -> None:
        self._graph_repo = graph_repo
        self._log_context = log_context_repository
        self._renderer = GraphRenderer()

    async def __call__(self, params: BuildGraphParams) -> BuildGraphResult:
        self._log_context.emit_input(path=params.path, format=params.output_format)

        root = Path(params.path).resolve()
        if not root.is_dir():
            self._log_context.emit_result(result="error", reason="not a directory")
            return BuildGraphError(f"Path is not a directory: {params.path}")

        graph = await self._graph_repo.build(str(root), mode=params.mode)

        try:
            fmt = OutputFormat(params.output_format)
        except ValueError:
            fmt = OutputFormat.JSON

        rendered = self._renderer.render(graph, fmt)

        self._log_context.emit_result(
            result="success",
            nodes=graph.node_count,
            edges=graph.edge_count,
        )
        return BuildGraphSuccess(graph=graph, rendered=rendered)
