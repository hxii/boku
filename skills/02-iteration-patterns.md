---
name: "iteration-patterns"
description: "Loop over lists and inline values with boku's iterate feature"
version: "1.0"
---
# Iteration Patterns

The `iterate` field runs a task once per item in a list.

## Over a Variable

```yaml
variables:
  packages:
    - fzf
    - eza
    - bat

tasks:
  install:
    iterate: packages
    run: 'brew install {}'
```

The `{}` placeholder is replaced with each item. **Quote it** to prevent YAML parsing `{}` as an empty mapping.

## Over an Inline List

```yaml
tasks:
  cleanup:
    iterate:
      - /tmp
      - ~/.cache
      - ~/.local/share/trash
    run: 'rm -rf {}/* 2>/dev/null || true'
```

## Nested Iteration (Multiple Placeholders)

When items are sub-lists, multiple `{}` placeholders are consumed in order:

```yaml
variables:
  deps:
    - [-r requirements.txt, ""]
    - [-e, .]

tasks:
  install:
    iterate: deps
    run: 'pip install {} {}'
```

## With a Filter

Only iterate over items matching a pattern:

```yaml
variables:
  repos:
    - github.com/user/a
    - gitlab.com/user/b
    - bitbucket.org/user/c

tasks:
  clone_github:
    iterate: repos
    run: 'git clone {}'
```

## Common Pitfalls

| Problem | Fix |
|---------|-----|
| `ScannerError` on `{}` | Always quote: `run: 'echo {}'` |
| Items not iterating | Confirm the variable is a `list`, not a string |
| Wrong item substituted | Check variable name spelling under `variables:` |
