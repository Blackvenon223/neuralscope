# MCP Server

NeuralScope exposes all features via the [Model Context Protocol](https://modelcontextprotocol.io/).

## Setup

Add to your MCP client config (e.g. Claude Desktop):

```json
{
  "mcpServers": {
    "neuralscope": {
      "command": "neuralscope-mcp",
      "args": []
    }
  }
}
```

Or with Docker:

```json
{
  "mcpServers": {
    "neuralscope": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "neuralscope:latest", "neuralscope-mcp"]
    }
  }
}
```

## Tools (11)

| Tool | Description | Required Args |
|------|-------------|---------------|
| `review` | AI code review | `path` |
| `docs` | Generate documentation | `path` |
| `build_graph` | Build dependency graph | `path` |
| `impact` | Analyze change impact | `path` |
| `scan` | Security vulnerability scan | `path` |
| `generate_tests` | Generate unit tests | `path` |
| `ask` | Codebase Q&A | `question` |
| `health` | Project health metrics | `path` |
| `pr_summary` | Generate PR description | — |
| `validate_arch` | Validate architecture | `path` |
| `list_models` | List LLM providers | — |

## Resources (1)

| URI | Description |
|-----|-------------|
| `neuralscope://health` | Real-time project health dashboard |
