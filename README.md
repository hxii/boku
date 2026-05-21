# Boku

![Boku Logo](boku.png)

## What is this?

Boku (僕, servant from Japanese) is a simple, sequential YAML task runner written in Python.
While other, most likely much better tools exist that achieve this and much more, the intention
was to create a lightweight tool that can help me with recurring tasks without writing much code
to achieve this.

## Why?

The idea was (and remains) to create a simple tool that I can personally use to automate simple tasks
(with some added benefits like dependencies) without having to write code (either bash or python) to achieve this.
It's NOT meant to be a replacement to other, much better and more sophisticated tools, but rather a simple
solution to a simple problem with little to no learning curve, hence a simple YAML based syntax.

## Installation

You can easily install/run boku via tools like `pipx` or `uv`:

- Via `pipx`: `pipx install https://git.sr.ht/~hxii/boku/archive/0.2.3.tar.gz`.
- Via `uv`: `uv tool install https://git.sr.ht/~hxii/boku/archive/0.2.3.tar.gz`.

!!! Note
    I will figure out a brew formula for this at some point.

!!! Note
    There is probably a way to install the latest version when deploying on SourceHut, but I haven't gotten around to figuring that out yet.

## Configuration

!!! IMPORTANT
    Configuration is yet to be implemented. Sorry!

See configuration documentation [here](docs/configuration.md).

## Documentation

- [Taskfiles](docs/taskfiles.md)
- [Tasks](docs/tasks.md)
- [Helpers](docs/helpers.md)
- [Variables](docs/variables.md)
- [Arguments](docs/arguments.md) - This is not working yet.

## Skills

Step-by-step guides for common patterns and features - check the `skills/` directory:

- [Quick Start](skills/01-quick-start.md) - First taskfile in 5 minutes
- [Iteration](skills/02-iteration-patterns.md) - Loop over lists
- [Dependencies](skills/03-task-dependencies.md) - Control execution order
- [Variables](skills/04-variables-and-secrets.md) - Cross-references
- [Conditionals](skills/05-conditionals-and-helpers.md) - Skip and integrate
- [Why Boku](skills/06-why-boku.md) - When to use vs other tools
