from pathlib import Path

from class_translation.extract import extract_code, extract_python
from class_translation.prompts import smell_messages
from class_translation.providers import ScriptedChatClient
from class_translation.state import ClassTask, load_task
from class_translation.translate import translate_class

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "counter"

JAVA_TASK = ClassTask(
    "box",
    "python",
    "java",
    "Box",
    "class Box:\n    pass\n",
    "def test_box():\n    assert True\n",
    "oracle",
)


def test_extract_python_prefers_fenced_block():
    text = "nota\n```python\nclass Counter:\n    pass\n```\nfim"
    assert extract_python(text).startswith("class Counter:")


def test_extract_code_follows_target_language():
    java = "note\n```java\npublic class Box {}\n```\nend"
    python = "note\n```python\nclass Box:\n    pass\n```\nend"
    bare = "```\npublic class Box {}\n```"
    whole = "public class Box {}\n"
    mixed = "```python\nclass Box:\n    pass\n```\n```java\npublic class Box {}\n```"
    assert extract_code(java, "java").startswith("public class Box")
    assert extract_code(python, "python").startswith("class Box:")
    assert extract_code(bare, "java").startswith("public class Box")
    assert extract_code(whole, "java").startswith("public class Box")
    assert extract_code(mixed, "java").startswith("public class Box")
    assert "class Box:" not in extract_code(mixed, "java")


def test_translate_sends_java_spec_and_returns_code():
    task = load_task(FIXTURE)
    client = ScriptedChatClient(["```python\nclass Counter:\n    pass\n```"])
    code = translate_class(task, client)
    prompt = client.prompts[0][-1]["content"]
    assert "class Counter" in prompt and "assertEquals" in prompt
    assert "code smell" in prompt.lower() or "code smells" in prompt.lower()
    assert "Print only the python class." in prompt
    assert code.startswith("class Counter:")


def test_translate_prompt_asks_for_the_target_language_class():
    client = ScriptedChatClient(["```java\npublic class Box {}\n```"])
    code = translate_class(JAVA_TASK, client)
    prompt = client.prompts[0][-1]["content"]
    assert "Print only the java class." in prompt
    assert "Print only the Python class." not in prompt
    assert "package org.example" in prompt
    assert code.startswith("public class Box")


def test_translate_python_box_asks_for_java_class():
    task = load_task(Path(__file__).resolve().parents[1] / "fixtures" / "box")
    client = ScriptedChatClient(["```java\npackage org.example;\npublic class Box {}\n```"])
    code = translate_class(task, client)
    prompt = client.prompts[0][-1]["content"]
    assert "class Box" in prompt
    assert "assertEqual" in prompt
    assert "Print only the java class." in prompt
    assert "Print only the Python class." not in prompt
    assert code.startswith("package org.example;")


def test_smell_prompt_names_the_target_linter():
    java_prompt = smell_messages(JAVA_TASK, "public class Box {}", "unused")[-1]["content"]
    python_prompt = smell_messages(load_task(FIXTURE), "class Counter: pass", "unused")[-1]["content"]
    assert "PMD:" in java_prompt
    assert "Print only the java class." in java_prompt
    assert "Pylint:" in python_prompt
    assert "Print only the python class." in python_prompt
