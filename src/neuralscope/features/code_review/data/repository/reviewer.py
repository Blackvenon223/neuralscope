"""Data repository wiring LLM datasource to domain contract."""

from __future__ import annotations

from neuralscope.features.code_review.data.datasource.llm_reviewer.implementation import (
    LlmReviewerDatasource,
)
from neuralscope.features.code_review.domain.repository.reviewer import (
    GetReviewErrorResult,
    GetReviewRepositoryResult,
    GetReviewSuccessResult,
    IReviewerRepository,
)


class ReviewerRepository(IReviewerRepository):
    def __init__(self, datasource: LlmReviewerDatasource) -> None:
        self._ds = datasource

    async def review_file(self, file_path: str, source: str) -> GetReviewRepositoryResult:
        try:
            review = await self._ds.review_source(file_path, source)
            return GetReviewSuccessResult(review)
        except Exception as exc:
            return GetReviewErrorResult(f"Review failed: {exc}")

    async def review_diff(self, diff: str) -> GetReviewRepositoryResult:
        try:
            review = await self._ds.review_diff(diff)
            return GetReviewSuccessResult(review)
        except Exception as exc:
            return GetReviewErrorResult(f"Diff review failed: {exc}")
