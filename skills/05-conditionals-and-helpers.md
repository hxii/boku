---
name: "conditionals-and-helpers"
description: "Conditional execution and helper integration - skip tasks when tools aren't available"
version: "1.0"
---
# Conditionals and Helpers

Run tasks only when conditions are met, and integrate external tools.

## Conditional Execution

### Tool Availability
```yaml
tasks:
  install_python_package:
    if: command -v pip
    run: pip install requests
```

### File/Directory Existence
```yaml
tasks:
  remove_cache:
    if: test -d ~/.cache/myapp
    run: rm -rf ~/.cache/myapp
```

### Platform Detection
```yaml
tasks:
  macos_only:
    if: test "$(uname)" = Darwin
    run: brew install --cask rectangle
```

## Helper Integration

Helpers extend boku with external tools.

```yaml
tasks:
  notify_done:
    use: notify
    with_arguments:
      title: Build Complete
      message: All tests passed!
```

### Available Helpers
- `notify` - Desktop notifications
- `discord` - Discord webhook messages
- `slack` - Slack webhook messages

## Combining Features

```yaml
tasks:
  maybe_docker:
    if: command -v docker
    use: notify
    with_arguments:
      title: Starting Docker
      message: Building container...

  build_image:
    depends_on: maybe_docker
    run: docker build -t myapp .
```

## Common Conditions

| Condition | Purpose |
|-----------|---------|
| `command -v name` | Tool is available |
| `test -f file` | File exists |
| `test -d dir` | Directory exists |
| `test "$(uname)" = Linux` | Platform check |
| `pgrep process` | Process running |
