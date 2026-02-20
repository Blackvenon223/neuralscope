"""Generate tests use case."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from neuralscope.core.log_context import ILogContextRepository
from neuralscope.features.test_generator.domain.entities.test_suite import TestSuite
from neuralscope.features.test_generator.domain.repository.generator import IGeneratorRepository


@dataclass(frozen=True)
class GenerateTestsParams:
    path: str


@dataclass(frozen=True)
class GenerateTestsSuccess:
    suite: TestSuite
    def is_success(self) -> bool:
        return True


@dataclass(frozen=True)
class GenerateTestsError:
    message: str
    def is_success(self) -> bool:
        return False


class GenerateTestsUseCase:
    def __init__(
        self,
        generator_repo: IGeneratorRepository,
        log_context_repository: ILogContextRepository,
    ) -> None:
        self._generator = generator_repo
        self._log_context = log_context_repository

    async def __call__(
        self, params: GenerateTestsParams,
    ) -> GenerateTestsSuccess | GenerateTestsError:
        self._log_context.emit_input(path=params.path)

        file_path = Path(params.path)
        if not file_path.is_file():
            self._log_context.emit_result(result="error", reason="file not found")
            return GenerateTestsError(f"File not found: {params.path}")

        try:
            source = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            self._log_context.emit_result(result="error", reason=str(exc))
            return GenerateTestsError(f"Cannot read file: {exc}")

        try:
            suite = await self._generator.generate_tests(str(file_path), source)
        except Exception as exc:
            self._log_context.emit_result(result="error", reason=str(exc))
            return GenerateTestsError(f"Test generation failed: {exc}")

        self._log_context.emit_result(result="success", tests=suite.count)
        return GenerateTestsSuccess(suite=suite)
