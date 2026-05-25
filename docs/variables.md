# Variables

[← Back to README](../README.md)

Variables are define in the `variables` section of a taskfile, and are defined as a dictionary of key-value pairs.

## Defining Variables

YAML-valid types are supported:

```yaml
variables:
  myfile: "demotask.yml"
  head_n: 5
  secret_variable: "thisismysupersecrettokenstring"
  files_to_check:
    - "file1.txt"
    - "file2.txt"
```

## Using Variables

In commands (i.e. `run`), variables are referenced using the `${variable_name}` syntax:

```yaml
tasks:
  check_file:
    run: test -f ${myfile}
  first_5:
    run: head -n ${head_n} demotask.yml
```

In iteration, variables are referenced as a string:

```yaml
check_files:
  iterate: files_to_check
  run: test -f {}
```

### Environment Variables

You can access environment variables using the `${env:ENV_VAR}` syntax:

```yaml
tasks:
  print_env_var:
    run: echo ${env:HOME}
```

### Sensitive Variables

You can flag variables and environment variables as 'sensitive' using the `@{variable_name}` syntax, which will prevent the variable from being printed in the output:

```yaml
tasks:
  curl_req:
    run: echo @{secret_variable}
```

Which would result in:

```
2025-05-26 12:40:35,497 - boku - INFO - taskfile.py:143 - Executing task curl_req [1/1]
2025-05-26 12:40:35,498 - boku - INFO - task.py:152 - Command: echo $(curl -s --oauth2-bearer **** http://127.0.0.1:8000/messages | jq '.messages[0].content')
2025-05-26 12:40:35,582 - boku - INFO - executor.py:74 - "Hello!"
```
