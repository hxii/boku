# TaskFile module
#

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import Any, Dict, Optional

import yaml
from packaging.version import Version

from boku import __version__
from boku.exceptions import BokuDependencyError, BokuTaskfileError
from boku.logger import logger
from boku.models import BokuArgs
from boku.task import Task


@dataclass
class TaskFile:
    """Taskfile Object."""

    version: str = ""
    """Version of boku required to run the task file."""
    author: str = "Unknown"
    """Author of the task file."""
    description: str = "No Description"
    """Description of the purpose of the task file."""
    tasks: Dict[str, "Task"] = field(default_factory=dict)
    """Dictionary of tasks."""
    taskfile_path: Path = Path()
    """Path to the taskfile."""
    taskfile_raw: str = ""
    """Raw taskfile content."""
    taskfile_yaml: Dict[str, Any] = field(default_factory=dict)
    """Parsed taskfile content."""
    variables: Dict[str, Any] = field(default_factory=dict)
    """Variables to be used in tasks."""
    args: Optional[BokuArgs] = None
    """Command line arguments."""
    working_dir: Path | None = None
    """Working directory for task execution (defaults to taskfile's parent)."""

    def __post_init__(self):
        """Run basic checks on the taskfile."""
        if not self.taskfile_path.exists():
            raise BokuTaskfileError(f"Taskfile not found: {self.taskfile_path}")
        if not self.taskfile_path.is_file():
            raise BokuTaskfileError(f"Taskfile is not a file: {self.taskfile_path}")
        if self.taskfile_path.suffix not in (".yaml", ".yml"):
            raise BokuTaskfileError(f"Taskfile is not a valid YAML file: {self.taskfile_path}")
        logger.debug(f"Taskfile: {self.taskfile_path.absolute()}")
        logger.debug(f"Modified: {datetime.fromtimestamp(self.taskfile_path.stat().st_mtime)}")
        logger.debug(f"Size: {self.taskfile_path.stat().st_size}")
        logger.debug(f"Owner: {self.taskfile_path.owner()}")
        self.parse_taskfile()

    def __str__(self) -> str:
        return dedent(f"""
        Author: {self.author}
        Tasks ({len(self.tasks)}): {", ".join(self.tasks.keys())}
        Variables ({len(self.variables)}): {", ".join(self.variables.keys())}

        Description:
        {self.description}
        """)

    def parse_taskfile(self) -> None:
        """Parse the taskfile and populate tasks and variables."""
        logger.info("Parsing taskfile")
        try:
            logger.debug("Reading taskfile")
            self.taskfile_raw = self.taskfile_path.read_text()
            logger.debug("Loading YAML")
            self.taskfile_yaml = yaml.safe_load(self.taskfile_raw)
            logger.info("Extracting metadata")
            self.author = self.taskfile_yaml.get("author", "Unknown")
            self.description = self.taskfile_yaml.get("description", "")
            self.version = self.taskfile_yaml.get("version", "")
            logger.info(f"Description: {self.description}")
            logger.info(f"Author: {self.author}, version: {self.version}")
            if not self.version:
                logger.warning(f"Version not specified in taskfile; assuming current version {__version__}")
                self.version = __version__
            if Version(self.version) < Version(__version__):
                logger.warning(f"Taskfile has version {self.version}, which is older than Boku version {__version__}")
            logger.info("Extracting variables")
            self.variables = self.taskfile_yaml.get("variables", {})
            # Variable resolution for cross-references and appending
            from boku.variables import VariableParser

            def resolve_all_variables(variables):
                parser = VariableParser(variables)
                changed = True
                while changed:
                    changed = False
                    for k, v in variables.items():
                        parsed = parser.parse(v)
                        if parsed != v:
                            variables[k] = parsed
                            changed = True
                return variables

            self.variables = resolve_all_variables(self.variables)
            logger.debug(f"Variables: {self.variables}")
            logger.info("Extracting tasks")
            tasks_yaml = self.taskfile_yaml.get("tasks", {})
            for task_name, task_config in tasks_yaml.items():
                # Map 'if' to 'if_condition' if present
                if "if" in task_config:
                    task_config["if_condition"] = task_config.pop("if")
                task_config.setdefault(
                    "working_dir",
                    str(self.working_dir if self.working_dir is not None else self.taskfile_path.parent),
                )
                self.tasks[task_name] = Task(name=task_name, args=self.args, **task_config)
                logger.debug(f"Task: {task_name}")
        except yaml.YAMLError as e:
            raise BokuTaskfileError(f"Error parsing taskfile: {e}")

    def execute_tasks(self) -> None:
        """Execute tasks from the task file."""
        logger.info(f"Total tasks: {len(self.tasks)}")

        is_dry_run = self.args and self.args.is_dry_run()

        for index, (name, task) in enumerate(self.tasks.items(), start=1):
            deps_ok = True
            if task.depends_on:
                logger.info(f"Task {name} depends on {task.depends_on}")
                for dependency in task.depends_on:
                    if not self.tasks.get(dependency):
                        raise BokuDependencyError(f"Dependency {dependency} not found")

                    if is_dry_run and self.tasks[dependency].run_ok is None:
                        self.tasks[dependency].run_ok = True

                    if not self.tasks[dependency].run_ok:
                        status = "skipped" if self.tasks[dependency].run_ok is None else "failed"
                        logger.error(f"Task {name} depends on {dependency}, which {status}")
                        deps_ok = False
                        break
            if not deps_ok:
                continue
            prefix = "[DRY RUN] Would execute" if is_dry_run else "Executing"
            logger.info(f"{prefix} task {name} [{index}/{len(self.tasks)}]")

            task.execute(self.variables)
            if task.save_output:
                logger.info(f"Saving task output to {task.save_output}")
                if task.save_output in self.variables.keys():
                    logger.error(f"Will not save output because variable {task.save_output} already exists.")
                    continue
                self.variables[task.save_output] = task.output

            # Fail-fast support at the task level
            if hasattr(task, "fail_fast") and getattr(task, "fail_fast", False) and not task.run_ok:
                logger.error(f"Task {name} failed and fail_fast is set. Aborting further execution.")
                break
