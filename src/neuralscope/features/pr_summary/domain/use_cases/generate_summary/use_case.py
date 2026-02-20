"""Generate PR summary use case."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass

from neuralscope.core.log_context import ILogContextRepository
from neuralscope.features.pr_summary.domain.entities.pr import PRSummary
from neuralscope.features.pr_summary.domain.repository.summarizer import ISummarizerRepository


@dataclass(frozen=True)
class GenerateSummaryParams:
    diff_ref: str = "HEAD~1"
    cwd: str = "."


@dataclass(frozen=True)
class GenerateSummarySuccess:
    summary: PRSummary

    def is_success(self) -> bool:
        return True


@dataclass(frozen=True)
class GenerateSummaryError:
    message: str

    def is_success(self) -> bool:
        return False


class GenerateSummaryUseCase:
    def __init__(
        self,
        summarizer_repo: ISummarizerRepository,
        log_context_repository: ILogContextRepository,
    ) -> None:
        self._summarizer = summarizer_repo
        self._log_context = log_context_repository

    async def __call__(
        self,
        params: GenerateSummaryParams,
    ) -> GenerateSummarySuccess | GenerateSummaryError:
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
            return GenerateSummaryError(f"Cannot get diff: {exc}")

        if not diff.strip():
            self._log_context.emit_result(result="error", reason="empty_diff")
            return GenerateSummaryError("No changes found")

        try:
            summary = await self._summarizer.summarize_diff(diff)
        except Exception as exc:
            self._log_context.emit_result(result="error", reason=str(exc))
            return GenerateSummaryError(f"Summary generation failed: {exc}")

        self._log_context.emit_result(result="success", changes=summary.total_changes)
        return GenerateSummarySuccess(summary=summary)
