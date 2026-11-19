"""Exercise both translation directions using deterministic fixture responses."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from class_translation.pipeline import run_task
from class_translation.providers import ScriptedChatClient
from class_translation.state import load_task
from class_translation.tests.samples import BOX_BUGGY, BOX_CLEAN, BOX_SMELLY, BROKEN, BUGGY, CLEAN, SMELLY


def main() -> None:
    output = Path(sys.argv[1])
    root = Path(__file__).resolve().parents[1] / "class_translation" / "fixtures"
    cases = (
        ("counter", [BUGGY, SMELLY, CLEAN, BROKEN, BROKEN]),
        ("box", [BOX_BUGGY, BOX_SMELLY, BOX_CLEAN]),
    )
    rows = []
    for name, responses in cases:
        task = load_task(root / name)
        record = run_task(task, ScriptedChatClient(responses))
        row = {"client": "ScriptedChatClient", "model": None, "direction": f"{task.source_lang}_to_{task.target_lang}", **record.to_dict()}
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
