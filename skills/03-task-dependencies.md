---
name: "task-dependencies"
description: "Control execution order with depends_on - ensure tasks run in the right sequence"
version: "1.0"
---
# Task Dependencies

Use `depends_on` to control which tasks run when and in what order.

## Single Dependency

```yaml
tasks:
  build:
    run: make build

  test:
    depends_on: build  # Runs AFTER build completes
    run: make test
```

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

Tasks with `depends_on` wait for all listed tasks to complete successfully.

## Dependency Graph

```yaml
tasks:
  # Foundation tasks (no dependencies)
  install_deps:
    run: pip install -r requirements.txt

  # Middle tier
  setup_db:
    depends_on: install_deps
    run: python init_db.py

  start_cache:
    depends_on: install_deps
    run: redis-server

  # Final tier
  start_app:
    depends_on:
      - setup_db
      - start_cache
    run: python main.py
```

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

## Notes

- Tasks without `depends_on` run in YAML declaration order
- Circular dependencies cause errors - A→B→A is not allowed
- Failed dependencies skip dependent tasks
