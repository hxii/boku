from dataclasses import dataclass

import yaml
import jsonschema

from boku.logger import logger
from boku.exceptions import BokuHelperError
from boku.config import ConfigurationHandler
from boku.utils import HELPER_SCHEMA

DUMMY_HELPER = """telegram_message:
  usage: |
    Pass the following args:
    - token - Your bot token, which you can get via BotFather https://telegram.me/botfather
    - chat_id - The chat ID to send the message to
    - message - The message to send
  run: "curl -X POST https://api.telegram.org/bot{token}/sendMessage -d 'chat_id={chat_id}&text={message}'"
  args:
    - token
    - chat_id
    - message
osx_notification:
  usage: Show a macOS notification using osascript by passing the title and message
  run: osascript -e 'display notification "{message}" with title "{title}"'
  args:
    - title
    - message
"""


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

    def execute(self, **kwargs):
        logger.info(f"Executing helper {self.name}...")
        for key, value in kwargs.items():
            if key in ["usage", "command", "args"]:
                logger.debug(f"Skipping overwriting protected property {key}...")
                continue
            setattr(self, key, value)
            logger.debug(f"Set {key} to {value}...")
        command = self.run.format(**self.__dict__)
        self.run_command(command)

    def run_command(self, command: str) -> None:
        """Run a command."""
        from subprocess import run, PIPE

        logger.debug(f"Running helper command: {command}")
        run(command, shell=True, stdout=PIPE, stderr=PIPE)


class HelperHandler:
    _instance = None

    def __new__(cls) -> "HelperHandler":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(HelperHandler, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.ch = ConfigurationHandler()
        self.helper_file = self.ch.get_config_dir() / "helpers.yml"
        self.helpers: dict[str, Helper] = {}
        logger.debug(f"Helper file: {self.helper_file}")
        if not self.helper_file.exists():
            logger.debug("Helper file doesn't exist, creating...")
            self.create_empty_helper_file()
        self.parse_helpers()

    def parse_helpers(self):
        logger.debug("Parsing helpers...")
        helpers_yaml = yaml.safe_load(self.helper_file.read_text())
        for helper_name, helper in helpers_yaml.items():
            self.helpers[helper_name] = Helper(name=helper_name, **helper)
            logger.debug(f"Helper {helper_name} parsed successfully.")
        pass

    def create_empty_helper_file(self) -> int:
        return (
            self.helper_file.write_text(DUMMY_HELPER.strip())
            if not self.helper_file.exists()
            else 0
        )
