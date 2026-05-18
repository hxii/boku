import pytest

from boku.exceptions import BokuTaskError, BokuTaskfileError
from boku.logger import logger
from boku.main import Boku
from boku.task import Task


def test_invalid_task():
    with pytest.raises(BokuTaskError):
        task = Task(
            name="test",
            description="Testing task",
            run="echo 'Hello, Test!'",
            success_code="",
        )
        task.execute({})
        assert not task.run_ok


def test_task():
    task = Task(
        name="test",
        description="Testing task",
        run="echo 'Hello, Test!'",
        save_output="test_out",
    )
    task.execute({})
    assert task.run_ok
    assert task.output.strip() == "Hello, Test!"


@pytest.fixture
def taskfile():
    return """
    version: '0.1'
    author: 'Test Author'
    description: 'A simple test taskfile'
    tasks:
      greet:
        description: 'A task that greets'
        run: 'echo "Hello, Test!"'
        save_output: 'greeting'
        suppress_output: True
    """


@pytest.fixture
def taskfile_with_variables():
    return """
    version: '0.1'
    author: 'Test Author'
    description: 'A simple test taskfile'
    variables:
        greeting: 'Hello'
        name: 'Test'
    tasks:
      greet:
        description: 'A task that greets'
        run: 'echo "${greeting}, ${name}!"'
        save_output: 'greeting_output'
        suppress_output: True
    """


@pytest.fixture
def taskfile_invalid():
    return """
    version: '0.1'
    tasks:
        greet:
            description: 'A task that greets'
    """


def test_boku_taskfile_execution(tmp_path, taskfile):
    taskfile_content = taskfile

    taskfile_path = tmp_path / "Taskfile.yaml"
    taskfile_path.write_text(taskfile_content)

    boku = Boku()
    boku.load_taskfile(taskfile_path)

    boku.run(None)

    assert "greeting" in boku.taskfile.variables
    assert len(boku.taskfile.variables) == 1
    assert boku.taskfile.variables["greeting"].strip() == "Hello, Test!"


def test_boku_variable_taskfile_execution(tmp_path, taskfile_with_variables):
    taskfile_content = taskfile_with_variables
    taskfile_path = tmp_path / "Taskfile.yaml"
    taskfile_path.write_text(taskfile_content)

    logger.logger.setLevel("DEBUG")

    boku = Boku()
    boku.load_taskfile(taskfile_path)
    boku.run(None)

    assert "greeting" in boku.taskfile.variables
    assert boku.taskfile.variables["greeting_output"].strip() == "Hello, Test!"


def test_boku_no_taskfile():
    boku = Boku()
    with pytest.raises(BokuTaskfileError):
        boku.load_taskfile("non_existent_taskfile.yaml")


def test_boku_no_command(tmp_path, taskfile_invalid):
    taskfile_content = taskfile_invalid
    taskfile_path = tmp_path / "Taskfile.yaml"
    taskfile_path.write_text(taskfile_content)

    boku = Boku()
    with pytest.raises(BokuTaskError):
        boku.load_taskfile(taskfile_path)
