"""Repository contract for documentation generation."""

from __future__ import annotations

from abc import ABC, abstractmethod

from neuralscope.features.documentation.domain.entities.document import GeneratedDoc


class IDocumenterRepository(ABC):
    @abstractmethod
    async def generate_file_docs(self, file_path: str, source: str) -> GeneratedDoc:
        raise NotImplementedError
