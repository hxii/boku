# Changelog

## 0.2.4.1 - 2026-05-25

### Fixes

- Filename argument passed to `boku new` is now used instead of ignored
- Documentation updates

## 0.2.4 - 2026-05-18

### New Features

- `-w`/`--working-dir` CLI flag to set working directory for task execution
- Per-task `working_dir` support — each task can override the working directory
- `fail_fast: true` on tasks — abort remaining tasks on first failure
- `on_success` / `on_failure` handler commands per task
- Variable cross-references — `${var}` inside variable values resolves against the taskfile's variable map
- Multi-placeholder iteration — nested lists unpack into multiple `{}` placeholders in a single command
- Variables can hold lists, flattened on resolution
- YAML suffix will be auto-appended when using `run` without specifying `.yml`/`.yaml`, e.g. `boku run my-task`
- Dry-run output now includes the task name

### Fixes

- `post_execute` logs at `INFO` on success, `WARNING` on failure (was logging stderr as ERROR)
- Dry run tasks will be correctly marked as skipped instead of failed
- Task output will now be saved only if it's not empty

> ⚠️ Taskfile schema expanded — see `docs/taskfiles.md` and `docs/tasks.md` for updated schema.

## 0.2.3 - 2025-05-21

### Fixes

- Prevent `HelperHandler` from running `__init__` method multiple times
- Only save output of a command if it is not empty

## [0.2.2] - 2025-05-20

### New Features

- **Dry Run Mode**: Preview task execution without actually running commands using `--dry-run`
- **Show Help by Default**: Running `boku` with no arguments now displays help instead of an error
- **Task conditionals**: Specify `if` conditions for tasks, e.g.:

  ```yaml
  tasks:
    my_task:
      if: test -f README.md
      run: echo "README.md exists"
  ```

- **Helper-Only Tasks**: Create tasks that use predefined helpers without needing a `run` command

  ```yaml
  notify_failure:
    use: notify
    with_arguments:
      title: "Deployment Status"
      message: "Build process failed!"
  ```

- **Better Task Dependencies**: Tasks with dependencies now work properly in dry run mode

### Fixes

- Fixed conditional tasks behavior in dry run mode
- Improved error messages for failed tasks
- Better validation of task configurations
- More reliable task dependency handling
- Updated sample `demotask.yml` file

### Helpers

- Reworked default helpers.
