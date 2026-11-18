from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

_RUNNER = """
import json
import unittest

loader = unittest.TestLoader()
suite = loader.discover(".", pattern="test_*.py")
with open("_unittest_out.txt", "w", encoding="utf-8") as stream:
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
chunks = []
for test, tb in list(result.failures) + list(result.errors):
    chunks.append(str(test))
    chunks.append(tb)
passed = result.testsRun - len(result.failures) - len(result.errors)
payload = {
    "passed": passed,
    "total": result.testsRun,
    "feedback": "\\n".join(chunks)[:8000],
}
print("CLASS_TRANSLATION_RESULT " + json.dumps(payload))
"""


@dataclass(frozen=True)
class TestReport:
    passed: int
    total: int
    feedback: str

    @property
    def ok(self) -> bool:
        return self.total > 0 and self.passed == self.total


def run_unittest(code: str, oracle_tests: str, module_name: str) -> TestReport:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / f"{module_name}.py").write_text(code, encoding="utf-8")
        (root / "test_counter.py").write_text(oracle_tests, encoding="utf-8")
        (root / "_run_tests.py").write_text(_RUNNER, encoding="utf-8")
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        try:
            completed = subprocess.run(
                [sys.executable, "_run_tests.py"],
                cwd=directory,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
                check=False,
                env=env,
            )
        except subprocess.TimeoutExpired as error:
            return TestReport(0, 0, f"timeout: {error}")
        marker = "CLASS_TRANSLATION_RESULT "
        for line in completed.stdout.splitlines():
            if line.startswith(marker):
                payload = json.loads(line[len(marker):])
                return TestReport(
                    passed=int(payload["passed"]),
                    total=int(payload["total"]),
                    feedback=str(payload["feedback"]),
                )
        detail = completed.stderr or completed.stdout or "unittest runner produced no result"
        return TestReport(0, 0, detail[:8000])


_JUNIT_DIR = Path(__file__).resolve().parent / "tools" / "junit"
_JUNIT_JARS = (
    _JUNIT_DIR / "junit-4.13.1.jar",
    _JUNIT_DIR / "hamcrest-core-1.3.jar",
    _JUNIT_DIR / "junit-platform-console-standalone-1.8.1.jar",
)
_JUNIT_CONSOLE = _JUNIT_DIR / "junit-platform-console-standalone-1.8.1.jar"
_PUBLIC_CLASS = re.compile(r"\bpublic\s+(?:final\s+|abstract\s+)?class\s+(\w+)")
_PACKAGE = re.compile(r"(?m)^\s*package\s+([\w.]+)\s*;")


def run_target_tests(
    code: str,
    oracle_tests: str,
    module_name: str,
    target_lang: str,
) -> TestReport:
    if target_lang == "python":
        return run_unittest(code, oracle_tests, module_name)
    if target_lang == "java":
        return run_junit(code, oracle_tests, module_name)
    raise NotImplementedError(f"No test runner for target language {target_lang}")


def run_junit(code: str, oracle_tests: str, module_name: str) -> TestReport:
    missing = [str(path) for path in _JUNIT_JARS if not path.is_file()]
    if missing:
        return TestReport(0, 0, "missing JUnit classpath: " + ", ".join(missing))
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        classes = root / "classes"
        reports = root / "reports"
        classes.mkdir()
        class_file = root / f"{_java_class_name(code, module_name)}.java"
        test_file = root / f"{_java_class_name(oracle_tests, module_name + 'Test')}.java"
        class_file.write_text(code, encoding="utf-8")
        test_file.write_text(oracle_tests, encoding="utf-8")
        classpath = os.pathsep.join(str(path) for path in _JUNIT_JARS)
        try:
            compiled = subprocess.run(
                [
                    "javac",
                    "-encoding",
                    "UTF-8",
                    "-cp",
                    classpath,
                    "-d",
                    str(classes),
                    str(class_file),
                    str(test_file),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            return TestReport(0, 0, f"timeout: {error}")
        except FileNotFoundError as error:
            return TestReport(0, 0, f"javac not found: {error}")
        if compiled.returncode != 0:
            detail = compiled.stderr or compiled.stdout or "javac failed"
            return TestReport(0, 0, detail[:8000])
        test_class = _java_qualified_name(oracle_tests, test_file.stem)
        try:
            completed = subprocess.run(
                [
                    "java",
                    "-jar",
                    str(_JUNIT_CONSOLE),
                    "--disable-banner",
                    "--disable-ansi-colors",
                    "--details=none",
                    "--fail-if-no-tests",
                    "--class-path",
                    str(classes),
                    "--select-class",
                    test_class,
                    "--reports-dir",
                    str(reports),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            return TestReport(0, 0, f"timeout: {error}")
        report = _junit_report(reports)
        if report.total == 0:
            detail = completed.stderr or completed.stdout or report.feedback or "junit runner produced no result"
            return TestReport(0, 0, detail[:8000])
        return report


def _java_class_name(source: str, fallback: str) -> str:
    match = _PUBLIC_CLASS.search(source)
    return match.group(1) if match else fallback


def _java_qualified_name(source: str, class_name: str) -> str:
    match = _PACKAGE.search(source)
    if not match:
        return class_name
    return f"{match.group(1)}.{class_name}"


def _junit_report(directory: Path) -> TestReport:
    passed = 0
    total = 0
    chunks: list[str] = []
    for path in sorted(directory.glob("TEST-*.xml")):
        suite = ET.parse(path).getroot()
        tests = int(suite.attrib.get("tests", "0"))
        failures = int(suite.attrib.get("failures", "0"))
        errors = int(suite.attrib.get("errors", "0"))
        skipped = int(suite.attrib.get("skipped", "0"))
        total += tests
        passed += max(0, tests - failures - errors - skipped)
        for case in suite.findall("testcase"):
            label = f"{case.attrib.get('classname', '')}.{case.attrib.get('name', '')}"
            for tag in ("failure", "error"):
                for node in case.findall(tag):
                    message = node.attrib.get("message", "")
                    body = (node.text or "").strip()
                    chunks.append("\n".join(part for part in (label, message, body) if part))
    return TestReport(passed, total, "\n".join(chunks)[:8000])
