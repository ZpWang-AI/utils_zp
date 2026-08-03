from __future__ import annotations

"""List supported checkpoints from the configured checkpoint registry."""

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
class CheckpointInfo:
    checkpoint_id: str
    name: str
    parameter_size: str
    summary: str
    target_path: str


def _read_checkpoints(index_path: Path, *, only_marked: bool = True) -> list[CheckpointInfo]:
    checkpoints: list[CheckpointInfo] = []
    for item in load_yaml_items(index_path):
        checkpoint_id = normalize_version_id(item.get("id", ""))
        name = str(item.get("name", "")).strip()
        parameter_size = str(item.get("parameter_size", "")).strip()
        summary = str(item.get("summary", "")).strip()
        target_path = get_target_path(item)
        if not checkpoint_id or not name or not parameter_size or not summary or not target_path:
            continue
        if only_marked and not is_marked(item):
            continue

        checkpoints.append(
            CheckpointInfo(
                checkpoint_id=checkpoint_id,
                name=name,
                parameter_size=parameter_size,
                summary=summary,
                target_path=target_path,
            )
        )
    return checkpoints


def collect_checkpoints(index_path: Path | None = None) -> list[CheckpointInfo]:
    resolved_index_path = index_path or setting.TARGET_CHECKPOINT_VERSIONS_PATH
    return _read_checkpoints(resolved_index_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zpckpt",
        description="Show supported checkpoints from model/checkpoint_versions.yaml.",
    )
    parser.add_argument(
        "checkpoint_number",
        nargs="?",
        type=int,
        help="Print the selected checkpoint detail by number, for example: zpckpt 2",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="List all checkpoints, including unmarked ones.",
    )
    mark_group = parser.add_mutually_exclusive_group()
    mark_group.add_argument(
        "-m",
        "--mark",
        dest="mark_number",
        type=int,
        help="Mark the selected checkpoint by id, for example: zpckpt -m 2",
    )
    mark_group.add_argument(
        "-um",
        "--unmark",
        dest="unmark_number",
        type=int,
        help="Unmark the selected checkpoint by id, for example: zpckpt -um 2",
    )
    return parser


def _find_checkpoint(
    checkpoints: list[CheckpointInfo], checkpoint_number: int
) -> CheckpointInfo | None:
    for checkpoint in checkpoints:
        if int(checkpoint.checkpoint_id) == checkpoint_number:
            return checkpoint
    return None


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    index_path = setting.TARGET_CHECKPOINT_VERSIONS_PATH
    if not index_path.exists():
        print(f"missing checkpoint versions file: {index_path}")
        return 1

    if args.mark_number is not None:
        try:
            item = set_mark_status(index_path, args.mark_number, True)
        except ValueError:
            print(f"unknown checkpoint number: {args.mark_number}")
            return 1
        print(f"marked checkpoint {normalize_version_id(item.get('id', ''))}: {item.get('name', '')}")
        return 0

    if args.unmark_number is not None:
        try:
            item = set_mark_status(index_path, args.unmark_number, False)
        except ValueError:
            print(f"unknown checkpoint number: {args.unmark_number}")
            return 1
        print(f"unmarked checkpoint {normalize_version_id(item.get('id', ''))}: {item.get('name', '')}")
        return 0

    if args.checkpoint_number is not None:
        checkpoints = _read_checkpoints(index_path, only_marked=False)
        checkpoint = _find_checkpoint(checkpoints, args.checkpoint_number)
        if checkpoint is None:
            print(f"unknown checkpoint number: {args.checkpoint_number}")
            return 1

        detail_section = None
        for item in load_yaml_items(index_path):
            if normalize_version_id(item.get("id", "")) == checkpoint.checkpoint_id:
                detail_section = get_detail_markdown(item)
                break

        print(f"Target checkpoint versions path: {index_path}")
        print()
        print(f"ID: {checkpoint.checkpoint_id}")
        print(f"名称: {checkpoint.name}")
        print(f"参数量: {checkpoint.parameter_size}")
        print(f"简要说明: {checkpoint.summary}")
        print(f"目标路径: {checkpoint.target_path}")
        if detail_section is not None:
            print()
            print(detail_section, end="")
        return 0

    checkpoints = _read_checkpoints(index_path, only_marked=not args.full)
    print(f"Target checkpoint versions path: {index_path}")
    print("id | 名称 | 参数量 | 简要说明")
    for checkpoint in checkpoints:
        print(f"{checkpoint.checkpoint_id} | {checkpoint.name} | {checkpoint.parameter_size} | {checkpoint.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
