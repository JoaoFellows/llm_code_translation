from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from class_translation.smells import count_target_smells, pmd_executable


EXTENSIONS = {
    "Python": (".py",), "Java": (".java",), "Go": (".go",),
    "Rust": (".rs",), "JavaScript": (".js", ".jsx", ".ts", ".tsx"),
    "C": (".c", ".h"), "C++": (".cpp", ".cc", ".cxx", ".h", ".hpp"),
    "C#": (".cs",), "Matlab": (".m",),
}
_EXCLUDED = {".git", "node_modules", "target", "build", "dist", ".venv", "venv", "public_tests", "original_tests", "tests", "test"}


def code_files(root: Path, language: str, *, exclude_tests: bool = False) -> list[Path]:
    suffixes = EXTENSIONS.get(language)
    if suffixes is None:
        raise ValueError(f"Unsupported language: {language}")
    excluded = _EXCLUDED if exclude_tests else _EXCLUDED - {"public_tests", "original_tests", "tests", "test"}
    return sorted(path for path in root.rglob("*") if path.is_file()
                  and path.suffix.lower() in suffixes
                  and not any(part in excluded for part in path.relative_to(root).parts[:-1])
                  and (not exclude_tests or not path.stem.lower().startswith("test_")))


@dataclass(frozen=True)
class TestResult:
    passed: bool
    exit_code: int | None
    output: str


_ANSI = re.compile(r"\x1b\[[0-9;]*m")
_MAVEN_TESTS = re.compile(r"Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+),\s*Skipped:\s*(\d+)")


def _zero_tests_executed(output: str) -> bool:
    clean = _ANSI.sub("", output)
    if re.search(r"\b(?:Tests are skipped\.|Not compiling test sources)\b", clean, re.IGNORECASE):
        return True
    maven_matches = _MAVEN_TESTS.findall(clean)
    if maven_matches:
        last_run = int(maven_matches[-1][0])
        if last_run == 0:
            return True
    if re.search(r"\b(?:no tests ran|collected 0 items)\b", clean, re.IGNORECASE) and not re.search(r"\b[1-9]\d*\s+passed\b", clean):
        return True
    return False


def run_benchmark_tests(dataset_root: Path, workdir: Path, image: str, timeout: int = 600) -> TestResult:
    root = dataset_root.resolve()
    relative = workdir.resolve().relative_to(root)
    if not (workdir / "run_tests.sh").is_file():
        raise FileNotFoundError(workdir / "run_tests.sh")
    container_dir = "/workspace/" + relative.as_posix()
    try:
        completed = subprocess.run(
            ["docker", "run", "--rm", "--network", "none", "-e", "PYTHONPATH=.", "--mount",
             f"type=bind,source={root},target=/workspace", "--workdir", container_dir,
             image, "bash", "run_tests.sh"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired as error:
        return TestResult(False, None, f"Test timeout after {timeout}s: {error}")
    output = (completed.stdout + "\n" + completed.stderr)[-12000:]
    passed = completed.returncode == 0
    if passed and _zero_tests_executed(output):
        passed = False
        output = (output + "\n[EVAL] Marked as failed: test runner exited 0 but executed 0 tests.")[-12000:]
    return TestResult(passed, completed.returncode, output)


@dataclass(frozen=True)
class SmellResult:
    count: int
    feedback: str


def count_repository_smells(workdir: Path, target_language: str) -> SmellResult | None:
    if target_language not in {"Python", "Java"}:
        return None
    paths = code_files(workdir, target_language, exclude_tests=True)
    if not paths:
        raise ValueError(f"No {target_language} source files to evaluate in {workdir}")
    if target_language == "Python":
        env = os.environ.copy()
        env["PYTHONPATH"] = str(workdir)
        env["PYTHONIOENCODING"] = "utf-8"
        completed = subprocess.run(
            [sys.executable, "-m", "pylint", "--output-format=json", "--score=n",
             *(str(path.relative_to(workdir)) for path in paths)],
            cwd=workdir, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=120, check=False, env=env,
        )
        if completed.returncode & 32:
            raise RuntimeError(f"Pylint could not analyze repository: {completed.stderr[-2000:]}")
        try:
            messages = json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"Pylint did not produce JSON: {completed.stderr[-2000:]}") from error
        if not isinstance(messages, list):
            raise RuntimeError("Pylint returned an unexpected result")
        lines = [f"{item.get('path', '')}: {item.get('symbol', '')}: {item.get('message', '')}"
                 for item in messages if isinstance(item, dict)]
        return SmellResult(len(lines), "\n".join(lines)[:12000])
    if target_language == "Java" and pmd_executable() is None:
        return None
    total = 0
    feedback = []
    for path in paths:
        report = count_target_smells(path.read_text(encoding="utf-8"), path.stem, target_language.lower())
        total += report.count
        if report.feedback:
            feedback.append(f"{path.relative_to(workdir).as_posix()}: {report.feedback}")
    return SmellResult(total, "\n".join(feedback)[:12000])
