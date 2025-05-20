from unittest.mock import patch

import pytest

from boku.config import ConfigurationHandler
from boku.exceptions import BokuHelperError
from boku.helpers import Helper, HelperHandler

# Sample valid and invalid helper configurations
VALID_HELPER = """
telegram_message:
  usage: |
    Pass the following args:
    - token - Your bot token, which you can get via BotFather https://telegram.me/botfather
    - chat_id - The chat ID to send the message to
    - message - The message to send
  run: "echo Sending message with token {token} to chat_id {chat_id}: {message}"
  args:
    - token
    - chat_id
    - message
"""

INVALID_HELPER_BAD_SCHEMA = """
bad_schema_helper:
  usage: "This helper has incorrectly typed args"
  run: "echo {invalid}"
  args:
    - arg1: 2
    - arg2:
      - 2
"""


@pytest.fixture
def temp_helpers_file(tmp_path):
    helpers_path = tmp_path / "helpers.yml"
    helpers_path.write_text(VALID_HELPER)
    return helpers_path


@pytest.fixture
def temp_invalid_helpers_file_bad_schema(tmp_path):
    helpers_path = tmp_path / "helpers.yml"
    helpers_path.write_text(INVALID_HELPER_BAD_SCHEMA)
    return helpers_path


def test_valid_helper_creation():
    helper_data = {
        "name": "telegram_message",
        "usage": "Send a message via Telegram.",
        "run": "echo Sending message with token {token} to chat_id {chat_id}: {message}",
        "args": ["token", "chat_id", "message"],
    }
    helper = Helper(**helper_data)
    assert helper.name == "telegram_message"
    assert helper.run == helper_data["run"]
    assert helper.args == helper_data["args"]


def test_helper_bad_schema():
    helper_data = {
        "name": "bad_schema_helper",
        "usage": "This helper has incorrectly typed args",
        "run": "echo {invalid}",
        "args": ["arg1", {"arg2": 2}],  # Invalid arg format
    }
    with pytest.raises(BokuHelperError) as excinfo:
        Helper(**helper_data)
    assert "is invalid" in str(excinfo.value)


def test_helper_handler_load_helpers(temp_helpers_file):
    handler = HelperHandler()
    # Mock the ConfigurationHandler to return the temporary helpers file
    with patch.object(ConfigurationHandler, "get_config_dir", return_value=temp_helpers_file.parent):
        handler = HelperHandler()
    assert "telegram_message" in handler.helpers
    helper = handler.helpers["telegram_message"]
    assert helper.name == "telegram_message"
    assert helper.args == ["token", "chat_id", "message"]


def test_helper_handler_load_invalid_helper_bad_schema(
    temp_invalid_helpers_file_bad_schema,
):
    with patch.object(
        ConfigurationHandler,
        "get_config_dir",
        return_value=temp_invalid_helpers_file_bad_schema.parent,
    ):
        with pytest.raises(BokuHelperError) as excinfo:
            HelperHandler()
    assert "is invalid" in str(excinfo.value)
