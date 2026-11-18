from pathlib import Path

import pytest

from class_translation.classeval import load_classeval_task

_SOLUTION = """\
'''
class Box:
    def add(self, amount):
        \"\"\"skeleton only\"\"\"
'''

class Box:
    def __init__(self):
        self.value = 0

    def add(self, amount):
        self.value += amount
"""

_PYTHON_TEST = """\
import unittest


class BoxTest(unittest.TestCase):
    def test_add(self):
        box = Box()
        box.add(2)
        self.assertEqual(box.getValue(), 2)
"""

_JAVA_SOURCE = """\
package org.example;

public class Box {
    private int value;

    public void add(int amount) {
        this.value += amount;
    }
}
"""

_JAVA_TEST = """\
package org.example;

import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class BoxTest {
    @Test
    public void testAdd() {
        Box box = new Box();
        box.add(2);
        assertEquals(2, box.getValue());
    }
}
"""


def _write_benchmark(root: Path) -> None:
    benchmark = root / "ClassEval_T"
    (benchmark / "java" / "solutuon").mkdir(parents=True)
    (benchmark / "java" / "test").mkdir(parents=True)
    (benchmark / "py" / "solution").mkdir(parents=True)
    (benchmark / "py" / "test").mkdir(parents=True)
    (benchmark / "java" / "solutuon" / "Box.java").write_text(_JAVA_SOURCE, encoding="utf-8")
    (benchmark / "java" / "test" / "BoxTest.java").write_text(_JAVA_TEST, encoding="utf-8")
    (benchmark / "py" / "solution" / "Box.py").write_text(_SOLUTION, encoding="utf-8")
    (benchmark / "py" / "test" / "Box.py").write_text(_PYTHON_TEST, encoding="utf-8")


def test_java_to_python_loads_solution_spec_and_import(tmp_path: Path):
    _write_benchmark(tmp_path)
    task = load_classeval_task(tmp_path, "Box")
    assert (task.source_lang, task.target_lang) == ("java", "python")
    assert "public class Box" in task.source_code
    assert "import org.junit.Test" in task.source_tests
    assert task.oracle_tests.startswith("from Box import Box\n")
    assert "unittest" in task.oracle_tests


def test_python_to_java_loads_implementation_not_the_skeleton(tmp_path: Path):
    _write_benchmark(tmp_path)
    task = load_classeval_task(tmp_path, "Box", direction="python_to_java")
    assert (task.source_lang, task.target_lang) == ("python", "java")
    assert "self.value += amount" in task.source_code
    assert "skeleton only" not in task.source_code
    assert "self.assertEqual" in task.source_tests
    assert "import org.junit.Test" in task.oracle_tests
    assert "from Box import Box" not in task.oracle_tests


def test_unknown_direction_is_refused(tmp_path: Path):
    _write_benchmark(tmp_path)
    with pytest.raises(NotImplementedError):
        load_classeval_task(tmp_path, "Box", direction="rust_to_go")
