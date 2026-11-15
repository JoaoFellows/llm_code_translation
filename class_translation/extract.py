from __future__ import annotations

import re

_FENCE = re.compile(r"```(?:python)?\s*([\s\S]*?)```", re.IGNORECASE)


def extract_python(text: str) -> str:
    match = _FENCE.search(text)
    code = match.group(1) if match else text
    return code.strip() + "\n"
