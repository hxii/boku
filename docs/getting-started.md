# Getting Started

[← Back to README](../README.md)

Getting started with `boku` is simple, and this document will guide you how.

## Creating a New Taskfile

You can run `boku new` and provide a filename, which will create a dummy taskfile.
Or you can also just create an empty file like `touch mynewtask.yaml` and then
edit it according to the [taskfile schema](./taskfiles.md).

## Editing a Taskfile

You can edit the taskfile using your favorite editor.
For convenience, you can quickly edit [global taskfiles](./taskfiles.md) using `boku global edit <taskfile_name>`.

You can read how tasks are defined [here](./tasks.md).

## Running a Taskfile

In order to run a taskfile use `boku run <taskfile_name>`. If you choose to omit
the `.yml/.yaml` suffix, boku will append it automatically when locating the file.

Running a global taskfile is done similarly via `boku global run <taskfile_name>`.

### Dry Run

It's possible to run a taskfile without it executing any of the commands. This is useful
when debugging the flow. This can be done by specifying `--dry_run/-d` as an argument:
`boku run --dry_run <taskfile_name>`, and to make sure you see all the messages you
can use `--verbose`: `boku --verbose run --dry_run <taskfile_name>`

## Information About a Taskfile

To quickly glance at what a taskfile does, run `boku info <taskfile_name>`
