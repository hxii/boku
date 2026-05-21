---
name: "why-boku"
description: "When to use boku vs other tools - simple automation without programming overhead"
version: "1.0"
---
# Why Boku?

A quick comparison to help you decide if boku fits your workflow.

## Boku vs Bash Scripts

| Aspect | Bash | Boku |
|--------|------|------|
| Learning curve | Steep (syntax, quoting, arrays) | Gentle (YAML, minimal syntax) |
| Iteration | `for pkg in a b c; do ...` | `iterate: [a, b, c]` |
| Dependencies | Manual ordering | `depends_on:` explicit |
| Conditions | `if cmd; then ...` | `if: cmd` |
| Variables | `$var`, `${var}`, exported | `${var}` in YAML |
| Cross-platform | Shell-dependent | Python-based |

### Example: Installing packages

**Bash:**
```bash
#!/bin/bash
packages=("fzf" "eza" "bat")
for pkg in "${packages[@]}"; do
  if command -v brew &>/dev/null; then
    brew install "$pkg"
  fi
done
```

**Boku:**
```yaml
variables:
  packages: [fzf, eza, bat]

tasks:
  install:
    if: command -v brew
    iterate: packages
    run: 'brew install {}'
```

## Boku vs Make

| Aspect | Make | Boku |
|--------|------|------|
| Syntax | Domain-specific (tabs matter!) | Standard YAML |
| Shell commands | Recipe lines | `run:` field |
| Variables | `$(VAR)` | `${var}` |
| Dependencies | `target: dep1 dep2` | `depends_on: [dep1, dep2]` |
| Iteration | Manual loops | Built-in `iterate` |
| Conditionals | `ifeq` syntax | `if:` field |

## Boku vs Taskfile (Go)

| Aspect | Taskfile | Boku |
|--------|----------|------|
| Language | Go (single binary) | Python (pip/pix) |
| Config format | YAML | YAML |
| Syntax | Rich (includes, templating) | Minimal (variables, iteration) |
| Overhead | More features to learn | Simpler surface area |

## When to Choose Boku

✅ **Good fit:**
- Simple automation tasks
- Package installation scripts
- Project setup workflows
- CI/CD helper tasks
- Git workflow sequences

❌ **Consider alternatives if:**
- Need complex programming logic
- Require parallel execution
- Want container orchestration
- Need remote task execution

## Quick Decision Matrix

| Need | Tool |
|------|------|
| Simple loops + bash | **Boku** |
| Complex logic + modules | Python script |
| Parallel builds | Make/Gulp |
| Container orchestration | Docker Compose |
| Remote execution | Ansible |
| CI/CD pipelines | GitHub Actions |

## Try Boku

```bash
# Install
pipx install boku

# Create your first taskfile
echo 'tasks:
  hello:
    run: echo "Hello from boku!"' > task.yaml

# Run
boku run task.yaml
```
