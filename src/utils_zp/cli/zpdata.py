from __future__ import annotations

"""List marked datasets from the configured dataset index."""

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .. import setting
from ._yaml_index import (
    get_detail_markdown,
    get_target_path,
    is_marked,
    load_yaml_items,
    normalize_version_id,
    set_mark_status,
)


@dataclass(frozen=True)
class DatasetInfo:
    dataset_id: str
    name: str
    size: str
    summary: str
    target_path: str


def _iter_dataset_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        flattened.append(item)
        derived_versions = item.get("derived_versions")
        if isinstance(derived_versions, list):
            flattened.extend(_iter_dataset_items(derived_versions))
    return flattened


def _build_dataset_info(item: dict[str, Any], *, display_id: str | None = None) -> DatasetInfo | None:
    dataset_id = display_id or normalize_version_id(item.get("id", ""))
    name = str(item.get("name", "")).strip()
    size = str(item.get("size", "")).strip()
    summary = str(item.get("summary", "")).strip()
    target_path = get_target_path(item)
    if not dataset_id or not name or not size or not summary or not target_path:
        return None
    return DatasetInfo(
        dataset_id=dataset_id,
        name=name,
        size=size,
        summary=summary,
        target_path=target_path,
    )


def _read_datasets(index_path: Path, *, only_marked: bool = True) -> list[DatasetInfo]:
    datasets: list[DatasetInfo] = []
    for item in _iter_dataset_items(load_yaml_items(index_path)):
        if only_marked and not is_marked(item):
            continue

        dataset = _build_dataset_info(item)
        if dataset is not None:
            datasets.append(dataset)

    return datasets


def collect_datasets(index_path: Path) -> list[DatasetInfo]:
    return _read_datasets(index_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zpdata",
        description="Show marked datasets from data/dataset_versions.yaml.",
    )
    parser.add_argument(
        "-tree",
        "--tree",
        action="store_true",
        help="Print the dataset derivation tree.",
    )
    parser.add_argument(
        "dataset_number",
        nargs="?",
        help="Print the selected dataset detail by id, for example: zpdata 7 or zpdata 11.1",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="List all datasets, including unmarked ones.",
    )
    mark_group = parser.add_mutually_exclusive_group()
    mark_group.add_argument(
        "-m",
        "--mark",
        dest="mark_number",
        help="Mark the selected dataset by id, for example: zpdata -m 7 or zpdata -m 11.1",
    )
    mark_group.add_argument(
        "-um",
        "--unmark",
        dest="unmark_number",
        help="Unmark the selected dataset by id, for example: zpdata -um 7 or zpdata -um 11.1",
    )
    return parser


def _find_item_by_primary_id(items: list[dict[str, Any]], dataset_id: str) -> dict[str, Any] | None:
    for item in items:
        if normalize_version_id(item.get("id", "")) == dataset_id:
            return item
    return None


def _find_item_by_alias(items: list[dict[str, Any]], dataset_id: str) -> dict[str, Any] | None:
    for item in items:
        for alias_key in ("derived_id", "legacy_version_id"):
            if normalize_version_id(item.get(alias_key, "")) == dataset_id:
                return item
    return None


def _find_dataset_item(items: list[dict[str, Any]], dataset_id: str) -> dict[str, Any] | None:
    normalized_id = normalize_version_id(dataset_id)
    if not normalized_id:
        return None
    item = _find_item_by_primary_id(items, normalized_id)
    if item is not None:
        if _is_legacy_top_level_item(item):
            aliased_item = _find_item_by_alias(items, normalized_id)
            if aliased_item is not None:
                return aliased_item
        return item
    return _find_item_by_alias(items, normalized_id)


def _get_detail_markdown_with_fallback(items: list[dict[str, Any]], item: dict[str, Any]) -> str | None:
    detail_section = get_detail_markdown(item)
    if detail_section is not None:
        return detail_section

    legacy_version_id = normalize_version_id(item.get("legacy_version_id", ""))
    if not legacy_version_id:
        return None
    legacy_item = _find_item_by_primary_id(items, legacy_version_id)
    if legacy_item is None:
        return None
    return get_detail_markdown(legacy_item)


def _find_parent_item(items: list[dict[str, Any]], target_item: dict[str, Any]) -> dict[str, Any] | None:
    for item in items:
        derived_versions = item.get("derived_versions")
        if not isinstance(derived_versions, list):
            continue
        for child in derived_versions:
            if child is target_item:
                return item
        nested_parent = _find_parent_item([child for child in derived_versions if isinstance(child, dict)], target_item)
        if nested_parent is not None:
            return nested_parent
    return None


def _format_related_derived_versions(item: dict[str, Any]) -> str | None:
    derived_versions = item.get("derived_versions")
    if not isinstance(derived_versions, list):
        return None

    lines: list[str] = []
    for child in derived_versions:
        if not isinstance(child, dict):
            continue
        child_id = normalize_version_id(child.get("id", ""))
        child_name = str(child.get("name", "")).strip()
        child_summary = str(child.get("summary", "")).strip()
        child_relation = str(child.get("relation", "")).strip() or "-"
        if not child_id or not child_name or not child_summary:
            continue
        lines.append(f"- {child_id} | {child_relation} | {child_name} | {child_summary}")

    if not lines:
        return None
    return "相关派生版本:\n" + "\n".join(lines) + "\n"


def _format_parent_context(root_items: list[dict[str, Any]], all_items: list[dict[str, Any]], item: dict[str, Any]) -> str | None:
    relation = str(item.get("relation", "")).strip()
    parent_item: dict[str, Any] | None = None

    derived_from_version_id = normalize_version_id(item.get("derived_from_version_id", ""))
    if derived_from_version_id:
        parent_item = _find_item_by_primary_id(all_items, derived_from_version_id)
    legacy_version_id = normalize_version_id(item.get("legacy_version_id", ""))
    if not relation and legacy_version_id:
        legacy_item = _find_item_by_primary_id(all_items, legacy_version_id)
        if legacy_item is not None:
            relation = str(legacy_item.get("relation", "")).strip()
    if parent_item is None:
        parent_item = _find_parent_item(root_items, item)

    lines: list[str] = []
    if parent_item is not None:
        parent_id = normalize_version_id(parent_item.get("id", ""))
        parent_name = str(parent_item.get("name", "")).strip()
        if parent_id and parent_name:
            lines.append(f"父版本: {parent_id} | {parent_name}")
    if relation:
        lines.append(f"派生关系: {relation}")

    if not lines:
        return None
    return "\n".join(lines) + "\n"


def _is_legacy_top_level_item(item: dict[str, Any]) -> bool:
    return bool(normalize_version_id(item.get("derived_id", "")))


def _format_tree_label(item: dict[str, Any]) -> str | None:
    item_id = normalize_version_id(item.get("id", ""))
    name = str(item.get("name", "")).strip()
    if not item_id or not name:
        return None

    legacy_version_id = normalize_version_id(item.get("legacy_version_id", ""))
    legacy_suffix = f" (legacy: {legacy_version_id})" if legacy_version_id else ""
    return f"{item_id} {name}{legacy_suffix}"


def _get_tree_children(item: dict[str, Any], all_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged_children: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    def add_children(children: Any) -> None:
        if not isinstance(children, list):
            return
        for child in children:
            if not isinstance(child, dict):
                continue
            child_id = normalize_version_id(child.get("id", ""))
            if not child_id or child_id in seen_ids:
                continue
            seen_ids.add(child_id)
            merged_children.append(child)

    add_children(item.get("derived_versions"))

    legacy_version_id = normalize_version_id(item.get("legacy_version_id", ""))
    if legacy_version_id:
        legacy_item = _find_item_by_primary_id(all_items, legacy_version_id)
        if legacy_item is not None:
            add_children(legacy_item.get("derived_versions"))

    return merged_children


def _build_tree_lines(items: list[dict[str, Any]], all_items: list[dict[str, Any]], prefix: str = "") -> list[str]:
    lines: list[str] = []
    valid_items = [item for item in items if isinstance(item, dict)]
    for index, item in enumerate(valid_items):
        label = _format_tree_label(item)
        if label is None:
            continue

        is_last = index == len(valid_items) - 1
        branch = "└── " if is_last else "├── "
        lines.append(f"{prefix}{branch}{label}")

        derived_versions = _get_tree_children(item, all_items)
        if derived_versions:
            child_prefix = f"{prefix}{'    ' if is_last else '│   '}"
            lines.extend(_build_tree_lines(derived_versions, all_items, child_prefix))

    return lines


def _format_dataset_tree(root_items: list[dict[str, Any]]) -> str:
    tree_lines: list[str] = []
    all_items = _iter_dataset_items(root_items)
    structural_roots = [item for item in root_items if isinstance(item, dict) and not _is_legacy_top_level_item(item)]

    for item in structural_roots:
        label = _format_tree_label(item)
        if label is None:
            continue
        tree_lines.append(label)
        derived_versions = _get_tree_children(item, all_items)
        if derived_versions:
            tree_lines.extend(_build_tree_lines(derived_versions, all_items))
        tree_lines.append("")

    while tree_lines and tree_lines[-1] == "":
        tree_lines.pop()
    return "\n".join(tree_lines) + ("\n" if tree_lines else "")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    index_path = setting.TARGET_DATASET_VERSIONS_PATH
    if not index_path.exists():
        print(f"missing dataset versions file: {index_path}")
        return 1

    if args.mark_number is not None:
        target_id = normalize_version_id(args.mark_number)
        try:
            item = set_mark_status(index_path, target_id, True)
        except ValueError:
            print(f"unknown dataset number: {target_id}")
            return 1
        print(f"marked dataset {normalize_version_id(item.get('id', ''))}: {item.get('name', '')}")
        return 0

    if args.unmark_number is not None:
        target_id = normalize_version_id(args.unmark_number)
        try:
            item = set_mark_status(index_path, target_id, False)
        except ValueError:
            print(f"unknown dataset number: {target_id}")
            return 1
        print(f"unmarked dataset {normalize_version_id(item.get('id', ''))}: {item.get('name', '')}")
        return 0

    if args.tree:
        root_items = load_yaml_items(index_path)
        print(f"Target dataset versions path: {index_path}")
        print()
        print(_format_dataset_tree(root_items), end="")
        return 0

    if args.dataset_number is not None:
        root_items = load_yaml_items(index_path)
        all_items = _iter_dataset_items(root_items)
        requested_id = normalize_version_id(args.dataset_number)
        dataset_item = _find_dataset_item(all_items, requested_id)
        if dataset_item is None:
            print(f"unknown dataset number: {requested_id}")
            return 1
        dataset = _build_dataset_info(dataset_item, display_id=requested_id)
        if dataset is None:
            print(f"unknown dataset number: {requested_id}")
            return 1

        print(f"Target dataset versions path: {index_path}")
        print()
        print(f"ID: {dataset.dataset_id}")
        print(f"名称: {dataset.name}")
        print(f"数据量: {dataset.size}")
        print(f"简要说明: {dataset.summary}")
        print(f"目标路径: {dataset.target_path}")

        parent_context = _format_parent_context(root_items, all_items, dataset_item)
        if parent_context is not None:
            print()
            print(parent_context, end="")

        related_versions = _format_related_derived_versions(dataset_item)
        if related_versions is not None:
            print()
            print(related_versions, end="")

        detail_section = _get_detail_markdown_with_fallback(all_items, dataset_item)
        if detail_section is not None:
            print()
            print(detail_section, end="")
        return 0

    datasets = _read_datasets(index_path, only_marked=not args.full)
    print(f"Target dataset versions path: {index_path}")
    print("id | 名称 | 数据量 | 简要说明")
    for dataset in datasets:
        print(f"{dataset.dataset_id} | {dataset.name} | {dataset.size} | {dataset.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
