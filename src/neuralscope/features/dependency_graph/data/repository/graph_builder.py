"""Data layer implementation of graph builder repository.

Supports two modes:
- AST: fast, offline, deterministic — parses Python AST
- LLM: AI-powered, finds architectural patterns AST can't detect
"""

from __future__ import annotations

from pathlib import Path

from langchain_core.language_models import BaseChatModel

from neuralscope.features.dependency_graph.data.datasource.ast_parser.implementation import (
    AstParser,
)
from neuralscope.features.dependency_graph.data.datasource.llm_graph_analyzer.implementation import (  # noqa: E501
    LlmGraphAnalyzer,
)
from neuralscope.features.dependency_graph.domain.entities.graph import DependencyGraph
from neuralscope.features.dependency_graph.domain.repository.graph_builder import (
    IGraphBuilderRepository,
)

SKIP_DIRS = {".venv", "venv", "__pycache__", ".git", "node_modules", ".tox"}


class GraphBuilderRepository(IGraphBuilderRepository):
    def __init__(self, llm: BaseChatModel | None = None) -> None:
        self._llm = llm

    async def build(self, root_path: str, *, mode: str = "ast") -> DependencyGraph:
        if mode == "llm" and self._llm is not None:
            return await self._build_llm(root_path)
        return await self._build_ast(root_path)

    async def _build_ast(self, root_path: str) -> DependencyGraph:
        parser = AstParser(Path(root_path))
        nodes, edges = parser.parse()
        return DependencyGraph(root_path=root_path, nodes=nodes, edges=edges)

    async def _build_llm(self, root_path: str) -> DependencyGraph:
        root = Path(root_path)
        files: dict[str, str] = {}
        for f in sorted(root.rglob("*.py")):
            if self._skip(f, root):
                continue
            try:
                source = f.read_text(encoding="utf-8")
                if source.strip():
                    files[str(f.relative_to(root))] = source
            except (OSError, UnicodeDecodeError):
                continue

        analyzer = LlmGraphAnalyzer(self._llm)
        return await analyzer.analyze(root_path, files)

    @staticmethod
    def _skip(path: Path, root: Path) -> bool:
        return bool(SKIP_DIRS & set(path.relative_to(root).parts))
