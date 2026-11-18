import json
from pathlib import Path

import pytest

from repo_translation.benchmark import load_projects
from repo_translation.evaluation import SmellResult, TestResult as BenchmarkTestResult, run_benchmark_tests
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


def test_repairs_then_rolls_back_failing_smell_refactor(tmp_path, monkeypatch):
    project = dataset(tmp_path)
    def fake_tests(root, workdir, image):
        code = (workdir / "src" / "example.py").read_text(encoding="utf-8")
        return BenchmarkTestResult("correct" in code and "broken" not in code,
                                   0 if "correct" in code and "broken" not in code else 1, "test feedback")
    def fake_smells(workdir, target):
        code = (workdir / "src" / "example.py").read_text(encoding="utf-8")
        return SmellResult(0 if "clean" in code else 2, "unused-variable")
    monkeypatch.setattr("repo_translation.pipeline.run_benchmark_tests", fake_tests)
    monkeypatch.setattr("repo_translation.pipeline.count_repository_smells", fake_smells)
    client = FakeClient("buggy", "correct smelly", "broken clean", "correct clean")
    record = run_project(project, tmp_path, tmp_path / "translated_projects", client, "fake-image",
                         max_corrections=1, max_smell_iterations=2)
    assert record.status == "passed"
    assert record.correction_iterations == 1
    assert record.smell_iterations == 2
    assert (record.smells_after_translation, record.smells_after_correction, record.smells_after_smell_loop) == (2, 2, 0)
    assert (Path(record.workdir) / "src" / "example.py").read_text(encoding="utf-8") == "correct clean"


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
