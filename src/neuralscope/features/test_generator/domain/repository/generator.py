"""Repository contract for test generation."""

from __future__ import annotations

from abc import ABC, abstractmethod

from neuralscope.features.test_generator.domain.entities.test_suite import TestSuite


class IGeneratorRepository(ABC):
    @abstractmethod
    async def generate_tests(self, file_path: str, source: str) -> TestSuite:
        raise NotImplementedError
