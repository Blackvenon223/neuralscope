"""Repository contract for PR summary."""

from __future__ import annotations

from abc import ABC, abstractmethod

from neuralscope.features.pr_summary.domain.entities.pr import PRSummary


class ISummarizerRepository(ABC):
    @abstractmethod
    async def summarize_diff(self, diff: str) -> PRSummary:
        raise NotImplementedError
