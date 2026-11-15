from pathlib import Path

from class_translation.extract import extract_python
from class_translation.providers import ScriptedChatClient
from class_translation.state import load_task
from class_translation.translate import translate_class

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "counter"


def test_extract_python_prefers_fenced_block():
    text = "nota\n```python\nclass Counter:\n    pass\n```\nfim"
    assert extract_python(text).startswith("class Counter:")


def test_translate_sends_java_spec_and_returns_code():
    task = load_task(FIXTURE)
    client = ScriptedChatClient(["```python\nclass Counter:\n    pass\n```"])
    code = translate_class(task, client)
    prompt = client.prompts[0][-1]["content"]
    assert "class Counter" in prompt and "assertEquals" in prompt
    assert "code smell" in prompt.lower() or "code smells" in prompt.lower()
    assert code.startswith("class Counter:")
