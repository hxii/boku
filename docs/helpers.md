# Helpers

[← Back to README](../README.md)

Helpers, which are located in `~/.config/boku/helpers.yml`, are globally available "shortcuts" that your task can utilize to perform common or repeating operations within your taskfile.

Helpers are not as powerful or as configurable as tasks.

Boku comes with a few built-in helpers, but you're more than welcome to edit this file to add your own, as well as share them with the community.

## Built-in Helpers

| Helper | Purpose |
|--------|---------|
| `notify` | Desktop notification (macOS `osascript` or Linux `notify-send`) |
| `notify_kitten` | macOS notification via Kitty terminal's kitten utility |
| `download` | Download a URL to the current directory using `wget` |
| `http_get` | Make an HTTP GET request using `curl` |
| `brew` | Install a Homebrew package by name |
| `git_clone` | Clone a git repository |

## Syntax

```YAML
helper_id:
  usage: "This is a description of the helper"
  # Run a command with the provided arguments
  run: "echo {message}"
  # Define configurable arguments in the `args` section
  args:
    - message
```

### Arguments

Arguments are placeholders in the `run` command that get substituted when the helper is called. Define them as a list of strings:

```YAML
download:
  usage: "Download a URL {url} with optional {flags}"
  run: "wget {url} {flags}"
  args:
    - url
    - flags
```

When another task calls this helper via `use`, it passes values through `with_arguments`:

```YAML
tasks:
  fetch_data:
    use: download
    with_arguments:
      url: "https://example.com/data.json"
      flags: "-q"
```

Argument values can contain spaces when quoted:

```yaml
with_arguments:
  message: "Hello world"
```
