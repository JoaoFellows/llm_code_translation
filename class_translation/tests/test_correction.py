from pathlib import Path

from class_translation.correction import correct
from class_translation.providers import ScriptedChatClient
from class_translation.state import load_task
from class_translation.tests.samples import BOX_BUGGY, BOX_CLEAN, BUGGY, CLEAN

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "counter"
BOX = Path(__file__).resolve().parents[1] / "fixtures" / "box"


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


def test_java_repair_stops_when_tests_pass():
    task = load_task(BOX)
    client = ScriptedChatClient([BOX_CLEAN])
    result = correct(task, BOX_BUGGY, client)
    assert result.iterations == 1
    assert result.passed == result.total == 2
    assert result.status == "passed"
    prompt = client.prompts[0][-1]["content"]
    assert "Print only the java class." in prompt
    assert "package org.example" in prompt


def test_repair_stops_at_three_failures():
    task = load_task(FIXTURE)
    client = ScriptedChatClient([BUGGY, BUGGY, BUGGY, CLEAN])
    result = correct(task, BUGGY, client)
    assert result.iterations == 3
    assert result.status == "failed"
    assert len(client.prompts) == 3
