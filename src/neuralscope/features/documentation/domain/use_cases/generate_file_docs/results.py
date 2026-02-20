"""Generate file docs use case results."""

from __future__ import annotations

from dataclasses import dataclass

from neuralscope.features.documentation.domain.entities.document import GeneratedDoc


@dataclass(frozen=True)
class GenerateDocsSuccess:
    doc: GeneratedDoc

    def is_success(self) -> bool:
        return True


@dataclass(frozen=True)
class GenerateDocsError:
    message: str

    def is_success(self) -> bool:
        return False


GenerateDocsResult = GenerateDocsSuccess | GenerateDocsError
