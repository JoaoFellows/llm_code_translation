from dataset_readiness import assess_datasets, task_ids_from_index


def test_assess_datasets_lists_missing_index_files(tmp_path):
    (tmp_path / "evalplus").mkdir()
    report = assess_datasets(str(tmp_path))
    by_name = {item["dataset"]: item for item in report}

    assert set(by_name) == {"codenet", "avatar", "evalplus", "evoeval"}
    assert by_name["evalplus"]["ready"] is False
    assert "evalplus/translation_data_evalplus.csv" in by_name["evalplus"]["missing"]
    assert by_name["codenet"]["ready"] is False


def test_assess_datasets_accepts_a_minimal_tree(tmp_path):
    for name in ("codenet", "avatar", "evalplus", "evoeval"):
        root = tmp_path / name
        root.mkdir()
        (root / f"translation_data_{name}.csv").write_text("id\n", encoding="utf-8")
        (root / "data").mkdir()
        (root / "test_cases").mkdir()
        if name in ("evalplus", "evoeval"):
            (root / "test_cases" / "in").mkdir()
            (root / "test_cases" / "out").mkdir()
            (root / "problem_description").mkdir()

    report = assess_datasets(str(tmp_path))
    assert all(item["ready"] for item in report)


def test_task_ids_from_index_respects_each_dataset_column(tmp_path):
    evalplus = tmp_path / "eval.csv"
    evalplus.write_text("id\nHumanEval_1.py\nHumanEval_1.py\nHumanEval_2.py\n", encoding="utf-8")
    avatar = tmp_path / "avatar.csv"
    avatar.write_text("avatar_id\natcoder_ABC042_A\ncodeforces_1\n", encoding="utf-8")
    codenet = tmp_path / "codenet.csv"
    codenet.write_text("id\np1\np2\np3\n", encoding="utf-8")

    assert task_ids_from_index(str(evalplus), "evalplus", 1) == ["HumanEval_1"]
    assert task_ids_from_index(str(avatar), "avatar", None) == ["atcoder_ABC042_A", "codeforces_1"]
    assert task_ids_from_index(str(codenet), "codenet", 2) == ["p1", "p2"]
