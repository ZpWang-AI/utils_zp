from __future__ import annotations

"""List marked pretrained models from the configured model index."""

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
class PretrainedModelInfo:
    model_id: str
    name: str
    parameter_size: str
    summary: str
    target_path: str


def _read_pretrained_models(
    index_path: Path, *, only_marked: bool = True
) -> list[PretrainedModelInfo]:
    models: list[PretrainedModelInfo] = []
    for item in load_yaml_items(index_path):
        model_id = normalize_version_id(item.get("id", ""))
        name = str(item.get("name", "")).strip()
        parameter_size = str(item.get("parameter_size", "")).strip()
        summary = str(item.get("summary", "")).strip()
        target_path = get_target_path(item)
        if not model_id or not name or not parameter_size or not summary or not target_path:
            continue
        if only_marked and not is_marked(item):
            continue

        models.append(
            PretrainedModelInfo(
                model_id=model_id,
                name=name,
                parameter_size=parameter_size,
                summary=summary,
                target_path=target_path,
            )
        )

    return models


def collect_pretrained_models(index_path: Path) -> list[PretrainedModelInfo]:
    return _read_pretrained_models(index_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zppremodel",
        description="Show marked pretrained models from pretrained_models/model_versions.yaml.",
    )
    parser.add_argument(
        "model_number",
        nargs="?",
        type=int,
        help="Print the selected pretrained model detail by number, for example: zppremodel 3",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="List all models, including unmarked ones.",
    )
    mark_group = parser.add_mutually_exclusive_group()
    mark_group.add_argument(
        "-m",
        "--mark",
        dest="mark_number",
        type=int,
        help="Mark the selected model by id, for example: zppremodel -m 3",
    )
    mark_group.add_argument(
        "-um",
        "--unmark",
        dest="unmark_number",
        type=int,
        help="Unmark the selected model by id, for example: zppremodel -um 3",
    )
    return parser


def _find_pretrained_model(
    models: list[PretrainedModelInfo], model_number: int
) -> PretrainedModelInfo | None:
    for model in models:
        if int(model.model_id) == model_number:
            return model
    return None


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    index_path = setting.TARGET_PRETRAINED_MODEL_VERSIONS_PATH
    if not index_path.exists():
        print(f"missing pretrained model versions file: {index_path}")
        return 1

    if args.mark_number is not None:
        try:
            item = set_mark_status(index_path, args.mark_number, True)
        except ValueError:
            print(f"unknown pretrained model number: {args.mark_number}")
            return 1
        print(f"marked pretrained model {normalize_version_id(item.get('id', ''))}: {item.get('name', '')}")
        return 0

    if args.unmark_number is not None:
        try:
            item = set_mark_status(index_path, args.unmark_number, False)
        except ValueError:
            print(f"unknown pretrained model number: {args.unmark_number}")
            return 1
        print(f"unmarked pretrained model {normalize_version_id(item.get('id', ''))}: {item.get('name', '')}")
        return 0

    if args.model_number is not None:
        models = _read_pretrained_models(index_path, only_marked=False)
        model = _find_pretrained_model(models, args.model_number)
        if model is None:
            print(f"unknown pretrained model number: {args.model_number}")
            return 1

        print(f"Target pretrained model versions path: {index_path}")
        print()
        print(f"ID: {model.model_id}")
        print(f"模型名: {model.name}")
        print(f"参数量: {model.parameter_size}")
        print(f"简要说明: {model.summary}")
        print(f"目标路径: {model.target_path}")

        detail_section = None
        for item in load_yaml_items(index_path):
            if normalize_version_id(item.get("id", "")) == model.model_id:
                detail_section = get_detail_markdown(item)
                break
        if detail_section is not None:
            print()
            print(detail_section, end="")
        return 0

    models = _read_pretrained_models(index_path, only_marked=not args.full)
    print(f"Target pretrained model versions path: {index_path}")
    print("id | 名称 | 参数量 | 简要说明")
    for model in models:
        print(f"{model.model_id} | {model.name} | {model.parameter_size} | {model.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
