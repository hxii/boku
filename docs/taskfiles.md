# Taskfiles

[← Back to README](../README.md)

Taskfiles in Boku are defined as `YAML` files, and can have either `.yml` or `.yaml` suffix.

There are two kinds of taskfiles, that only differ in their availability.

- Local - taskfiles located in your current working directory.
- Global - globally available taskfiles located in the `tasks` directory within `boku`'s [configuration directory](docs/configuration.md).

Global taskfiles are just a convenience, so you can, of course, run either taskfile type if you provide the absolute path to it.

## Taskfile Anatomy

The goal is to have a simple structure throughout:

```yaml
# boku-taskfile <- Used for schema manifest
version: 0.2.3 # Version of boku the task was written for
author: Your Name <your@email.com>
description: A description of what this taskfile is for or what it does

variables: # A dictionary of variables
tasks: # A dictionary of tasks
```

## Example Taskfile

Here's a somewhat realistic example taskfile that will use `brew` to install three packages, and notify the user when done:

```yaml
version: 0.2.3
author: hxii <hxii@email.com>
description: A demo taskfile.

variables:
  brew_packages:
    - fzf
    - eza
    - uv

tasks:
  install_packages:
    if: test -x "$(command -v brew)"
    iterate: brew_packages
    run: brew install {}
  let_me_know:
    use: notify
    with_arguments:
      title: "Boku Task Completed"
      message: "All done!"
```
