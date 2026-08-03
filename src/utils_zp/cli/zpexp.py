from __future__ import annotations

"""List experiments under the configured exp directory."""

import argparse
from dataclasses import dataclass
from pathlib import Path
import re

from .. import setting
from ._yaml_index import (
    get_detail_markdown,
    get_target_path,
    is_marked,
    load_yaml_items,
    normalize_version_id,
    set_mark_status,
)


PROGRESS_RE = re.compile(r"^(?P<done>\d+)[/／](?P<total>\d+)$")
EXP_VERSIONS_FILE = "exp_versions.yaml"


def _importance_sort_key(importance: str) -> tuple[int, int | str]:
    normalized = importance.strip().upper()
    if normalized.startswith("T") and normalized[1:].isdigit():
        return (0, int(normalized[1:]))
    chinese_rank = {"高": 0, "中": 1, "低": 2}
    if importance in chinese_rank:
        return (1, chinese_rank[importance])
    return (2, normalized)


@dataclass(frozen=True)
class ExperimentInfo:
    exp_id: str
    importance: str
    name: str
    progress: str
    summary: str
    target_path: str


def _normalize_progress(progress: str) -> str:
    match = PROGRESS_RE.fullmatch(progress.strip())
    if match is None:
        return progress.strip()
    return f"{match.group('done')}/{match.group('total')}"


def _read_exp_versions(exp_root: Path, *, only_marked: bool = True) -> list[ExperimentInfo]:
    versions_path = exp_root / EXP_VERSIONS_FILE
    if not versions_path.exists():
        raise ValueError(f"missing exp versions file: {versions_path}")

    experiments: list[ExperimentInfo] = []
    for item in load_yaml_items(versions_path):
        exp_id = normalize_version_id(item.get("id", ""))
        importance = str(item.get("importance", "")).strip()
        name = str(item.get("name", "")).strip()
        progress = _normalize_progress(str(item.get("progress", "")).strip())
        summary = str(item.get("summary", "")).strip()
        target_path = get_target_path(item)
        if not (exp_id and importance and name and progress and summary and target_path):
            continue
        if only_marked and not is_marked(item):
            continue

        experiments.append(
            ExperimentInfo(
                exp_id=exp_id,
                importance=importance,
                name=name,
                progress=progress,
                summary=summary,
                target_path=target_path,
            )
        )

    return experiments


def collect_experiments(exp_root: Path) -> list[ExperimentInfo]:
    return sorted(_read_exp_versions(exp_root), key=lambda experiment: int(experiment.exp_id))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zpexp",
        description="Show marked experiments from exp/exp_versions.yaml.",
    )
    parser.add_argument(
        "exp_number",
        nargs="?",
        type=int,
        help="Print the selected experiment detail by number, for example: zpexp 4",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="List all experiments, including unmarked ones.",
    )
    mark_group = parser.add_mutually_exclusive_group()
    mark_group.add_argument(
        "-m",
        "--mark",
        dest="mark_number",
        type=int,
        help="Mark the selected experiment by id, for example: zpexp -m 3",
    )
    mark_group.add_argument(
        "-um",
        "--unmark",
        dest="unmark_number",
        type=int,
        help="Unmark the selected experiment by id, for example: zpexp -um 3",
    )
    return parser


def _find_experiment(experiments: list[ExperimentInfo], exp_number: int) -> ExperimentInfo | None:
    for experiment in experiments:
        if int(experiment.exp_id) == exp_number:
            return experiment
    return None


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    versions_path = setting.TARGET_EXP_PATH / EXP_VERSIONS_FILE
    if not versions_path.exists():
        print(f"missing exp versions file: {versions_path}")
        return 1

    if args.mark_number is not None:
        try:
            item = set_mark_status(versions_path, args.mark_number, True)
        except ValueError:
            print(f"unknown exp number: {args.mark_number}")
            return 1
        print(f"marked exp {normalize_version_id(item.get('id', ''))}: {item.get('name', '')}")
        return 0

    if args.unmark_number is not None:
        try:
            item = set_mark_status(versions_path, args.unmark_number, False)
        except ValueError:
            print(f"unknown exp number: {args.unmark_number}")
            return 1
        print(f"unmarked exp {normalize_version_id(item.get('id', ''))}: {item.get('name', '')}")
        return 0

    if args.exp_number is not None:
        experiments = _read_exp_versions(setting.TARGET_EXP_PATH, only_marked=False)
        experiment = _find_experiment(experiments, args.exp_number)
        if experiment is None:
            print(f"unknown exp number: {args.exp_number}")
            return 1

        print(f"Target exp versions path: {versions_path}")
        print()
        print(f"ID: {experiment.exp_id}")
        print(f"名称: {experiment.name}")
        print(f"重要性: {experiment.importance}")
        print(f"进度: {experiment.progress}")
        print(f"简要说明: {experiment.summary}")
        print(f"目标路径: {experiment.target_path}")

        detail_section = None
        for item in load_yaml_items(versions_path):
            if normalize_version_id(item.get("id", "")) == experiment.exp_id:
                detail_section = get_detail_markdown(item)
                break
        if detail_section is not None:
            print()
            print(detail_section, end="")
        return 0

    experiments = sorted(
        _read_exp_versions(setting.TARGET_EXP_PATH, only_marked=not args.full),
        key=lambda experiment: int(experiment.exp_id),
    )
    print(f"Target exp versions path: {versions_path}")
    print("id | 重要性 | 进度 | 名称 | 简要说明")
    for experiment in experiments:
        print(
            f"{experiment.exp_id} | {experiment.importance} | {experiment.progress} | "
            f"{experiment.name} | {experiment.summary}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
