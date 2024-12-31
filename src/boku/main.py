import os
import re
import shutil
import subprocess
from argparse import Namespace
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from packaging.version import Version
from picksy import Picksy

from boku.exceptions import (
    BokuDependencyError,
    BokuTaskError,
    BokuTaskfileError,
    BokuVariableError,
)
from boku.logger import logger
from boku.utils import TASK_SCHEMA, edit_file, yaml_suffixer

__version__ = "0.2.0"


class Boku:
    def __init__(self) -> None:
        """Initialize Boku."""
        self.taskfile: TaskFile | None = None
        logger.info(f"Boku initialized {datetime.now()}")
        logger.info("Getting environment variables")
        self.environment = os.environ.copy()
        logger.debug(f"Environment: {self.environment}")
        pass

    def load_taskfile(self, taskfile: str | Path) -> int:
        """Load a taskfile from the system.

        Args:
            taskfile (str|Path): Path to the taskfile.

        Returns:
            size (int): Size of the taskfile.
        """
        logger.info(f"Loading taskfile: {taskfile}")
        self.taskfile = TaskFile(taskfile_path=Path(taskfile))
        return self.taskfile.taskfile_path.stat().st_size

    def run(self, args) -> None:
        """Run the taskfile."""
        if not self.taskfile:
            raise BokuTaskfileError("No taskfile loaded")
        self.taskfile.execute_tasks()


@dataclass
class TaskFile:
    """Taskfile Object."""

    version: str = ""
    """Version of boku required to run the task file."""
    author: str = "Unknown"
    """Author of the task file."""
    description: str = "No Description"
    """Description of the purpose of the task file."""
    tasks: dict[str, "Task"] = field(default_factory=dict)
    """Dictionary of tasks."""
    taskfile_path: Path = Path()
    """Path to the taskfile."""
    taskfile_raw: str = ""
    """Raw taskfile content."""
    taskfile_yaml: dict[str, Any] = field(default_factory=dict)
    """Parsed taskfile content."""
    variables: dict[str, Any] = field(default_factory=dict)
    """Variables to be used in tasks."""

    def __post_init__(self):
        """Run basic checks on the taskfile."""
        if not self.taskfile_path.exists():
            raise BokuTaskfileError(f"Taskfile not found: {self.taskfile_path}")
        if not self.taskfile_path.is_file():
            raise BokuTaskfileError(f"Taskfile is not a file: {self.taskfile_path}")
        if self.taskfile_path.suffix not in (".yaml", ".yml"):
            raise BokuTaskfileError(
                f"Taskfile is not a valid YAML file: {self.taskfile_path}"
            )
        logger.debug(f"Taskfile: {self.taskfile_path.absolute()}")
        logger.debug(
            f"Modified: {datetime.fromtimestamp(self.taskfile_path.stat().st_mtime)}"
        )
        logger.debug(f"Size: {self.taskfile_path.stat().st_size}")
        logger.debug(f"Owner: {self.taskfile_path.owner()}")
        self.parse_taskfile()

    def parse_taskfile(self) -> None:
        """Parse the taskfile and populate tasks and variables."""
        logger.info("Parsing taskfile")
        try:
            logger.debug("Reading taskfile")
            self.taskfile_raw = self.taskfile_path.read_text()
            logger.debug("Loding YAML")
            self.taskfile_yaml = yaml.safe_load(self.taskfile_raw)
            logger.info("Extracting metadata")
            self.author = self.taskfile_yaml.get("author", "Unknown")
            self.description = self.taskfile_yaml.get("description", "")
            self.version = self.taskfile_yaml.get("version", "")
            logger.info(f"Description: {self.description}")
            logger.info(f"Author: {self.author}, version: {self.version}")
            if not self.version:
                logger.warning(
                    f"Version not specified in taskfile; assuming current version {__version__}"
                )
                self.version = __version__
            if Version(self.version) < Version(__version__):
                logger.warning(
                    f"Taskfile has version {self.version}, which is older than Boku version {__version__}"
                )
            logger.info("Extracting variables")
            self.variables = self.taskfile_yaml.get("variables", {})
            logger.debug(f"Variables: {self.variables}")
            logger.info("Extracting tasks")
            tasks_yaml = self.taskfile_yaml.get("tasks", {})
            for task_name, task_config in tasks_yaml.items():
                # task = Task.from_dict(task_config)
                # self.tasks[task_name] = task
                self.tasks[task_name] = Task(name=task_name, **task_config)
                logger.debug(f"Task: {task_name}")
        except yaml.YAMLError as e:
            raise BokuTaskfileError(f"Error parsing taskfile: {e}")

    def execute_tasks(self) -> None:
        """Execute tasks from the task file."""
        logger.info(f"Total tasks: {len(self.tasks)}")
        for index, (name, task) in enumerate(self.tasks.items(), start=1):
            deps_ok = True
            if task.depends_on:
                logger.info(f"Task {name} depends on {task.depends_on}")
                for dependency in task.depends_on:
                    if not self.tasks.get(dependency):
                        raise BokuDependencyError(f"Dependency {dependency} not found")
                    if not self.tasks[dependency].run_ok:
                        logger.error(
                            f"Task {name} depends on {dependency}, which failed"
                        )
                        deps_ok = False
                        break
            if not deps_ok:
                continue
            logger.info(f"Executing task {name} [{index}/{len(self.tasks)}]")
            task.execute(self.variables)
            if task.save_output:
                logger.info(f"Saving task output to {task.save_output}")
                if task.save_output in self.variables.keys():
                    logger.error(
                        f"Will not save output because variable {task.save_output} already exists."
                    )
                    return
                self.variables[task.save_output] = task.output


@dataclass
class Task:
    """Task Object"""

    # metadata
    name: str
    """Task identifier."""
    description: str = ""
    """Optional. Description of the task."""
    run_ok: None | bool = None
    """Did the task run successfully?"""
    # exectuion
    run: str = ""
    """Command to run."""
    working_dir: str = os.getcwd()
    """Optional. Working directory for the command. Default: current directory."""
    save_output: str = ""
    """Optional. Save the output of the command to a variable."""
    iterate: str | list[str] = field(default_factory=list)
    """Optional. Iterate over a list of items."""
    depends_on: str | list[str] = field(default_factory=list)
    """Optional. List of tasks that need to succeed for this task to run."""
    success_code: int = 0
    """Optional. The expected return code for a successful command. Default: 0."""
    on_success: str = ""
    """Optional. Command to run on success."""
    on_failure: str = ""
    """Optional. Command to run on failure."""

    def __post_init__(self):
        self._is_valid_task()

    def _is_valid_task(self) -> None:
        """Check whether the task is valid."""
        from jsonschema import validate

        try:
            validate(self.__dict__, TASK_SCHEMA)
        except Exception as e:
            raise BokuTaskError(f"Task {self.name} is invalid:\n{e}")

    def execute(self, variables: dict[str, Any]) -> None:
        """Execute the task command.

        Args:
            variables: dict[str, Any]: Variables from the taskfile to be used in the task.
        """
        self.variables = variables
        if self.description:
            logger.info(f"Description: {self.description}")
        execution_results: list[bool] = []
        outputs = []
        if self.iterate:
            if isinstance(self.iterate, str):
                logger.debug(
                    f"Iteration is string {self.iterate}, trying to get variable"
                )
                iter_list = self.variables.get(self.iterate, [])
                if not iter_list:
                    raise BokuVariableError(f"Variable {self.iterate} not found")
                self.iterate = iter_list
            logger.info(f"Iterating over {len(self.iterate)} items")
            for item in self.iterate:
                command = VariableParser(self.variables).parse(f"{self.run} {item}")
                logger.info(f"Command: {command}")
                success, output = self.run_command(command)
                execution_results.append(success)
                outputs.append(output)
        else:
            command = VariableParser(self.variables).parse(self.run)
            logger.info(f"Command: {command}")
            success, output = self.run_command(command)
            execution_results.append(success)
            outputs.append(output)
        self.output = "\n".join(outputs)
        logger.debug(self.output)
        self.run_ok = all(execution_results)
        self.post_execute(self.run_ok)

    def post_execute(self, success: bool) -> None:
        handlers = {
            True: self.on_success,
            False: self.on_failure,
        }
        if (handler := handlers.get(success)) and handler:
            logger.info(f"Running post-execute handler: {handler}")
            self.run_command(handler)

    def run_command(self, command: str) -> tuple[bool, str]:
        """Run a command and return the success bool and output.

        Args:
            command (str): Command to run.
        """
        command_output: list[str] = []
        try:
            logger.debug(f"Running command {command}")
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.working_dir,
                text=True,  # Return strings instead of bytes
                bufsize=1,  # Line buffered
                universal_newlines=True,
            )

            # Process output as it comes
            while True:
                output = process.stdout.readline()
                if self.save_output:
                    command_output.append(output.strip())
                if output:
                    logger.debug(output.strip())
                error = process.stderr.readline()
                if error:
                    logger.error(error.strip())
                # Break if process is done and no more output
                if output == "" and error == "" and process.poll() is not None:
                    break

            return_code = process.wait()
            if return_code != self.success_code:
                raise subprocess.CalledProcessError(return_code, self.run)
            return True, "\n".join(command_output)

        except subprocess.CalledProcessError as e:
            logger.error(f"Task {self.name} failed with exit code {e.returncode}")
            return False, "\n".join(command_output)


class VariableParser:
    """Handles variable substitution in strings and lists"""

    def __init__(self, variables: dict[str, Any]):
        """Initialize VariableParser.

        Args:
            variables (dict[str, Any]): Variables to parse against.
        """
        self.variables = variables
        self.environment = os.environ.copy()

    def parse(self, text: str | list[str]) -> str | list[str]:
        """Parse ${var} references in strings/lists.

        Args:
            text (str|list[str]): Text to parse.

        Returns:
            str|list[str]: Parsed text.
        """
        if isinstance(text, list):
            return [self.parse(item) for item in text]

        pattern = r"\${(env:)?([^}]+)}"

        def replace_var(match: re.Match) -> str:
            is_env_var = match.group(1) is not None
            var_name = match.group(2)
            if is_env_var:
                if var_name not in self.environment:
                    raise BokuVariableError(
                        f"Environment variable '{var_name}' not found"
                    )
                return str(self.environment.get(var_name))
            else:
                if var_name not in self.variables:
                    raise BokuVariableError(f"Variable '{var_name}' not found")
                return str(self.variables[var_name])

        return re.sub(pattern, replace_var, str(text))


class ConfigurationHandler:
    """Handle boku config file."""

    DEFAULT_CONFIG = f"""
    # Boku config - version {__version__}
    """

    _instance = None

    def __new__(cls) -> "ConfigurationHandler":
        """Singleton class."""
        if cls._instance is None:
            cls._instance = super(ConfigurationHandler, cls).__new__(cls)
            cls._instance.__init__()
        return cls._instance

    def __init__(self) -> None:
        """Initialize ConfigurationHandler."""
        self.config_dir = self.get_config_dir()
        self.global_task_dir = self.config_dir / "tasks"
        self.global_task_dir.mkdir(exist_ok=True)

    def get_config_dir(self) -> Path:
        """Get config directory for boku.

        Returns:
            (Path) path of the config directory.
        """
        if os.environ.get("BOKU_CONFIG_DIR"):
            config_dir = Path(os.environ.get("BOKU_CONFIG_DIR", "")).expanduser()
            logger.debug(f"Using BOKU_CONFIG_DIR env var: {config_dir}")
        else:
            if os.name == "nt":  # Windows
                base = os.environ.get("APPDATA") or os.path.expanduser(
                    "~\\AppData\\Roaming"
                )
            else:  # Unix-like systems (Linux, macOS)
                base = os.path.expanduser(
                    os.environ.get("XDG_CONFIG_HOME", "~/.config")
                )
                config_dir = Path(base) / "boku"
                logger.debug(f"Using default config dir: {config_dir}")

        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    def get_config_file(self) -> Path:
        """Return config file path."""
        config_path = self.config_dir / "config.yml"
        if not config_path.exists():
            self.default_config(config_path)
        return config_path

    def default_config(self, config_path: Path) -> str:
        """Write default configuration to file."""
        logger.debug(f"Config file {config_path} doesn't exist. Creating default.")
        config_path.touch()
        config_path.write_text(self.DEFAULT_CONFIG.strip())
        return ""


class GlobalTasks:
    """Global Task Object"""

    def __init__(self) -> None:
        self.config_handler = ConfigurationHandler()
        self.global_tasks: dict[str, Path] = {
            task.stem: task
            for task in self.config_handler.global_task_dir.glob("*.y*ml")
        }
        """Dictionary of file stem -> task path."""

    def add(self, args: Namespace) -> None:
        """Add a global task from a local file.

        Args:
            args: Namespace object from argparse.
        """
        if not args.file:
            raise BokuTaskfileError("No file specified")
        taskfile = TaskFile(taskfile_path=Path(args.file))
        if taskfile.taskfile_path.stem in self.global_tasks.keys():
            raise BokuTaskfileError(
                f"Taskfile {args.file} already exists in global tasks."
            )
        print(f"{taskfile.description}\nby {taskfile.author}")
        proceed = input("Add global task? [y/N]: ").lower().strip() == "y"
        if proceed:
            return_path = shutil.copy(
                taskfile.taskfile_path.absolute(),
                self.config_handler.global_task_dir / taskfile.taskfile_path.name,
            )
            print(f"Task copied to {return_path}")

    def remove(self, args: Namespace) -> None:
        if not args.file:
            raise BokuTaskfileError("No file specified")
        if args.file in self.global_tasks.keys():
            logger.debug(f"Taskfile {args.file} found in global tasks.")
            taskfile_path: Path = self.global_tasks.get(args.file)
            if input(f"Delete {taskfile_path}? [y/N]: ").lower().strip() == "y":
                taskfile_path.unlink()
                print(f"Taskfile {taskfile_path} deleted.")
        else:
            raise BokuTaskfileError(f"Taskfile {args.file} not found in global tasks.")

    @staticmethod
    def edit(args) -> None:
        """Edit a global task using $EDITOR.

        Args:
            args: Namespace object from argparse.
        """
        ch = ConfigurationHandler()
        global_tasks = {task.name: task for task in ch.global_task_dir.glob("*.y*ml")}
        if not args.file:
            p = Picksy(list(global_tasks.values()))
            logger.debug(f"Choice: {p.get_choice()}")
            edit_file(str(p.get_choice()))
        else:
            taskfile = yaml_suffixer(args.file)
            for name, task in global_tasks.items():
                if taskfile == name:
                    edit_file(str(task))

    def _list(self, args: Namespace) -> None:
        """List all global tasks.

        Args:
            args: Namespace object from argparse.
        """
        print("Tasks available globally:")
        for task in self.global_tasks.keys():
            print(task)

    def run(self, args) -> None:
        """Run a global task.

        Args:
            args: Namespace object from argparse.
        """
        for name, task in self.global_tasks.items():
            if args.file == name:
                logger.debug(f"Global taskfile: {task}")
                boku = Boku()
                boku.load_taskfile(task)
                boku.run(args)
                return
        raise BokuTaskfileError(f"Taskfile {args.file} not found in global tasks.")
