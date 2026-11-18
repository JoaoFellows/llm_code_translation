from pathlib import Path

from class_translation.state import load_task
from class_translation.testing import run_junit, run_unittest
from class_translation.tests.samples import BUGGY, CLEAN

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "counter"


def test_clean_code_passes_oracle():
    task = load_task(FIXTURE)
    report = run_unittest(CLEAN, task.oracle_tests, task.module_name)
    assert report.passed == report.total == 2


def test_buggy_code_fails_oracle():
    task = load_task(FIXTURE)
    report = run_unittest(BUGGY, task.oracle_tests, task.module_name)
    assert report.total == 2 and report.passed < report.total
    assert report.feedback


PASSING_JAVA = """\
package org.example;

public class Box {
    private int value;

    public void add(int amount) {
        this.value += amount;
    }

    public int getValue() {
        return this.value;
    }
}
"""

FAILING_JAVA = """\
package org.example;

public class Box {
    private int value;

    public void add(int amount) {
        this.value = 0;
    }

    public int getValue() {
        return this.value;
    }
}
"""

JAVA_ORACLE = """\
package org.example;

import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class BoxTest {
    @Test
    public void testJUnit4() {
        Box box = new Box();
        box.add(2);
        assertEquals(2, box.getValue());
    }

    @org.junit.jupiter.api.Test
    public void testJupiter() {
        Box box = new Box();
        box.add(3);
        org.junit.jupiter.api.Assertions.assertEquals(3, box.getValue());
    }
}
"""


def test_junit_runner_passes_minimal_class():
    report = run_junit(PASSING_JAVA, JAVA_ORACLE, "Box")
    assert report.passed == report.total == 2
    assert report.ok


def test_junit_runner_fails_minimal_class():
    report = run_junit(FAILING_JAVA, JAVA_ORACLE, "Box")
    assert report.total == 2 and report.passed < report.total
    assert not report.ok
    assert report.feedback
