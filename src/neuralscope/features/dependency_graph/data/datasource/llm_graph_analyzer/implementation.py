"""LLM-based dependency graph analyzer.

Sends source code to LLM to identify modules, classes, functions,
and their relationships. Useful for understanding architectural
dependencies that AST alone can't capture (e.g. runtime deps, patterns).
"""

from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from neuralscope.core.logging import get_logger
from neuralscope.features.dependency_graph.domain.entities.graph import (
    DependencyGraph,
    GraphEdge,
    GraphNode,
    NodeKind,
)

logger = get_logger("llm_graph_analyzer")

SYSTEM_PROMPT = """\
You are an expert software architect. Analyze the provided Python project files \
and extract the dependency graph.

Return a JSON object:
{
  "nodes": [
    {
      "id": "<unique_id: module.class or module.function>",
      "name": "<short name>",
      "kind": "module|class|function|package",
      "file_path": "<relative path>",
      "line": <int, 0 if unknown>,
      "description": "<one-line description of purpose>"
    }
  ],
  "edges": [
    {
      "source": "<node_id that depends>",
      "target": "<node_id being depended on>",
      "relation": "imports|inherits|calls|uses|composes"
    }
  ]
}

Focus on:
- Import relationships between modules
- Class inheritance
- Composition / dependency injection patterns
- Function call chains between modules
- Pattern usage (Factory, Repository, Strategy, etc.)

Return ONLY the JSON object."""

NODE_KIND_MAP = {
    "module": NodeKind.MODULE,
    "class": NodeKind.CLASS,
    "function": NodeKind.FUNCTION,
    "package": NodeKind.PACKAGE,
}

SKIP_DIRS = {".venv", "venv", "__pycache__", ".git", "node_modules", ".tox"}


class LlmGraphAnalyzer:
    def __init__(self, llm: BaseChatModel) -> None:
        self._llm = llm

    async def analyze(self, root_path: str, files: dict[str, str]) -> DependencyGraph:
        file_listing = "\n\n".join(
            f"### {path}\n```python\n{source[:2000]}\n```"
            for path, source in files.items()
        )

        response = await self._llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Project files:\n\n{file_listing}"),
        ])
        return self._parse(root_path, str(response.content))

    def _parse(self, root_path: str, raw: str) -> DependencyGraph:
        try:
            cleaned = self._extract_json(raw)
            data: dict[str, Any] = json.loads(cleaned)
        except (json.JSONDecodeError, ValueError):
            logger.warning("Failed to parse LLM graph response")
            return DependencyGraph(root_path=root_path)

        nodes = [
            GraphNode(
                id=n.get("id", ""),
                name=n.get("name", ""),
                kind=NODE_KIND_MAP.get(n.get("kind", "module"), NodeKind.MODULE),
                file_path=n.get("file_path", ""),
                line=n.get("line", 0),
                docstring=n.get("description"),
            )
            for n in data.get("nodes", [])
        ]

        edges = [
            GraphEdge(
                source=e.get("source", ""),
                target=e.get("target", ""),
                relation=e.get("relation", "imports"),
            )
            for e in data.get("edges", [])
        ]

        return DependencyGraph(root_path=root_path, nodes=nodes, edges=edges)

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
