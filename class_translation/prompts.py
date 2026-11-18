from __future__ import annotations

from class_translation.state import ClassTask

_LINTERS = {"python": "Pylint", "java": "PMD"}


def _class_only(task: ClassTask) -> str:
    return f"Print only the {task.target_lang} class."


def _package_line(task: ClassTask) -> str:
    if task.target_lang == "java":
        return "The class must declare package org.example.\n"
    return ""


def _linter_name(target_lang: str) -> str:
    try:
        return _LINTERS[target_lang]
    except KeyError as error:
        raise NotImplementedError(
            f"No linter prompt for target language {target_lang}"
        ) from error


def translation_messages(task: ClassTask) -> list[dict[str, str]]:
    system = (
        "You are a skilled programmer translating code. "
        "Produce functionally correct code with few code smells."
    )
    user = (
        f"Translate the following {task.source_lang} class to {task.target_lang}.\n"
        "The translation must keep the same behavior and should contain few code smells.\n"
        f"{_class_only(task)}\n"
        f"{_package_line(task)}\n"
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
        f"The {task.target_lang} tests failed. Fix the {task.target_lang} class.\n"
        f"{_class_only(task)}\n"
        f"{_package_line(task)}\n"
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
        f"Do not change observable behavior. {_class_only(task)}\n"
        f"{_package_line(task)}\n"
        f"Source {task.source_lang} class, for behavior:\n{task.source_code}\n\n"
        f"Current translation:\n{code}\n\n"
        f"{_linter_name(task.target_lang)}:\n{feedback}\n"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
