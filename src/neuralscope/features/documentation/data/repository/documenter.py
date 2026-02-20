"""Data repository for documentation generation."""

from __future__ import annotations

from neuralscope.features.documentation.data.datasource.llm_documenter.implementation import (
    LlmDocumenterDatasource,
)
from neuralscope.features.documentation.domain.entities.document import GeneratedDoc
from neuralscope.features.documentation.domain.repository.documenter import (
    IDocumenterRepository,
)


class DocumenterRepository(IDocumenterRepository):
    def __init__(self, datasource: LlmDocumenterDatasource) -> None:
        self._ds = datasource

    async def generate_file_docs(self, file_path: str, source: str) -> GeneratedDoc:
        return await self._ds.generate(file_path, source)
