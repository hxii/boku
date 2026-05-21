---
name: "iteration-patterns"
description: "Master boku's iteration feature - loop over lists, files, and dynamic values"
version: "1.0"
---
# Iteration Patterns

Boku's `iterate` feature replaces repetitive shell loops with clean YAML.

## Basic Iteration

```yaml
variables:
  packages:
    - fzf
    - eza
    - bat

tasks:
  install_packages:
    iterate: packages
    run: 'brew install {}'
```

**Key:** Quote `{}` to prevent YAML parsing it as an empty dict.

## Multiple Lists

```yaml
variables:
  node_packages:
    - typescript
    - prettier
  python_packages:
    - requests
    - pyyaml

tasks:
  install_node:
    iterate: node_packages
    run: 'npm install -g {}'

  install_python:
    iterate: python_packages
    run: 'pip install {}'
```

## Conditional Iteration

```yaml
tasks:
  cleanup_old_files:
    if: command -v find
    iterate:
      - /tmp
      - ~/.cache
    run: 'rm -rf {}/* 2>/dev/null || true'
```

## With Dependencies

```yaml
tasks:
  setup_venv:
    run: python -m venv .venv

  install_deps:
    iterate:
      - -r requirements.txt
      - -e .
    run: '.venv/bin/pip install {}'
    depends_on: setup_venv
```

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| `yaml.scanner.ScannerError` | Quote `{}`: `run: 'echo {}'` |
| Iteration doesn't run | Verify variable is a list under `variables:` |
| Wrong values substituted | Check for typos in variable names |
