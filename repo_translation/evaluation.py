from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

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
    tests_passed: int | None = None
    tests_total: int | None = None

    @property
    def pass_rate(self) -> float | None:
        if self.tests_total is None or self.tests_total == 0 or self.tests_passed is None:
            return None
        return round(100 * self.tests_passed / self.tests_total, 2)


def parse_test_counts(output: str, exit_code: int) -> tuple[int | None, int | None]:
    # Use only explicit runner summaries; a successful process is not a test count.
    maven = re.findall(r"Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+)(?:,\s*Skipped:\s*(\d+))?", output)
    if maven:
        total, failures, errors = map(int, maven[-1][:3])
        total -= int(maven[-1][3] or 0)
        failed = failures + errors
        return max(0, total - failed), total
    cargo = re.findall(r"test result:\s*(?:ok|FAILED)\.\s*(\d+) passed;\s*(\d+) failed", output)
    if cargo:
        passed = sum(int(item[0]) for item in cargo)
        failed = sum(int(item[1]) for item in cargo)
        return passed, passed + failed
    jest = re.findall(r"Tests:\s*(?:(\d+) failed,?\s*)?(?:(\d+) passed,?\s*)?(\d+) total", output)
    if jest:
        failed, passed, total = jest[-1]
        return int(passed or 0), int(total)
    pytest_summaries = re.findall(r"^=+\s*([^\n]*\b(?:passed|failed|error|errors)\b[^\n]*)\s*=+\s*$", output, re.MULTILINE)
    if pytest_summaries:
        summary = pytest_summaries[-1]
        passed = re.search(r"(\d+) passed", summary)
        failed = re.search(r"(\d+) failed", summary)
        errors = re.search(r"(\d+) errors?", summary)
        skipped = re.search(r"(\d+) skipped", summary)
        values = [int(x.group(1)) if x else 0 for x in (passed, failed, errors, skipped)]
        if any(values):
            return values[0], sum(values[:3])
    unittest = re.search(r"Ran (\d+) tests? in [^\n]+", output)
    if unittest:
        total = int(unittest.group(1))
        if exit_code == 0:
            return total, total
        failures = re.search(r"failures=(\d+)", output)
        errors = re.search(r"errors=(\d+)", output)
        if failures or errors:
            return max(0, total - int(failures.group(1) if failures else 0) - int(errors.group(1) if errors else 0)), total
    return None, None


def run_benchmark_tests(dataset_root: Path, workdir: Path, image: str, timeout: int = 600) -> TestResult:
    root = dataset_root.resolve()
    relative = workdir.resolve().relative_to(root)
    if not (workdir / "run_tests.sh").is_file():
        raise FileNotFoundError(workdir / "run_tests.sh")
    container_dir = "/workspace/" + relative.as_posix()
    try:
        completed = subprocess.run(
            ["docker", "run", "--rm", "--network", "none", "--mount",
             f"type=bind,source={root},target=/workspace", "--workdir", container_dir,
             image, "bash", "run_tests.sh"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired as error:
        return TestResult(False, None, f"Test timeout after {timeout}s: {error}")
    output = (completed.stdout + "\n" + completed.stderr)[-12000:]
    passed, total = parse_test_counts(output, completed.returncode)
    return TestResult(completed.returncode == 0, completed.returncode, output, passed, total)
