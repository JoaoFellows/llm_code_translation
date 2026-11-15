from pathlib import Path

from class_translation.correction import correct
from class_translation.providers import ScriptedChatClient
from class_translation.state import load_task
from class_translation.tests.samples import BUGGY, CLEAN

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "counter"


def test_repair_stops_when_tests_pass():
    task = load_task(FIXTURE)
    client = ScriptedChatClient([CLEAN])
    result = correct(task, BUGGY, client)
    assert result.iterations == 1
    assert result.passed == result.total == 2
    assert result.status == "passed"
    prompt = client.prompts[0][-1]["content"]
    assert "assertEquals" in prompt
    assert "import unittest" not in prompt
    assert "AssertionError" in prompt or "Test feedback" in prompt


def test_repair_stops_at_three_failures():
    task = load_task(FIXTURE)
    client = ScriptedChatClient([BUGGY, BUGGY, BUGGY, CLEAN])
    result = correct(task, BUGGY, client)
    assert result.iterations == 3
    assert result.status == "failed"
    assert len(client.prompts) == 3
