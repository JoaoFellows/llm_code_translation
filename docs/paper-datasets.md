# Paper datasets audit (Frente 2)

Audit of the CodeNet, Avatar, EvalPlus, and EvoEval inputs that `prepare_dataset.py` loads, and of the Docker image `testing:t6`. Branch `TAES/paper-models`, commit `351a5cddc921b874182396ee5baca65d9c96a282`. Worktree `C:\Users\joaov\.t3\worktrees\llm_code_translation\t3-33e4234d-b7eb08d6a87784ff`. Checked on 2026-11-17.

`class_translation/` was left unchanged. The `LLMs` list in `config.py` was left unchanged. No model API was called. `.env` was not read. No sample dataset was created. `base_path_data`, `base_path_testing_docker`, and `tco_path` were left empty. No translation, test suite, or code-smell run was started.

## Config paths

In this branch, `config.py` sets:

| key | value |
| --- | --- |
| `base_path_data` | empty string |
| `base_path_testing_docker` | empty string |
| `tco_path` | empty string |
| `base_path_data_vm` | empty string |

The same four values are empty in `C:\llm_code_translation\config.py` and in `C:\Users\joaov\.t3\worktrees\llm_code_translation\t3-3cb4e575-a993984a55c0bdc3\config.py`. There is no configured root to point at a dataset directory.

`prepare_datasets` is `codenet`, `avatar`, `evalplus`, `evoeval`. For each name, `prepare_dataset.py` expects:

- `<base_path_data>/<dataset>/translation_data_<dataset>.csv`
- sources under `<base_path_data>/<dataset>/data/`
- cases under `<base_path_data>/<dataset>/test_cases/`

Avatar further splits AtCoder (`atcoder_<contest>_<level>`, sources under `data/<contest>/<level>/<language>/`, cases under `test_cases/<contest>/<level>/in` and `out`) and Codeforces (`codeforces_<id>`, sources under `data/<id>/<language>/`, cases under `test_cases/<id>/samples`).

## Datasets

| dataset | path on disk | `load_to_cache` |
| --- | --- | --- |
| CodeNet | absent | not attempted |
| Avatar | absent | not attempted |
| EvalPlus | absent | not attempted |
| EvoEval | absent | not attempted |

No `translation_data_codenet.csv`, `translation_data_avatar.csv`, `translation_data_evalplus.csv`, or `translation_data_evoeval.csv` was found. No `data/` or `test_cases/` tree for those four names was found. The AtCoder and Codeforces split for Avatar is absent on disk; it was not confirmed from files.

`prepare_dataset.load_to_cache` was not called. The index CSVs and the source and test-case trees are not on disk, so loading one problem from each dataset was not attempted.

### Where this was looked up

- This worktree, including a search for `translation_data_*.csv`. Top-level directories are `class_translation`, `datastructures`, and `docs`.
- `C:\llm_code_translation`, depth 4 for `translation_data_*.csv` and depth 3 for directories named `codenet`, `avatar`, `evalplus`, `evoeval`, `data`, or `test_cases`. None.
- `C:\Users\joaov`, depth 3 for `translation_data_*.csv`. None.
- `C:\Users\joaov\develop`, `C:\Users\joaov\source`, `C:\Users\joaov\Documents`, `C:\Users\joaov\Downloads`, and `C:\Users\joaov\OneDrive`, depth 2 for `translation_data_*.csv` and for directories named `codenet`, `avatar`, `evalplus`, or `evoeval`. None.
- The other worktree `C:\Users\joaov\.t3\worktrees\llm_code_translation\t3-3cb4e575-a993984a55c0bdc3` contains the code checkout, not these dataset trees.
- `C:\llm_code_translation-paper`, `C:\data`, and `C:\datasets` are absent. The only filesystem drive is `C:`.

`C:\ClassEval-T` exists. It is a different benchmark and is not a path for CodeNet, Avatar, EvalPlus, or EvoEval.

## Docker image `testing:t6`

Command:

```
docker image inspect testing:t6
```

The Docker daemon is not running. `docker.exe` is installed at `C:\Program Files\Docker\Docker\resources\bin\docker.exe`. The inspect call failed before it could report whether the image exists:

```
error during connect: this error may indicate that the docker daemon is not running: Get "http://%2F%2F.%2Fpipe%2Fdocker_engine/v1.45/images/testing:t6/json": open //./pipe/docker_engine: The system cannot find the file specified.
```

Docker was not installed and the daemon was not started. Presence of `testing:t6` is unknown because the daemon is down.

## Original submission test

An original-submission test cannot run. The four dataset trees are absent, and the Docker daemon is down, so `testing:t6` could not be inspected. No test command was executed.

## Stop

Frente 2 stops at this audit. A dataset is missing, and the testing image could not be confirmed. The new model client was not implemented. No model was added beside the existing `LLMs` list.
