from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from class_translation.providers import PRESETS, build_client
from repo_translation.benchmark import load_projects
from repo_translation.pipeline import run_project


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate a batch of RepoTransBench repositories")
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--provider", choices=sorted(PRESETS), default="openai")
    parser.add_argument("--docker-image", required=True)
    parser.add_argument("--source", help="Filter source language")
    parser.add_argument("--target", help="Filter target language")
    parser.add_argument("--max-per-pair", type=int, default=1)
    args = parser.parse_args(argv)
    if args.max_per_pair < 1:
        parser.error("--max-per-pair must be positive")
    root = args.dataset_root.resolve()
    projects = [p for p in load_projects(root)
                if (not args.source or p.source_language == args.source)
                and (not args.target or p.target_language == args.target)]
    projects.sort(key=lambda p: (p.source_language, p.target_language, p.name))
    counts: dict[tuple[str, str], int] = {}
    selected = []
    for project in projects:
        pair = (project.source_language, project.target_language)
        if counts.get(pair, 0) < args.max_per_pair:
            selected.append(project)
            counts[pair] = counts.get(pair, 0) + 1
    if not selected:
        raise ValueError("No projects matched the requested languages")
    image = subprocess.run(["docker", "image", "inspect", args.docker_image],
                           capture_output=True, text=True, check=False)
    if image.returncode != 0:
        raise RuntimeError(f"Docker image unavailable: {args.docker_image}\n{image.stderr[-1000:]}")
    client = build_client(args.provider)
    output = root / "translated_projects" / args.provider
    failures = 0
    for index, project in enumerate(selected, 1):
        destination = output / project.source_language / project.target_language / project.name
        result_file = destination.parent / f"{project.name}.result.json"
        if result_file.is_file():
            print(f"{index}/{len(selected)} skip {project.name}: result exists", flush=True)
            continue
        if destination.exists():
            raise FileExistsError(f"Incomplete run at {destination}; move it before resuming")
        print(f"{index}/{len(selected)} {project.name} {project.source_language}->{project.target_language}", flush=True)
        try:
            record = run_project(project, root, output, client, args.docker_image)
            result = record.to_dict()
            if record.status != "passed":
                failures += 1
        except Exception as error:
            failures += 1
            result = {"project_name": project.name, "source_language": project.source_language,
                      "target_language": project.target_language, "status": "error",
                      "error": f"{type(error).__name__}: {error}", "workdir": str(destination)}
        result_file.parent.mkdir(parents=True, exist_ok=True)
        result_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False), flush=True)
    results = []
    for project in selected:
        path = output / project.source_language / project.target_language / f"{project.name}.result.json"
        results.append(json.loads(path.read_text(encoding="utf-8")))
    evaluated = [row for row in results if row.get("status") in {"passed", "failed"}]
    passed = sum(row["status"] == "passed" for row in evaluated)
    counted = [row for row in evaluated if isinstance(row.get("tests_passed"), int)
               and isinstance(row.get("tests_total"), int) and row["tests_total"] > 0]
    tests_passed = sum(row["tests_passed"] for row in counted)
    tests_total = sum(row["tests_total"] for row in counted)
    summary = {
        "selected_projects": len(selected),
        "evaluated_projects": len(evaluated),
        "passed_projects": passed,
        "project_success_rate": round(100 * passed / len(evaluated), 2) if evaluated else None,
        "projects_with_test_counts": len(counted),
        "tests_passed": tests_passed if counted else None,
        "tests_total": tests_total if counted else None,
        "test_pass_rate": round(100 * tests_passed / tests_total, 2) if tests_total else None,
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if failures or any(row.get("status") != "passed" for row in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
