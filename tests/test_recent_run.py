from config import config
from recent_run import apply_run_config, key_status, providers_for_run


def test_api_models_are_registered_and_translation_stays_off():
    for name in ("api:openai", "api:openrouter", "api:deepseek", "api:gemini", "api:ollama"):
        assert config["LLMs"][name]["max_attempts"] == 3
        assert config["LLMs"][name]["provider"]
    assert "meta-llama/Meta-Llama-3-70B-Instruct" in config["LLMs"]
    assert config["steps"]["run_translation"] == []
    assert config["api_prompt_id"] == "p1"


def test_key_status_reports_presence_without_values(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "secret-value")
    monkeypatch.delenv("OLLAMA_API_KEY", raising=False)

    status = dict(key_status())

    assert status["openai"] is True
    assert status["ollama"] is False
    assert "secret-value" not in str(status)


def test_apply_run_config_limits_tasks_and_leaves_docker_off(tmp_path):
    for name in ("codenet", "avatar"):
        root = tmp_path / name
        root.mkdir()
        (root / f"translation_data_{name}.csv").write_text("id,avatar_id\np1,atcoder_ABC042_A\np2,codeforces_1\n", encoding="utf-8")
        (root / "data").mkdir()
        (root / "test_cases").mkdir()

    plan = apply_run_config(
        base_path=str(tmp_path),
        model_names=["api:deepseek", "api:ollama"],
        ready_providers={"deepseek", "openai"},
        task_limit=1,
        with_tests=False,
    )

    assert plan["steps"]["prepare_datasets"] == ["codenet", "avatar"]
    assert plan["steps"]["run_translation"] == ["api:deepseek"]
    assert plan["steps"]["run_tests"] is False
    assert plan["steps"]["run_code_smell_detection"] is False
    assert plan["steps"]["only_specific_tasks"] is True
    assert plan["steps"]["specific_tasks"]["codenet"] == ["p1"]
    assert plan["steps"]["specific_tasks"]["avatar"] == ["atcoder_ABC042_A"]
    assert providers_for_run(["api:deepseek", "api:ollama"], {"deepseek"}) == ["api:deepseek"]
