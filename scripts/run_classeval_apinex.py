"""Run one ClassEval-T class in both directions with a configured provider."""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from openai import APIStatusError

from class_translation.classeval import load_classeval_task
from class_translation.extract import extract_code
from class_translation.pipeline import run_task
from class_translation.providers import PRESETS, build_client, load_project_env
from class_translation.smells import count_target_smells
from class_translation.testing import run_target_tests


class RecordingClient:
    """Capture tests and smells for each translation, repair, and refactor candidate."""

    def __init__(self, client, task, emit: bool = True) -> None:
        self.client = client
        self.task = task
        self.emit = emit
        self.trace: list[dict[str, object]] = []
        self.accepted_smells: int | None = None

    def complete(self, messages: list[dict[str, str]]) -> str:
        response = self.client.complete(messages)
        system = messages[0]["content"].lower()
        if "removing code smells" in system:
            phase = "smell_graph"
        elif "fixing a code translation" in system:
            phase = "correction"
        else:
            phase = "translation"
        code = extract_code(response, self.task.target_lang)
        tests = run_target_tests(
            code, self.task.oracle_tests, self.task.module_name, self.task.target_lang
        )
        smells = count_target_smells(code, self.task.module_name, self.task.target_lang).count
        event: dict[str, object] = {
            "phase": phase,
            "iteration": sum(item["phase"] == phase for item in self.trace) + 1,
            "tests_passed": tests.passed,
            "tests_total": tests.total,
            "smells": smells,
        }
        if phase == "translation":
            event["iteration"] = 0
        elif phase == "smell_graph":
            accepted = tests.ok and self.accepted_smells is not None and smells < self.accepted_smells
            event["accepted"] = accepted
            if accepted:
                self.accepted_smells = smells
        elif tests.ok:
            self.accepted_smells = smells
        if phase == "translation" and tests.ok:
            self.accepted_smells = smells
        self.trace.append(event)
        if self.emit:
            print("LOOP " + json.dumps(event, ensure_ascii=False), flush=True)
        return response


def safe_error(error: Exception) -> dict[str, object]:
    info: dict[str, object] = {"type": type(error).__name__}
    if isinstance(error, APIStatusError):
        info["status_code"] = error.status_code
        info["code"] = getattr(error, "code", None)
        if "no credits remaining" in str(error).lower():
            info["reason"] = "no_credits"
    return info


def run_with_retry(task, client):
    for attempt in range(3):
        try:
            return run_task(task, client)
        except APIStatusError as error:
            if (
                error.status_code not in (429, 503)
                or "no credits remaining" in str(error).lower()
                or attempt == 2
            ):
                raise
            time.sleep(30 * (attempt + 1))
    raise AssertionError("Unreachable")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_id", nargs="?", default="BankAccount")
    parser.add_argument("--provider", choices=("apinex", "openai"), default="apinex")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    load_project_env()
    root = Path(os.environ.get("CLASSEVAL_T_PATH", r"C:\ClassEval-T"))
    client = build_client(args.provider, timeout=120)
    output = args.output or Path(f"reports/classeval_{args.provider}_{args.task_id.lower()}.jsonl")
    output.parent.mkdir(parents=True, exist_ok=True)
    had_error = False

    for direction in ("python_to_java", "java_to_python"):
        started = time.monotonic()
        print(f"START {direction} {args.task_id}", flush=True)
        row: dict[str, object] = {
            "provider": args.provider,
            "model": PRESETS[args.provider]["model"],
            "direction": direction,
            "task_id": args.task_id,
            "run_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        recording_client = None
        try:
            task = load_classeval_task(root, args.task_id, direction=direction)
            recording_client = RecordingClient(client, task)
            row.update(run_with_retry(task, recording_client).to_dict())
            row["loop_trace"] = recording_client.trace
        except Exception as error:
            had_error = True
            row.update(status="error", error=safe_error(error))
            if recording_client is not None:
                row["loop_trace"] = recording_client.trace
        row["elapsed_s"] = round(time.monotonic() - started, 1)
        with output.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(json.dumps(row, ensure_ascii=False), flush=True)
    if had_error:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
