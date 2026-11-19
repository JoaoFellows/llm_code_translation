from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

from openai import APIError

from class_translation.classeval import load_classeval_task
from class_translation.pipeline import run_task
from class_translation.providers import PRESETS, build_client, load_project_env

_RESULTS = Path(__file__).resolve().parent / "results" / "classeval_gemini_py2java.jsonl"
_REPO_ROOT = Path(__file__).resolve().parents[1]
_PARENT_ENV = Path(r"C:\llm_code_translation\.env")
_CREDIT_MARKERS = (
    "insufficient_quota",
    "billing_hard_limit",
    "credit_balance_exhausted",
    "exceeded your current quota",
    "insufficient balance",
    "credit balance",
    "no credits remaining",
    "payment required",
)


def _copy_env_if_missing() -> None:
    target = _REPO_ROOT / ".env"
    if target.is_file() or not _PARENT_ENV.is_file():
        return
    target.write_bytes(_PARENT_ENV.read_bytes())


def _done_ids(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    done: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        done.add(json.loads(line)["task_id"])
    return done


def _is_credit_error(error: APIError) -> bool:
    code = str(getattr(error, "code", "") or "").lower()
    status = getattr(error, "status_code", None)
    text = str(error).lower()
    if code in {"insufficient_quota", "billing_hard_limit_reached"}:
        return True
    if status == 402:
        return True
    return any(marker in text for marker in _CREDIT_MARKERS)


def _safe_error(error: APIError) -> str:
    status = getattr(error, "status_code", None)
    code = getattr(error, "code", None)
    return f"status={status} code={code}"


def _task_ids(root: Path) -> list[str]:
    folder = root / "ClassEval_T" / "java" / "solutuon"
    return sorted(path.stem for path in folder.glob("*.java"))


def _redact(text: str) -> str:
    for name in ("GEMINI_API_KEY", "OPENAI_API_KEY"):
        secret = os.environ.get(name, "")
        if secret:
            text = text.replace(secret, "REDACTED")
    return text[:500]


def _write_row(row: dict[str, object]) -> None:
    _RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with _RESULTS.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row) + "\n")
    print(json.dumps(row), flush=True)


def run(task_id: str, root: Path) -> None:
    _RESULTS.parent.mkdir(parents=True, exist_ok=True)
    if task_id in _done_ids(_RESULTS):
        print(f"skip {task_id}", flush=True)
        return
    task = load_classeval_task(root, task_id, direction="python_to_java")
    presets = ["openai", "gemini"]
    for index, preset in enumerate(presets):
        try:
            client = build_client(preset, timeout=120)
        except RuntimeError:
            if preset == "openai":
                print("OpenAI key missing. Trying Gemini.", flush=True)
                continue
            raise SystemExit(1) from None
        started = time.time()
        try:
            client.complete([{"role": "user", "content": "Reply with the single word ok"}])
            record = run_task(task, client)
        except APIError as error:
            print(f"{preset}: {_safe_error(error)}", flush=True)
            if preset == "openai" and _is_credit_error(error) and index == 0:
                print("OpenAI sem crédito. Tentando Gemini.", flush=True)
                continue
            raise SystemExit(1) from None
        _write_row(
            {
                "provider": preset,
                "model": PRESETS[preset]["model"],
                "elapsed_s": round(time.time() - started, 1),
                **record.to_dict(),
            }
        )
        return
    raise SystemExit(1)


def _retryable(error: Exception) -> bool:
    if isinstance(error, APIError):
        if _is_credit_error(error):
            return False
        status = getattr(error, "status_code", None)
        return status in {408, 409, 429, 500, 502, 503, 504}
    return error.__class__.__name__ in {"APIConnectionError", "APITimeoutError"}


def run_all(root: Path) -> None:
    ids = _task_ids(root)
    if not ids:
        raise SystemExit(f"No ClassEval-T classes under {root}")
    _RESULTS.parent.mkdir(parents=True, exist_ok=True)
    done = _done_ids(_RESULTS)
    client = build_client("gemini", timeout=120)
    print(f"tasks={len(ids)} already_done={len(done)}", flush=True)
    for index, task_id in enumerate(ids, start=1):
        if task_id in done:
            continue
        started = time.time()
        print(f"{index}/{len(ids)} {task_id}", flush=True)
        row: dict[str, object] | None = None
        for attempt in range(1, 6):
            try:
                task = load_classeval_task(root, task_id, direction="python_to_java")
                record = run_task(task, client)
                row = {
                    "provider": "gemini",
                    "model": PRESETS["gemini"]["model"],
                    "elapsed_s": round(time.time() - started, 1),
                    **record.to_dict(),
                }
                break
            except APIError as error:
                if _is_credit_error(error):
                    print(f"Gemini sem crédito em {task_id}: {_safe_error(error)}", flush=True)
                    raise SystemExit(1) from None
                if _retryable(error) and attempt < 5:
                    print(f"retry {attempt} {task_id}: {_safe_error(error)}", flush=True)
                    time.sleep(min(60, 5 * attempt))
                    continue
                row = {
                    "provider": "gemini",
                    "model": PRESETS["gemini"]["model"],
                    "task_id": task_id,
                    "status": "error",
                    "error": _redact(f"{type(error).__name__}: {_safe_error(error)}"),
                    "elapsed_s": round(time.time() - started, 1),
                }
                break
            except Exception as error:
                if _retryable(error) and attempt < 5:
                    print(f"retry {attempt} {task_id}: {type(error).__name__}", flush=True)
                    time.sleep(min(60, 5 * attempt))
                    continue
                row = {
                    "provider": "gemini",
                    "model": PRESETS["gemini"]["model"],
                    "task_id": task_id,
                    "status": "error",
                    "error": _redact(f"{type(error).__name__}: {error}"),
                    "elapsed_s": round(time.time() - started, 1),
                }
                break
        if row is not None:
            _write_row(row)
    print(f"DONE {len(ids)}", flush=True)


def main() -> None:
    _copy_env_if_missing()
    load_project_env()
    configured = os.environ.get("CLASSEVAL_T_PATH", "").strip()
    root = Path(configured) if configured else Path(r"C:\ClassEval-T")
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        run_all(root)
        return
    task_id = sys.argv[1] if len(sys.argv) > 1 else "AvgPartition"
    run(task_id, root)


if __name__ == "__main__":
    main()
