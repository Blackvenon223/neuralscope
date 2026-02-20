"""Repository contract for code review."""

from __future__ import annotations

from abc import ABC, abstractmethod

from neuralscope.features.code_review.domain.entities.review import ReviewResult


class GetReviewRepositoryResult(ABC):
    @abstractmethod
    def is_success(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_review(self) -> ReviewResult:
        raise NotImplementedError


class GetReviewSuccessResult(GetReviewRepositoryResult):
    def __init__(self, review: ReviewResult) -> None:
        self._review = review

    def is_success(self) -> bool:
        return True

    def get_review(self) -> ReviewResult:
        return self._review


class GetReviewErrorResult(GetReviewRepositoryResult):
    def __init__(self, message: str) -> None:
        self._message = message

    def is_success(self) -> bool:
        return False

    def get_review(self) -> ReviewResult:
        raise ValueError(self._message)

    @property
    def message(self) -> str:
        return self._message


class IReviewerRepository(ABC):
    @abstractmethod
    async def review_file(self, file_path: str, source: str) -> GetReviewRepositoryResult:
        raise NotImplementedError

    @abstractmethod
    async def review_diff(self, diff: str) -> GetReviewRepositoryResult:
        raise NotImplementedError
