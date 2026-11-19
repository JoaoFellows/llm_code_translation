from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from class_translation.providers import PRESETS, build_client
from class_translation.smells import pmd_executable
from repo_translation.benchmark import load_projects, select_project
from repo_translation.pipeline import run_project


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Translate and evaluate RepoTransBench repositories")
    parser.add_argument("--dataset-root", type=Path, required=True,
                        help="Directory containing source_projects and target_projects")
    parser.add_argument("--project", required=True, help="project_name in projects_summary.jsonl")
    parser.add_argument("--source", required=True, help="Source language label, for example Java")
    parser.add_argument("--target", required=True, help="Target language label, for example Python")
    parser.add_argument("--provider", choices=sorted(PRESETS), default="openai")
    parser.add_argument("--docker-image", required=True, help="Image with benchmark test dependencies")
    parser.add_argument("--output-root", type=Path, help="Must be inside dataset-root; default translated_projects/<provider>")
    parser.add_argument("--max-corrections", type=int, default=3)
    parser.add_argument("--max-smell-iterations", type=int, default=3)
    args = parser.parse_args(argv)

    root = args.dataset_root.resolve()
    project = select_project(load_projects(root), args.project, args.source, args.target)
    provider_name = re.sub(r"[^A-Za-z0-9_.-]", "_", args.provider)
    output = (args.output_root or root / "translated_projects" / provider_name).resolve()
    output.relative_to(root)
    if output == root or output.is_relative_to(root / "source_projects") or output.is_relative_to(root / "target_projects"):
        raise ValueError("Output must be separate from source_projects and target_projects")
    image = subprocess.run(["docker", "image", "inspect", args.docker_image],
                           capture_output=True, text=True, check=False)
    if image.returncode != 0:
        raise RuntimeError(f"Docker image unavailable: {args.docker_image}\n{image.stderr[-1000:]}")
    if args.target == "Java" and pmd_executable() is None:
        print("[AVISO] PMD 7.1.0 não encontrado no host. A contagem de smells será desativada para alvos Java.", file=sys.stderr)
    client = build_client(args.provider)
    record = run_project(project, root, output, client, args.docker_image,
                         args.max_corrections, args.max_smell_iterations)
    result_path = Path(record.workdir).parent / f"{project.name}.result.json"
    result_path.write_text(json.dumps(record.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(record.to_dict(), ensure_ascii=False, indent=2))
    print(f"Result: {result_path}", file=sys.stderr)
    return 0 if record.status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
