from pathlib import Path

from class_translation.pipeline import run_task
from class_translation.providers import ScriptedChatClient
from class_translation.state import load_task
from class_translation.tests.samples import BOX_BUGGY, BOX_CLEAN, BOX_SMELLY, BROKEN, BUGGY, CLEAN, SMELLY

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "counter"
BOX = Path(__file__).resolve().parents[1] / "fixtures" / "box"


def test_pipeline_record_for_scripted_box():
    task = load_task(BOX)
    client = ScriptedChatClient([BOX_BUGGY, BOX_SMELLY, BOX_CLEAN])
    record = run_task(task, client)
    assert record.task_id == "box"
    assert record.tests_passed == record.tests_total == 2
    assert record.status == "passed"
    assert record.correction_iterations == 1
    assert record.smell_iterations == 1
    assert record.smells_after_smell_graph < record.smells_after_correction
    assert record.to_dict()["status"] == "passed"


def test_pipeline_record_for_scripted_counter():
    task = load_task(FIXTURE)
    client = ScriptedChatClient([BUGGY, SMELLY, CLEAN, BROKEN, BROKEN])
    record = run_task(task, client)
    assert record.task_id == "counter"
    assert record.tests_passed == record.tests_total == 2
    assert record.status == "passed"
    assert record.correction_iterations == 1
    assert record.smell_iterations == 3
    assert record.smells_after_smell_graph < record.smells_after_correction
    assert record.to_dict()["status"] == "passed"
