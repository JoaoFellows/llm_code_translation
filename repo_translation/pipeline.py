from __future__ import annotations

import json
import re
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path

from class_translation.providers import ChatClient
from repo_translation.benchmark import Project
from repo_translation.evaluation import EXTENSIONS, code_files, count_repository_smells, run_benchmark_tests


_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)
_BLOCKED_PARTS = {"public_tests", "original_tests", "tests", "test", ".git"}
_CONFIG_FILES = {"pyproject.toml", "requirements.txt", "pom.xml", "build.gradle", "build.gradle.kts",
                 "settings.gradle", "settings.gradle.kts", "package.json", "cargo.toml", "go.mod",
                 "cmakelists.txt", "makefile"}


def _safe_path(workdir: Path, value: str, target_language: str) -> Path:
    path = Path(value.replace("\\", "/"))
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"Invalid generated path: {value}")
    if any(part.lower() in _BLOCKED_PARTS for part in path.parts[:-1]):
        raise ValueError(f"Model may not edit benchmark tests: {value}")
    if path.name.lower().startswith("test_") or path.name.lower().endswith("_test" + path.suffix.lower()):
        raise ValueError(f"Model may not edit test files: {value}")
    if path.suffix.lower() not in EXTENSIONS[target_language] and path.name.lower() not in _CONFIG_FILES and path.suffix.lower() != ".csproj":
        all_code_exts = {ext for exts in EXTENSIONS.values() for ext in exts}
        if path.suffix.lower() in all_code_exts:
            path = path.with_suffix(EXTENSIONS[target_language][0])
        else:
            raise ValueError(f"Expected {target_language} source or build config file: {value}")
    resolved = (workdir / path).resolve()
    if not resolved.is_relative_to(workdir.resolve()):
        raise ValueError(f"Path leaves project: {value}")
    return resolved


def _parse_edits(response: str, workdir: Path, target_language: str, *, allow_empty: bool = False) -> dict[Path, str]:
    text = response.strip()
    if not text:
        if allow_empty:
            return {}
        raise ValueError("Model returned empty response")
    raw = _FENCE.sub("", text).strip()
    payload = None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        # Locate outer JSON object or array if wrapped in markdown or commentary
        candidates = []
        obj_s, obj_e = raw.find("{"), raw.rfind("}")
        arr_s, arr_e = raw.find("["), raw.rfind("]")
        if arr_s != -1 and arr_e > arr_s and (obj_s == -1 or arr_s < obj_s):
            candidates.append(raw[arr_s:arr_e + 1])
        if obj_s != -1 and obj_e > obj_s:
            candidates.append(raw[obj_s:obj_e + 1])
        if arr_s != -1 and arr_e > arr_s and raw[arr_s:arr_e + 1] not in candidates:
            candidates.append(raw[arr_s:arr_e + 1])
        last_exc: Exception | None = None
        for cand in candidates:
            try:
                payload = json.loads(cand)
                break
            except Exception as exc:
                last_exc = exc
        if payload is None:
            print(f"[DEBUG PARSE ERROR] response length={len(response)}, repr={response[:300]!r} ... {response[-300:]!r}", flush=True)
            raise last_exc or ValueError("Could not parse JSON from model response")
    if isinstance(payload, list):
        payload = {"files": payload}
    if not isinstance(payload, dict) or not isinstance(payload.get("files"), list):
        raise ValueError('Model must return {"files": [{"path": "...", "content": "..."}]}')
    if not payload["files"]:
        if allow_empty:
            return {}
        raise ValueError('Model must return {"files": [{"path": "...", "content": "..."}]}')
    edits = {}
    first_error: ValueError | None = None
    for item in payload["files"]:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str) or not isinstance(item.get("content"), str):
            if first_error is None:
                first_error = ValueError("Invalid file edit")
            continue
        try:
            path = _safe_path(workdir, item["path"], target_language)
        except ValueError as err:
            if first_error is None:
                first_error = err
            continue
        edits[path] = item["content"]
    if not edits:
        if allow_empty:
            return {}
        raise first_error or ValueError('Model must return {"files": [{"path": "...", "content": "..."}]}')
    return edits


def _apply(edits: dict[Path, str]) -> None:
    for path, content in edits.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _restore(before: dict[Path, str | None], edits: dict[Path, str]) -> None:
    for path in edits:
        old = before[path]
        if old is None:
            path.unlink()
        else:
            path.write_text(old, encoding="utf-8")


def _files_context(root: Path, language: str, limit: int = 30000) -> str:
    blocks = []
    size = 0
    for path in code_files(root, language, exclude_tests=True):
        content = path.read_text(encoding="utf-8", errors="replace")
        block = f"\nFILE {path.relative_to(root).as_posix()}\n{content[:10000]}\n"
        if size + len(block) > limit:
            break
        blocks.append(block)
        size += len(block)
    return "".join(blocks)


def _config_context(root: Path, limit: int = 8000) -> str:
    blocks = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name.lower() not in _CONFIG_FILES and path.suffix.lower() != ".csproj":
            continue
        if any(part.lower() in _BLOCKED_PARTS for part in path.relative_to(root).parts[:-1]):
            continue
        blocks.append(f"\nFILE {path.relative_to(root).as_posix()}\n{path.read_text(encoding='utf-8', errors='replace')[:4000]}")
        if sum(map(len, blocks)) >= limit:
            break
    return "".join(blocks)[:limit]


def _complete_json(client: ChatClient, messages: list[dict[str, str]]) -> str:
    try:
        return client.complete(messages, json_mode=True)  # type: ignore[call-arg]
    except TypeError:
        return client.complete(messages)


def _ask(client: ChatClient, instruction: str, workdir: Path, target_language: str, *, allow_empty: bool = False) -> dict[Path, str]:
    target_ext = EXTENSIONS[target_language][0]
    java_hint = (
        " For Java Maven projects, include a valid pom.xml using Java 11, "
        "maven-compiler-plugin:3.11.0, maven-surefire-plugin:3.2.5, and any needed pre-cached dependencies: "
        "org.junit.jupiter:junit-jupiter:5.9.3, junit:junit:4.13.2, org.mockito:mockito-core:5.5.0, "
        "org.mockito:mockito-junit-jupiter:5.5.0, com.google.code.gson:gson:2.10.1, "
        "com.fasterxml.jackson.core:jackson-databind:2.15.2."
        if target_language == "Java" else ""
    )
    messages = [
        {"role": "system", "content": f"Translate repository code to {target_language}. Reply only with a valid JSON object: "
         '{"files":[{"path":"relative/path' + target_ext + '","content":"complete file"}]}. '
         f"Write complete {target_language} source files (MUST end with {target_ext}) or build configs (e.g., pom.xml, requirements.txt). "
         f"Follow the target paths shown in project_structure.txt if provided.{java_hint} "
         "NEVER include test files, tests/, public_tests/, original_tests/, run_tests.sh, or .txt files in your JSON."},
        {"role": "user", "content": instruction},
    ]
    response = _complete_json(client, messages)
    try:
        return _parse_edits(response, workdir, target_language, allow_empty=allow_empty)
    except json.JSONDecodeError:
        retry_messages = [
            *messages,
            {"role": "user", "content": "Your previous response was not valid JSON (likely an unescaped quote or backslash). "
             'Return ONLY a strictly valid JSON object {"files":[{"path":"...","content":"..."}]} with properly escaped strings.'},
        ]
        return _parse_edits(_complete_json(client, retry_messages), workdir, target_language, allow_empty=allow_empty)


@dataclass(frozen=True)
class RepositoryRecord:
    project_name: str
    source_language: str
    target_language: str
    status: str
    test_exit_code: int | None
    correction_iterations: int
    smell_iterations: int
    smells_after_translation: int | None
    smells_after_correction: int | None
    smells_after_smell_loop: int | None
    test_feedback: str
    workdir: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def run_project(project: Project, dataset_root: Path, output_root: Path, client: ChatClient,
                docker_image: str, max_corrections: int = 3, max_smell_iterations: int = 3) -> RepositoryRecord:
    if max_corrections < 0 or max_smell_iterations < 0:
        raise ValueError("Iteration limits must be nonnegative")
    root = dataset_root.resolve()
    workdir = (output_root / project.source_language / project.target_language / project.name).resolve()
    workdir.relative_to(root)  # Docker mounts the whole benchmark workspace.
    if workdir.exists():
        shutil.rmtree(workdir, ignore_errors=True)
    sources = code_files(project.source_dir, project.source_language, exclude_tests=True)
    if not sources:
        raise ValueError(f"No {project.source_language} source files in {project.source_dir}")
    shutil.copytree(project.target_dir, workdir)
    scaffold = "\n".join(p.relative_to(workdir).as_posix() for p in sorted(workdir.rglob("*")) if p.is_file())[:8000]
    structure_file = workdir / "project_structure.txt"
    structure_text = structure_file.read_text(encoding="utf-8", errors="replace")[:4000] if structure_file.is_file() else ""
    signatures = []
    for source in sources:
        relative = source.relative_to(project.source_dir).as_posix()
        content = source.read_text(encoding="utf-8", errors="replace")
        prompt = (f"Translate {project.source_language} to {project.target_language} for repository {project.name}.\n"
                  f"Target scaffold files:\n{scaffold}\n"
                  f"{'Target project_structure.txt:' + chr(10) + structure_text + chr(10) if structure_text else ''}"
                  f"Target build configs:\n{_config_context(workdir)}\n"
                  f"Prior translated files:\n{_files_context(workdir, project.target_language, 10000)}\n"
                  f"Source inventory:\n{chr(10).join(p.relative_to(project.source_dir).as_posix() for p in sources)[:8000]}\n"
                  f"Translate this source file, preserving cross-file imports and APIs: {relative}\n{content}\n"
                  f"Previously translated public signatures/context:\n{''.join(signatures)[-6000:]}")
        edits = _ask(client, prompt, workdir, project.target_language)
        _apply(edits)
        signatures.append("\n".join(path.relative_to(workdir).as_posix() for path in edits))

    initial_smells = count_repository_smells(workdir, project.target_language)
    tests = run_benchmark_tests(root, workdir, docker_image)
    correction_iterations = 0
    while not tests.passed and correction_iterations < max_corrections:
        prompt = (f"Repair the translated {project.target_language} repository {project.name}.\n"
                  f"{'Target project_structure.txt:' + chr(10) + structure_text + chr(10) if structure_text else ''}"
                  f"Source files:\n{_files_context(project.source_dir, project.source_language, 10000)}\n"
                  f"Target files:\n{_files_context(workdir, project.target_language)}\n"
                  f"Target build configs:\n{_config_context(workdir)}\n"
                  f"Test command: bash run_tests.sh\nExit code: {tests.exit_code}\nFeedback:\n{tests.output[-8000:]}\n"
                  "Return only the complete files that need to change.")
        try:
            edits = _ask(client, prompt, workdir, project.target_language, allow_empty=True)
        except (ValueError, json.JSONDecodeError):
            break
        if not edits:
            break
        _apply(edits)
        correction_iterations += 1
        tests = run_benchmark_tests(root, workdir, docker_image)

    corrected_smells = count_repository_smells(workdir, project.target_language)
    current_smells = corrected_smells
    smell_iterations = 0
    while tests.passed and current_smells is not None and current_smells.count > 0 and smell_iterations < max_smell_iterations:
        prompt = (f"Reduce {project.target_language} code smells in repository {project.name} without changing behavior.\n"
                  f"Target files:\n{_files_context(workdir, project.target_language)}\n"
                  f"Current smell count: {current_smells.count}\nLinter feedback:\n{current_smells.feedback}\n"
                  "Return only complete changed files. The benchmark tests must still pass.")
        try:
            edits = _ask(client, prompt, workdir, project.target_language, allow_empty=True)
        except (ValueError, json.JSONDecodeError):
            break
        if not edits:
            break
        before = {path: path.read_text(encoding="utf-8") if path.exists() else None for path in edits}
        _apply(edits)
        candidate_tests = run_benchmark_tests(root, workdir, docker_image)
        candidate_smells = count_repository_smells(workdir, project.target_language)
        smell_iterations += 1
        if candidate_tests.passed and candidate_smells is not None and candidate_smells.count < current_smells.count:
            tests, current_smells = candidate_tests, candidate_smells
        else:
            _restore(before, edits)

    return RepositoryRecord(
        project.name, project.source_language, project.target_language,
        "passed" if tests.passed else "failed", tests.exit_code,
        correction_iterations, smell_iterations,
        initial_smells.count if initial_smells else None,
        corrected_smells.count if corrected_smells else None,
        current_smells.count if current_smells else None,
        tests.output[-4000:], str(workdir),
    )
