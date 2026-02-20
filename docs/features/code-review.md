# Code Review

AI-powered code review with scoring, issue detection, and suggestions.

## SDK

```python
from neuralscope import NeuralScope

ns = NeuralScope(model="openai/gpt-5.2")
review = await ns.review("./src/service.py")
```

## CLI

```bash
neuralscope review ./src/service.py
neuralscope review ./src/service.py --diff
```

## How it works

1. Read source file or git diff
2. Send to LLM with structured review prompt
3. Parse JSON response into `ReviewResult` with issues, score, and strengths
4. Each `Issue` has: line, severity, category, suggestion

## Entities

- **ReviewResult** — score (1-10), summary, issues[], strengths[]
- **Issue** — line, message, severity (info/warning/error/critical), category, suggestion
- **Severity** — INFO, WARNING, ERROR, CRITICAL
- **IssueCategory** — BUG, SECURITY, PERFORMANCE, STYLE, MAINTAINABILITY, COMPLEXITY, NAMING, DOCUMENTATION
