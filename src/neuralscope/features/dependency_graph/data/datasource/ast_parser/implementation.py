"""AST-based Python import parser.

Walks a project tree, parses each .py file with `ast`, and extracts:
- module-level imports (import X, from X import Y)
- class and function definitions
- cross-module dependencies as edges
"""

from __future__ import annotations

import ast
from pathlib import Path

from neuralscope.core.logging import get_logger
from neuralscope.features.dependency_graph.domain.entities.graph import (
    GraphEdge,
    GraphNode,
    NodeKind,
)

logger = get_logger("ast_parser")


class AstParser:
    """Parses a Python project into nodes and edges using the `ast` module."""

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def parse(self) -> tuple[list[GraphNode], list[GraphEdge]]:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []

        py_files = sorted(self._root.rglob("*.py"))
        for file_path in py_files:
            if self._should_skip(file_path):
                continue
            file_nodes, file_edges = self._parse_file(file_path)
            nodes.extend(file_nodes)
            edges.extend(file_edges)

        return nodes, edges

    def _parse_file(
        self, file_path: Path
    ) -> tuple[list[GraphNode], list[GraphEdge]]:
        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except (SyntaxError, UnicodeDecodeError) as exc:
            logger.warning("Skipping %s: %s", file_path, exc)
            return [], []

        rel = file_path.relative_to(self._root)
        module_id = self._path_to_module_id(rel)

        nodes: list[GraphNode] = [
            GraphNode(
                id=module_id,
                name=rel.stem,
                kind=NodeKind.MODULE,
                file_path=str(rel),
                line=1,
                docstring=ast.get_docstring(tree),
            )
        ]

        edges: list[GraphEdge] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_id = f"{module_id}.{node.name}"
                nodes.append(
                    GraphNode(
                        id=class_id,
                        name=node.name,
                        kind=NodeKind.CLASS,
                        file_path=str(rel),
                        line=node.lineno,
                        docstring=ast.get_docstring(node),
                    )
                )

            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                func_id = f"{module_id}.{node.name}"
                nodes.append(
                    GraphNode(
                        id=func_id,
                        name=node.name,
                        kind=NodeKind.FUNCTION,
                        file_path=str(rel),
                        line=node.lineno,
                        docstring=ast.get_docstring(node),
                    )
                )

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    edges.append(
                        GraphEdge(source=module_id, target=alias.name, relation="imports")
                    )

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    edges.append(
                        GraphEdge(
                            source=module_id,
                            target=node.module,
                            relation="imports",
                        )
                    )

        return nodes, edges

    def _should_skip(self, file_path: Path) -> bool:
        parts = file_path.relative_to(self._root).parts
        skip_dirs = {".venv", "venv", "__pycache__", ".git", "node_modules", ".tox", ".nox"}
        return bool(skip_dirs & set(parts))

    @staticmethod
    def _path_to_module_id(rel_path: Path) -> str:
        """Convert relative path to dotted module id: src/foo/bar.py → src.foo.bar"""
        parts = list(rel_path.parts)
        if parts[-1] == "__init__.py":
            parts = parts[:-1]
        else:
            parts[-1] = parts[-1].removesuffix(".py")
        return ".".join(parts)
