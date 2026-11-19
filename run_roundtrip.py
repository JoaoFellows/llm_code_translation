"""Translate the Java results back to Python and compare them with the oracle."""

import json
import subprocess
import sys
from pathlib import Path

from llm_api import ApiLLM, load_env

BASE = Path(r"C:/llm_code_translation_data/evalplus")
ROOT = Path(r"C:/llm_code_translation")
MODELS = ("api:openai", "api:gemini")
RUNNER = r"""
import json, sys
source = open(sys.argv[1], encoding="utf-8").read()
entry = sys.argv[2]
namespace = {}
exec(source, namespace)
function = namespace.get(entry)
if not callable(function):
    functions = [value for name, value in namespace.items() if callable(value) and not name.startswith("_")]
    function = functions[0] if len(functions) == 1 else None
if function is None:
    raise SystemExit(2)
json.dump(function(*json.load(sys.stdin)), sys.stdout)
"""


def values_match(left, right) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return abs(float(left) - float(right)) <= 1e-5 + 1e-5 * max(abs(float(left)), abs(float(right)))
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(values_match(item, other) for item, other in zip(left, right))
    return left == right


def model_dir(model: str) -> str:
    return model.replace(":", "_")


def translate_back(model: str, java_path: Path, task_id: str) -> str:
    destination = java_path.with_name("reverse.py")
    if destination.is_file() and destination.stat().st_size > 0:
        return destination.read_text(encoding="utf-8")
    sample = type("Sample", (), {})()
    sample.path = str(java_path)
    sample.programming_language = "java"
    sample.dataset = "evalplus"
    sample.submission_id = task_id
    code = ApiLLM(model).translate(sample, "python", "evalplus", task_id, 1)[0]
    destination.write_text(code, encoding="utf-8")
    return code


def run_case(source: Path, entry: str, args) -> tuple[str, object]:
    try:
        completed = subprocess.run(
            [sys.executable, "-c", RUNNER, str(source), entry],
            input=json.dumps(args),
            text=True,
            capture_output=True,
            timeout=3,
        )
    except subprocess.TimeoutExpired:
        return "timeout", None
    if completed.returncode != 0:
        return "error", (completed.stderr or completed.stdout)[-400:]
    try:
        return "ok", json.loads(completed.stdout)
    except json.JSONDecodeError:
        return "error", completed.stdout[-400:]


def pylint_count(source: Path) -> dict:
    completed = subprocess.run(
        ["docker", "run", "--rm", "-v", f"{source.parent}:/work", "-w", "/work", "testing:t6",
         "pylint", "--output-format=json", source.name],
        text=True,
        capture_output=True,
        timeout=60,
    )
    try:
        messages = json.loads(completed.stdout or "[]")
    except json.JSONDecodeError:
        return {"status": "unparsed", "count": None, "items": []}
    items = [{"line": item.get("line"), "symbol": item.get("symbol"), "message": item.get("message")} for item in messages]
    return {"tool": "pylint", "status": "ok", "count": len(items), "items": items}


def main() -> None:
    load_env(ROOT / ".env")
    tasks = sorted(path.stem for path in (BASE / "drivers").glob("HumanEval_*.json"))
    report = []
    blocked = set()
    for task_id in tasks:
        spec = json.loads((BASE / "drivers" / f"{task_id}.json").read_text(encoding="utf-8"))
        inputs = (BASE / "test_cases" / "in" / f"tc_{task_id}.txt").read_text(encoding="utf-8").splitlines()
        outputs = (BASE / "test_cases" / "out" / f"tc_{task_id}.txt").read_text(encoding="utf-8").splitlines()
        cases = list(zip(inputs, outputs))
        for model in MODELS:
            if model in blocked:
                continue
            java_path = BASE / "translations" / task_id / model_dir(model) / "0" / f"0__default__{task_id}.java"
            entry = {"model": model, "problem_id": task_id, "entry_point": spec["entry_point"], "java_present": java_path.is_file()}
            if not java_path.is_file():
                entry["status"] = "missing_java"
                report.append(entry)
                continue
            try:
                code = translate_back(model, java_path, task_id)
            except Exception as exc:
                entry["status"] = "translation_error"
                entry["error"] = str(exc)[:400]
                report.append(entry)
                print(f"{model} {task_id} translation failed", flush=True)
                if "429" in str(exc):
                    blocked.add(model)
                    print(f"{model} paused after rate limit", flush=True)
                continue
            reverse = java_path.with_name("reverse.py")
            if code.startswith("MAX ATTEMPT"):
                reverse.unlink(missing_ok=True)
                entry["status"] = "rate_limited"
                report.append(entry)
                blocked.add(model)
                print(f"{model} paused after rate limit", flush=True)
                continue
            passed = 0
            details = []
            for index, (raw, expected_raw) in enumerate(cases):
                status, got = run_case(reverse, spec["entry_point"], json.loads(raw))
                expected = json.loads(expected_raw)
                ok = status == "ok" and values_match(got, expected)
                if ok:
                    passed += 1
                else:
                    details.append({"id": f"tc_{index}", "status": status, "got": got if status == "ok" else None})
                    break
            entry.update({
                "status": "tested",
                "tests_expected": len(cases),
                "tests_passed": passed,
                "pass_rate": passed / len(cases) if cases else None,
                "early_exit": passed < len(cases),
                "first_failure": details[0] if details else None,
                "code_smells": pylint_count(reverse),
                "reverse_path": str(reverse),
            })
            report.append(entry)
            print(f"{model} {task_id} {passed}/{len(cases)}", flush=True)
    destination = ROOT / "results" / "roundtrip_python_java.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(destination)


if __name__ == "__main__":
    main()
