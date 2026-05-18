from dataclasses import dataclass

import jsonschema
import yaml

from boku.config import ConfigurationHandler
from boku.exceptions import BokuHelperError
from boku.logger import logger
from boku.utils import HELPER_SCHEMA, HELPER_TEMPLATE


@dataclass
class Helper:
    """Helper object"""

    name: str
    usage: str
    run: str
    args: list[str | dict[str, str]]

    def __post_init__(self):
        for arg in self.args:
            if isinstance(arg, str):
                setattr(self, arg, None)
            elif isinstance(arg, dict):
                for key, value in arg.items():
                    setattr(self, key, value)
        self._is_valid_helper()

    def _is_valid_helper(self) -> None:
        """Check whether the task is valid."""
        from jsonschema import validate

        logger.debug(f"Validating helper {self.name}...")
        try:
            validate(self.__dict__, HELPER_SCHEMA)
        except jsonschema.ValidationError as e:
            raise BokuHelperError(f"Helper {self.name} is invalid:\n{e.message}")
        if not self.run:
            raise BokuHelperError(f"Helper {self.name} has no command to run")

    def execute(self, executor, **kwargs) -> bool:
        """Execute the helper with the provided arguments using the given executor.

        Args:
            executor: CommandExecutor instance to use for running the command.
            **kwargs: Arguments to format the helper command.

        Returns:
            bool: True if executed successfully, False otherwise
        """
        logger.info(f"Executing helper {self.name}...")
        for key, value in kwargs.items():
            if key in ["usage", "command", "args"]:
                logger.debug(f"Skipping overwriting protected property {key}...")
                continue
            setattr(self, key, value)
            logger.debug(f"Set {key} to {value}...")
        command = self.run.format(**self.__dict__)
        result = executor.execute(command=command)
        return result.success

    # Removed run_command; now handled by CommandExecutor


class HelperHandler:
    _instance = None
    helpers: dict[str, Helper] = {}

    def __new__(cls) -> "HelperHandler":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(HelperHandler, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.ch = ConfigurationHandler()
        self.helper_file = self.ch.get_config_dir() / "helpers.yml"
        self.helpers = {}
        logger.debug(f"Helper file: {self.helper_file}")
        if not self.helper_file.exists():
            logger.debug("Helper file doesn't exist, creating...")
            self.create_empty_helper_file()
        self.parse_helpers()

    def parse_helpers(self):
        logger.debug("Parsing helpers...")
        helpers_yaml = yaml.safe_load(self.helper_file.read_text())
        for helper_name, helper in helpers_yaml.items():
            self.helpers[helper_name] = Helper(
                name=helper_name,
                usage=helper.get("usage", ""),
                run=helper.get("run", ""),
                args=helper.get("args", []),
            )
            logger.debug(f"Helper {helper_name} parsed successfully.")
        pass

    def create_empty_helper_file(self) -> int:
        return self.helper_file.write_text(HELPER_TEMPLATE.strip()) if not self.helper_file.exists() else 0
