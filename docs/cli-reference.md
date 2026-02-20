# CLI Reference

## Global Options

| Option | Description |
|--------|-------------|
| `--version`, `-V` | Show version |
| `--model`, `-m` | Override LLM model |
| `--profile`, `-p` | Prompt profile |

## Commands

### `neuralscope review <path>`
AI-powered code review with scoring and issue detection.

```bash
neuralscope review ./src/service.py
neuralscope review ./src/service.py --diff
neuralscope review ./src/service.py --model anthropic/claude-sonnet-4-6-20260217
```

### `neuralscope docs <path>`
Generate documentation from source code.

```bash
neuralscope docs ./src/models.py
neuralscope docs ./src/models.py --format markdown
```

### `neuralscope graph <path>`
Build dependency graph for a project.

```bash
neuralscope graph ./src --output json
neuralscope graph ./src --output dot
```

### `neuralscope impact <path>`
Analyze change impact via dependency graph.

```bash
neuralscope impact ./src --diff HEAD~3
```

### `neuralscope scan <path>`
Scan for security vulnerabilities.

```bash
neuralscope scan ./src
```

### `neuralscope test-gen <path>`
Generate pytest tests for a file.

```bash
neuralscope test-gen ./src/utils.py
```

### `neuralscope ask <question>`
Ask questions about the codebase (RAG-powered).

```bash
neuralscope ask "How does authentication work?" --project ./src
```

### `neuralscope health [path]`
Show project health dashboard.

```bash
neuralscope health ./src
```

### `neuralscope pr-summary`
Generate PR description from git diff.

```bash
neuralscope pr-summary --diff HEAD~1
```

### `neuralscope validate <path>`
Validate architecture rules.

```bash
neuralscope validate ./src --rules ./rules.yaml
```

### `neuralscope profile-create <name>`
Create a new prompt profile.

```bash
neuralscope profile-create security-lead --desc "Security-focused reviewer" --temp 0.3
```

### `neuralscope profile-list`
List all prompt profiles.

```bash
neuralscope profile-list
```

### `neuralscope models`
List available LLM providers and models.

```bash
neuralscope models
```
