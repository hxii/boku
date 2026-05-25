---
name: "why-boku"
description: "When to use boku vs other automation tools"
version: "1.0"
---
# Why Boku?

Boku is a simple, sequential YAML task runner. It's not trying to replace complex tools — it's for the everyday scripts you'd otherwise write in bash.

## Boku vs Bash Scripts

| Aspect | Bash | Boku |
|--------|------|------|
| Syntax | Quoting, arrays, subshells | YAML, minimal syntax |
| Iteration | `for pkg in a b c; do ...` | `iterate: [a, b, c]` |
| Dependencies | Manual ordering | `depends_on:` explicit |
| Conditions | `if cmd; then ... fi` | `if: cmd` |
| Variables | `$var`, `${var}`, exported | `${var}` in YAML |

### Example: Install packages

**Bash:**
```bash
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
| Syntax | Tabs matter, `.PHONY` | Standard YAML |
| Variables | `$(VAR)` | `${var}` |
| Dependencies | `target: dep1 dep2` | `depends_on: [dep1, dep2]` |
| Iteration | Manual loops | Built-in `iterate` |

## Boku vs Taskfile (Go)

| Aspect | Taskfile | Boku |
|--------|----------|------|
| Binary | Go single binary | Python (pip install) |
| Config | YAML + includes/templates | Minimal YAML |
| Learning curve | More features to learn | Smaller surface area |

## When to Reach for Boku

**Good fit:**
- Package installation scripts
- Project setup workflows
- Git workflow sequences
- Simple CI/CD helper steps
- Recurring maintenance tasks

**Consider alternatives when:**
- You need parallel execution
- Complex conditional logic
- Container orchestration
- Remote task execution

## Install

```bash
pip install boku2
```

Or if you have [pipx](https://pipx.pypa.io):

```bash
pipx install boku2
```

Then run `boku run task.yaml`.
