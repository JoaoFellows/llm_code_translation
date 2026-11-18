from __future__ import annotations

from pathlib import Path

from class_translation.state import ClassTask

_JAVA_SOLUTION_DIR = "solutuon"
_JAVA_TO_PYTHON = "java_to_python"
_PYTHON_TO_JAVA = "python_to_java"


def load_classeval_task(
    root: Path,
    task_id: str,
    direction: str = _JAVA_TO_PYTHON,
) -> ClassTask:
    benchmark = root / "ClassEval_T"
    if direction == _JAVA_TO_PYTHON:
        source = _read(benchmark / "java" / _JAVA_SOLUTION_DIR / f"{task_id}.java")
        tests = _read(benchmark / "java" / "test" / f"{task_id}Test.java")
        oracle = _ensure_python_import(
            _read(benchmark / "py" / "test" / f"{task_id}.py"),
            task_id,
        )
        source_lang, target_lang = "java", "python"
    elif direction == _PYTHON_TO_JAVA:
        source = _implemented_python(
            _read(benchmark / "py" / "solution" / f"{task_id}.py")
        )
        tests = _read(benchmark / "py" / "test" / f"{task_id}.py")
        oracle = _read(benchmark / "java" / "test" / f"{task_id}Test.java")
        source_lang, target_lang = "python", "java"
    else:
        raise NotImplementedError(f"ClassEval direction {direction} is not implemented")
    return ClassTask(
        task_id=task_id,
        source_lang=source_lang,
        target_lang=target_lang,
        module_name=task_id,
        source_code=source,
        source_tests=tests,
        oracle_tests=oracle,
    )


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _ensure_python_import(oracle: str, task_id: str) -> str:
    import_line = f"from {task_id} import {task_id}"
    if import_line in oracle:
        return oracle
    return import_line + "\n" + oracle


def _implemented_python(text: str) -> str:
    stripped = text.lstrip()
    if stripped.startswith("'''") or stripped.startswith('"""'):
        quote = stripped[:3]
        end = stripped.find(quote, 3)
        if end != -1:
            body = stripped[end + 3 :].strip()
            if body:
                return body if body.endswith("\n") else body + "\n"
    return text if text.endswith("\n") else text + "\n"
