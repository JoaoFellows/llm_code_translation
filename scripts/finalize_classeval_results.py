"""Keep the latest result for each ClassEval-T task and direction."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True, action="append")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--benchmark-root", type=Path)
    parser.add_argument("--pending-output", type=Path)
    args = parser.parse_args()
    latest: dict[tuple[str, str], dict[str, object]] = {}
    attempts = 0
    for input_path in args.input:
        for line in input_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            latest[(str(row["direction"]), str(row["task_id"]))] = row
            attempts += 1
    rows = [latest[key].copy() for key in sorted(latest)]
    for row in rows:
        if "tests_passed" in row and int(row["tests_passed"]) < 0:
            row["raw_tests_passed"] = row["tests_passed"]
            row["tests_passed"] = 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    for direction in ("java_to_python", "python_to_java"):
        subset = [row for row in rows if row["direction"] == direction]
        statuses = Counter(str(row["status"]) for row in subset)
        print(json.dumps({
            "direction": direction,
            "tasks": len(subset),
            "passed": statuses["passed"],
            "failed": statuses["failed"],
            "error": statuses["error"],
            "tests_passed": sum(max(0, int(row.get("tests_passed", 0))) for row in subset),
            "tests_total": sum(int(row.get("tests_total", 0)) for row in subset),
        }))
    print(f"attempts={attempts} unique_results={len(rows)} output={args.output}")
    if args.benchmark_root and args.pending_output:
        source_dir = args.benchmark_root / "ClassEval_T" / "java" / "solutuon"
        ids = sorted(path.stem for path in source_dir.glob("*.java"))
        pending = {}
        for direction in ("java_to_python", "python_to_java"):
            pending[direction] = {
                "missing": [task_id for task_id in ids if (direction, task_id) not in latest],
                "error": [task_id for task_id in ids if latest.get((direction, task_id), {}).get("status") == "error"],
            }
        args.pending_output.parent.mkdir(parents=True, exist_ok=True)
        args.pending_output.write_text(json.dumps(pending, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"pending_output={args.pending_output}")


if __name__ == "__main__":
    main()
