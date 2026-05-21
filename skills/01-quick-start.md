---
name: "quick-start"
description: "Get started with boku - your first taskfile in 5 minutes"
version: "1.0"
---
# Quick Start Guide

A minimal taskfile to get you running with boku immediately.

## Your First Taskfile

Create `task.yaml`:
```yaml
version: 0.2.4
description: My first boku taskfile

tasks:
  hello:
    run: echo "Hello from boku!"

  date_info:
    run: date
```

Run it:
```bash
boku run task.yaml
```

## Add Some Features

```yaml
version: 0.2.4
variables:
  packages:
    - ripgrep
    - fd
    - bat

tasks:
  list_packages:
    description: Show what will be installed
    run: |
      echo "Will install: ${packages}"  # Variables not expanded in shell

  install_all:
    iterate: packages
    run: 'brew install {}'
```

## Run Options

| Command | What it does |
|---------|--------------|
| `boku run task.yaml` | Execute all tasks |
| `boku run task.yaml -d` | Dry run (show commands, don't execute) |
| `boku run task.yaml --check-only` | Validate YAML/schema only |
| `boku run task.yaml -v` | Verbose output |
