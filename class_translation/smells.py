from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SmellReport:
    count: int
    feedback: str


def count_smells(code: str, module_name: str) -> SmellReport:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        filename = f"{module_name}.py"
        (root / filename).write_text(code, encoding="utf-8")
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "pylint",
                filename,
                "--output-format=json",
                "--score=n",
            ],
            cwd=directory,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            check=False,
            env=env,
        )
        stdout = completed.stdout.strip()
        if not stdout:
            raw = completed.stderr.strip()
            if not raw:
                return SmellReport(0, "")
            return SmellReport(1, raw[:8000])
        try:
            messages = json.loads(stdout)
        except json.JSONDecodeError:
            return SmellReport(1, (stdout or completed.stderr)[:8000])
        if not isinstance(messages, list):
            return SmellReport(1, stdout[:8000])
        lines = [
            f"{item.get('symbol', 'unknown')}: {item.get('message', '')}"
            for item in messages
            if isinstance(item, dict)
        ]
        return SmellReport(len(lines), "\n".join(lines))
