# Tasks

[← Back to README](../README.md)

Tasks are defined in the `tasks` section of a taskfile, and are defined as a dictionary of key-value pairs.
The only _required_ key is `run`, which specifies the command to run.

Task arguments are defined as follows:

| Argument         | Type                       | Required | Description                                                                                               |
| ---------------- | -------------------------- | -------- | --------------------------------------------------------------------------------------------------------- |
| `description`    | String                     | No       | Description of what the task does. Mainly used when reading the taskfile. Shown when `--verbose` is used. |
| `run`            | String                     | Yes      | The command that boku will run. Can be multiline.                                                         |
| `working_dir`    | String                     | No       | Change the working directory for the command. Default inherits from taskfile.                             |
| `save_output`    | String                     | No       | The name of the [variable](./variables.md) to save the output to.                                         |
| `iterate`        | List(String)               | No       | Each item will execute the command defined in `run`                                                       |
| `fail_fast`      | Boolean                    | No       | Default of `False`. Setting this to `True` will halt taskfile execution if this task fails                |
| `depends_on`     | List(String)               | No       | List of tasks that have to succeed in order for this task to be executed                                  |
| `success_code`   | Integer                    | No       | Default of `0`. Which return code is considered as a successful execution                                 |
| `on_success`     | String                     | No       | The command to execute if this task finished successfully                                                 |
| `on_failure`     | String                     | No       | The command to execute if this task finished unsuccessfully                                               |
| `use`            | String                     | No       | The name of the [helper](./helpers.md) to use for this task                                               |
| `with_arguments` | Dictionary(String, String) | No       | Arguments to pass to the helper defined in `use`                                                          |
| `if`             | String                     | No       | The command that must execute successfully in order for `run` to execute                                  |
