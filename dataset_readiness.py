import csv
import os

DATASET_ORDER = ["codenet", "avatar", "evalplus", "evoeval"]

REQUIRED = {
    "codenet": {
        "files": ["translation_data_codenet.csv"],
        "dirs": ["data", "test_cases"],
    },
    "avatar": {
        "files": ["translation_data_avatar.csv"],
        "dirs": ["data", "test_cases"],
    },
    "evalplus": {
        "files": ["translation_data_evalplus.csv"],
        "dirs": ["data", "test_cases/in", "test_cases/out", "problem_description"],
    },
    "evoeval": {
        "files": ["translation_data_evoeval.csv"],
        "dirs": ["data", "test_cases/in", "test_cases/out", "problem_description"],
    },
}


def assess_datasets(base_path: str) -> list:
    report = []
    for dataset in DATASET_ORDER:
        spec = REQUIRED[dataset]
        missing = []
        for relative in spec["files"] + spec["dirs"]:
            parts = [dataset, *relative.split("/")]
            candidate = os.path.join(base_path, *parts) if base_path else os.path.join(*parts)
            if not os.path.exists(candidate):
                missing.append("/".join(parts))
        report.append({"dataset": dataset, "ready": not missing, "missing": missing})
    return report


def _kept(row: dict) -> bool:
    if "neglect" not in row:
        return True
    return str(row.get("neglect", "")).strip().lower() not in {"true", "1", "yes"}


def task_ids_from_index(csv_path: str, dataset: str, limit):
    with open(csv_path, newline="", encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle) if _kept(row)]
    if dataset in ("evalplus", "evoeval"):
        values = [str(row["id"]).split(".")[0] for row in rows]
    elif dataset == "avatar":
        values = [str(row["avatar_id"]) for row in rows]
    elif dataset == "codenet":
        values = [str(row["id"]) for row in rows]
    else:
        raise KeyError(dataset)
    unique = []
    for value in values:
        if value not in unique:
            unique.append(value)
    if limit is None:
        return unique
    return unique[:limit]
