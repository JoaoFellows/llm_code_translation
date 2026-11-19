from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

from class_translation.providers import PRESETS, build_client
from class_translation.smells import pmd_executable
from repo_translation.benchmark import load_projects
from repo_translation.evaluation import code_files
from repo_translation.pipeline import run_project


def _source_file_count(project) -> int:
    try:
        return len(code_files(project.source_dir, project.source_language, exclude_tests=True))
    except Exception:
        return 9999


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate a batch of RepoTransBench repositories")
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--provider", choices=sorted(PRESETS), default="openai")
    parser.add_argument("--docker-image", required=True)
    parser.add_argument("--source", help="Filter source language")
    parser.add_argument("--target", help="Filter target language")
    parser.add_argument("--max-per-pair", type=int, default=1)
    parser.add_argument("--max-corrections", type=int, default=3)
    parser.add_argument("--max-smell-iterations", type=int, default=3)
    parser.add_argument("--force", action="store_true", help="Force rerun even if result already exists")
    parser.add_argument("--sort-by-size", action="store_true", help="Sort projects by number of source files (smallest first)")
    parser.add_argument("--max-source-files", type=int, default=0, help="Skip projects with more than N source files (0 = no limit)")
    args = parser.parse_args(argv)
    if args.max_per_pair < 1:
        parser.error("--max-per-pair must be positive")
    root = args.dataset_root.resolve()
    projects = [p for p in load_projects(root)
                if (not args.source or p.source_language == args.source)
                and (not args.target or p.target_language == args.target)]
    if args.sort_by_size:
        projects.sort(key=lambda p: (_source_file_count(p), p.source_language, p.target_language, p.name))
    else:
        projects.sort(key=lambda p: (p.source_language, p.target_language, p.name))
    counts: dict[tuple[str, str], int] = {}
    selected = []
    for project in projects:
        pair = (project.source_language, project.target_language)
        n_src = _source_file_count(project)
        if n_src == 0:
            continue
        if args.max_source_files > 0 and n_src > args.max_source_files:
            continue
        if counts.get(pair, 0) < args.max_per_pair:
            selected.append(project)
            counts[pair] = counts.get(pair, 0) + 1
    if not selected:
        raise ValueError("No projects matched the requested languages")
    image = subprocess.run(["docker", "image", "inspect", args.docker_image],
                           capture_output=True, text=True, check=False)
    if image.returncode != 0:
        raise RuntimeError(f"Docker image unavailable: {args.docker_image}\n{image.stderr[-1000:]}")
    if any(p.target_language == "Java" for p in selected) and pmd_executable() is None:
        print("[AVISO] PMD 7.1.0 não encontrado no host. A contagem de smells será desativada para alvos Java.", flush=True)
    client = build_client(args.provider)
    output = root / "translated_projects" / args.provider
    failures = 0
    for index, project in enumerate(selected, 1):
        destination = output / project.source_language / project.target_language / project.name
        result_file = destination.parent / f"{project.name}.result.json"
        if result_file.is_file() and not args.force:
            try:
                existing_data = json.loads(result_file.read_text(encoding="utf-8"))
                if existing_data.get("status") in {"passed", "failed"}:
                    print(f"{index}/{len(selected)} skip {project.name}: result exists ({existing_data.get('status')})", flush=True)
                    continue
                else:
                    print(f"{index}/{len(selected)} re-running {project.name}: previous status was '{existing_data.get('status')}'", flush=True)
            except Exception:
                pass
        if destination.exists():
            shutil.rmtree(destination, ignore_errors=True)
        print(f"{index}/{len(selected)} {project.name} {project.source_language}->{project.target_language}", flush=True)
        try:
            record = run_project(project, root, output, client, args.docker_image,
                                 args.max_corrections, args.max_smell_iterations)
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
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
