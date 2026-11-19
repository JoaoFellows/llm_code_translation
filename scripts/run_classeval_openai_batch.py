"""Run all 94 ClassEval-T classes in both directions with resumable JSONL output."""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from openai import APIStatusError

from class_translation.classeval import load_classeval_task
from class_translation.providers import PRESETS, build_client, load_project_env
import class_translation.correction as correction_module
import class_translation.pipeline as pipeline_module
import class_translation.smell_graph as smell_graph_module
import scripts.run_classeval_apinex as single_module
from scripts.run_classeval_apinex import RecordingClient, run_with_retry, safe_error


def cache_local_checks():
    """Reuse deterministic test and linter results within each class run."""
    tests = lru_cache(maxsize=32)(single_module.run_target_tests)
    smells = lru_cache(maxsize=32)(single_module.count_target_smells)
    for module in (correction_module, pipeline_module, smell_graph_module, single_module):
        if hasattr(module, "run_target_tests"):
            module.run_target_tests = tests
        if hasattr(module, "count_target_smells"):
            module.count_target_smells = smells
    return tests, smells


def completed(path: Path) -> set[tuple[str, str]]:
    if not path.exists():
        return set()
    return {
        (row["direction"], row["task_id"])
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
        for row in [json.loads(line)]
        if row.get("status") in ("passed", "failed")
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path, default=Path("reports/classeval_openai_gpt41mini_2026-11-19.jsonl")
    )
    parser.add_argument("--direction", choices=("both", "python_to_java", "java_to_python"), default="both")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--stop", type=int, default=94)
    args = parser.parse_args()

    load_project_env()
    root = Path(os.environ.get("CLASSEVAL_T_PATH", r"C:\ClassEval-T"))
    source_dir = root / "ClassEval_T" / "java" / "solutuon"
    ids = sorted(path.stem for path in source_dir.glob("*.java"))
    if len(ids) != 94:
        raise RuntimeError(f"Expected 94 classes, found {len(ids)}")
    if not (1 <= args.start <= args.stop <= 94):
        raise ValueError("Expected 1 <= start <= stop <= 94")
    selected = list(enumerate(ids, 1))[args.start - 1 : args.stop]
    directions = ("python_to_java", "java_to_python") if args.direction == "both" else (args.direction,)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    done = completed(args.output)
    client = build_client("openai", timeout=120)
    cached_tests, cached_smells = cache_local_checks()
    print(f"TOTAL classes={len(selected)} directions={len(directions)} completed={len(done)}", flush=True)

    for direction in directions:
        for index, task_id in selected:
            if (direction, task_id) in done:
                continue
            print(f"START {direction} {index}/94 {task_id}", flush=True)
            cached_tests.cache_clear()
            cached_smells.cache_clear()
            started = time.monotonic()
            row: dict[str, object] = {
                "provider": "openai",
                "model": PRESETS["openai"]["model"],
                "direction": direction,
                "task_id": task_id,
                "run_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            recording_client = None
            fatal = False
            try:
                task = load_classeval_task(root, task_id, direction=direction)
                recording_client = RecordingClient(client, task, emit=False)
                row.update(run_with_retry(task, recording_client).to_dict())
            except Exception as error:
                row.update(status="error", error=safe_error(error))
                fatal = isinstance(error, APIStatusError) and (
                    error.status_code in (401, 402, 403)
                    or getattr(error, "code", None) in ("credit_balance_exhausted", "insufficient_quota")
                    or "no credits remaining" in str(error).lower()
                )
            row["loop_trace"] = recording_client.trace if recording_client is not None else []
            row["elapsed_s"] = round(time.monotonic() - started, 1)
            with args.output.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            print("RESULT " + json.dumps(row, ensure_ascii=False), flush=True)
            if fatal:
                print("STOP account or billing error", flush=True)
                raise SystemExit(2)


if __name__ == "__main__":
    main()
