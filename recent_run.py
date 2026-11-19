import copy
import os
import subprocess
import sys

from config import config
from dataset_readiness import assess_datasets, task_ids_from_index
from llm_api import DEFAULT_API_MODELS, PROVIDERS, load_env

DOCKER_IMAGE = "testing:t6"


def key_status():
    return [
        (name, bool(os.environ.get(spec["api_key_env"], "").strip()))
        for name, spec in PROVIDERS.items()
    ]


def providers_for_run(model_names, ready_providers):
    selected = []
    for model_name in model_names:
        provider = model_name.split(":", 1)[1]
        if provider in ready_providers:
            selected.append(model_name)
    return selected


def apply_run_config(base_path, model_names, ready_providers, task_limit, with_tests,
                     testing_docker="", tco_path="", with_smells=False):
    plan = copy.deepcopy(config)
    ready = [item["dataset"] for item in assess_datasets(base_path) if item["ready"]]
    plan["base_path_data"] = base_path
    plan["base_path_testing_docker"] = testing_docker
    plan["tco_path"] = tco_path
    plan["steps"]["prepare_datasets"] = ready
    plan["steps"]["run_translation"] = providers_for_run(model_names, ready_providers)
    plan["steps"]["run_tests"] = with_tests
    plan["steps"]["run_code_smell_detection"] = with_smells
    plan["steps"]["only_specific_tasks"] = task_limit is not None
    if task_limit is not None:
        for dataset in ready:
            csv_path = os.path.join(base_path, dataset, f"translation_data_{dataset}.csv")
            plan["steps"]["specific_tasks"][dataset] = task_ids_from_index(csv_path, dataset, task_limit)
    return plan


def docker_status() -> str:
    try:
        result = subprocess.run(
            ["docker", "image", "inspect", DOCKER_IMAGE],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except FileNotFoundError:
        return "docker executable not found"
    except subprocess.TimeoutExpired:
        return "docker inspect timed out"
    if result.returncode == 0:
        return f"{DOCKER_IMAGE} is present"
    detail = (result.stderr or result.stdout or "").lower()
    if "docker daemon" in detail or "pipe" in detail or "npipe" in detail or "cannot find the file" in detail:
        return f"Docker daemon is not running. {DOCKER_IMAGE} was not inspected."
    return f"{DOCKER_IMAGE} was not found. The repository does not include a Dockerfile for it."


def format_report(base_path: str) -> str:
    lines = ["API keys (set or missing, values are not shown):"]
    for name, present in key_status():
        spec = PROVIDERS[name]
        lines.append(
            f"  {spec['api_key_env']}: {'set' if present else 'missing'} "
            f"(default model {spec['default_model']}, override with {spec['model_env']})"
        )
    lines.append("")
    lines.append(f"Dataset root: {base_path or '(empty)'}")
    if not base_path:
        lines.append("Set BASE_PATH_DATA in .env to the directory that contains codenet, avatar, evalplus, and evoeval.")
    for item in assess_datasets(base_path):
        if item["ready"]:
            lines.append(f"  {item['dataset']}: ready")
        else:
            lines.append(f"  {item['dataset']}: missing {', '.join(item['missing'])}")
    lines.append("")
    lines.append(f"Docker: {docker_status()}")
    lines.append("")
    lines.append(
        "prepare_dataset.py reads translation_data_<dataset>.csv plus the data and test_cases trees. "
        "It does not download CodeNet, Avatar, EvalPlus, or EvoEval, and the sample-size numbers in config.py are not applied."
    )
    lines.append(
        "Translation can start when a dataset is ready. Tests and code-smell detection also need the testing:t6 image."
    )
    return "\n".join(lines)


def commit_plan(plan) -> None:
    config.clear()
    config.update(plan)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    load_env()
    base_path = os.environ.get("BASE_PATH_DATA", config["base_path_data"]).strip()
    testing_docker = os.environ.get("BASE_PATH_TESTING_DOCKER", config["base_path_testing_docker"]).strip()
    tco_path = os.environ.get("TCO_PATH", config["tco_path"]).strip()
    print(format_report(base_path))
    if "--run" not in argv:
        print("")
        print("Check only. No model was called and no test suite was started.")
        return 0

    ready_providers = {name for name, present in key_status() if present}
    selected = os.environ.get("RECENT_MODELS", "").strip()
    model_names = [name.strip() for name in selected.split(",") if name.strip()] or DEFAULT_API_MODELS
    raw_limit = os.environ.get("RECENT_MODELS_TASK_LIMIT", "").strip()
    task_limit = int(raw_limit) if raw_limit else None
    plan = apply_run_config(
        base_path=base_path,
        model_names=model_names,
        ready_providers=ready_providers,
        task_limit=task_limit,
        with_tests="--with-tests" in argv,
        with_smells="--with-smells" in argv,
        testing_docker=testing_docker,
        tco_path=tco_path,
    )
    if not plan["steps"]["prepare_datasets"] or not plan["steps"]["run_translation"]:
        print("")
        print("Refusing to run. A ready dataset and at least one API key are required.")
        return 2
    if ("--with-tests" in argv or "--with-smells" in argv) and not docker_status().endswith("is present"):
        print("")
        print(f"Refusing to run tests. {DOCKER_IMAGE} is not available.")
        return 2
    commit_plan(plan)
    from main import main as pipeline_main

    pipeline_main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
