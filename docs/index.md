# 🧠🔬 NeuralScope

**AI-powered code analysis toolkit** — review, document, graph, scan, and more.

10 features, 3 interfaces (SDK · CLI · MCP), 7+ LLM providers.

## Quick Start

```bash
pip install neuralscope

# Review a file
neuralscope review ./src/auth/service.py

# Generate documentation
neuralscope docs ./src/models.py

# Security scan
neuralscope scan ./src

# Build dependency graph
neuralscope graph ./src --output json

# Ask about the codebase
neuralscope ask "How does authentication work?"
```

## Python SDK

```python
from neuralscope import NeuralScope

ns = NeuralScope(model="openai/gpt-5.2")

# Code review
review = await ns.review("./src/service.py")

# Generate tests
tests = await ns.generate_tests("./src/utils.py")

# Health dashboard
health = await ns.health("./src")
```

## Features

| Feature | Description | CLI Command |
|---------|-------------|-------------|
| **Code Review** | AI-powered review with scoring | `neuralscope review` |
| **Documentation** | Generate docs from source | `neuralscope docs` |
| **Dependency Graph** | AST-based module graph + impact analysis | `neuralscope graph` |
| **Vulnerability Scan** | Bandit + AI security analysis | `neuralscope scan` |
| **Test Generator** | Generate pytest tests | `neuralscope test-gen` |
| **Codebase Q&A** | RAG-powered Q&A via Qdrant | `neuralscope ask` |
| **Health Dashboard** | Complexity, coverage, metrics | `neuralscope health` |
| **PR Summary** | Auto-generate PR descriptions | `neuralscope pr-summary` |
| **Prompt Studio** | Manage prompt profiles | `neuralscope profile-*` |
| **Architecture Validator** | Validate architecture rules | `neuralscope validate` |

## LLM Providers

Supports **7 providers** including proxy services:

- **OpenAI** — GPT-5.2, GPT-5.1, o3, o4-mini
- **Anthropic** — Claude Sonnet 4.6, Claude Opus 4.6
- **Google** — Gemini 3 Pro, Gemini 3 Flash
- **Ollama** — Llama 4, Qwen 3, Deepseek R1
- **Azure OpenAI**
- **OpenRouter** — any model via openrouter.ai
- **LiteLLM** — any model via your proxy

## Architecture

```
neuralscope/
├── core/           # Settings, LLM registry, embeddings, cache, tracing
├── features/       # 10 domain modules (Clean Architecture)
│   └── <feature>/
│       ├── domain/     # Entities, repository contracts, use cases
│       └── data/       # Datasources, repository implementations
├── sdk/            # Python SDK client
├── cli/            # Typer + Rich CLI (14 commands)
└── mcp/            # MCP server (11 tools + 1 resource)
```
