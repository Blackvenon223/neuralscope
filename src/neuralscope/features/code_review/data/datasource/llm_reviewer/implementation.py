"""LLM-based code reviewer datasource.

Sends source code to an LLM with a structured prompt and parses
the response into ReviewResult entities.
"""

from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from neuralscope.core.logging import get_logger
from neuralscope.features.code_review.domain.entities.review import (
    Issue,
    IssueCategory,
    ReviewResult,
    Severity,
)

logger = get_logger("llm_reviewer")

SYSTEM_PROMPT = """\
You are an expert code reviewer. Analyze the provided code and return a JSON object with:
{
  "score": <float 1-10>,
  "summary": "<2-3 sentence overview>",
  "issues": [
    {
      "line": <int>,
      "message": "<what's wrong>",
      "severity": "info|warning|error|critical",
      "category": "bug|security|performance|style|maintainability|complexity|naming|documentation",
      "suggestion": "<how to fix>"
    }
  ],
  "strengths": ["<positive aspect>", ...]
}

Be thorough but fair. Focus on real problems, not nitpicks.
Return ONLY the JSON object, no markdown fences."""

DIFF_SYSTEM_PROMPT = """\
You are an expert code reviewer. Analyze the provided git diff and return a JSON object with:
{
  "score": <float 1-10>,
  "summary": "<2-3 sentence overview of the changes>",
  "issues": [
    {
      "line": <int>,
      "message": "<what's wrong with this change>",
      "severity": "info|warning|error|critical",
      "category": "bug|security|performance|style|maintainability|complexity|naming|documentation",
      "suggestion": "<how to fix>"
    }
  ],
  "strengths": ["<positive aspect of the changes>", ...]
}

Focus on the diff context, not the entire file. Return ONLY the JSON object."""


class LlmReviewerDatasource:
    def __init__(self, llm: BaseChatModel) -> None:
        self._llm = llm

    async def review_source(self, file_path: str, source: str) -> ReviewResult:
        prompt = f"File: {file_path}\n\n```\n{source}\n```"
        raw = await self._invoke(SYSTEM_PROMPT, prompt)
        return self._parse(file_path, raw)

    async def review_diff(self, diff: str) -> ReviewResult:
        raw = await self._invoke(DIFF_SYSTEM_PROMPT, diff)
        return self._parse("(diff)", raw)

    async def _invoke(self, system: str, user: str) -> str:
        response = await self._llm.ainvoke(
            [
                SystemMessage(content=system),
                HumanMessage(content=user),
            ]
        )
        return str(response.content)

    def _parse(self, file_path: str, raw: str) -> ReviewResult:
        try:
            cleaned = self._extract_json(raw)
            data: dict[str, Any] = json.loads(cleaned)
        except (json.JSONDecodeError, ValueError):
            logger.warning("Failed to parse LLM response, returning raw summary")
            return ReviewResult(
                file_path=file_path,
                score=5.0,
                summary=raw[:500],
            )

        issues = [
            Issue(
                line=i.get("line", 0),
                message=i.get("message", ""),
                severity=Severity(i.get("severity", "info")),
                category=IssueCategory(i.get("category", "style")),
                suggestion=i.get("suggestion", ""),
            )
            for i in data.get("issues", [])
        ]

        return ReviewResult(
            file_path=file_path,
            score=float(data.get("score", 5.0)),
            summary=data.get("summary", ""),
            issues=issues,
            strengths=data.get("strengths", []),
        )

    @staticmethod
    def _extract_json(text: str) -> str:
        """Strip markdown fences if the LLM wraps its response."""
        match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
        if match:
            return match.group(1)
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return text[start:end]
        return text
