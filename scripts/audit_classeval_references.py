"""Run this project's target test runners against ClassEval-T reference solutions."""

from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from class_translation.classeval import _implemented_python, load_classeval_task
from class_translation.testing import run_junit, run_unittest


def check(root: Path, task_id: str, direction: str) -> dict[str, object]:
    try:
        task = load_classeval_task(root, task_id, direction=direction)
        if direction == "java_to_python":
            path = root / "ClassEval_T" / "py" / "solution" / f"{task_id}.py"
            code = _implemented_python(path.read_text(encoding="utf-8"))
            result = run_unittest(code, task.oracle_tests, task.module_name)
        else:
            path = root / "ClassEval_T" / "java" / "solutuon" / f"{task_id}.java"
            result = run_junit(path.read_text(encoding="utf-8"), task.oracle_tests, task.module_name)
        return {
            "task_id": task_id,
            "direction": direction,
            "passed": result.passed,
            "total": result.total,
            "ok": result.ok,
            "feedback": result.feedback[:1000],
        }
    except Exception as error:
        return {
            "task_id": task_id,
            "direction": direction,
            "passed": 0,
            "total": 0,
            "ok": False,
            "feedback": f"{type(error).__name__}: {error}"[:1000],
        }


def main() -> None:
    root = Path(sys.argv[1]).resolve()
    output = Path(sys.argv[2]).resolve()
    java = {p.stem for p in (root / "ClassEval_T" / "java" / "solutuon").glob("*.java")}
    python = {p.stem for p in (root / "ClassEval_T" / "py" / "solution").glob("*.py")}
    ids = sorted(java & python)
    work = [(task_id, direction) for task_id in ids for direction in ("java_to_python", "python_to_java")]
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(check, root, task_id, direction): (task_id, direction) for task_id, direction in work}
        for future in as_completed(futures):
            row = future.result()
            rows.append(row)
            print(f"{len(rows)}/{len(work)} {row['direction']} {row['task_id']} {row['passed']}/{row['total']}", flush=True)
    rows.sort(key=lambda row: (str(row["direction"]), str(row["task_id"])))
    with output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    for direction in ("java_to_python", "python_to_java"):
        subset = [row for row in rows if row["direction"] == direction]
        print(json.dumps({"direction": direction, "tasks": len(subset), "passed_tasks": sum(bool(row["ok"]) for row in subset), "passed_tests": sum(int(row["passed"]) for row in subset), "total_tests": sum(int(row["total"]) for row in subset)}))


if __name__ == "__main__":
    main()
