"""QA repository: indexes files, searches context, generates answers."""

from __future__ import annotations

from neuralscope.features.codebase_qa.data.datasource.file_indexer.implementation import (
    FileIndexer,
)
from neuralscope.features.codebase_qa.data.datasource.llm_answerer.implementation import (
    LlmAnswerer,
)
from neuralscope.features.codebase_qa.domain.entities.answer import Answer
from neuralscope.features.codebase_qa.domain.repository.qa import IQARepository


class QARepository(IQARepository):
    """Simple keyword-search QA. For production, swap search with Qdrant vectors."""

    def __init__(self, indexer: FileIndexer, answerer: LlmAnswerer) -> None:
        self._indexer = indexer
        self._answerer = answerer
        self._chunks: dict[str, list] = {}

    async def index_project(self, project_path: str) -> int:
        chunks = self._indexer.index(project_path)
        self._chunks[project_path] = chunks
        return len(chunks)

    async def ask(self, question: str, project_path: str) -> Answer:
        if project_path not in self._chunks:
            await self.index_project(project_path)

        chunks = self._chunks.get(project_path, [])
        q_lower = question.lower()

        scored = []
        for chunk in chunks:
            score = sum(1 for word in q_lower.split() if word in chunk.content.lower())
            if score > 0:
                scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:5]

        if not top:
            top = [(0, c) for c in chunks[:5]]

        context = [f"# {c.file_path}:{c.line_start}-{c.line_end}\n{c.content}" for _, c in top]

        return await self._answerer.answer(question, context)
