# Tasks

[← Back to README](../README.md)

Tasks are define in the `tasks` section of a taskfile, and are defined as a dictionary of key-value pairs.
The only *required* key is `run`, which specifies the command to run.

Task arguments are defined as follows:

- `description` - A string describing the task.
- `run` - A string with the command to run.
- `working_dir` - A string with the working directory to use. If not specified, the current directory is used.
- `save_output` - A string with the name of the [variable](docs/variables.md) to save the output of `run` to.
- `iterate` - An array of strings to iterate the `run` command over. If a string is provided, it will be considered as a variable name to iterate over.
- `depends_on` - An array of task names that this task depends on. The task will not run if any of the dependent tasks fail.
- `success_code` - An integer representing the success exit code of the command. Defaults to `0`.
- `on_success` - A string with the command to run on success.
- `on_failure` - A string with the command to run on failure.
- `use` - A string with the name of a [helper](docs/helpers.md) function to use.
- `with_arguments` - A dictionary of arguments to pass to the helper function.
- `if` - A string with a condition to check before running the task. The condition is a command, e.g. `test -f myfile.txt`.
