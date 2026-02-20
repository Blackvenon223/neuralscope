# Dependency Graph

AST-based module dependency graph with impact analysis.

## Usage

```bash
neuralscope graph ./src --output json
neuralscope impact ./src --diff HEAD~3
```

## How it works

1. Walk Python files, parse AST
2. Extract modules, classes, functions as GraphNodes
3. Extract imports as GraphEdges
4. Build DependencyGraph with adjacency queries
5. Render as DOT, JSON, or SVG
6. Impact analysis: BFS on reverse dependencies
