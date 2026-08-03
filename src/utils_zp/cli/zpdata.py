from __future__ import annotations

"""List marked datasets from the configured dataset index."""

import argparse
from dataclasses import dataclass
from pathlib import Path

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


def _read_datasets(index_path: Path, *, only_marked: bool = True) -> list[DatasetInfo]:
    datasets: list[DatasetInfo] = []
    for item in load_yaml_items(index_path):
        dataset_id = normalize_version_id(item.get("id", ""))
        name = str(item.get("name", "")).strip()
        size = str(item.get("size", "")).strip()
        summary = str(item.get("summary", "")).strip()
        target_path = get_target_path(item)
        if not dataset_id or not name or not size or not summary or not target_path:
            continue
        if only_marked and not is_marked(item):
            continue

        datasets.append(
            DatasetInfo(
                dataset_id=dataset_id,
                name=name,
                size=size,
                summary=summary,
                target_path=target_path,
            )
        )

    return datasets


def collect_datasets(index_path: Path) -> list[DatasetInfo]:
    return _read_datasets(index_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zpdata",
        description="Show marked datasets from data/dataset_versions.yaml.",
    )
    parser.add_argument(
        "dataset_number",
        nargs="?",
        type=int,
        help="Print the selected dataset detail by number, for example: zpdata 7",
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
        type=int,
        help="Mark the selected dataset by id, for example: zpdata -m 7",
    )
    mark_group.add_argument(
        "-um",
        "--unmark",
        dest="unmark_number",
        type=int,
        help="Unmark the selected dataset by id, for example: zpdata -um 7",
    )
    return parser


def _find_dataset(datasets: list[DatasetInfo], dataset_number: int) -> DatasetInfo | None:
    for dataset in datasets:
        if int(dataset.dataset_id) == dataset_number:
            return dataset
    return None


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    index_path = setting.TARGET_DATASET_VERSIONS_PATH
    if not index_path.exists():
        print(f"missing dataset versions file: {index_path}")
        return 1

    if args.mark_number is not None:
        try:
            item = set_mark_status(index_path, args.mark_number, True)
        except ValueError:
            print(f"unknown dataset number: {args.mark_number}")
            return 1
        print(f"marked dataset {normalize_version_id(item.get('id', ''))}: {item.get('name', '')}")
        return 0

    if args.unmark_number is not None:
        try:
            item = set_mark_status(index_path, args.unmark_number, False)
        except ValueError:
            print(f"unknown dataset number: {args.unmark_number}")
            return 1
        print(f"unmarked dataset {normalize_version_id(item.get('id', ''))}: {item.get('name', '')}")
        return 0

    if args.dataset_number is not None:
        datasets = _read_datasets(index_path, only_marked=False)
        dataset = _find_dataset(datasets, args.dataset_number)
        if dataset is None:
            print(f"unknown dataset number: {args.dataset_number}")
            return 1

        print(f"Target dataset versions path: {index_path}")
        print()
        print(f"ID: {dataset.dataset_id}")
        print(f"名称: {dataset.name}")
        print(f"数据量: {dataset.size}")
        print(f"简要说明: {dataset.summary}")
        print(f"目标路径: {dataset.target_path}")

        detail_section = None
        for item in load_yaml_items(index_path):
            if normalize_version_id(item.get("id", "")) == dataset.dataset_id:
                detail_section = get_detail_markdown(item)
                break
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
