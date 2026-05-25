---
name: "task-dependencies"
description: "Control task execution order with depends_on"
version: "1.0"
---
# Task Dependencies

Use `depends_on` to declare that a task requires other tasks to succeed first.

## Single Dependency

```yaml
tasks:
  build:
    run: make build

  test:
    depends_on: build
    run: make test
```

`test` waits for `build` to complete successfully. If `build` fails, `test` is skipped.

## Multiple Dependencies

```yaml
tasks:
  setup_db:
    run: createdb myapp

  run_migrations:
    run: alembic upgrade head

  start_server:
    depends_on:
      - setup_db
      - run_migrations
    run: uvicorn main:app
```

All listed dependencies must succeed before the task runs.

## Dependency Chain Example

```yaml
tasks:
  install_deps:
    run: pip install -r requirements.txt

  setup_db:
    depends_on: install_deps
    run: python init_db.py

  start_cache:
    depends_on: install_deps
    run: redis-server

  start_app:
    depends_on:
      - setup_db
      - start_cache
    run: python main.py
```

This creates a diamond-shaped dependency graph — `install_deps` runs once, then both `setup_db` and `start_cache` run, then `start_app`.

## With Iteration

```yaml
variables:
  services:
    - postgres
    - redis
    - nginx

tasks:
  pull_images:
    iterate: services
    run: 'docker pull {}:latest'

  start_containers:
    depends_on: pull_images
    iterate: services
    run: 'docker run -d {}'
```

## Behavior Notes

- **Skipped dependencies propagate**: If a dependency has `run_ok: None` (skipped via `if`), dependent tasks are also skipped.
- **Failed dependencies skip dependents**: A dependent task will not run and will not trigger its `on_failure` handler.
- **No circular deps**: Circular dependency graphs cause errors.
- **No `depends_on`**: Tasks run in YAML declaration order alongside other independent tasks.
