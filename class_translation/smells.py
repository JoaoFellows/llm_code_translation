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


_PMD_BIN = Path(__file__).resolve().parent / "tools" / "pmd-bin-7.1.0" / "bin"


def pmd_executable() -> Path | None:
    for name in ("pmd.bat", "pmd"):
        path = _PMD_BIN / name
        if path.is_file():
            return path
    return None


def count_target_smells(code: str, module_name: str, target_lang: str) -> SmellReport:
    if target_lang == "python":
        return count_smells(code, module_name)
    if target_lang == "java":
        return count_pmd(code, module_name)
    raise NotImplementedError(f"No smell counter for target language {target_lang}")


def count_pmd(code: str, module_name: str) -> SmellReport:
    executable = pmd_executable()
    if executable is None:
        raise FileNotFoundError("PMD 7.1.0 binary is not installed")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        filename = f"{module_name}.java"
        (root / filename).write_text(code, encoding="utf-8")
        completed = subprocess.run(
            [
                str(executable),
                "check",
                "-d",
                filename,
                "-R",
                "rulesets/java/quickstart.xml",
                "-f",
                "json",
            ],
            cwd=directory,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            check=False,
        )
        return _pmd_report(completed.stdout, completed.stderr)


def _pmd_report(stdout: str, stderr: str) -> SmellReport:
    text = stdout.strip()
    start = text.find("{")
    if start == -1:
        raw = stderr.strip() or text
        if not raw:
            return SmellReport(0, "")
        return SmellReport(1, raw[:8000])
    try:
        payload = json.loads(text[start:])
    except json.JSONDecodeError:
        return SmellReport(1, (text or stderr)[:8000])
    if not isinstance(payload, dict):
        return SmellReport(1, text[:8000])
    lines: list[str] = []
    for item in payload.get("files", []):
        if not isinstance(item, dict):
            continue
        for violation in item.get("violations", []):
            if isinstance(violation, dict):
                rule = violation.get("rule", "unknown")
                description = violation.get("description", "")
                lines.append(f"{rule}: {description}")
    for error in payload.get("processingErrors", []):
        if isinstance(error, dict):
            lines.append(f"processing-error: {error.get('message', error)}")
        elif error:
            lines.append(f"processing-error: {error}")
    return SmellReport(len(lines), "\n".join(lines)[:8000])
