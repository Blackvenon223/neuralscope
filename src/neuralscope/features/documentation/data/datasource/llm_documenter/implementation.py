"""LLM-based documentation generator datasource."""

from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from neuralscope.core.logging import get_logger
from neuralscope.features.documentation.domain.entities.document import (
    ClassDoc,
    FunctionDoc,
    GeneratedDoc,
)

logger = get_logger("llm_documenter")

SYSTEM_PROMPT = """\
You are an expert technical writer. Generate comprehensive documentation for the provided Python source code.

Return a JSON object:
{
  "module_docstring": "<module-level description>",
  "classes": [
    {
      "name": "<class name>",
      "docstring": "<class description>",
      "bases": ["<base class>"],
      "methods": [
        {
          "name": "<method>",
          "signature": "<full signature>",
          "docstring": "<what it does>",
          "params": ["param1: type - description"],
          "returns": "<return description>"
        }
      ]
    }
  ],
  "functions": [
    {
      "name": "<function>",
      "signature": "<full signature>",
      "docstring": "<what it does>",
      "params": ["param1: type - description"],
      "returns": "<return description>"
    }
  ]
}

Be precise and technical. Return ONLY the JSON object."""


class LlmDocumenterDatasource:
    def __init__(self, llm: BaseChatModel) -> None:
        self._llm = llm

    async def generate(self, file_path: str, source: str) -> GeneratedDoc:
        prompt = f"File: {file_path}\n\n```python\n{source}\n```"
        response = await self._llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
        return self._parse(file_path, str(response.content))

    def _parse(self, file_path: str, raw: str) -> GeneratedDoc:
        try:
            cleaned = self._extract_json(raw)
            data: dict[str, Any] = json.loads(cleaned)
        except (json.JSONDecodeError, ValueError):
            logger.warning("Failed to parse LLM doc response")
            return GeneratedDoc(file_path=file_path, module_docstring=raw[:500])

        classes = [
            ClassDoc(
                name=c.get("name", ""),
                docstring=c.get("docstring", ""),
                bases=c.get("bases", []),
                methods=[
                    FunctionDoc(
                        name=m.get("name", ""),
                        signature=m.get("signature", ""),
                        docstring=m.get("docstring", ""),
                        params=m.get("params", []),
                        returns=m.get("returns", ""),
                    )
                    for m in c.get("methods", [])
                ],
            )
            for c in data.get("classes", [])
        ]

        functions = [
            FunctionDoc(
                name=f.get("name", ""),
                signature=f.get("signature", ""),
                docstring=f.get("docstring", ""),
                params=f.get("params", []),
                returns=f.get("returns", ""),
            )
            for f in data.get("functions", [])
        ]

        return GeneratedDoc(
            file_path=file_path,
            module_docstring=data.get("module_docstring", ""),
            classes=classes,
            functions=functions,
        )

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
