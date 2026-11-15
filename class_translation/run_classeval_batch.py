from __future__ import annotations

import json
import os
import time
from pathlib import Path

from class_translation.classeval import load_classeval_task
from class_translation.pipeline import run_task
from class_translation.providers import build_client

_RESULTS = Path(__file__).resolve().parent / "results" / "classeval_gemini.jsonl"


def _task_ids(root: Path) -> list[str]:
    folder = root / "ClassEval_T" / "java" / "solutuon"
    return sorted(path.stem for path in folder.glob("*.java"))


def _done_ids(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    done: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        done.add(json.loads(line)["task_id"])
    return done


def _redact(text: str) -> str:
    secret = os.environ.get("GEMINI_API_KEY", "")
    if secret:
        text = text.replace(secret, "REDACTED")
    return text[:500]


def main() -> None:
    configured = os.environ.get("CLASSEVAL_T_PATH", "").strip()
    root = Path(configured) if configured else Path(r"C:\ClassEval-T")
    ids = _task_ids(root)
    _RESULTS.parent.mkdir(parents=True, exist_ok=True)
    done = _done_ids(_RESULTS)
    client = build_client("gemini", timeout=120)
    print(f"tasks={len(ids)} already_done={len(done)}", flush=True)
    for index, task_id in enumerate(ids, start=1):
        if task_id in done:
            continue
        started = time.time()
        print(f"{index}/{len(ids)} {task_id}", flush=True)
        try:
            task = load_classeval_task(root, task_id)
            record = run_task(task, client)
            row: dict[str, object] = {
                "provider": "gemini",
                "model": "gemini-3.5-flash-lite",
                "elapsed_s": round(time.time() - started, 1),
                **record.to_dict(),
            }
        except Exception as error:
            row = {
                "provider": "gemini",
                "model": "gemini-3.5-flash-lite",
                "task_id": task_id,
                "status": "error",
                "error": _redact(f"{type(error).__name__}: {error}"),
                "elapsed_s": round(time.time() - started, 1),
            }
        with _RESULTS.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row) + "\n")
        print(json.dumps(row), flush=True)
    print(f"DONE {len(ids)}", flush=True)


if __name__ == "__main__":
    main()
