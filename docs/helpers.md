# Helpers

[← Back to README](README.md)

Helpers, which are located in `~/.config/boku/helpers.yml`, are globally available "shortcuts" that your task can utilize to perform common or repeating operations within your taskfile.

Helpers are not as powerful or as configurable as tasks.

Boku comes with a few built-in helpers, but you're more than welcome to edit this file to add your own, as well as share them with the community.

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
