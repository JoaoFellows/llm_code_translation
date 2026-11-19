"""Run ClassEval-T with Gemini into a new, resumable JSONL result file."""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from openai import APIStatusError

from class_translation.classeval import load_classeval_task
from class_translation.pipeline import run_task
from class_translation.providers import PRESETS, build_client, load_project_env

DIRECTIONS = ("java_to_python", "python_to_java")


def completed(path: Path) -> set[tuple[str, str]]:
    if not path.exists():
        return set()
    rows = (json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    return {(row["direction"], row["task_id"]) for row in rows if row.get("status") != "error"}


def safe_error(error: Exception) -> dict[str, object]:
    info: dict[str, object] = {"type": type(error).__name__}
    if isinstance(error, APIStatusError):
        info["status_code"] = error.status_code
        info["code"] = getattr(error, "code", None)
    return info


def run_with_retry(task, client):
    for attempt in range(3):
        try:
            return run_task(task, client)
        except APIStatusError as error:
            if error.status_code not in (429, 503) or attempt == 2:
                raise
            delay = 30 * (attempt + 1)
            print(f"RETRY status={error.status_code} wait={delay}s", flush=True)
            time.sleep(delay)
    raise AssertionError("Unreachable")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--only", help="Run one task ID; otherwise run all 94")
    parser.add_argument("--direction", choices=("both", *DIRECTIONS), default="both")
    parser.add_argument("--start", type=int, default=1, help="First 1-based sorted task index")
    parser.add_argument("--stop", type=int, default=94, help="Last 1-based sorted task index")
    args = parser.parse_args()
    load_project_env()
    root = Path(os.environ["CLASSEVAL_T_PATH"]).resolve()
    source_dir = root / "ClassEval_T" / "java" / "solutuon"
    ids = sorted(path.stem for path in source_dir.glob("*.java"))
    if len(ids) != 94:
        raise RuntimeError(f"Expected 94 ClassEval-T classes, found {len(ids)} in {source_dir}")
    if not (1 <= args.start <= args.stop <= 94):
        raise ValueError("Expected 1 <= start <= stop <= 94")
    ids = ids[args.start - 1 : args.stop]
    if args.only:
        if args.only not in ids:
            raise ValueError(f"Unknown task ID: {args.only}")
        ids = [args.only]
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    done = completed(output)
    client = build_client("gemini", timeout=120)
    print(f"model={PRESETS['gemini']['model']} tasks={len(ids)} directions={len(DIRECTIONS)} already_done={len(done)}", flush=True)
    directions = DIRECTIONS if args.direction == "both" else (args.direction,)
    for direction in directions:
        for index, task_id in enumerate(ids, start=1):
            if (direction, task_id) in done:
                continue
            started = time.monotonic()
            print(f"START {direction} {index}/{len(ids)} {task_id}", flush=True)
            base: dict[str, object] = {
                "provider": "gemini",
                "model": PRESETS["gemini"]["model"],
                "direction": direction,
                "task_id": task_id,
                "run_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            try:
                task = load_classeval_task(root, task_id, direction=direction)
                record = run_with_retry(task, client)
                row = {**base, **record.to_dict()}
            except Exception as error:
                row = {**base, "status": "error", "error": safe_error(error)}
            row["elapsed_s"] = round(time.monotonic() - started, 1)
            with output.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            print(json.dumps(row, ensure_ascii=False), flush=True)
    print(f"DONE output={output}", flush=True)


if __name__ == "__main__":
    main()
