import os
import shutil
from datetime import datetime
from pathlib import Path
from textwrap import dedent

from picksy import Picksy

from boku.config import ConfigurationHandler
from boku.exceptions import BokuTaskfileError
from boku.logger import logger
from boku.taskfile import TaskFile
from boku.utils import edit_file, yaml_suffixer
from boku.models import BokuArgs


class Boku:
    def __init__(self, args: BokuArgs) -> None:
        """Initialize Boku."""
        self.taskfile: TaskFile | None = None
        self.args = args
        self.working_dir = None
        logger.info(f"Boku initialized {datetime.now()}")
        logger.info("Getting environment variables")
        self.environment = os.environ.copy()
        logger.debug(f"Environment: {self.environment}")

    def load_taskfile(self, taskfile: str | Path) -> int:
        """Load a taskfile from the system.

        Args:
            taskfile (str|Path): Path to the taskfile.

        Returns:
            size (int): Size of the taskfile.
        """
        logger.info(f"Loading taskfile: {taskfile}")
        self.taskfile = TaskFile(taskfile_path=Path(taskfile), args=self.args)
        self.taskfile.working_dir = (
            self.taskfile.taskfile_path.absolute().parent
            if not self.args.working_dir
            else Path(self.args.working_dir).expanduser()
        )
        self.print_taskfile()
        return self.taskfile.taskfile_path.stat().st_size

    def print_taskfile(self) -> None:
        if not self.args.is_quiet():
            print(
                dedent(
                    f"""
                            \uf15b File: {self.taskfile.taskfile_path}
                            \uf4d4 Working Dir: {self.taskfile.working_dir}
                            \uf4ff Author: {self.taskfile.author}
                            \ue64e Description: {self.taskfile.description}""".strip("\n")
                ),
            )

    def run(self) -> None:
        """Run the taskfile."""
        if not self.taskfile:
            raise BokuTaskfileError("No taskfile loaded")
        self.taskfile.execute_tasks()


class GlobalTasks:
    """Global Task Object"""

    def __init__(self, args: BokuArgs) -> None:
        self.config_handler = ConfigurationHandler()
        self.args = args
        self.global_tasks: dict[str, Path] = {
            task.stem: task for task in self.config_handler.global_task_dir.glob("*.y*ml")
        }
        """Dictionary of file stem -> task path."""

    def add(self) -> None:
        """Add a global task from a local file."""
        if not self.args.file:
            raise BokuTaskfileError("No file specified")
        taskfile = TaskFile(taskfile_path=Path(self.args.file))
        if taskfile.taskfile_path.stem in self.global_tasks.keys():
            raise BokuTaskfileError(f"Taskfile {self.args.file} already exists in global tasks.")
        print(f"{taskfile.description}\nby {taskfile.author}")
        proceed = input("Add global task? [y/N]: ").lower().strip() == "y"
        if proceed:
            return_path = shutil.copy(
                taskfile.taskfile_path.absolute(),
                self.config_handler.global_task_dir / taskfile.taskfile_path.name,
            )
            print(f"Task copied to {return_path}")

    def remove(self) -> None:
        """Remove a global task."""
        if not self.args.file:
            raise BokuTaskfileError("No file specified")
        if self.args.file in self.global_tasks.keys():
            logger.debug(f"Taskfile {self.args.file} found in global tasks.")
            taskfile_path: Path = self.global_tasks.get(self.args.file)
            if input(f"Delete {taskfile_path}? [y/N]: ").lower().strip() == "y":
                taskfile_path.unlink()
                print(f"Taskfile {taskfile_path} deleted.")
        else:
            raise BokuTaskfileError(f"Taskfile {self.args.file} not found in global tasks.")

    def edit(self) -> None:
        """Edit a global task using $EDITOR."""
        ch = ConfigurationHandler()
        global_tasks = {task.name: task for task in ch.global_task_dir.glob("*.y*ml")}
        if not self.args.file:
            p = Picksy(list(global_tasks.values()))
            logger.debug(f"Choice: {p.get_choice()}")
            edit_file(str(p.get_choice()))
        else:
            taskfile = yaml_suffixer(self.args.file)
            for name, task in global_tasks.items():
                if taskfile == name:
                    edit_file(str(task))

    def list_tasks(self) -> None:
        """List all global tasks."""
        print("Tasks available globally:")
        for task in self.global_tasks.keys():
            print(task)

    def run(self) -> None:
        """Run a global task."""
        for name, task in self.global_tasks.items():
            if self.args.file == name:
                logger.debug(f"Global taskfile: {task}")
                boku = Boku(self.args)
                boku.load_taskfile(task)
                boku.run()
                return
        raise BokuTaskfileError(f"Taskfile {self.args.file} not found in global tasks.")
