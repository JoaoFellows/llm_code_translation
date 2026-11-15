from pathlib import Path

from class_translation.state import load_task
from class_translation.testing import run_unittest
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
