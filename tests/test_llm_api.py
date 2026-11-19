import os
from types import SimpleNamespace

import pytest

from llm_api import ApiLLM, is_api_model, load_env, resolve_api_model, strip_model_code


def test_load_env_reads_values_and_does_not_override(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "# comment",
                "OPENAI_API_KEY=from-file",
                "DEEPSEEK_API_KEY=\"abc\"",
                "GEMINI_API_KEY='xyz'",
                "EMPTY_KEY=",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("OPENAI_API_KEY", "already")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    load_env(env_file)

    assert os.environ["OPENAI_API_KEY"] == "already"
    assert os.environ["DEEPSEEK_API_KEY"] == "abc"
    assert os.environ["GEMINI_API_KEY"] == "xyz"
    assert "EMPTY_KEY" not in os.environ


def test_resolve_api_model_uses_provider_defaults_and_env_override(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_MODEL", raising=False)
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test")

    deepseek = resolve_api_model("api:deepseek")
    gemini = resolve_api_model("api:gemini")

    assert deepseek["provider"] == "deepseek"
    assert deepseek["model"] == "deepseek-chat"
    assert deepseek["base_url"] == "https://api.deepseek.com"
    assert deepseek["api_key_env"] == "DEEPSEEK_API_KEY"
    assert gemini["model"] == "gemini-test"
    assert gemini["base_url"].startswith("https://generativelanguage.googleapis.com")
    assert gemini["api_key_env"] == "GEMINI_API_KEY"


def test_is_api_model_marks_only_the_new_prefix():
    assert is_api_model("api:deepseek")
    assert not is_api_model("openai_gpt-4.1-mini")
    assert not is_api_model("meta-llama/Meta-Llama-3-70B-Instruct")


def test_resolve_api_model_rejects_unknown_provider():
    with pytest.raises(KeyError, match="unknown-provider"):
        resolve_api_model("api:unknown-provider")


def test_strip_model_code_removes_fences_and_markers():
    raw = "```java\nclass A {}\n```\n|End-of-Code|"
    assert strip_model_code(raw) == "class A {}\n"


def test_translate_returns_one_cleaned_string_per_sample(tmp_path, monkeypatch):
    source = tmp_path / "sample.py"
    source.write_text("print(1)\n", encoding="utf-8")
    calls = []

    def complete(model, messages):
        calls.append((model, messages))
        return "```java\nclass A {}\n```\n|End-of-Code|"

    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    sample = SimpleNamespace(
        path=str(source),
        programming_language="python",
        dataset="evalplus",
        submission_id="s1",
    )
    llm = ApiLLM("api:deepseek", complete=complete)

    codes = llm.translate(sample, "java", "evalplus", "task-1", 2)

    assert codes == ["class A {}\n", "class A {}\n"]
    assert calls[0][0] == "deepseek-chat"
    assert calls[0][1][0]["role"] == "system"
    assert "print(1)" in calls[0][1][1]["content"]
    assert "java" in calls[0][1][1]["content"]


def test_translate_requires_the_provider_key(tmp_path, monkeypatch):
    source = tmp_path / "sample.py"
    source.write_text("print(1)\n", encoding="utf-8")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    sample = SimpleNamespace(
        path=str(source),
        programming_language="python",
        dataset="evalplus",
        submission_id="s1",
    )
    llm = ApiLLM("api:openai")

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        llm.translate(sample, "java", "evalplus", "task-1", 1)
