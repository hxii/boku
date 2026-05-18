# Task module
#
import logging

from dataclasses import dataclass, field
from typing import Any, cast

from boku.exceptions import BokuTaskError, BokuVariableError
from boku.helpers import Helper, HelperHandler
from boku.logger import logger
from boku.models import BokuArgs
from boku.task.executor import CommandExecutor
from boku.utils import TASK_SCHEMA


@dataclass
class Task:
    """Task Object"""

    args: BokuArgs
    """Command line arguments."""

    # metadata
    name: str
    """Task identifier."""
    description: str = ""
    """Optional. Description of the task."""
    run_ok: bool | None = None
    """Did the task run successfully?"""
    # execution
    run: str = ""
    """Command to run."""
    working_dir: str | None = None
    """Optional. Working directory for the command. Default: current directory."""
    save_output: str = ""
    """Optional. Save the output of the command to a variable."""
    suppress_output: bool = False
    """Optional. Suppress output of the command."""
    iterate: str | list[str] = field(default_factory=list)
    """Optional. Iterate over a list of items."""
    depends_on: list[str] = field(default_factory=list)
    """Optional. List of tasks that need to succeed for this task to run."""
    success_code: int = 0
    """Optional. The expected return code for a successful command. Default: 0."""
    on_success: str = ""
    """Optional. Command to run on success."""
    on_failure: str = ""
    """Optional. Command to run on failure."""
    fail_fast: bool = False
    """Optional. If true, abort execution after this task fails."""
    # helpers
    use: str = ""
    """Optional. Helper to use."""
    with_arguments: dict[str, Any] = field(default_factory=dict)
    """Optional. Arguments to pass to the helper."""
    # conditional
    if_condition: str = ""
    """Optional. Shell condition that must be true for the task to run."""

    # runtime
    output: str = ""
    """Output of the command."""
    variables: dict[str, Any] = field(default_factory=dict, repr=False)
    """Variables to use in command."""
    executor: CommandExecutor | None = field(default=None, repr=False)
    """Command executor to use for running commands."""

    def __post_init__(self):
        self._is_valid_task()

    def _is_valid_task(self) -> None:
        """Check whether the task is valid."""
        from jsonschema import validate

        try:
            validate(self.__dict__, TASK_SCHEMA)
        except Exception as e:
            raise BokuTaskError(f"Task {self.name} is invalid:\n{str(e)}")
        if not self.run and not self.use:
            raise BokuTaskError(f"Task {self.name} must have either a 'run' command or a 'use' helper")

    def execute(self, variables: dict[str, Any]) -> None:
        """Execute the task command.

        Args:
            variables: Dict[str, Any]: Variables from the taskfile to be used in the task.
            args: Optional arguments from command line.
        """
        if self.executor is None:
            self.executor = CommandExecutor(self.args, executing_task=self)

        self.variables = variables
        if self.description:
            logger.info(f"Description: {self.description}")

        if self.if_condition:
            from boku.variables import VariableParser

            variable_parser = VariableParser(self.variables)
            parsed_condition = str(variable_parser.parse(self.if_condition))
            logger.info(f"{'Checking' if not self.args.is_dry_run() else 'Would Check'} condition: {parsed_condition}")

            result = self.executor.execute(
                command=parsed_condition,
                working_dir=self.working_dir,
                suppress_output=True,
                success_code=0,
            )

            if not result.success:
                logger.info(f"Skipping task '{self.name}' - condition failed")
                self.run_ok = None
                return

        # Execute helper if no run command set
        if self.use and not self.run:
            if self.args.is_dry_run():
                logger.info(f"[DRY RUN] Would execute helper: {self.use}")
                for key, value in self.with_arguments.items():
                    logger.info(f"  with {key}={value}")
                self.run_ok = True
                self.output = "[DRY RUN]"
            else:
                self._execute_helper(self.executor)

            if self.run_ok is not None:
                self.post_execute(bool(self.run_ok))
            return

        from boku.variables import VariableParser

        variable_parser = VariableParser(self.variables)

        if self.iterate:
            iteration_items = self._resolve_iteration_items()
            logger.info(f"Iterating over {len(iteration_items)} items")

            results = self.executor.execute_with_iteration(
                command_template=self.run,
                items=iteration_items,
                working_dir=self.working_dir,
                success_code=self.success_code,
                suppress_output=self.suppress_output,
                save_output=bool(self.save_output),
                use_placeholder="{}" in self.run,
            )

            self.output = "\n".join(result.output for result in results)
            self.run_ok = all(cast(bool, result.success) for result in results)

        else:
            masked_command = variable_parser.parse(self.run, True)
            command = str(variable_parser.parse(self.run))
            logger.info(f"Command: {masked_command}")

            result = self.executor.execute(
                command=command,
                working_dir=self.working_dir,
                success_code=self.success_code,
                suppress_output=self.suppress_output,
                save_output=bool(self.save_output),
            )

            self.output = "[DRY RUN]" if self.args.is_dry_run() else result.output
            self.run_ok = True if self.args.is_dry_run() else cast(bool, result.success)

        # Execute helper after run command if both set
        if self.use:
            if self.args.is_dry_run():
                logger.info(f"[DRY RUN] Would execute helper: {self.use}")
                for key, value in self.with_arguments.items():
                    logger.info(f"  with {key}={value}")
            else:
                self._execute_helper(self.executor)

        if self.run_ok is not None:
            self.post_execute(bool(self.run_ok))

    def _resolve_iteration_items(self) -> list[Any]:
        """Resolve iteration items from string variable name or list, with variable parsing."""
        from boku.variables import VariableParser

        variable_parser = VariableParser(self.variables)

        def parse_item(item):
            if isinstance(item, list):
                return [parse_item(subitem) for subitem in item]
            elif isinstance(item, str):
                return variable_parser.parse(item)
            else:
                return item

        if isinstance(self.iterate, str):
            logger.debug(f"Iteration is string {self.iterate}, trying to get variable")
            iter_list = self.variables.get(self.iterate, [])
            if not iter_list:
                raise BokuVariableError(f"Variable {self.iterate} not found")
            return [parse_item(x) for x in iter_list]
        return [parse_item(x) for x in self.iterate]

    def _execute_helper(self, executor) -> None:
        """Execute a helper with the specified arguments using the provided executor."""
        helper_handler = HelperHandler()
        helper: Helper | None = helper_handler.helpers.get(self.use)
        if not helper:
            raise BokuVariableError(f"Helper {self.use} not found")
        try:
            success = helper.execute(executor, **self.with_arguments)
            self.run_ok = success
            if not success:
                logger.error(f"Helper {self.use} execution failed")
        except Exception as e:
            logger.error(f"Helper execution failed: {str(e)}")
            self.run_ok = False

    def post_execute(self, success: bool) -> None:
        """Run post-execution commands based on success or failure.

        Args:
            success: Whether the task execution was successful
        """
        handlers = {
            True: self.on_success,
            False: self.on_failure,
        }

        if (handler := handlers.get(success)) and handler:
            logger._log(
                logging.INFO if success else logging.WARNING,
                f"Task {self.name} - Running post-execute handler: {handler}",
            )
            from boku.variables import VariableParser

            variable_parser = VariableParser(self.variables)
            command = str(variable_parser.parse(handler))

            self.executor.execute(
                command=command,
                working_dir=self.working_dir,
                success_code=0,
                suppress_output=self.suppress_output,
            )
