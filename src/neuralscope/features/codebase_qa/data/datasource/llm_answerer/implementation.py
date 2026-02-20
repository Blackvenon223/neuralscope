"""LLM answerer: takes question + context chunks → structured answer."""

from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from neuralscope.core.logging import get_logger
from neuralscope.features.codebase_qa.domain.entities.answer import Answer, SourceReference

logger = get_logger("llm_answerer")

SYSTEM_PROMPT = """\
You are a codebase expert. Answer the question based ONLY on the provided code context.

Return a JSON object:
{
  "answer": "<detailed answer based on the code>",
  "confidence": <float 0-1>,
  "sources": [
    {
      "file_path": "<file>",
      "line_start": <int>,
      "line_end": <int>,
      "snippet": "<relevant code snippet>"
    }
  ]
}

If you cannot answer from the context, set confidence to 0.0 and explain why.
Return ONLY the JSON object."""


class LlmAnswerer:
    def __init__(self, llm: BaseChatModel) -> None:
        self._llm = llm

    async def answer(self, question: str, context_chunks: list[str]) -> Answer:
        context = "\n\n---\n\n".join(context_chunks)
        prompt = f"Question: {question}\n\nCode Context:\n{context}"

        response = await self._llm.ainvoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]
        )
        return self._parse(question, str(response.content))

    def _parse(self, question: str, raw: str) -> Answer:
        try:
            cleaned = self._extract_json(raw)
            data: dict[str, Any] = json.loads(cleaned)
        except (json.JSONDecodeError, ValueError):
            logger.warning("Failed to parse LLM answer response")
            return Answer(question=question, answer=raw[:1000], confidence=0.3)

        sources = [
            SourceReference(
                file_path=s.get("file_path", ""),
                line_start=s.get("line_start", 0),
                line_end=s.get("line_end", 0),
                snippet=s.get("snippet", ""),
            )
            for s in data.get("sources", [])
        ]

        return Answer(
            question=question,
            answer=data.get("answer", ""),
            confidence=float(data.get("confidence", 0.5)),
            sources=sources,
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
