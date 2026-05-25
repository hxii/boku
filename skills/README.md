# Boku Skills

Step-by-step guides for mastering boku's features.

## Fundamentals
- [Quick Start](01-quick-start.md) — Create and run your first taskfile
- [Iteration Patterns](02-iteration-patterns.md) — Loop over lists and values
- [Task Dependencies](03-task-dependencies.md) — Control execution order

## Intermediate
- [Variables and Secrets](04-variables-and-secrets.md) — Cross-references and sensitive values
- [Conditionals and Helpers](05-conditionals-and-helpers.md) — Skip tasks and use built-in tools

## Reference
- [Why Boku](06-why-boku.md) — When to use boku vs other tools

## Using These Skills

Each file is self-contained. Point an LLM agent at a specific file for guidance on that feature:

```
Read /path/to/boku/skills/02-iteration-patterns.md
```

Built-in helpers (defined in `helpers.yml`): `notify`, `notify_kitten`, `download`, `http_get`, `brew`, `git_clone`.
