---
name: "variables-and-secrets"
description: "Use variables, environment references, and sensitive values in taskfiles"
version: "1.0"
---

# Variables and Secrets

## Basic Variables

```yaml
variables:
  project_name: myapp
  python_version: "3.11"

tasks:
  check:
    run: echo "Using Python ${python_version} for ${project_name}"
```

Variables are referenced with `${name}` in commands.

## Cross-References

Variables can reference other variables:

```yaml
variables:
  base_dir: /usr/local
  bin_dir: ${base_dir}/bin
```

Boku resolves these iteratively until all references are expanded.

## Environment Variables

Read environment variables with `${env:VAR}`:

```yaml
tasks:
  show_home:
    run: echo "${env:HOME}"
```

## Sensitive Values

Prefix with `@` to mark a variable as sensitive. Its value is masked (`****`) in log output:

```yaml
variables:
  api_key: "@{env:API_KEY}"

tasks:
  deploy:
    run: ./deploy.sh "${api_key}"
```

The `@` tells boku to mask the value in logs. The actual value is still passed to shell commands.

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
boku -v run task.yaml   # See resolved variable values in output
```

## Common Errors

| Error                                | Cause                                      |
| ------------------------------------ | ------------------------------------------ |
| `Undefined variable`                 | Variable name not found under `variables:` |
| `Environment variable 'X' not found` | Referenced `${env:X}` but X is not set     |
