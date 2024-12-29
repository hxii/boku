# Boku

## What is this?

Boku (僕, servant from Japanese) is a simple, sequential YAML task runner written in Python.
While other, most likely much better tools exist that achieve this and much more, the intention
was to create a lightweight tool that can help me with recurring tasks without writing much code
to achieve this.

## Features

- Configure tasks as YAML files.
- Pass in arguments via `-a key value`.
- Pre-set variables via:

  ```YAML
  variables:
    my_variable: my value
  ```

- Save output to variables via `save_output: variable_name`.
- Use variables with `${variable_name}`.
- Use environment variables with `${env:ENV_VAR}`.
- Iterate on multiple values via:

  ```YAML
  tasks:
    remove_cache:
      iterate:
        - ~/dev/boku2/*.tmp
        - ~/dev/cache_dev/
      run: rm -r
  ```

- Simple dependencies via:

  ```YAML
  tasks:
    my_first_task:
      run: brew update
    my_second_task:
      depends_on: brew upgrade
      run: brew upgrade
  ```

- Set success return code via `success_code: 1`.
- Run command `on_success`.
- Run command `on_failure`.
- TODO: Global helper wrappers, e.g.:

  ```YAML
  helpers:
  - name: telegram_message
    command: "curl -X POST https://api.telegram.org/bot<token>/sendMessage -d 'chat_id=<chat_id>&text=<message>'"
    args:
      - token
      - chat_id
      - message
  ```
