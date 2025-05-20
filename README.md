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

- Via `pipx`: `pipx install https://git.sr.ht/~hxii/boku/archive/0.2.0.tar.gz`.
- Via `uv`: `uv tool install https://git.sr.ht/~hxii/boku/archive/0.2.0.tar.gz`.

!!! Note
    I will figure out a brew formula for this at some point.

## Features

- Configure tasks as YAML files.
- Conditional tasks via `if`, e.g. `if: test -f README.md`
- Pass in arguments via `-a key value`.
- Pre-set variables via:

  ```YAML
  variables:
    my_variable: my value
  ```

- Save output to variables via `save_output: variable_name`.
- Use variables with `${variable_name}`.
- Use environment variables with `${env:ENV_VAR}`.
- Use sensitive variables with `@{variable_name}` or `@{env:secret_env_var}`, which will not print the value in logs.
- Iterate on multiple values via:

  ```YAML
  tasks:
    remove_cache:
      iterate:
        - ~/dev/boku2/*.tmp
        - ~/dev/cache_dev/
      run: rm -r {}
  ```

- Simple dependencies via:

  ```YAML
  tasks:
    my_first_task:
      run: brew update
    my_second_task:
      depends_on: my_first_task
      run: brew upgrade
  ```

- Set success return code via `success_code: 1`.
- Run command `on_success`.
- Run command `on_failure`.
- Configure global helper wrappers in `~/.config/boku/helpers.yml`
- Preset helpers are configured by default:
  - `notify` - Cross-platform system notifications
  - `notify_kitten` - Send notifications to via KittyTerm's Kitten utility
  - `download` - Download a file from a URL via `wget`
  - `http_get` - Make HTTP requests and process responses
  - `git_clone` - Clone git repositories with optional target directory

  - Example of using the HTTP helper:

    ```YAML
    notify_test:
      use: notify
      with_arguments:
        title: Hello from boku!
        message: Hello world!
    ```

- Use global helpers:

  ```yaml
  tasks:
    send_success_notification:
      use: osx_notification
      with_arguments:
        title: My notification
        message: Hello from Boku!
  ```

- TODO: Allow reading tasks from STDIN or URL.
- TODO: Allow `boku global install` from URL.

## Full Schema

```YAML
version: 0.1.0 # Boku version
author: Paul Glushak <hxii@0xff.nu> # Author information
description: This is the description of the task file.

variables:
  my_first_var: "A string value"
  my_second_var: 80085
  my_third_var:
    - "list"
    - "of"
    - "items"
  my_secret_var: "A totally secret value"

tasks: # Dict of tasks
  prerequisite_task:
    description: "Dummy task"
    run: "true"
  my_task:
    description: "Optional description of the task"
    run: echo "{}" # The command to run.
    # If `iterate` is used, the iteration will replace `{}` or be appended to the command.
    working_dir: "~"
    save_output: my_task # Variable name to save the output to
    iterate: my_third_var # List of items to iterate over.
    # Str evaluates to a variable.
    depends_on: # List of successful tasks that this task depends on.
      - prerequisite_task
    success_code: 0 # Which return code do we consider successful
    on_success: echo "Done!" # Command to run if successful
    on_failure: echo "Oh no!" # Command to run if failed
  my_final_task:
    depends_on:
      - my_task
    run: |
      echo "${my_task}" | tr -d '\n'
      echo "We can also use multiline commands"
  my_secret_task:
    run: 'echo "We can also hide secret variables with the @ symbol: @{my_secret_var}"'
    suppress_output: true
```
