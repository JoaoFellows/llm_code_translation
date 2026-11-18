from pathlib import Path

import pytest

from class_translation.state import ClassTask, ensure_java_to_python, load_task

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "counter"


def test_load_counter_fixture():
    task = load_task(FIXTURE)
    assert task.task_id == "counter"
    assert (task.source_lang, task.target_lang) == ("java", "python")
    assert "class Counter" in task.source_code
    assert "assertEquals" in task.source_tests
    assert "unittest" in task.oracle_tests


def test_reverse_direction_is_representable_and_refused():
    accepted = ClassTask("x", "python", "java", "box", "class Box {}", "tests", "oracle")
    ensure_java_to_python(accepted)

    unknown = ClassTask("x", "rust", "go", "box", "fn main() {}", "tests", "oracle")
    with pytest.raises(NotImplementedError):
        ensure_java_to_python(unknown)
