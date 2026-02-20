# Getting Started

## Installation

```bash
pip install neuralscope
```

### With LLM providers

```bash
# OpenAI
pip install neuralscope[openai]

# Anthropic
pip install neuralscope[anthropic]

# Google
pip install neuralscope[google]

# All providers + security tools
pip install neuralscope[all]
```

### From source

```bash
git clone https://github.com/neuralscope/neuralscope.git
cd neuralscope
poetry install
```

## Configuration

Create a `.env` file or set environment variables:

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-5.2
OPENAI_API_KEY=sk-...
```

### All settings

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `openai` | LLM provider |
| `LLM_MODEL` | `gpt-5.2` | Model name |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `ANTHROPIC_API_KEY` | — | Anthropic API key |
| `GOOGLE_API_KEY` | — | Google AI API key |
| `OPENROUTER_API_KEY` | — | OpenRouter API key |
| `LITELLM_API_BASE` | `http://localhost:4000` | LiteLLM proxy URL |
| `QDRANT_URL` | `http://localhost:6333` | Qdrant URL for RAG |
| `QDRANT_API_KEY` | — | Qdrant API key |

## Docker

```bash
docker compose up -d
```

This starts:

- **NeuralScope** on port 8000
- **Qdrant** on ports 6333/6334

## Verify installation

```bash
neuralscope --version
neuralscope models
```
