"""LLM-based test writer datasource."""

from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from neuralscope.core.logging import get_logger
from neuralscope.features.test_generator.domain.entities.test_suite import TestCase, TestSuite

logger = get_logger("llm_test_writer")

SYSTEM_PROMPT = """\
You are an expert Python test engineer. Generate pytest test cases for the provided code.

Return a JSON object:
{
  "test_cases": [
    {
      "name": "test_<descriptive_name>",
      "body": "<complete test function body>",
      "description": "<what this test verifies>"
    }
  ]
}

Generate at least 3 test cases covering: happy path, edge cases, and error conditions.
Use pytest fixtures and assertions. Return ONLY the JSON object."""


class LlmTestWriterDatasource:
    def __init__(self, llm: BaseChatModel) -> None:
        self._llm = llm

    async def generate(self, file_path: str, source: str) -> TestSuite:
        prompt = f"File: {file_path}\n\n```python\n{source}\n```"
        response = await self._llm.ainvoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]
        )
        return self._parse(file_path, str(response.content))

    def _parse(self, file_path: str, raw: str) -> TestSuite:
        try:
            cleaned = self._extract_json(raw)
            data: dict[str, Any] = json.loads(cleaned)
        except (json.JSONDecodeError, ValueError):
            logger.warning("Failed to parse LLM test response")
            return TestSuite(source_file=file_path, rendered=raw[:2000])

        cases = [
            TestCase(
                name=tc.get("name", "test_unnamed"),
                body=tc.get("body", ""),
                description=tc.get("description", ""),
            )
            for tc in data.get("test_cases", [])
        ]

        suite = TestSuite(source_file=file_path, test_cases=cases)
        suite.rendered = self._render(suite)
        return suite

    @staticmethod
    def _render(suite: TestSuite) -> str:
        lines = [f'"""Auto-generated tests for {suite.source_file}."""', "", "import pytest", ""]
        for tc in suite.test_cases:
            lines.extend([f"def {tc.name}():", f"    {tc.body}", "", ""])
        return "\n".join(lines)

    @staticmethod
    def _extract_json(text: str) -> str:
        match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
        if match:
            return match.group(1)
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return text[start:end]
        return text
