# Changelog

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
