"""Review diff use case results."""

from __future__ import annotations

from dataclasses import dataclass

from neuralscope.features.code_review.domain.entities.review import ReviewResult


@dataclass(frozen=True)
class ReviewDiffSuccess:
    review: ReviewResult

    def is_success(self) -> bool:
        return True


@dataclass(frozen=True)
class ReviewDiffError:
    message: str

    def is_success(self) -> bool:
        return False


ReviewDiffResult = ReviewDiffSuccess | ReviewDiffError
