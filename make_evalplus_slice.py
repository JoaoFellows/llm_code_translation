import json
from pathlib import Path

import pandas as pd
from evalplus.data import get_human_eval_plus

from evalplus_driver import encode_json_case

root = Path(r"C:/llm_code_translation_data/evalplus")
wanted = 50
rows = []
for task_id, problem in get_human_eval_plus().items():
    if len(rows) >= wanted:
        break
    stem = task_id.replace("/", "_")
    filename = stem + ".py"
    namespace = {}
    exec(problem["prompt"] + problem["canonical_solution"], namespace)
    function = namespace[problem["entry_point"]]
    encoded = []
    kind = None
    for args in problem["base_input"]:
        result = function(*args)
        raw, expected, kind = encode_json_case(args, result)
        encoded.append((raw, expected))
    (root / "data").mkdir(parents=True, exist_ok=True)
    (root / "data" / filename).write_text(
        problem["prompt"] + problem["canonical_solution"], encoding="utf-8"
    )
    (root / "problem_description").mkdir(parents=True, exist_ok=True)
    (root / "problem_description" / f"{stem}.txt").write_text(problem["prompt"], encoding="utf-8")
    for side in ("in", "out"):
        (root / "test_cases" / side).mkdir(parents=True, exist_ok=True)
    (root / "test_cases" / "in" / f"tc_{stem}.txt").write_text(
        "\n".join(raw for raw, _ in encoded) + "\n", encoding="utf-8"
    )
    (root / "test_cases" / "out" / f"tc_{stem}.txt").write_text(
        "\n".join(expected for _, expected in encoded) + "\n", encoding="utf-8"
    )
    driver_dir = root / "drivers"
    driver_dir.mkdir(parents=True, exist_ok=True)
    (driver_dir / f"{stem}.json").write_text(
        json.dumps({"entry_point": problem["entry_point"], "kind": kind}), encoding="utf-8"
    )
    rows.append({"id": filename, "neglect": False})
    print(f"{stem}: {len(encoded)} tests, kind={kind}")
pd.DataFrame(rows).to_csv(root / "translation_data_evalplus.csv", index=False)
print(f"wrote {len(rows)} tasks to {root}")
