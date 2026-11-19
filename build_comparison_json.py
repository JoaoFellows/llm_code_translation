import json
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(r"C:/llm_code_translation_data")
TESTS = Path(r"C:/llm_code_translation/tco_llm.csv")
EXPECTED = {"HumanEval_0": 7, "HumanEval_1": 4}
MODELS = {
    "api:openai": {"provider": "openai", "model": "gpt-4o-mini"},
    "api:gemini": {"provider": "gemini", "model": "gemini-3.5-flash-lite"},
}
FIRST_COMPILE = {
    ("api:openai", "HumanEval_0"): {
        "compiled": False,
        "recompiled": True,
        "reason": "The generated method takes double[] and double. The first test driver passed List<Double>, so javac reported a compilation failure. The driver was aligned to the declared signature and the same source was compiled again. The model was not called again.",
        "compiler_message": "method hasCloseElements in class CloseElementsChecker cannot be applied to given types; required: double[],double; found: List<Double>,double",
    }
}


def outcome_name(value: str) -> str:
    text = str(value)
    if "." in text:
        return text.split(".")[-1]
    return text


def smell_details(raw: str, language: str) -> dict:
    if raw in ("", "PARSE_ERROR") or raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return {"status": "unavailable", "count": None, "items": []}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {"status": "unparsed", "count": None, "items": [str(raw)[:500]]}
    if language == "python" and isinstance(parsed, list):
        items = [
            {
                "line": item.get("line"),
                "symbol": item.get("symbol"),
                "message": item.get("message"),
                "type": item.get("type"),
            }
            for item in parsed
        ]
        return {"tool": "pylint", "status": "ok", "count": len(items), "items": items}
    files = parsed.get("files", []) if isinstance(parsed, dict) else []
    violations = []
    for file_entry in files:
        for violation in file_entry.get("violations", []):
            violations.append(
                {
                    "rule": violation.get("rule"),
                    "ruleset": violation.get("ruleset"),
                    "begin_line": violation.get("beginline"),
                    "end_line": violation.get("endline"),
                    "message": violation.get("description"),
                    "priority": violation.get("priority"),
                }
            )
    return {"tool": "pmd", "status": "ok", "count": len(violations), "items": violations}


def load_smells(path: Path) -> dict:
    frame = pd.read_csv(path, sep="@", quotechar="'")
    smells = {}
    for _, row in frame.iterrows():
        sample_path = str(row["path"]).replace("\\", "/")
        language = "python" if sample_path.endswith(".py") else "java"
        smells[sample_path] = smell_details(row["code_smell_result"], language)
    return smells


def main() -> None:
    tests = pd.read_csv(TESTS)
    source_smells = load_smells(ROOT / "data_code_smell_results.csv")
    translation_smells = load_smells(ROOT / "llm_code_smell_results_29076.csv")
    grouped = defaultdict(list)
    for _, row in tests.iterrows():
        grouped[(row["Llm"], row["Problem ID"])].append(row)

    by_model = {}
    tasks = []
    for model, meta in MODELS.items():
        passed = failed = compiler_errors = exceptions = 0
        task_reports = []
        for problem, expected in EXPECTED.items():
            rows = grouped.get((model, problem), [])
            cases = []
            for row in rows:
                name = outcome_name(row["Outcome"])
                if name == "PASSED":
                    passed += 1
                elif name == "COMPILER_ERROR":
                    compiler_errors += 1
                elif name == "EXCEPTION":
                    exceptions += 1
                else:
                    failed += 1
                cases.append(
                    {
                        "id": row["Testcase_id"],
                        "outcome": name,
                        "error": None if pd.isna(row["Error"]) else row["Error"],
                        "stacktrace": None if pd.isna(row["Stacktrace"]) else row["Stacktrace"],
                    }
                )
            recorded = len(cases)
            compile_info = FIRST_COMPILE.get(
                (model, problem),
                {
                    "compiled": True,
                    "recompiled": False,
                    "reason": "The Java source compiled on the test execution. There was no second compilation and no new model call.",
                    "compiler_message": None,
                },
            )
            sample_path = str(rows[0]["Path"]).replace("\\", "/") if rows else ""
            smell = translation_smells.get(sample_path, {"status": "missing", "count": None, "items": []})
            task_reports.append(
                {
                    "problem_id": problem,
                    "entry_point": "has_close_elements" if problem == "HumanEval_0" else "separate_paren_groups",
                    "tests_expected": expected,
                    "tests_recorded": recorded,
                    "tests_passed": sum(1 for case in cases if case["outcome"] == "PASSED"),
                    "pass_rate": (sum(1 for case in cases if case["outcome"] == "PASSED") / expected) if expected else None,
                    "early_exit_on_failure": recorded < expected,
                    "compilation": compile_info,
                    "model_called_again": False,
                    "repair_iterations": 0,
                    "code_smells": smell,
                    "cases": cases,
                    "translation_path": sample_path,
                }
            )
        total = sum(EXPECTED.values())
        by_model[model] = {
            **meta,
            "tests_expected": total,
            "tests_passed": passed,
            "tests_failed": failed,
            "compiler_errors_in_final_run": compiler_errors,
            "exceptions": exceptions,
            "pass_rate": passed / total if total else None,
            "translations_regenerated": model == "api:openai",
            "tasks": task_reports,
        }
        tasks.extend({"model": model, **task} for task in task_reports)

    source = []
    for path, smell in source_smells.items():
        problem = "HumanEval_0" if "HumanEval_0" in path else "HumanEval_1" if "HumanEval_1" in path else path
        source.append({"problem_id": problem, "language": "python", "path": path, "code_smells": smell})

    report = {
        "scope": {
            "dataset": "evalplus",
            "slice": "first two HumanEval+ tasks, base_input cases only",
            "source_language": "python",
            "target_language": "java",
            "prompt_id": "p1",
            "translations_per_task": 1,
            "iterative_repair": False,
            "backtranslation": False,
            "docker_image": "testing:t6",
            "test_runner": "java Main.java inside Docker, with an EvalPlus driver that calls the translated method",
            "smell_tools": {"python": "pylint 3.3.1", "java": "PMD 7.1.0 rulesets/java/quickstart.xml"},
        },
        "rates": {
            model: {
                "pass_rate": details["pass_rate"],
                "tests_passed": details["tests_passed"],
                "tests_expected": details["tests_expected"],
                "compiler_errors_in_final_run": details["compiler_errors_in_final_run"],
            }
            for model, details in by_model.items()
        },
        "models": by_model,
        "source_python": source,
    }
    destination = Path(r"C:/llm_code_translation/results/gemini_gpt_evalplus.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(destination)
    print(json.dumps(report["rates"], indent=2))
    for item in source:
        print("source", item["problem_id"], item["code_smells"].get("status"), item["code_smells"].get("count"))
    for model, details in by_model.items():
        for task in details["tasks"]:
            print(model, task["problem_id"], "smells", task["code_smells"].get("status"), task["code_smells"].get("count"))


if __name__ == "__main__":
    main()
