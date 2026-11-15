from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from openai import APIError

from class_translation.classeval import load_classeval_task
from class_translation.pipeline import run_task
from class_translation.providers import build_client

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


def run(task_id: str, root: Path) -> None:
    task = load_classeval_task(root, task_id)
    presets = ["openai", "gemini"]
    for index, preset in enumerate(presets):
        client = build_client(preset)
        try:
            client.complete([{"role": "user", "content": "Reply with the single word ok"}])
            record = run_task(task, client)
        except APIError as error:
            print(f"{preset}: {_safe_error(error)}")
            if preset == "openai" and _is_credit_error(error) and index == 0:
                print("OpenAI sem crédito. Tentando Gemini.")
                continue
            raise
        print(json.dumps({"provider": preset, **record.to_dict()}, indent=2))
        return


def main() -> None:
    task_id = sys.argv[1] if len(sys.argv) > 1 else "AvgPartition"
    configured = os.environ.get("CLASSEVAL_T_PATH", "").strip()
    root = Path(configured) if configured else Path(r"C:\ClassEval-T")
    run(task_id, root)


if __name__ == "__main__":
    main()
