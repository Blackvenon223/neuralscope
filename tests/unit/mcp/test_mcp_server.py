"""Tests for MCP server tool registration."""

import pytest

mcp_available = True
try:
    from neuralscope.mcp.server import TOOLS, server
except ImportError:
    mcp_available = False

pytestmark = pytest.mark.skipif(not mcp_available, reason="mcp package not installed")


def test_mcp_server_has_correct_tool_count():
    assert len(TOOLS) == 11


def test_mcp_tools_have_names():
    names = {t.name for t in TOOLS}
    expected = {
        "review", "docs", "build_graph", "impact", "scan",
        "generate_tests", "ask", "health", "pr_summary",
        "validate_arch", "list_models",
    }
    assert names == expected


def test_mcp_tools_have_schemas():
    for tool in TOOLS:
        assert tool.inputSchema is not None
        assert tool.inputSchema.get("type") == "object"


def test_server_name():
    assert server.name == "neuralscope"
