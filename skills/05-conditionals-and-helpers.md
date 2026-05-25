---
name: "conditionals-and-helpers"
description: "Skip tasks with conditions and extend boku with built-in helpers"
version: "1.0"
---
# Conditionals and Helpers

## Conditional Execution

Use `if` to run a task only when a condition is true:

### Tool Availability

```yaml
tasks:
  install_python:
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

When `if` evaluates to false, the task is **skipped** (`run_ok` is set to `None`). Dependent tasks will also be skipped.

## Built-in Helpers

Helpers are shortcuts for common operations, configured in `~/.config/boku/helpers.yml`.

Boku ships with these built-in helpers:

| Helper | What it does |
|--------|-------------|
| `notify` | System notification (macOS `osascript`, Linux `notify-send`) |
| `notify_kitten` | Kitty terminal notification |
| `download` | Download a URL with `wget` |
| `http_get` | HTTP GET request with `curl` |
| `brew` | Install a Homebrew package |
| `git_clone` | Clone a git repository |

### Using a Helper

```yaml
tasks:
  build:
    run: make build

  done:
    use: notify
    with_arguments:
      title: Build Complete
      message: All tasks passed!
```

### Adding Custom Helpers

Edit `~/.config/boku/helpers.yml`:

```yaml
my_helper:
  usage: "Do something useful"
  run: 'echo "{arg1}" "{arg2}"'
  args:
    - arg1
    - arg2
```

## Combining Conditionals + Helpers

```yaml
tasks:
  maybe_docker:
    if: command -v docker
    use: notify
    with_arguments:
      title: Docker available
      message: Docker is installed on this machine
```

## Common Conditions Reference

| Condition | Purpose |
|-----------|---------|
| `command -v name` | Check if a tool is installed |
| `test -f path` | File exists |
| `test -d path` | Directory exists |
| `test "$(uname)" = Linux` | OS check |
| `pgrep name` | Process is running |
