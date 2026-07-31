from __future__ import annotations

"""Helpers for selecting numbered markdown sections like `### 03. title`."""

import re


NUMBERED_SECTION_RE = re.compile(r"^###\s+(?P<number>\d+)\.\s+.*$")


def extract_numbered_section(content: str, number: int) -> str | None:
    lines = content.splitlines()
    start_index: int | None = None

    for index, line in enumerate(lines):
        match = NUMBERED_SECTION_RE.match(line)
        if match and int(match.group("number")) == number:
            start_index = index
            break

    if start_index is None:
        return None

    end_index = len(lines)
    for index in range(start_index + 1, len(lines)):
        if NUMBERED_SECTION_RE.match(lines[index]):
            end_index = index
            break

    return "\n".join(lines[start_index:end_index]).rstrip() + "\n"
