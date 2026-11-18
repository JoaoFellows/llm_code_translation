from __future__ import annotations

from class_translation.extract import extract_code
from class_translation.prompts import translation_messages
from class_translation.providers import ChatClient
from class_translation.state import ClassTask, ensure_java_to_python


def translate_class(task: ClassTask, client: ChatClient) -> str:
    ensure_java_to_python(task)
    return extract_code(client.complete(translation_messages(task)), task.target_lang)
