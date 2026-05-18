import pytest

from boku.exceptions import BokuVariableError
from boku.variables import VariableParser


@pytest.fixture
def variables():
    return {"name": "Alice", "greeting": "Hello", "password": "secret_password"}


@pytest.fixture
def parser(variables):
    return VariableParser(variables)


def test_simple_variable_substitution(parser):
    text = "${name}"
    expected = "Alice"
    result = parser.parse(text)
    assert result == expected


def test_multiple_variables(parser):
    text = "${greeting}, ${name}!"
    expected = "Hello, Alice!"
    result = parser.parse(text)
    assert result == expected


def test_missing_variable(parser):
    text = "${age}"
    with pytest.raises(BokuVariableError) as exc_info:
        parser.parse(text)
    assert "Variable 'age' not found" in str(exc_info.value)


def test_environment_variable(variables, monkeypatch):
    monkeypatch.setenv("LOCATION", "Wonderland")
    parser = VariableParser(variables)  # Initialize after setting env var
    text = "${env:LOCATION}"
    expected = "Wonderland"
    result = parser.parse(text)
    assert result == expected


def test_sensitive_variable_masking(parser):
    text = "@{password}"
    expected = "****"
    result = parser.parse(text)
    assert result == expected


def test_list_of_strings(parser):
    texts = ["${greeting}", "${name}"]
    expected = ["Hello", "Alice"]
    result = parser.parse(texts)
    assert result == expected


def test_iteration_variable_substitution(parser):
    text = "User: ${name}"
    expected = "User: Alice"
    result = parser.parse(text)
    assert result == expected
