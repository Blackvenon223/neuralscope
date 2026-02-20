"""Repository contract for architecture validation."""

from __future__ import annotations

from abc import ABC, abstractmethod

from neuralscope.features.architecture_validator.domain.entities.validation import ValidationReport


class IValidatorRepository(ABC):
    @abstractmethod
    async def validate(self, project_path: str, rules_path: str | None = None) -> ValidationReport:
        raise NotImplementedError
