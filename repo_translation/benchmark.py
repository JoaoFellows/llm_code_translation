from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


_NAME = re.compile(r"^[A-Za-z0-9_.+-]+$")


@dataclass(frozen=True)
class Project:
    name: str
    source_language: str
    target_language: str
    source_dir: Path
    target_dir: Path


def load_projects(dataset_root: Path) -> list[Project]:
    root = dataset_root.resolve()
    index = root / "target_projects" / "projects_summary.jsonl"
    if not index.is_file():
        raise FileNotFoundError(f"RepoTransBench index not found: {index}")
    projects = []
    for number, line in enumerate(index.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        values = [row[key] for key in ("project_name", "source_language", "target_language")]
        if not all(isinstance(value, str) and _NAME.fullmatch(value) for value in values):
            raise ValueError(f"Invalid project metadata on line {number}")
        name, source, target = values
        source_dir = root / "source_projects" / source / name
        target_dir = root / "target_projects" / source / target / name
        if not source_dir.is_dir() or not target_dir.is_dir():
            raise FileNotFoundError(f"Missing source or target project on line {number}: {name}")
        if not (target_dir / "run_tests.sh").is_file():
            raise FileNotFoundError(f"Missing run_tests.sh for {name}")
        projects.append(Project(name, source, target, source_dir, target_dir))
    return projects


def select_project(projects: list[Project], name: str, source: str, target: str) -> Project:
    matches = [p for p in projects if (p.name, p.source_language, p.target_language) == (name, source, target)]
    if len(matches) != 1:
        raise ValueError(f"Expected one project for {name} ({source} -> {target}); found {len(matches)}")
    return matches[0]
