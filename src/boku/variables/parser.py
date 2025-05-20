# Variable Parser
#

import os
import re
from typing import Any

from boku.exceptions import BokuVariableError


class VariableParser:
    """Handles variable substitution in strings and lists"""

    def __init__(self, variables: dict[str, Any]):
        """Initialize VariableParser.

        Args:
            variables (dict[str, Any]): Variables to parse against.
        """
        self.variables = variables
        self.environment = os.environ.copy()

    def parse(self, text: str | list[str], mask_sensitive: bool = False) -> str | list[str]:
        """Parse ${var} and @{var} references in strings/lists.

        Args:
            text (Union[str, list[str]]): Text to parse.
            mask_sensitive (bool): Mask sensitive variables.

        Returns:
            str | list: Parsed text.
        """
        if isinstance(text, list):
            return [self.parse(item, mask_sensitive) for item in text]

        pattern = r"(\@|\$)\{(env:)?([^}]+)\}"

        def replace_var(match: re.Match) -> str:
            is_sensitive = match.group(1) == "@"
            is_env_var = match.group(2) is not None
            var_name = match.group(3)

            if is_env_var:
                if var_name not in self.environment:
                    raise BokuVariableError(f"Environment variable '{var_name}' not found")
                value = str(self.environment.get(var_name))
            else:
                if var_name not in self.variables:
                    raise BokuVariableError(f"Variable '{var_name}' not found")
                value = str(self.variables[var_name])

            if is_sensitive and mask_sensitive:
                return "****"
            return value

        return re.sub(pattern, replace_var, str(text))
