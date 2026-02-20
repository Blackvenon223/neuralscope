# Codebase Q&A

RAG-powered codebase questions via Qdrant vector search.

## Usage

```bash
neuralscope ask 'How does auth work?' --project ./src
```

## Entities

- **Answer** - question, answer, sources, confidence
- **SourceReference** - file path, line range, snippet
