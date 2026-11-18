import json
from pathlib import Path

import pytest

from repo_translation.benchmark import load_projects
from repo_translation.evaluation import TestResult as BenchmarkTestResult, parse_test_counts, run_benchmark_tests
from repo_translation.pipeline import _parse_edits, run_project


class FakeClient:
    def __init__(self, *outputs):
        self.outputs = iter(outputs)

    def complete(self, messages):
        return json.dumps({"files": [{"path": "src/example.py", "content": next(self.outputs)}]})


def dataset(tmp_path: Path):
    source = tmp_path / "source_projects" / "Java" / "example"
    target = tmp_path / "target_projects" / "Java" / "Python" / "example"
    source.mkdir(parents=True)
    target.mkdir(parents=True)
    (source / "Example.java").write_text("class Example {}", encoding="utf-8")
    (target / "run_tests.sh").write_text("pytest", encoding="utf-8")
    (target / "public_tests").mkdir()
    (target / "public_tests" / "test_example.py").write_text("assert True", encoding="utf-8")
    (tmp_path / "target_projects" / "projects_summary.jsonl").write_text(
        json.dumps({"project_name": "example", "source_language": "Java", "target_language": "Python"}) + "\n",
        encoding="utf-8",
    )
    return load_projects(tmp_path)[0]


def test_loads_benchmark_and_rejects_test_edits(tmp_path):
    project = dataset(tmp_path)
    assert project.name == "example"
    with pytest.raises(ValueError, match="test"):
        _parse_edits(json.dumps({"files": [{"path": "public_tests/test_example.py", "content": "pass"}]}),
                     tmp_path, "Python")
    with pytest.raises(ValueError, match="Invalid generated path"):
        _parse_edits(json.dumps({"files": [{"path": "../escape.py", "content": "pass"}]}),
                     tmp_path, "Python")


@pytest.mark.parametrize("code,expected_status", [("correct", "passed"), ("buggy", "failed")])
def test_translates_once_and_runs_tests_once(tmp_path, monkeypatch, code, expected_status):
    project = dataset(tmp_path)
    calls = []
    def fake_tests(root, workdir, image):
        calls.append(workdir)
        translated = (workdir / "src" / "example.py").read_text(encoding="utf-8")
        ok = translated == "correct"
        return BenchmarkTestResult(ok, 0 if ok else 1, "test feedback", 2 if ok else 1, 2)
    monkeypatch.setattr("repo_translation.pipeline.run_benchmark_tests", fake_tests)
    client = FakeClient(code)
    record = run_project(project, tmp_path, tmp_path / "translated_projects", client, "fake-image")
    assert record.status == expected_status
    assert len(calls) == 1
    assert record.test_pass_rate == (100.0 if code == "correct" else 50.0)
    assert (Path(record.workdir) / "src" / "example.py").read_text(encoding="utf-8") == code


def test_runs_benchmark_script_in_project_container(tmp_path, monkeypatch):
    project = dataset(tmp_path)
    workdir = tmp_path / "translated_projects" / "Java" / "Python" / "example"
    workdir.mkdir(parents=True)
    (workdir / "run_tests.sh").write_text("exit 0", encoding="utf-8")
    calls = []
    class Completed:
        returncode = 0
        stdout = "2 passed"
        stderr = ""
    def fake_run(args, **kwargs):
        calls.append(args)
        return Completed()
    monkeypatch.setattr("repo_translation.evaluation.subprocess.run", fake_run)
    result = run_benchmark_tests(tmp_path, workdir, "benchmark-image")
    assert result.passed
    assert calls[0][-3:] == ["benchmark-image", "bash", "run_tests.sh"]
    assert "/workspace/translated_projects/Java/Python/example" in calls[0]


@pytest.mark.parametrize("output,exit_code,expected", [
    ("=== 2 passed, 1 failed in 0.4s ===", 1, (2, 3)),
    ("=== 2 passed, 1 skipped in 0.4s ===", 0, (2, 2)),
    ("Tests run: 4, Failures: 1, Errors: 0, Skipped: 0", 1, (3, 4)),
    ("Tests run: 4, Failures: 0, Errors: 0, Skipped: 1", 0, (3, 3)),
    ("test result: ok. 3 passed; 0 failed; 0 ignored", 0, (3, 3)),
    ("unknown runner output", 0, (None, None)),
])
def test_parse_only_explicit_counts(output, exit_code, expected):
    assert parse_test_counts(output, exit_code) == expected
