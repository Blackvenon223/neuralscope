"""NeuralScope MCP Server — exposes all 10 features as MCP tools + 1 resource."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, Tool

from neuralscope.sdk.client import NeuralScope

server = Server("neuralscope")

TOOLS = [
    Tool(name="review", description="AI-powered code review", inputSchema={
        "type": "object",
        "properties": {"path": {"type": "string"}, "diff": {"type": "boolean", "default": False}},
        "required": ["path"],
    }),
    Tool(name="docs", description="Generate documentation for a file", inputSchema={
        "type": "object",
        "properties": {"path": {"type": "string"}, "format": {"type": "string", "default": "markdown"}},
        "required": ["path"],
    }),
    Tool(name="build_graph", description="Build dependency graph", inputSchema={
        "type": "object",
        "properties": {"path": {"type": "string"}, "output": {"type": "string", "default": "json"}},
        "required": ["path"],
    }),
    Tool(name="impact", description="Analyze change impact", inputSchema={
        "type": "object",
        "properties": {"path": {"type": "string"}, "diff": {"type": "string", "default": "HEAD~1"}},
        "required": ["path"],
    }),
    Tool(name="scan", description="Scan for security vulnerabilities", inputSchema={
        "type": "object",
        "properties": {"path": {"type": "string"}},
        "required": ["path"],
    }),
    Tool(name="generate_tests", description="Generate unit tests for a file", inputSchema={
        "type": "object",
        "properties": {"path": {"type": "string"}},
        "required": ["path"],
    }),
    Tool(name="ask", description="Ask a question about the codebase", inputSchema={
        "type": "object",
        "properties": {"question": {"type": "string"}, "project": {"type": "string", "default": "."}},
        "required": ["question"],
    }),
    Tool(name="health", description="Analyze project health metrics", inputSchema={
        "type": "object",
        "properties": {"path": {"type": "string"}},
        "required": ["path"],
    }),
    Tool(name="pr_summary", description="Generate PR summary from diff", inputSchema={
        "type": "object",
        "properties": {"diff": {"type": "string", "default": "HEAD~1"}},
    }),
    Tool(name="validate_arch", description="Validate architecture rules", inputSchema={
        "type": "object",
        "properties": {"path": {"type": "string"}, "rules": {"type": "string"}},
        "required": ["path"],
    }),
    Tool(name="list_models", description="List available LLM providers and models", inputSchema={
        "type": "object", "properties": {},
    }),
]


@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    ns = NeuralScope()
    handlers: dict[str, Any] = {
        "review": lambda: ns.review(arguments["path"], diff=arguments.get("diff", False)),
        "docs": lambda: ns.docs(arguments["path"], format=arguments.get("format", "markdown")),
        "build_graph": lambda: ns.build_graph(arguments["path"], output=arguments.get("output", "json")),
        "impact": lambda: ns.impact(arguments["path"], diff=arguments.get("diff", "HEAD~1")),
        "scan": lambda: ns.scan(arguments["path"]),
        "generate_tests": lambda: ns.generate_tests(arguments["path"]),
        "ask": lambda: ns.ask(arguments["question"], project=arguments.get("project", ".")),
        "health": lambda: ns.health(arguments["path"]),
        "pr_summary": lambda: ns.pr_summary(diff=arguments.get("diff", "HEAD~1")),
        "validate_arch": lambda: ns.validate_arch(arguments["path"], rules=arguments.get("rules")),
        "list_models": lambda: asyncio.coroutine(lambda: ns.list_models())(),
    }

    handler = handlers.get(name)
    if not handler:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    try:
        if name == "list_models":
            result = ns.list_models()
        else:
            result = await handler()
        return [TextContent(type="text", text=json.dumps(result, default=str, indent=2))]
    except NotImplementedError as exc:
        return [TextContent(type="text", text=f"Feature not yet wired: {exc}")]
    except Exception as exc:
        return [TextContent(type="text", text=f"Error: {exc}")]


@server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri="neuralscope://health",
            name="Project Health Dashboard",
            description="Real-time project health metrics including complexity, coverage, and dependency stats",
            mimeType="application/json",
        ),
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    if uri == "neuralscope://health":
        ns = NeuralScope()
        try:
            result = await ns.health(".")
            return json.dumps(result, default=str, indent=2)
        except NotImplementedError:
            return json.dumps({"status": "not_wired", "message": "Health feature not yet connected"})
    return json.dumps({"error": f"Unknown resource: {uri}"})


async def run_server() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
