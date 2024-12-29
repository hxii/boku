import argparse

from boku.exceptions import BokuException
from boku.logger import logger
from boku.main import Boku, __version__, GlobalTasks
from boku.utils import frame

epilog = f"Boku {__version__}"
gt = GlobalTasks()

# Main parser
parser = argparse.ArgumentParser(
    prog="boku",
    description="Simple, sequential task runner",
    epilog=epilog,
)
parser.add_argument("-v", "--verbose", action="count", help="Verbose output.")
parser.add_argument(
    "-V", "--version", action="version", version=f"%(prog)s {__version__}"
)
parser.add_argument(
    "-q", "--quiet", action="store_true", help="Do not output anything except errors."
)

# Create top-level subparsers
subparsers = parser.add_subparsers(dest="command", required=True)

# Global command group
global_parser = subparsers.add_parser("global", help="Interact with global tasks")
global_subparsers = global_parser.add_subparsers(dest="global_command", required=True)

# Global list command
global_list = global_subparsers.add_parser("list", help="List global tasks")
global_list.set_defaults(func=lambda args: gt._list(args))

# Global add command
global_add = global_subparsers.add_parser("add", help="Add a global task")
global_add.add_argument("file", help="YAML task file to add globally", type=str)
global_add.set_defaults(func=lambda args: gt.add(args))

# Global run command
global_run = global_subparsers.add_parser("run", help="Run a global task")
global_run.add_argument("file", help="Global task to run", type=str)
global_run.set_defaults(func=lambda args: gt.run(args))

# Global edit command
global_edit = global_subparsers.add_parser("edit", help="Edit a global task")
global_edit.add_argument("file", help="YAML task file to edit", type=str, nargs="?")
global_edit.set_defaults(func=GlobalTasks.edit)

# Global remove command
global_remove = global_subparsers.add_parser("remove", help="Remove a global task")
global_remove.add_argument("file", help="YAML task file to remove", type=str, nargs="?")
global_remove.set_defaults(func=lambda args: gt.remove(args))

# Regular command parser
run_parser = subparsers.add_parser("run", help="Run a task file")
run_parser.add_argument(
    "-c",
    "--check-only",
    action="store_true",
    help="Only validate YAML schema and exit.",
)

run_parser.add_argument(
    "-d",
    "--dry_run",
    action="store_true",
    help="Dry run the taskfile, do not execute commands.",
)
run_parser.add_argument(
    "-t",
    "--text_only",
    action="store_true",
    help="Only show task text, omitting the output.",
)
run_parser.add_argument("--trust", action="store_true", help="Trust STDIN taskfiles")
run_parser.add_argument("file", help="A valid YAML task file", type=str)
run_parser.add_argument(
    "-a",
    "--arg",
    action="append",
    nargs=2,
    metavar=("KEY", "VALUE"),
    help="Pass arguments as key=value pairs",
)

args = parser.parse_args()
if not args.quiet:
    print(frame(f"boku {__version__}"))
logger.set_verbose(args.verbose or 0)
logger.debug(f"Arguments: {args}")
if "arg" in args:
    task_args = dict(args.arg) if args.arg else {}


def run():
    try:
        if args.command == "global":
            args.func(args)
            return

        if args.command == "run":
            boku = Boku()
            boku.load_taskfile(args.file)
            if not args.quiet:
                print(
                    f"Loaded {boku.taskfile.taskfile_path.name} by {boku.taskfile.author}"
                )
            boku.taskfile.execute_tasks()
    except KeyboardInterrupt:
        print("\n!!!\nABORTED BY USER\n!!!")
    except BokuException as e:
        message = f"[x] boku Error: {e.message}"
        logger.error(message)
