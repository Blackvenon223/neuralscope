"""Validate project architecture use case."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from neuralscope.core.log_context import ILogContextRepository
from neuralscope.features.architecture_validator.domain.entities.validation import ValidationReport
from neuralscope.features.architecture_validator.domain.repository.validator import IValidatorRepository


@dataclass(frozen=True)
class ValidateProjectParams:
    path: str
    rules_path: str | None = None


@dataclass(frozen=True)
class ValidateProjectSuccess:
    report: ValidationReport
    def is_success(self) -> bool:
        return True


@dataclass(frozen=True)
class ValidateProjectError:
    message: str
    def is_success(self) -> bool:
        return False


class ValidateProjectUseCase:
    def __init__(
        self,
        validator_repo: IValidatorRepository,
        log_context_repository: ILogContextRepository,
    ) -> None:
        self._validator = validator_repo
        self._log_context = log_context_repository

    async def __call__(self, params: ValidateProjectParams) -> ValidateProjectSuccess | ValidateProjectError:
        self._log_context.emit_input(path=params.path, rules=params.rules_path)

        root = Path(params.path).resolve()
        if not root.is_dir():
            self._log_context.emit_result(result="error", reason="not a directory")
            return ValidateProjectError(f"Path is not a directory: {params.path}")

        try:
            report = await self._validator.validate(str(root), params.rules_path)
        except Exception as exc:
            self._log_context.emit_result(result="error", reason=str(exc))
            return ValidateProjectError(f"Validation failed: {exc}")

        self._log_context.emit_result(
            result="success",
            violations=report.violation_count,
            passed=report.passed,
        )
        return ValidateProjectSuccess(report=report)
