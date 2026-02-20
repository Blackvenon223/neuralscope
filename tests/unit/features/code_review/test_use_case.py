"""Tests for review_file use case."""

import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from neuralscope.core.log_context import LogContextRepository
from neuralscope.features.code_review.domain.entities.review import ReviewResult
from neuralscope.features.code_review.domain.repository.reviewer import (
    GetReviewErrorResult,
    GetReviewSuccessResult,
    IReviewerRepository,
)
from neuralscope.features.code_review.domain.use_cases.review_file.use_case import (
    ReviewFileParams,
    ReviewFileUseCase,
)


class FakeReviewerRepo(IReviewerRepository):
    def __init__(self, result=None) -> None:
        self._result = result

    async def review_file(self, file_path, source):
        return self._result

    async def review_diff(self, diff):
        return self._result


@pytest.mark.asyncio
async def test_review_file_success(tmp_path: Path):
    source = "def hello():\n    print('hi')\n"
    (tmp_path / "app.py").write_text(source)

    review = ReviewResult(file_path=str(tmp_path / "app.py"), score=8.0, summary="Good")
    repo = FakeReviewerRepo(GetReviewSuccessResult(review))

    uc = ReviewFileUseCase(
        reviewer_repo=repo,
        log_context_repository=LogContextRepository("review_file"),
    )
    result = await uc(ReviewFileParams(path=str(tmp_path / "app.py")))
    assert result.is_success()
    assert result.review.score == 8.0


@pytest.mark.asyncio
async def test_review_file_not_found():
    repo = FakeReviewerRepo()
    uc = ReviewFileUseCase(
        reviewer_repo=repo,
        log_context_repository=LogContextRepository("review_file"),
    )
    result = await uc(ReviewFileParams(path="/nonexistent/file.py"))
    assert not result.is_success()
    assert "not found" in result.message


@pytest.mark.asyncio
async def test_review_file_llm_error(tmp_path: Path):
    (tmp_path / "app.py").write_text("x = 1\n")
    repo = FakeReviewerRepo(GetReviewErrorResult("LLM timeout"))

    uc = ReviewFileUseCase(
        reviewer_repo=repo,
        log_context_repository=LogContextRepository("review_file"),
    )
    result = await uc(ReviewFileParams(path=str(tmp_path / "app.py")))
    assert not result.is_success()
    assert "failed" in result.message.lower()
