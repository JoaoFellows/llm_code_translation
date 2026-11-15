from __future__ import annotations

from class_translation.state import ClassTask


def translation_messages(task: ClassTask) -> list[dict[str, str]]:
    system = (
        "You are a skilled programmer translating code. "
        "Produce functionally correct code with few code smells."
    )
    user = (
        f"Translate the following {task.source_lang} class to {task.target_lang}.\n"
        "The translation must keep the same behavior and should contain few code smells.\n"
        "Print only the Python class.\n\n"
        f"Source class:\n{task.source_code}\n\n"
        "Behavioral specification (source tests, do not translate them):\n"
        f"{task.source_tests}\n"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def repair_messages(task: ClassTask, code: str, feedback: str) -> list[dict[str, str]]:
    system = (
        "You are a skilled programmer fixing a code translation. "
        "Restore functional correctness and keep code smells low."
    )
    user = (
        f"The {task.source_lang} class below was translated to {task.target_lang}.\n"
        "The Python tests failed. Fix the Python class.\n"
        "Print only the Python class.\n\n"
        f"Source class:\n{task.source_code}\n\n"
        f"Behavioral specification:\n{task.source_tests}\n\n"
        f"Current translation:\n{code}\n\n"
        f"Test feedback:\n{feedback}\n"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def smell_messages(task: ClassTask, code: str, feedback: str) -> list[dict[str, str]]:
    system = (
        "You are a skilled programmer removing code smells without changing behavior."
    )
    user = (
        f"Refactor the following {task.target_lang} class so it has fewer code smells.\n"
        "Do not change observable behavior. Print only the Python class.\n\n"
        f"Source {task.source_lang} class, for behavior:\n{task.source_code}\n\n"
        f"Current translation:\n{code}\n\n"
        f"Pylint:\n{feedback}\n"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
