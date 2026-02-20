"""File indexer: walks project, splits source into chunks for vector indexing."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from neuralscope.features.codebase_qa.domain.entities.answer import SourceReference

SKIP_DIRS = {".venv", "venv", "__pycache__", ".git", "node_modules", ".tox"}


@dataclass
class CodeChunk:
    file_path: str
    content: str
    line_start: int
    line_end: int

    def to_source_ref(self, snippet: str = "") -> SourceReference:
        return SourceReference(
            file_path=self.file_path,
            line_start=self.line_start,
            line_end=self.line_end,
            snippet=snippet or self.content[:200],
        )


class FileIndexer:
    """Walks .py files and produces chunks suitable for embedding."""

    def __init__(self, max_chunk_lines: int = 60) -> None:
        self._max_lines = max_chunk_lines

    def index(self, project_path: str) -> list[CodeChunk]:
        root = Path(project_path)
        chunks: list[CodeChunk] = []

        for f in sorted(root.rglob("*.py")):
            if self._skip(f, root):
                continue
            try:
                source = f.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if not source.strip():
                continue

            rel = str(f.relative_to(root))
            file_chunks = self._chunk_by_ast(rel, source)
            if not file_chunks:
                file_chunks = self._chunk_by_lines(rel, source)
            chunks.extend(file_chunks)

        return chunks

    def _chunk_by_ast(self, file_path: str, source: str) -> list[CodeChunk]:
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []

        lines = source.splitlines()
        chunks: list[CodeChunk] = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start = node.lineno
                end = node.end_lineno or start
                body = "\n".join(lines[start - 1 : end])
                chunks.append(CodeChunk(
                    file_path=file_path,
                    content=body,
                    line_start=start,
                    line_end=end,
                ))

        if not chunks and lines:
            chunks.append(CodeChunk(
                file_path=file_path,
                content=source[:3000],
                line_start=1,
                line_end=len(lines),
            ))

        return chunks

    def _chunk_by_lines(self, file_path: str, source: str) -> list[CodeChunk]:
        lines = source.splitlines()
        chunks: list[CodeChunk] = []
        for i in range(0, len(lines), self._max_lines):
            batch = lines[i : i + self._max_lines]
            chunks.append(CodeChunk(
                file_path=file_path,
                content="\n".join(batch),
                line_start=i + 1,
                line_end=i + len(batch),
            ))
        return chunks

    @staticmethod
    def _skip(path: Path, root: Path) -> bool:
        return bool(SKIP_DIRS & set(path.relative_to(root).parts))
