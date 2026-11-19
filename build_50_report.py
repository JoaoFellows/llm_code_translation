import json
from pathlib import Path

import pandas as pd

from build_comparison_json import smell_details

BASE = Path(r"C:/llm_code_translation_data/evalplus")
ROOT = Path(r"C:/llm_code_translation")
TESTS = ROOT / "tcos" / "llm" / "tco_2348.csv"
JAVA_SMELLS = BASE.parent / "llm_code_smell_results_2348.csv"
SOURCE_SMELLS = BASE.parent / "data_code_smell_results_2348.csv"
ROUNDTRIP = ROOT / "results" / "roundtrip_python_java.json"
MODELS = {
    "api:openai": "gpt-4o-mini",
    "api:gemini": "gemini-3.5-flash-lite",
}


def expected_counts() -> dict[str, int]:
    counts = {}
    for path in (BASE / "test_cases" / "out").glob("tc_HumanEval_*.txt"):
        task = path.stem.removeprefix("tc_")
        counts[task] = len([line for line in path.read_text(encoding="utf-8").splitlines() if line != ""])
    return counts


def outcome_name(value: str) -> str:
    text = str(value)
    return text.split(".")[-1] if "." in text else text


def load_smell_map(path: Path) -> dict:
    if not path.is_file():
        return {}
    frame = pd.read_csv(path, sep="@", quotechar="'")
    smells = {}
    for _, row in frame.iterrows():
        sample = str(row["path"]).replace("\\", "/")
        language = "python" if sample.endswith(".py") else "java"
        smells[sample] = smell_details(row["code_smell_result"], language)
    return smells


def main() -> None:
    expected = expected_counts()
    tests = pd.read_csv(TESTS)
    java_smells = load_smell_map(JAVA_SMELLS)
    source_smells = load_smell_map(SOURCE_SMELLS)
    roundtrip = json.loads(ROUNDTRIP.read_text(encoding="utf-8"))
    reverse_by_key = {(item["model"], item["problem_id"]): item for item in roundtrip}

    tasks = []
    for (model, problem), group in tests.groupby(["Llm", "Problem ID"]):
        cases = []
        for _, row in group.iterrows():
            cases.append({
                "id": row["Testcase_id"],
                "outcome": outcome_name(row["Outcome"]),
                "error": None if pd.isna(row["Error"]) else str(row["Error"])[:500],
            })
        passed = sum(case["outcome"] == "PASSED" for case in cases)
        total = expected.get(problem, len(cases))
        sample_path = str(group.iloc[0]["Path"]).replace("\\", "/")
        compiler_errors = [case for case in cases if case["outcome"] == "COMPILER_ERROR"]
        tasks.append({
            "model": model,
            "model_name": MODELS.get(model, model),
            "problem_id": problem,
            "direction": "python_to_java",
            "tests_expected": total,
            "tests_recorded": len(cases),
            "tests_passed": passed,
            "pass_rate": passed / total if total else None,
            "fully_passed": passed == total and not compiler_errors,
            "compilation": {
                "compiled": not compiler_errors,
                "recompiled": False,
                "compiler_errors": compiler_errors,
                "note": "Java is compiled when the test runs, with java Main.java. There is no repair loop and no second model call.",
            },
            "code_smells": java_smells.get(sample_path, {"status": "missing", "count": None, "items": []}),
            "roundtrip_java_to_python": reverse_by_key.get((model, problem)),
            "translation_path": sample_path,
            "cases": cases,
        })

    summary = {}
    for model, name in MODELS.items():
        owned = [task for task in tasks if task["model"] == model]
        expected_sum = sum(task["tests_expected"] for task in owned)
        passed_sum = sum(task["tests_passed"] for task in owned)
        full = sum(1 for task in owned if task["fully_passed"])
        reverses = [task["roundtrip_java_to_python"] for task in owned if task["roundtrip_java_to_python"]]
        reverse_full = sum(1 for item in reverses if item.get("status") == "tested" and item.get("tests_passed") == item.get("tests_expected"))
        reverse_tested = sum(1 for item in reverses if item.get("status") == "tested")
        summary[model] = {
            "model_name": name,
            "methods_translated_python_to_java": len(owned),
            "methods_fully_passed_python_to_java": full,
            "python_to_java_method_pass_rate": full / len(owned) if owned else None,
            "base_tests_expected": expected_sum,
            "base_tests_passed": passed_sum,
            "base_test_pass_rate": passed_sum / expected_sum if expected_sum else None,
            "methods_roundtrip_tested": reverse_tested,
            "methods_roundtrip_fully_passed": reverse_full,
            "roundtrip_method_pass_rate": reverse_full / reverse_tested if reverse_tested else None,
        }

    report = {
        "scope": {
            "methods_requested": 50,
            "dataset": "HumanEval+",
            "cases": "base_input only, not the augmented EvalPlus suite",
            "directions": ["python_to_java", "java_to_python"],
            "translations_per_direction": 1,
            "iterative_repair": False,
            "models": MODELS,
            "gemini_note": "Gemini returned HTTP 429 for most of the 50 methods. The methods without a Java file were not translated and were not tested.",
        },
        "summary": summary,
        "source_python_smells": [
            {"path": path, "code_smells": smell}
            for path, smell in source_smells.items()
        ],
        "tasks": tasks,
    }
    destination = ROOT / "results" / "gemini_gpt_50.json"
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(destination)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
