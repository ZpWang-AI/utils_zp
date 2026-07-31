from __future__ import annotations

"""List experiments under the configured exp directory."""

import argparse
from dataclasses import dataclass
from pathlib import Path
import re

from .. import setting
from ._numbered_sections import extract_numbered_section


PROGRESS_RE = re.compile(r"^(?P<done>\d+)[/／](?P<total>\d+)$")
TABLE_SEPARATOR_RE = re.compile(r"^:?-{3,}:?$")
EXP_VERSIONS_FILE = "exp_versions.md"
MARKED_VALUES = {"是", "yes", "true", "1", "y"}


@dataclass(frozen=True)
class ExperimentInfo:
    exp_id: str
    exp_path_id: str
    date_taskname: str
    importance: str
    name: str
    progress: str
    summary: str


def _normalize_progress(progress: str) -> str:
    match = PROGRESS_RE.fullmatch(progress.strip())
    if match is None:
        return progress.strip()
    return f"{match.group('done')}/{match.group('total')}"


def _split_markdown_row(line: str) -> list[str]:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return []
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def _is_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(TABLE_SEPARATOR_RE.fullmatch(cell) for cell in cells)


def _find_column_index(headers: list[str], keywords: tuple[str, ...]) -> int | None:
    normalized_headers = [header.replace("`", "").strip().lower() for header in headers]
    for index, header in enumerate(normalized_headers):
        if any(keyword in header for keyword in keywords):
            return index
    return None


def _read_exp_versions(exp_root: Path) -> list[ExperimentInfo]:
    versions_path = exp_root / EXP_VERSIONS_FILE
    if not versions_path.exists():
        raise ValueError(f"missing exp versions file: {versions_path}")

    lines = versions_path.read_text(encoding="utf-8").splitlines()
    header_cells: list[str] | None = None
    experiments: list[ExperimentInfo] = []

    for line in lines:
        cells = _split_markdown_row(line)
        if not cells:
            continue
        if header_cells is None:
            header_cells = cells
            continue
        if _is_separator_row(cells):
            continue

        id_index = _find_column_index(header_cells, ("id",))
        name_index = _find_column_index(header_cells, ("实验名", "名称"))
        importance_index = _find_column_index(header_cells, ("重要性",))
        progress_index = _find_column_index(header_cells, ("进度",))
        folder_index = _find_column_index(header_cells, ("文件夹", "date-taskname", "目录"))
        summary_index = _find_column_index(header_cells, ("简要说明", "说明", "摘要"))
        mark_index = _find_column_index(header_cells, ("标记",))
        if None in (id_index, importance_index, name_index, progress_index, folder_index, summary_index):
            break
        required_indexes = [id_index, importance_index, name_index, progress_index, folder_index, summary_index]
        if any(index >= len(cells) for index in required_indexes):
            continue

        if mark_index is not None:
            if mark_index >= len(cells):
                continue
            marked_value = cells[mark_index].replace("`", "").strip().lower()
            if marked_value not in MARKED_VALUES:
                continue

        exp_id = cells[id_index].replace("`", "").strip()
        importance = cells[importance_index].replace("`", "").strip()
        name = cells[name_index].replace("`", "").strip()
        progress = _normalize_progress(cells[progress_index].replace("`", "").strip())
        date_taskname = cells[folder_index].replace("`", "").strip()
        summary = cells[summary_index].replace("`", "").strip()
        if not (exp_id and importance and name and progress and date_taskname and summary):
            continue

        exp_path_id = f"{exp_id}-{date_taskname}"
        experiments.append(
            ExperimentInfo(
                exp_id=exp_id,
                exp_path_id=exp_path_id,
                date_taskname=date_taskname,
                importance=importance,
                name=name,
                progress=progress,
                summary=summary,
            )
        )

    return experiments


def collect_experiments(exp_root: Path) -> list[ExperimentInfo]:
    return _read_exp_versions(exp_root)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zpexp",
        description="Show marked experiments from exp/exp_versions.md.",
    )
    parser.add_argument(
        "exp_number",
        nargs="?",
        type=int,
        help="Print the selected experiment detail by number, for example: zpexp 4",
    )
    return parser


def _find_experiment(experiments: list[ExperimentInfo], exp_number: int) -> ExperimentInfo | None:
    for experiment in experiments:
        if int(experiment.exp_id) == exp_number:
            return experiment
    return None


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    exp_root = setting.TARGET_EXP_PATH
    if not exp_root.exists():
        print(f"missing exp path: {exp_root}")
        return 1

    versions_path = exp_root / EXP_VERSIONS_FILE
    if not versions_path.exists():
        print(f"missing exp versions file: {versions_path}")
        return 1

    content = versions_path.read_text(encoding="utf-8")
    experiments = collect_experiments(exp_root)
    if args.exp_number is not None:
        experiment = _find_experiment(experiments, args.exp_number)
        if experiment is None:
            print(f"unknown exp number: {args.exp_number}")
            return 1

        print(f"Target exp path: {exp_root}")
        print()
        print(f"ID: {experiment.exp_id}")
        print(f"名称: {experiment.name}")
        print(f"重要性: {experiment.importance}")
        print(f"进度: {experiment.progress}")
        print(f"目录: exp/{experiment.exp_path_id}/")
        print(f"简要说明: {experiment.summary}")

        detail_section = extract_numbered_section(content, args.exp_number)
        if detail_section is not None:
            print()
            print(detail_section, end="")
        return 0

    print(f"Target exp path: {exp_root}")
    print("id | 重要性 | 进度 | 名称 | 简要说明")
    for experiment in experiments:
        print(
            f"{experiment.exp_id} | {experiment.importance} | {experiment.progress} | "
            f"{experiment.name} | {experiment.summary}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
