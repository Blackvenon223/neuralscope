"""Review diff use case."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass

from neuralscope.core.log_context import ILogContextRepository
from neuralscope.features.code_review.domain.repository.reviewer import IReviewerRepository
from neuralscope.features.code_review.domain.use_cases.review_diff.results import (
    ReviewDiffError,
    ReviewDiffResult,
    ReviewDiffSuccess,
)


@dataclass(frozen=True)
class ReviewDiffParams:
    diff_ref: str = "HEAD~1"
    cwd: str = "."


class ReviewDiffUseCase:
    def __init__(
        self,
        reviewer_repo: IReviewerRepository,
        log_context_repository: ILogContextRepository,
    ) -> None:
        self._reviewer = reviewer_repo
        self._log_context = log_context_repository

    async def __call__(self, params: ReviewDiffParams) -> ReviewDiffResult:
        self._log_context.emit_input(diff_ref=params.diff_ref)

        try:
            diff = subprocess.check_output(
                ["git", "diff", params.diff_ref],
                cwd=params.cwd,
                text=True,
                stderr=subprocess.DEVNULL,
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            self._log_context.emit_result(result="error", reason=str(exc))
            return ReviewDiffError(f"Cannot get diff: {exc}")

        if not diff.strip():
            self._log_context.emit_result(result="error", reason="empty_diff")
            return ReviewDiffError("No changes found in diff")

        result = await self._reviewer.review_diff(diff)

        if not result.is_success():
            self._log_context.emit_result(result="error", reason="llm_failed")
            return ReviewDiffError("LLM diff review failed")

        review = result.get_review()
        self._log_context.emit_result(
            result="success",
            score=review.score,
            issues=review.issue_count,
        )
        return ReviewDiffSuccess(review=review)
