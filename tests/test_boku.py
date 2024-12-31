# tests/test_boku.py

import pytest

from boku.exceptions import BokuTaskfileError
from boku.main import Boku


@pytest.fixture
def simple_taskfile(tmp_path):
    content = """
    version: "0.2.0"
    author: "Test Author"
    description: "Simple test tasks"
    variables:
        greeting: "Hello"
    tasks:
        echo:
            description: "Echo test"
            run: "echo 'test'"
        with_var:
            run: echo "${greeting}"
            save_output: with_var_output
        with_deps:
            run: "echo 'dependent'"
            depends_on: "echo"
    """
    taskfile = tmp_path / "test_tasks.yaml"
    taskfile.write_text(content)
    return taskfile


def test_boku_load_taskfile(simple_taskfile):
    boku = Boku()
    size = boku.load_taskfile(simple_taskfile)
    assert size > 0
    assert boku.taskfile.author == "Test Author"
    assert len(boku.taskfile.tasks) == 3


def test_load_nonexistent_taskfile():
    boku = Boku()
    with pytest.raises(BokuTaskfileError):
        boku.load_taskfile("nonexistent.yaml")


def test_task_variable_substitution(simple_taskfile):
    boku = Boku()
    boku.load_taskfile(simple_taskfile)
    task = boku.taskfile.tasks["with_var"]
    task.execute(boku.taskfile.variables)
    print(boku.taskfile.variables)
    assert "Hello" in boku.taskfile.variables["with_var_output"]


def test_task_dependencies(simple_taskfile):
    boku = Boku()
    boku.load_taskfile(simple_taskfile)
    # Execute all tasks
    boku.taskfile.execute_tasks()
    # Verify all tasks ran successfully
    assert all(task.run_ok for task in boku.taskfile.tasks.values())


def test_invalid_task_yaml(tmp_path):
    content = """
    version: "0.2.0"
    tasks:
        invalid:
            description: "Missing required run field"
    """
    taskfile = tmp_path / "invalid.yaml"
    taskfile.write_text(content)

    boku = Boku()
    with pytest.raises(BokuTaskfileError):
        boku.load_taskfile(taskfile)


def test_task_execution_failure(tmp_path):
    content = """
    version: "0.2.0"
    tasks:
        failing:
            run: "nonexistent-command"
    """
    taskfile = tmp_path / "failing.yaml"
    taskfile.write_text(content)

    boku = Boku()
    boku.load_taskfile(taskfile)
    boku.taskfile.execute_tasks()
    assert not boku.taskfile.tasks["failing"].run_ok


def test_task_with_custom_success_code(tmp_path):
    content = """
    version: "0.2.0"
    tasks:
        custom_exit:
            run: "exit 1"
            success_code: 1
    """
    taskfile = tmp_path / "custom_exit.yaml"
    taskfile.write_text(content)

    boku = Boku()
    boku.load_taskfile(taskfile)
    boku.taskfile.execute_tasks()
    assert boku.taskfile.tasks["custom_exit"].run_ok
