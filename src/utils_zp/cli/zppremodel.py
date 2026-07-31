from __future__ import annotations

"""List marked pretrained models from the configured model index."""

import argparse
from dataclasses import dataclass
from pathlib import Path

from .. import setting
from ._numbered_sections import extract_numbered_section


TABLE_HEADER = "| ID | 模型名 |"


@dataclass(frozen=True)
class PretrainedModelInfo:
    model_id: str
    name: str
    parameter_size: str


def _strip_cell(text: str) -> str:
    return text.strip().strip("`")


def collect_pretrained_models(index_path: Path) -> list[PretrainedModelInfo]:
    lines = index_path.read_text(encoding="utf-8").splitlines()

    start_index: int | None = None
    for index, line in enumerate(lines):
        if TABLE_HEADER in line:
            start_index = index + 2
            break

    if start_index is None:
        raise ValueError(f"missing pretrained model table: {index_path}")

    models: list[PretrainedModelInfo] = []
    for line in lines[start_index:]:
        stripped = line.strip()
        if not stripped.startswith("|"):
            break

        cells = [cell.strip() for cell in stripped.split("|")[1:-1]]
        if len(cells) < 4:
            continue

        model_id = _strip_cell(cells[0])
        name = _strip_cell(cells[1])
        parameter_size = _strip_cell(cells[2])
        mark = _strip_cell(cells[3])
        if not model_id or not name or not parameter_size or mark != "是":
            continue

        models.append(
            PretrainedModelInfo(
                model_id=model_id,
                name=name,
                parameter_size=parameter_size,
            )
        )

    return models


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zppremodel",
        description="Show marked pretrained models from pretrained_models/model_versions.md.",
    )
    parser.add_argument(
        "model_number",
        nargs="?",
        type=int,
        help="Print the selected pretrained model detail by number, for example: zppremodel 3",
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

    content = index_path.read_text(encoding="utf-8")
    models = collect_pretrained_models(index_path)
    if args.model_number is not None:
        model = _find_pretrained_model(models, args.model_number)
        if model is None:
            print(f"unknown pretrained model number: {args.model_number}")
            return 1

        print(f"Target pretrained model versions path: {index_path}")
        print()
        print(f"ID: {model.model_id}")
        print(f"模型名: {model.name}")
        print(f"参数量: {model.parameter_size}")

        detail_section = extract_numbered_section(content, args.model_number)
        if detail_section is not None:
            print()
            print(detail_section, end="")
        return 0

    print(f"Target pretrained model versions path: {index_path}")
    print("id | name | 参数量")
    for model in models:
        print(f"{model.model_id} | {model.name} | {model.parameter_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
