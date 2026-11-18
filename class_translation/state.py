from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

MAX_CORRECTION_ITERATIONS = 3
MAX_SMELL_ITERATIONS = 3


@dataclass(frozen=True)
class ClassTask:
    task_id: str
    source_lang: str
    target_lang: str
    module_name: str
    source_code: str
    source_tests: str
    oracle_tests: str


@dataclass(frozen=True)
class TaskRecord:
    task_id: str
    tests_passed: int
    tests_total: int
    status: str
    smells_after_translation: int
    smells_after_correction: int
    smells_after_smell_graph: int
    correction_iterations: int
    smell_iterations: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def load_task(fixture_dir: Path) -> ClassTask:
    meta = json.loads((fixture_dir / "task.json").read_text(encoding="utf-8"))
    return ClassTask(
        task_id=meta["task_id"],
        source_lang=meta["source_lang"],
        target_lang=meta["target_lang"],
        module_name=meta["module_name"],
        source_code=(fixture_dir / meta["source_filename"]).read_text(encoding="utf-8"),
        source_tests=(fixture_dir / meta["source_test_filename"]).read_text(encoding="utf-8"),
        oracle_tests=(fixture_dir / meta["oracle_filename"]).read_text(encoding="utf-8"),
    )


_SUPPORTED_DIRECTIONS = {("java", "python"), ("python", "java")}


def ensure_java_to_python(task: ClassTask) -> None:
    if (task.source_lang, task.target_lang) in _SUPPORTED_DIRECTIONS:
        return
    raise NotImplementedError(
        f"Translation direction {task.source_lang} -> {task.target_lang} is not implemented"
    )
