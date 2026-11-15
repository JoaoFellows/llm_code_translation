from __future__ import annotations

from pathlib import Path

from class_translation.state import ClassTask

_JAVA_SOLUTION_DIR = "solutuon"


def load_classeval_task(root: Path, task_id: str) -> ClassTask:
    benchmark = root / "ClassEval_T"
    java_code = (benchmark / "java" / _JAVA_SOLUTION_DIR / f"{task_id}.java").read_text(encoding="utf-8")
    java_tests = (benchmark / "java" / "test" / f"{task_id}Test.java").read_text(encoding="utf-8")
    oracle = (benchmark / "py" / "test" / f"{task_id}.py").read_text(encoding="utf-8")
    import_line = f"from {task_id} import {task_id}"
    if import_line not in oracle:
        oracle = import_line + "\n" + oracle
    return ClassTask(
        task_id=task_id,
        source_lang="java",
        target_lang="python",
        module_name=task_id,
        source_code=java_code,
        source_tests=java_tests,
        oracle_tests=oracle,
    )
