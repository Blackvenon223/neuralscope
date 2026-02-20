"""Generate file documentation use case."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from neuralscope.core.log_context import ILogContextRepository
from neuralscope.features.documentation.domain.entities.document import DocFormat
from neuralscope.features.documentation.domain.repository.documenter import (
    IDocumenterRepository,
)
from neuralscope.features.documentation.domain.use_cases.generate_file_docs.results import (
    GenerateDocsError,
    GenerateDocsResult,
    GenerateDocsSuccess,
)


@dataclass(frozen=True)
class GenerateFileDocsParams:
    path: str
    format: str = "markdown"


class GenerateFileDocsUseCase:
    def __init__(
        self,
        documenter_repo: IDocumenterRepository,
        log_context_repository: ILogContextRepository,
    ) -> None:
        self._documenter = documenter_repo
        self._log_context = log_context_repository

    async def __call__(self, params: GenerateFileDocsParams) -> GenerateDocsResult:
        self._log_context.emit_input(path=params.path, format=params.format)

        file_path = Path(params.path)
        if not file_path.is_file():
            self._log_context.emit_result(result="error", reason="file not found")
            return GenerateDocsError(f"File not found: {params.path}")

        try:
            source = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            self._log_context.emit_result(result="error", reason=str(exc))
            return GenerateDocsError(f"Cannot read file: {exc}")

        try:
            doc = await self._documenter.generate_file_docs(str(file_path), source)
        except Exception as exc:
            self._log_context.emit_result(result="error", reason=str(exc))
            return GenerateDocsError(f"Documentation generation failed: {exc}")

        doc.rendered = self._render(doc, params.format)

        self._log_context.emit_result(
            result="success",
            items=doc.item_count,
        )
        return GenerateDocsSuccess(doc=doc)

    @staticmethod
    def _render(doc, fmt: str) -> str:
        lines = [f"# {Path(doc.file_path).name}", ""]
        if doc.module_docstring:
            lines.extend([doc.module_docstring, ""])

        for cls in doc.classes:
            lines.append(f"## Class `{cls.name}`")
            if cls.bases:
                lines.append(f"Inherits: {', '.join(cls.bases)}")
            lines.extend(["", cls.docstring, ""])
            for method in cls.methods:
                lines.append(f"### `{method.signature}`")
                lines.extend([method.docstring, ""])

        for func in doc.functions:
            lines.append(f"## `{func.signature}`")
            lines.extend([func.docstring, ""])

        return "\n".join(lines)
