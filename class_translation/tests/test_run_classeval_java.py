import json
from pathlib import Path

from class_translation.run_classeval_java import _RESULTS, _done_ids


def test_results_file_is_the_python_to_java_log():
    assert _RESULTS.name == "classeval_gemini_py2java.jsonl"
    assert _RESULTS.name != "classeval_gemini.jsonl"


def test_done_ids_skips_recorded_tasks(tmp_path: Path):
    path = tmp_path / "out.jsonl"
    path.write_text(
        json.dumps({"task_id": "AvgPartition", "status": "passed"}) + "\n\n",
        encoding="utf-8",
    )
    assert _done_ids(path) == {"AvgPartition"}
    assert _done_ids(tmp_path / "missing.jsonl") == set()
