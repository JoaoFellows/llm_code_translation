import json
import logging
import os
import re
import time
from pathlib import Path

from config import config

logger = logging.getLogger("my_project_logger")

PROVIDERS = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "model_env": "OPENAI_MODEL",
        "default_model": "gpt-4.1-mini",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "model_env": "OPENROUTER_MODEL",
        "default_model": "openai/gpt-4.1-mini",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "api_key_env": "DEEPSEEK_API_KEY",
        "model_env": "DEEPSEEK_MODEL",
        "default_model": "deepseek-chat",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key_env": "GEMINI_API_KEY",
        "model_env": "GEMINI_MODEL",
        "default_model": "gemini-3.5-flash-lite",
    },
    "ollama": {
        "base_url": "http://127.0.0.1:11434/v1",
        "api_key_env": "OLLAMA_API_KEY",
        "model_env": "OLLAMA_MODEL",
        "default_model": "qwen2.5-coder",
    },
}

DEFAULT_API_MODELS = [f"api:{name}" for name in PROVIDERS]
_PROMPT_LIMIT = 60000


def load_env(path=None) -> None:
    env_file = Path(path) if path is not None else Path(__file__).resolve().parent / ".env"
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


def is_api_model(model_name: str) -> bool:
    return model_name.startswith("api:")


def resolve_api_model(model_name: str) -> dict:
    if not is_api_model(model_name):
        raise KeyError(model_name)
    provider = model_name.split(":", 1)[1]
    if provider not in PROVIDERS:
        raise KeyError(provider)
    spec = PROVIDERS[provider]
    override = os.environ.get(spec["model_env"], "").strip()
    return {
        "provider": provider,
        "model": override or spec["default_model"],
        "base_url": spec["base_url"],
        "api_key_env": spec["api_key_env"],
    }


def strip_model_code(text: str) -> str:
    cleaned = re.sub(r"(```.*$)|(\|Start-of-Code\|)|(\|End-of-Code\|)", "", text or "", flags=re.M)
    return cleaned.strip() + "\n"


def translation_messages(source_code: str, source_lang: str, target_lang: str, prompt_id: str) -> list:
    prompts_path = Path(config["prompt_selection_config"])
    if not prompts_path.is_file():
        prompts_path = Path(__file__).resolve().parent / config["prompt_selection_config"]
    prompt_config = json.loads(prompts_path.read_text(encoding="utf-8"))
    entry = prompt_config[prompt_id]
    prompt = entry["prompt"].format(source_code=source_code, source_lang=source_lang, target_lang=target_lang)
    return [
        {"role": "system", "content": entry["role"]},
        {"role": "user", "content": prompt},
    ]


class ApiLLM:
    def __init__(self, model: str, complete=None):
        self.model = model
        self._spec = resolve_api_model(model)
        self._complete = complete

    def translate(self, code_sample, target_lang: str, dataset: str, task_id: str, it_number: int,
                  prompt_crafting: bool = False, existing_translation=None, prompt_id: str = "default", data=None):
        if prompt_crafting or config["steps"].get("run_backtranslation"):
            raise RuntimeError(
                "The API client uses api_prompt_id for the first translation. "
                "Iterative repair and backtranslation stay disabled."
            )
        if self._complete is None:
            self._require_api_key()
        source = Path(code_sample.path).read_text(encoding="utf-8")
        if len(source) > _PROMPT_LIMIT:
            source = source[:_PROMPT_LIMIT]
        chosen_prompt = config["api_prompt_id"] if prompt_id == "default" else prompt_id
        messages = translation_messages(source, code_sample.programming_language, target_lang, chosen_prompt)
        return [self._generate_once(messages) for _ in range(it_number)]

    def _generate_once(self, messages) -> str:
        complete = self._complete or self._live_complete()
        attempts = config["LLMs"][self.model]["max_attempts"]
        last_error = None
        attempt = 0
        rate_waits = 0
        while attempt < attempts:
            try:
                return strip_model_code(complete(self._spec["model"], messages))
            except Exception as exc:
                last_error = exc
                logger.info("API request failed for %s: %s", self.model, exc)
                if "429" in str(exc) and rate_waits < 8:
                    rate_waits += 1
                    time.sleep(min(60, 15 * rate_waits))
                    continue
                attempt += 1
        logger.error("API request failed after %s attempts for %s: %s", attempts, self.model, last_error)
        return "MAX ATTEMPT EXCEEDED - NO CODE GENERATED\n"

    def _require_api_key(self) -> str:
        api_key = os.environ.get(self._spec["api_key_env"], "").strip()
        if api_key:
            return api_key
        if self._spec["provider"] == "ollama":
            return "ollama"
        raise RuntimeError(f"Missing environment variable {self._spec['api_key_env']}")

    def _live_complete(self):
        api_key = self._require_api_key()
        from openai import OpenAI

        client = OpenAI(base_url=self._spec["base_url"], api_key=api_key)

        def complete(model, messages):
            response = client.chat.completions.create(model=model, messages=messages, temperature=1)
            return response.choices[0].message.content or ""

        return complete
