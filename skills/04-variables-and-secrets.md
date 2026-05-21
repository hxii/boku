---
name: "variables-and-secrets"
description: "Master boku's variable system - cross-references, environment vars, and sensitive values"
version: "1.0"
---
# Variables and Secrets

Boku variables make taskfiles flexible and reusable.

## Basic Variables

```yaml
variables:
  project_name: myapp
  python_version: "3.11"

tasks:
  check_python:
    run: echo "Using Python ${python_version}"
```

## Cross-References

Variables can reference other variables:

```yaml
variables:
  base_dir: /usr/local
  bin_dir: ${base_dir}/bin
  venv_path: ${base_dir}/lib/python${python_version}/site-packages
```

Values resolve at runtime in the order declared.

## Environment Variables

```yaml
variables:
  user: ${env:USER}           # Current username
  home: ${env:HOME}           # Home directory
  api_key: "@{env:API_KEY}"   # SENSITIVE - masked in output
```

**Important:** Use `@{}` for sensitive values - they're masked in logs.

## Default Values

```yaml
variables:
  region: ${env:AWS_REGION:-us-east-1}
  retries: ${env:MAX_RETRIES:-3}
```

## In Commands

```yaml
tasks:
  greet:
    run: |
      echo "Hello ${user}"
      echo "Working in ${home}/projects/${project_name}"
```

## Debugging

```bash
# See resolved variables
boku run task.yaml -v
```

**Common error:** `Undefined variable` means the variable name isn't found under `variables:` in your taskfile.
