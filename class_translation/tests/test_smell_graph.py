from pathlib import Path

from class_translation.providers import ScriptedChatClient
from class_translation.smell_graph import reduce_smells
from class_translation.smells import count_smells
from class_translation.state import load_task
from class_translation.testing import run_unittest
from class_translation.tests.samples import BROKEN, CLEAN, SMELLY

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "counter"


def test_rollback_restores_previous_code_when_tests_break():
    task = load_task(FIXTURE)
    client = ScriptedChatClient([BROKEN, BROKEN, BROKEN])
    result = reduce_smells(task, SMELLY, client)
    assert result.iterations == 3
    assert result.status == "rolled_back"
    assert len(client.prompts) == 3
    assert "unused = amount" in result.code
    report = run_unittest(result.code, task.oracle_tests, task.module_name)
    assert report.passed == report.total


def test_accepts_refactor_that_lowers_smells_and_keeps_tests():
    task = load_task(FIXTURE)
    client = ScriptedChatClient([CLEAN])
    result = reduce_smells(task, SMELLY, client, max_iterations=1)
    assert result.iterations == 1
    assert "unused = amount" not in result.code
    assert count_smells(result.code, "counter").count < count_smells(SMELLY, "counter").count
