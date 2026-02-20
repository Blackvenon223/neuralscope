"""Tests for AST parser."""

import textwrap
from pathlib import Path

from neuralscope.features.dependency_graph.data.datasource.ast_parser.implementation import (
    AstParser,
)
from neuralscope.features.dependency_graph.domain.entities.graph import NodeKind


def test_parse_single_file(tmp_path: Path):
    (tmp_path / "app.py").write_text(
        textwrap.dedent("""\
            import os
            from pathlib import Path

            class Server:
                pass

            def main():
                pass
        """)
    )

    parser = AstParser(tmp_path)
    nodes, edges = parser.parse()

    node_names = {n.name for n in nodes}
    assert "app" in node_names
    assert "Server" in node_names
    assert "main" in node_names

    module_nodes = [n for n in nodes if n.kind == NodeKind.MODULE]
    assert len(module_nodes) == 1

    class_nodes = [n for n in nodes if n.kind == NodeKind.CLASS]
    assert len(class_nodes) == 1
    assert class_nodes[0].name == "Server"

    func_nodes = [n for n in nodes if n.kind == NodeKind.FUNCTION]
    assert len(func_nodes) == 1

    edge_targets = {e.target for e in edges}
    assert "os" in edge_targets
    assert "pathlib" in edge_targets


def test_parse_skips_venv(tmp_path: Path):
    venv = tmp_path / ".venv" / "lib" / "site.py"
    venv.parent.mkdir(parents=True)
    venv.write_text("x = 1")

    parser = AstParser(tmp_path)
    nodes, _ = parser.parse()
    assert len(nodes) == 0


def test_parse_package_structure(tmp_path: Path):
    pkg = tmp_path / "mypackage"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    (pkg / "core.py").write_text("from mypackage import utils\n")
    (pkg / "utils.py").write_text("def helper(): pass\n")

    parser = AstParser(tmp_path)
    nodes, edges = parser.parse()

    module_ids = {n.id for n in nodes if n.kind == NodeKind.MODULE}
    assert "mypackage" in module_ids
    assert "mypackage.core" in module_ids
    assert "mypackage.utils" in module_ids

    import_edges = [e for e in edges if e.relation == "imports"]
    assert any(e.source == "mypackage.core" and e.target == "mypackage" for e in import_edges)


def test_parse_handles_syntax_error(tmp_path: Path):
    (tmp_path / "broken.py").write_text("def broken(:\n    pass\n")
    parser = AstParser(tmp_path)
    nodes, edges = parser.parse()
    assert len(nodes) == 0
