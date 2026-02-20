"""Data repository for test generation."""

from __future__ import annotations

from neuralscope.features.test_generator.data.datasource.llm_test_writer.implementation import (
    LlmTestWriterDatasource,
)
from neuralscope.features.test_generator.domain.entities.test_suite import TestSuite
from neuralscope.features.test_generator.domain.repository.generator import IGeneratorRepository


class GeneratorRepository(IGeneratorRepository):
    def __init__(self, datasource: LlmTestWriterDatasource) -> None:
        self._ds = datasource

    async def generate_tests(self, file_path: str, source: str) -> TestSuite:
        return await self._ds.generate(file_path, source)
