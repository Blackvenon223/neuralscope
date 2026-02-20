"""Tests for build_graph use case."""

import textwrap
from pathlib import Path

import pytest

from neuralscope.core.log_context import LogContextRepository
from neuralscope.features.dependency_graph.data.repository.graph_builder import (
    GraphBuilderRepository,
)
from neuralscope.features.dependency_graph.domain.use_cases.build_graph.use_case import (
    BuildGraphParams,
    BuildGraphUseCase,
)


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    (tmp_path / "main.py").write_text(
        textwrap.dedent("""\
            from utils import helper

            class App:
                pass
        """)
    )
    (tmp_path / "utils.py").write_text("def helper(): pass\n")
    return tmp_path


@pytest.mark.asyncio
async def test_build_graph_success(project_dir: Path):
    uc = BuildGraphUseCase(
        graph_repo=GraphBuilderRepository(),
        log_context_repository=LogContextRepository("build_graph"),
    )
    result = await uc(BuildGraphParams(path=str(project_dir), output_format="json"))

    assert result.is_success()
    assert result.graph.node_count >= 2
    assert result.graph.edge_count >= 1
    assert '"nodes"' in result.rendered


@pytest.mark.asyncio
async def test_build_graph_dot_format(project_dir: Path):
    uc = BuildGraphUseCase(
        graph_repo=GraphBuilderRepository(),
        log_context_repository=LogContextRepository("build_graph"),
    )
    result = await uc(BuildGraphParams(path=str(project_dir), output_format="dot"))
    assert result.is_success()
    assert "digraph" in result.rendered


@pytest.mark.asyncio
async def test_build_graph_invalid_path():
    uc = BuildGraphUseCase(
        graph_repo=GraphBuilderRepository(),
        log_context_repository=LogContextRepository("build_graph"),
    )
    result = await uc(BuildGraphParams(path="/nonexistent/path"))
    assert not result.is_success()
    assert "not a directory" in result.message


def test_llm_graph_analyzer_parse():
    """Test LLM graph analyzer response parsing (no actual LLM call)."""
    import json

    from neuralscope.features.dependency_graph.data.datasource.llm_graph_analyzer.implementation import (
        LlmGraphAnalyzer,
    )

    raw = json.dumps({
        "nodes": [
            {"id": "app", "name": "app", "kind": "module", "file_path": "app.py", "line": 1},
            {"id": "app.Server", "name": "Server", "kind": "class", "file_path": "app.py", "line": 5},
            {"id": "db", "name": "db", "kind": "module", "file_path": "db.py", "line": 1},
        ],
        "edges": [
            {"source": "app", "target": "db", "relation": "imports"},
            {"source": "app.Server", "target": "db", "relation": "uses"},
        ],
    })

    analyzer = LlmGraphAnalyzer.__new__(LlmGraphAnalyzer)
    graph = analyzer._parse("/project", raw)
    assert graph.node_count == 3
    assert graph.edge_count == 2
    assert graph.nodes[1].kind.value == "class"
    assert graph.edges[1].relation == "uses"


def test_llm_graph_analyzer_parse_malformed():
    from neuralscope.features.dependency_graph.data.datasource.llm_graph_analyzer.implementation import (
        LlmGraphAnalyzer,
    )

    analyzer = LlmGraphAnalyzer.__new__(LlmGraphAnalyzer)
    graph = analyzer._parse("/project", "not json")
    assert graph.node_count == 0


@pytest.mark.asyncio
async def test_build_graph_mode_defaults_to_ast(project_dir: Path):
    uc = BuildGraphUseCase(
        graph_repo=GraphBuilderRepository(),
        log_context_repository=LogContextRepository("build_graph"),
    )
    result = await uc(BuildGraphParams(path=str(project_dir), mode="ast"))
    assert result.is_success()
    assert result.graph.node_count >= 2

