"""Tests for codebase Q&A: file indexer, LLM answerer, entities."""

import json
from pathlib import Path

from neuralscope.features.codebase_qa.data.datasource.file_indexer.implementation import (
    FileIndexer,
)
from neuralscope.features.codebase_qa.data.datasource.llm_answerer.implementation import (
    LlmAnswerer,
)
from neuralscope.features.codebase_qa.domain.entities.answer import Answer, SourceReference


def test_answer_source_count():
    answer = Answer(
        question="How does auth work?",
        answer="JWT tokens",
        sources=[
            SourceReference(file_path="auth.py", line_start=10, line_end=20),
            SourceReference(file_path="jwt.py", line_start=5),
        ],
        confidence=0.9,
    )
    assert answer.source_count == 2


def test_file_indexer_chunks_python(tmp_path: Path):
    (tmp_path / "app.py").write_text(
        "def hello():\n    return 'hi'\n\ndef world():\n    return 'world'\n"
    )
    (tmp_path / "empty.py").write_text("")

    indexer = FileIndexer()
    chunks = indexer.index(str(tmp_path))
    assert len(chunks) >= 2
    assert all(c.file_path == "app.py" for c in chunks)


def test_file_indexer_skips_venv(tmp_path: Path):
    venv = tmp_path / ".venv" / "lib"
    venv.mkdir(parents=True)
    (venv / "pkg.py").write_text("x = 1\n")
    (tmp_path / "main.py").write_text("y = 2\n")

    indexer = FileIndexer()
    chunks = indexer.index(str(tmp_path))
    files = {c.file_path for c in chunks}
    assert "main.py" in files
    assert not any(".venv" in f for f in files)


def test_file_indexer_to_source_ref(tmp_path: Path):
    (tmp_path / "a.py").write_text("def foo():\n    pass\n")
    indexer = FileIndexer()
    chunks = indexer.index(str(tmp_path))
    ref = chunks[0].to_source_ref()
    assert ref.file_path == "a.py"
    assert ref.line_start > 0


def test_answerer_parse_valid():
    raw = json.dumps(
        {
            "answer": "Auth uses JWT tokens",
            "confidence": 0.85,
            "sources": [
                {
                    "file_path": "auth.py",
                    "line_start": 10,
                    "line_end": 25,
                    "snippet": "def login():",
                }
            ],
        }
    )

    answerer = LlmAnswerer.__new__(LlmAnswerer)
    result = answerer._parse("How does auth work?", raw)
    assert result.answer == "Auth uses JWT tokens"
    assert result.confidence == 0.85
    assert result.source_count == 1


def test_answerer_parse_malformed():
    answerer = LlmAnswerer.__new__(LlmAnswerer)
    result = answerer._parse("question?", "not json")
    assert result.confidence == 0.3
    assert "not json" in result.answer
