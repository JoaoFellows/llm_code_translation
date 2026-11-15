import pytest

from class_translation.providers import PRESETS, ScriptedChatClient, build_client


def test_presets_read_key_from_env():
    assert set(PRESETS) == {"openai", "openrouter", "deepseek", "gemini", "ollama"}
    assert PRESETS["deepseek"]["api_key_env"] == "DEEPSEEK_API_KEY"
    assert PRESETS["openai"]["base_url"].startswith("https://")


def test_build_client_requires_key_without_network(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        build_client("openai")


def test_scripted_client_returns_queued_text():
    client = ScriptedChatClient(["first", "second"])
    assert client.complete([{"role": "user", "content": "a"}]) == "first"
    assert client.complete([{"role": "user", "content": "b"}]) == "second"
