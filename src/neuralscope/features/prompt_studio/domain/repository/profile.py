"""Repository contract for prompt profile management."""

from __future__ import annotations

from abc import ABC, abstractmethod

from neuralscope.features.prompt_studio.domain.entities.prompt_profile import PromptProfile


class IProfileRepository(ABC):
    @abstractmethod
    async def save(self, profile: PromptProfile) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, name: str) -> PromptProfile | None:
        raise NotImplementedError

    @abstractmethod
    async def list_all(self) -> list[PromptProfile]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, name: str) -> bool:
        raise NotImplementedError
