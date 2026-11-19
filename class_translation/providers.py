from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Protocol

import openai
from openai import OpenAI

_REPO_ROOT = Path(__file__).resolve().parents[1]


def load_project_env(path: Path | None = None) -> None:
    env_file = path if path is not None else _REPO_ROOT / ".env"
    if not env_file.is_file():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value and key not in os.environ:
            os.environ[key] = value


load_project_env()


class ChatClient(Protocol):
    def complete(self, messages: list[dict[str, str]]) -> str:
        """Return the assistant message content."""


PRESETS: dict[str, dict[str, str]] = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4.1-mini",
        "api_key_env": "OPENAI_API_KEY",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "model": "openai/gpt-4.1-mini",
        "api_key_env": "OPENROUTER_API_KEY",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "api_key_env": "DEEPSEEK_API_KEY",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model": "gemini-3.5-flash-lite",
        "api_key_env": "GEMINI_API_KEY",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "model": "openai/gpt-oss-120b",
        "api_key_env": "GROQ_API_KEY",
    },
    "nextforce": {
        "base_url": "https://router.nexforce.ai/v1",
        "model": "openai/gpt-4.1-mini",
        "api_key_env": "NEXTFORCE_API_KEY",
    },
    "ollama": {
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5-coder",
        "api_key_env": "OLLAMA_API_KEY",
    },
}


class OpenAICompatibleClient:
    def __init__(self, base_url: str, api_key: str, model: str, timeout: float | None = None) -> None:
        self._model = model
        client_kwargs: dict[str, object] = {"base_url": base_url, "api_key": api_key}
        if timeout is not None:
            client_kwargs["timeout"] = timeout
        self._client = OpenAI(**client_kwargs)

    def complete(self, messages: list[dict[str, str]], *, json_mode: bool = False) -> str:
        max_retries = 8
        delay = 5.0
        use_json_mode = json_mode
        for attempt in range(max_retries):
            try:
                kwargs: dict[str, object] = {
                    "model": self._model,
                    "messages": messages,
                    "temperature": 0,
                }
                if use_json_mode:
                    kwargs["response_format"] = {"type": "json_object"}
                response = self._client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content
                if content and content.strip():
                    return content
                if attempt == max_retries - 1:
                    return content or ""
                wait = min(delay * (2 ** attempt), 15.0)
                print(f"[EmptyResponse] Empty content – waiting {wait:.0f}s before retry {attempt + 1}/{max_retries - 1}…", flush=True)
                time.sleep(wait)
            except openai.BadRequestError:
                if use_json_mode:
                    use_json_mode = False
                    continue
                raise
            except openai.RateLimitError as exc:
                if attempt == max_retries - 1:
                    raise
                wait = delay * (2 ** attempt)
                print(f"[RateLimit] 429 – waiting {wait:.0f}s before retry {attempt + 1}/{max_retries - 1}…", flush=True)
                time.sleep(wait)
            except (openai.APITimeoutError, openai.APIConnectionError) as exc:
                if attempt == max_retries - 1:
                    raise
                wait = delay * (2 ** attempt)
                print(f"[Timeout/Connection] {exc} – waiting {wait:.0f}s before retry…", flush=True)
                time.sleep(wait)
        return ""  # unreachable


class ScriptedChatClient:
    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)
        self.prompts: list[list[dict[str, str]]] = []

    def complete(self, messages: list[dict[str, str]]) -> str:
        self.prompts.append(messages)
        if not self._responses:
            raise RuntimeError("ScriptedChatClient has no responses left")
        return self._responses.pop(0)


def build_client(
    preset: str,
    timeout: float | None = None,
    *,
    model: str | None = None,
    base_url: str | None = None,
) -> ChatClient:
    if preset not in PRESETS:
        raise KeyError(preset)
    config = PRESETS[preset]
    prefix = preset.upper()
    api_key = os.environ.get(config["api_key_env"], "")
    if not api_key:
        if preset == "ollama":
            api_key = "ollama"
        else:
            raise RuntimeError(f"Missing environment variable {config['api_key_env']}")
    resolved_base_url = base_url or os.environ.get(f"{prefix}_BASE_URL", "") or config["base_url"]
    if not resolved_base_url:
        raise RuntimeError(f"Missing base URL for provider '{preset}'. Set {prefix}_BASE_URL in .env or pass --base-url.")
    resolved_model = model or os.environ.get(f"{prefix}_MODEL", "") or config["model"]
    return OpenAICompatibleClient(
        base_url=resolved_base_url,
        api_key=api_key,
        model=resolved_model,
        timeout=timeout,
    )
