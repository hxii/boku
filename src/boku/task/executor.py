# CommandExecutor
#

import subprocess
import sys
from collections import namedtuple
from pathlib import Path
from typing import Any, TYPE_CHECKING

from boku.logger import logger
from boku.models import BokuArgs

if TYPE_CHECKING:
    from boku.task import Task

Result = namedtuple("Result", ["success", "output"])


class CommandExecutor:
    """Handles command execution for tasks."""

    def __init__(self, args: BokuArgs | None, executing_task: "Task") -> None:
        self.results: list[Result] = []
        self.args = args
        self.executing_task = executing_task

    def execute(
        self,
        command: str,
        working_dir: str | None = None,
        success_code: int = 0,
        suppress_output: bool = False,
        save_output: bool = False,
    ) -> Result:
        """Execute a command and return success status and output.

        Args:
            command: Command to execute
            working_dir: Directory to execute the command in
            success_code: Expected return code for success
            suppress_output: Whether to suppress command output
            save_output: Whether to save command output

        Returns:
            Result namedtuple with success status and output
        """
        working_dir = self.executing_task.working_dir
        assert self.args is not None
        if self.args.is_dry_run():
            logger.info(f"[DRY RUN] Task {self.executing_task.name} – Would execute: {command} in {working_dir}")
            return Result(success=True, output="[DRY RUN]")

        command_output: list[str] = []
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path(working_dir).expanduser(),
                text=True,  # Return strings instead of bytes
                bufsize=1,  # Line buffered
                universal_newlines=True,
            )

            # Process output as it comes
            while True:
                output = ""
                error = ""

                if process.stdout is not None:
                    line = process.stdout.readline()
                    if line is not None:
                        output = line

                if save_output and output:
                    command_output.append(output.strip())

                if not suppress_output and output:
                    print(output.strip())
                    logger.info(output.strip())

                if process.stderr is not None:
                    line = process.stderr.readline()
                    if line is not None:
                        error = line

                if error:
                    print(error.strip(), file=sys.stderr)
                    logger.error(error.strip())

                # Break if process is done and no more output
                if output == "" and error == "" and process.poll() is not None:
                    break

            return_code = process.wait()
            success = return_code == success_code
            if not success:
                raise subprocess.CalledProcessError(return_code, command)
            result = Result(success=True, output="\n".join(command_output))
            self.results.append(result)
            return result

        except subprocess.CalledProcessError as e:
            logger.error(f"Task {self.executing_task.name} – Command failed with exit code {e.returncode}: {command}")
            result = Result(success=False, output="\n".join(command_output))
            self.results.append(result)
            return result
        except Exception as e:
            if process and process.poll() is None:
                process.kill()
            logger.error(f"Task {self.executing_task.name} - Unexpected error executing command: {e}")
            result = Result(success=False, output=str(e))
            self.results.append(result)
            return result

    def execute_with_iteration(
        self,
        command_template: str,
        items: list[Any],
        working_dir: str | None = None,
        success_code: int = 0,
        suppress_output: bool = False,
        save_output: bool = False,
        use_placeholder: bool = True,
    ) -> list[Result]:
        """Execute a command for each item in the iteration.

        Args:
            command_template: Command template to execute, may contain {} placeholder
            items: List of items to iterate over
            working_dir: Directory to execute the command in
            success_code: Expected return code for success
            suppress_output: Whether to suppress command output
            save_output: Whether to save command output
            use_placeholder: Whether to replace {} with item or append item to command

        Returns:
            List of Result namedtuples with success status and output for each iteration
        """
        # if working_dir is None:
        # working_dir = self.executing_task.working_dir
        iteration_results: list[Result] = []

        for item in items:
            if use_placeholder and "{}" in command_template:
                # Support multiple placeholders by unpacking if item is a list/tuple
                if isinstance(item, (list, tuple)):
                    command = command_template.format(*item)
                else:
                    command = command_template.format(item)
            else:
                command = f"{command_template} {item}"

            assert self.args is not None
            if not self.args.is_dry_run():
                result = self.execute(
                    command=command,
                    working_dir=working_dir,
                    success_code=success_code,
                    suppress_output=suppress_output,
                    save_output=save_output,
                )

                iteration_results.append(result)
            else:
                iteration_results.append(Result(True, ""))

        return iteration_results

    def get_results(self) -> list[Result]:
        """Get all execution results."""
        return self.results

    def get_last_result(self) -> Result | None:
        """Get the most recent execution result."""
        return self.results[-1] if self.results else None

    def all_successful(self) -> bool:
        """Check if all executions were successful."""
        return all(result.success for result in self.results)
