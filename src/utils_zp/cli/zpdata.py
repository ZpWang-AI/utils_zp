from __future__ import annotations

"""List marked datasets from the configured dataset index."""

import argparse
from dataclasses import dataclass
from pathlib import Path

from .. import setting
from ._numbered_sections import extract_numbered_section


TABLE_HEADER = "| ID | 版本名 |"


@dataclass(frozen=True)
class DatasetInfo:
    dataset_id: str
    name: str
    size: str
    summary: str


def _strip_cell(text: str) -> str:
    return text.strip().strip("`")


def collect_datasets(index_path: Path) -> list[DatasetInfo]:
    lines = index_path.read_text(encoding="utf-8").splitlines()

    start_index: int | None = None
    for index, line in enumerate(lines):
        if TABLE_HEADER in line:
            start_index = index + 2
            break

    if start_index is None:
        raise ValueError(f"missing dataset table: {index_path}")

    datasets: list[DatasetInfo] = []
    for line in lines[start_index:]:
        stripped = line.strip()
        if not stripped.startswith("|"):
            break

        cells = [cell.strip() for cell in stripped.split("|")[1:-1]]
        if len(cells) < 5:
            continue

        dataset_id = _strip_cell(cells[0])
        name = _strip_cell(cells[1])
        size = _strip_cell(cells[2])
        summary = _strip_cell(cells[3])
        mark = _strip_cell(cells[4])
        if not dataset_id or not name or not size or not summary or mark != "是":
            continue

        datasets.append(
            DatasetInfo(
                dataset_id=dataset_id,
                name=name,
                size=size,
                summary=summary,
            )
        )

    return datasets


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zpdata",
        description="Show marked datasets from data/dataset_versions.md.",
    )
    parser.add_argument(
        "dataset_number",
        nargs="?",
        type=int,
        help="Print the selected dataset detail by number, for example: zpdata 7",
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

    content = index_path.read_text(encoding="utf-8")
    datasets = collect_datasets(index_path)
    if args.dataset_number is not None:
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

        detail_section = extract_numbered_section(content, args.dataset_number)
        if detail_section is not None:
            print()
            print(detail_section, end="")
        return 0

    print(f"Target dataset versions path: {index_path}")
    print("id | 名称 | 数据量 | 简要说明")
    for dataset in datasets:
        print(f"{dataset.dataset_id} | {dataset.name} | {dataset.size} | {dataset.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
