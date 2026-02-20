"""Repository contracts for codebase Q&A."""

from __future__ import annotations

from abc import ABC, abstractmethod

from neuralscope.features.codebase_qa.domain.entities.answer import Answer


class IQARepository(ABC):
    @abstractmethod
    async def index_project(self, project_path: str) -> int:
        """Index project files into vector store. Returns number of indexed chunks."""
        raise NotImplementedError

    @abstractmethod
    async def ask(self, question: str, project_path: str) -> Answer:
        raise NotImplementedError
