"""Review file use case."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from neuralscope.core.log_context import ILogContextRepository
from neuralscope.features.code_review.domain.repository.reviewer import IReviewerRepository
from neuralscope.features.code_review.domain.use_cases.review_file.results import (
    ReviewFileError,
    ReviewFileResult,
    ReviewFileSuccess,
)


@dataclass(frozen=True)
class ReviewFileParams:
    path: str
    diff: bool = False


class ReviewFileUseCase:
    def __init__(
        self,
        reviewer_repo: IReviewerRepository,
        log_context_repository: ILogContextRepository,
    ) -> None:
        self._reviewer = reviewer_repo
        self._log_context = log_context_repository

    async def __call__(self, params: ReviewFileParams) -> ReviewFileResult:
        self._log_context.emit_input(path=params.path, diff=params.diff)

        file_path = Path(params.path)
        if not file_path.is_file():
            self._log_context.emit_result(result="error", reason="file not found")
            return ReviewFileError(f"File not found: {params.path}")

        try:
            source = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            self._log_context.emit_result(result="error", reason=str(exc))
            return ReviewFileError(f"Cannot read file: {exc}")

        result = await self._reviewer.review_file(str(file_path), source)

        if not result.is_success():
            self._log_context.emit_result(result="error", reason="llm_failed")
            return ReviewFileError("LLM review failed")

        review = result.get_review()
        self._log_context.emit_result(
            result="success",
            score=review.score,
            issues=review.issue_count,
        )
        return ReviewFileSuccess(review=review)
