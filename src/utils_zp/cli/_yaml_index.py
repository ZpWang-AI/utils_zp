from __future__ import annotations

"""Helpers for reading structured YAML index files used by CLI commands."""

import json
from pathlib import Path
from typing import Any

import yaml


MARKED_VALUES = {"是", "yes", "true", "1", "y"}


class _YamlDumper(yaml.SafeDumper):
    pass


def _str_presenter(dumper: _YamlDumper, data: str) -> yaml.ScalarNode:
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


_YamlDumper.add_representer(str, _str_presenter)


def _quote_markdown_plain_scalars(text: str) -> str:
    repaired_lines: list[str] = []
    for line in text.splitlines():
        if ": `" not in line:
            repaired_lines.append(line)
            continue

        prefix, value = line.split(":", 1)
        stripped_value = value.lstrip()
        if not stripped_value.startswith("`"):
            repaired_lines.append(line)
            continue

        leading_spaces = value[: len(value) - len(stripped_value)]
        repaired_lines.append(f"{prefix}: {leading_spaces}{json.dumps(stripped_value, ensure_ascii=False)}")
    return "\n".join(repaired_lines)


def load_yaml_document(index_path: Path) -> dict[str, Any]:
    raw_text = index_path.read_text(encoding="utf-8")
    try:
        document = yaml.safe_load(raw_text)
    except yaml.YAMLError as error:
        repaired_text = _quote_markdown_plain_scalars(raw_text)
        if repaired_text == raw_text:
            raise error
        document = yaml.safe_load(repaired_text)
    if not isinstance(document, dict):
        raise ValueError(f"invalid yaml document: {index_path}")
    return document


def save_yaml_document(index_path: Path, document: dict[str, Any]) -> None:
    index_path.write_text(
        yaml.dump(document, Dumper=_YamlDumper, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )


def load_yaml_items(index_path: Path, item_key: str = "versions") -> list[dict[str, Any]]:
    document = load_yaml_document(index_path)
    items = document.get(item_key)
    if not isinstance(items, list):
        raise ValueError(f"missing yaml item list `{item_key}`: {index_path}")

    normalized_items: list[dict[str, Any]] = []
    for item in items:
        if isinstance(item, dict):
            normalized_items.append(item)
    return normalized_items


def is_marked(item: dict[str, Any]) -> bool:
    marked = item.get("marked", False)
    if isinstance(marked, bool):
        return marked
    return str(marked).strip().lower() in MARKED_VALUES


def get_detail_markdown(item: dict[str, Any]) -> str | None:
    detail_markdown = item.get("detail_markdown")
    if detail_markdown is None:
        return None

    text = str(detail_markdown).rstrip()
    if not text:
        return None
    return text + "\n"


def normalize_version_id(raw_id: Any) -> str:
    text = str(raw_id).strip()
    if not text:
        return ""
    if text.isdigit():
        return str(int(text))
    return text


def get_target_path(item: dict[str, Any]) -> str:
    return str(item.get("target_path", "")).strip()


def set_mark_status(index_path: Path, version_id: int, marked: bool, item_key: str = "versions") -> dict[str, Any]:
    document = load_yaml_document(index_path)
    items = document.get(item_key)
    if not isinstance(items, list):
        raise ValueError(f"missing yaml item list `{item_key}`: {index_path}")

    target_id = str(version_id)
    for item in items:
        if not isinstance(item, dict):
            continue
        if normalize_version_id(item.get("id", "")) != target_id:
            continue
        item["marked"] = marked
        save_yaml_document(index_path, document)
        return item

    raise ValueError(f"unknown version number: {version_id}")
