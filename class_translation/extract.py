from __future__ import annotations

import re


def extract_code(text: str, target_lang: str) -> str:
    language = re.escape(target_lang)
    tagged = re.compile(
        rf"```{language}[^\n]*\n([\s\S]*?)```",
        re.IGNORECASE,
    )
    bare = re.compile(r"```[ \t]*\r?\n([\s\S]*?)```")
    match = tagged.search(text) or bare.search(text)
    code = match.group(1) if match else text
    return code.strip() + "\n"


def extract_python(text: str) -> str:
    return extract_code(text, "python")
