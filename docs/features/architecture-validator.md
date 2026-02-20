# Architecture Validator

Validate project architecture against defined rules.

## Usage

```bash
neuralscope validate ./src --rules ./rules.yaml
```

## Entities

- **ValidationReport** - rules checked, violations, passed
- **Violation** - rule, file, message, severity (WARNING/ERROR)
