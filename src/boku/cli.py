import argparse
from pathlib import Path

from boku import __version__
from boku.config import ConfigurationHandler
from boku.exceptions import BokuException, BokuTaskfileError
from boku.helpers import HelperHandler
from boku.logger import logger
from boku.main import Boku, GlobalTasks
from boku.models import BokuArgs
from boku.utils import TASKFILE_TEMPLATE, edit_file, frame


def setup_parser():
    epilog = f"Boku {__version__}"
    ch = ConfigurationHandler()
    _ = HelperHandler()

    # -- Main parser
    parser = argparse.ArgumentParser(
        prog="boku",
        description="Simple, sequential task runner",
        epilog=epilog,
    )
    parser.add_argument("-v", "--verbose", action="count", help="Verbose output.")
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Do not output anything except errors.",
    )
    parser.add_argument(
        "-a",
        "--arg",
        action="append",
        nargs=2,
        metavar=("KEY", "VALUE"),
        help="Pass arguments as key=value pairs",
    )

    shared_parser = argparse.ArgumentParser(add_help=False)
    shared_parser.add_argument(
        "-d",
        "--dry_run",
        action="store_true",
        help="Dry run the taskfile, do not execute commands.",
    )

    subparsers = parser.add_subparsers(dest="command", required=False)

    # -- Global command group
    global_parser = subparsers.add_parser("global", help="Interact with global tasks")
    global_subparsers = global_parser.add_subparsers(dest="global_command", required=True)

    global_list = global_subparsers.add_parser("list", help="List global tasks")
    global_list.set_defaults(func=lambda args: GlobalTasks(args).list_tasks())

    global_add = global_subparsers.add_parser("add", help="Add a global task")
    global_add.add_argument("file", help="YAML task file to add globally", type=str)
    global_add.set_defaults(func=lambda args: GlobalTasks(args).add())

    global_run = global_subparsers.add_parser("run", help="Run a global task", parents=[shared_parser])
    global_run.add_argument("file", help="Global task to run", type=str)
    global_run.set_defaults(func=lambda args: GlobalTasks(args).run())

    global_edit = global_subparsers.add_parser("edit", help="Edit a global task")
    global_edit.add_argument("file", help="YAML task file to edit", type=str, nargs="?")
    global_edit.set_defaults(func=lambda args: GlobalTasks(args).edit())

    global_remove = global_subparsers.add_parser("remove", help="Remove a global task")
    global_remove.add_argument("file", help="YAML task file to remove", type=str, nargs="?")
    global_remove.set_defaults(func=lambda args: GlobalTasks(args).remove())

    # -- Config command
    config_parser = subparsers.add_parser("config", help="Configure boku")
    config_parser.set_defaults(func=lambda args: edit_file(ch.get_config_file()))

    # -- Run command
    run_parser = subparsers.add_parser("run", help="Run a task file", parents=[shared_parser])
    run_parser.add_argument(
        "-c",
        "--check-only",
        action="store_true",
        help="Only validate YAML schema and exit.",
    )
    run_parser.add_argument(
        "-t",
        "--text_only",
        action="store_true",
        help="Only show task text, omitting the output.",
    )
    run_parser.add_argument("--trust", action="store_true", help="Trust STDIN taskfiles")
    run_parser.add_argument("file", help="A valid YAML task file", type=str)

    # -- Info command
    info_parser = subparsers.add_parser("info", help="Show task information/help")
    info_parser.add_argument("file", help="A valid YAML task file", type=str)

    # -- New command
    new_parser = subparsers.add_parser("new", help="Create a new task file")
    new_parser.add_argument(
        "file",
        help="Task file to create",
        type=str,
        nargs="?",
    )

    return parser


def run_command(args: BokuArgs):
    if not args.is_quiet():
        print(frame(f"boku {__version__}"))
    logger.set_verbose(args.get_verbosity())
    logger.debug(f"Arguments: {args}")
    if "arg" in args:
        # NOTE: This is not working yet.
        _ = dict(args.arg) if args.arg else {}
    try:
        if args.command == "run":
            boku = Boku(args)
            # We know file is not None here because it's required for run command
            if args.file:
                assert args.file is not None  # Help type checker
                boku.load_taskfile(str(args.file))
                boku.run()
            else:
                raise BokuTaskfileError("No taskfile specified")
        elif args.command == "info":
            boku = Boku(args)
            # We know file is not None here because it's required for info command
            if args.file:
                assert args.file is not None  # Help type checker
                boku.load_taskfile(str(args.file))
                print(boku.taskfile)
            else:
                raise BokuTaskfileError("No taskfile specified")
        elif args.command == "new":
            if not args.file or (isinstance(args.file, str) and args.file.strip() == ""):  # type: ignore
                filename = input("Enter the name of the task file (task_file.yaml): ")
                filepath = Path().cwd() / filename
                if filepath.exists():
                    raise BokuTaskfileError("File already exists.")
                if filepath.suffix not in [".yaml", ".yml"]:
                    raise BokuTaskfileError("File must be a .yml/.yaml file.")
                filepath.write_text(TASKFILE_TEMPLATE)
                logger.info(f"Created task file: {filepath}")

        else:
            args.func(args)
    except KeyboardInterrupt:
        print(frame("!!!  ABORTED BY USER  !!!"))
    except BokuException as e:
        message = f"[x] boku Error: {e.message}"
        logger.error(message)


def main():
    parser = setup_parser()
    args = parser.parse_args(namespace=BokuArgs())

    if args.command is None:
        parser.print_help()
        return

    run_command(args)


if __name__ == "__main__":
    main()
