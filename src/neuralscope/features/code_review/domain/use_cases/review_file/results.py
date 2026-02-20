"""Review file use case results."""

from __future__ import annotations

from dataclasses import dataclass

from neuralscope.features.code_review.domain.entities.review import ReviewResult


@dataclass(frozen=True)
class ReviewFileSuccess:
    review: ReviewResult

    def is_success(self) -> bool:
        return True


@dataclass(frozen=True)
class ReviewFileError:
    message: str

    def is_success(self) -> bool:
        return False


ReviewFileResult = ReviewFileSuccess | ReviewFileError
