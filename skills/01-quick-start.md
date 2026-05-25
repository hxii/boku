---
name: "quick-start"
description: "Get started with boku - create and run your first taskfile"
version: "1.0"
---
# Quick Start Guide

Create and run a taskfile in under 5 minutes.

## Create a Taskfile

```bash
boku new mytasks
```

This creates `mytasks.yaml` with a template. Or create one manually:

```yaml
version: 0.2.4
author: your-name
description: My first taskfile

tasks:
  hello:
    description: Print a greeting
    run: echo "Hello from boku!"

  show_date:
    run: date
```

## Run It

```bash
boku run mytasks.yaml
```

## Key Flags

| Flag | What it does |
|------|-------------|
| `-d` | Dry run — show commands without executing |
| `-v` | Verbose — show INFO-level log output |
| `-q` | Quiet — suppress all non-error output |
| `--check-only` | Validate YAML/schema and exit |
| `--text-only` | Show task text, omit command output |
| `-w <dir>` | Set working directory for task execution |

## How Tasks Execute

Tasks run **sequentially** in the order they appear in the YAML file. Each task's `run` command is passed to a shell (`shell=True`), so you can use pipes, redirects, and chaining:

```yaml
tasks:
  check_system:
    run: df -h | head -5
```

## Variables

Variables are available in commands:

```yaml
variables:
  name: world

tasks:
  greet:
    run: echo "Hello ${name}"
```

Use `@{env:HOME}` to safely reference environment variables (masked in logs).
