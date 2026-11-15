from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
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
