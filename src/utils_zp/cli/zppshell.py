from __future__ import annotations

import argparse
import json
from typing import Sequence

from utils_zp.parallel_shell import TaskSpec, generate_parallel_shell, parse_task_spec


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zppshell",
        description="Generate a bash script that launches multiple tasks on specified GPUs in parallel.",
    )
    parser.add_argument("--output", required=True, help="Path to the generated shell script.")
    parser.add_argument(
        "--task",
        action="append",
        default=[],
        help="Task spec in the form 'name|gpu|command'. Repeat this flag for multiple tasks.",
    )
    parser.add_argument(
        "--workdir",
        default=".",
        help="Working directory used inside the generated shell before each task command runs.",
    )
    parser.add_argument(
        "--job-name",
        default=None,
        help="Optional job name used in the log directory. Defaults to the output filename stem.",
    )
    parser.add_argument(
        "--log-root",
        default=None,
        help="Optional log root directory. Defaults to '<workdir>/tmp/logs'.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the output shell if it already exists.",
    )
    parser.add_argument(
        "--allow-gpu-reuse",
        action="store_true",
        help="Allow multiple tasks to target the same GPU. By default duplicated GPU ids are rejected.",
    )
    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.task:
        parser.error("At least one --task is required.")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    tasks: list[TaskSpec] = [parse_task_spec(item) for item in args.task]
    summary = generate_parallel_shell(
        output=args.output,
        tasks=tasks,
        workdir=args.workdir,
        job_name=args.job_name,
        log_root=args.log_root,
        overwrite=bool(args.overwrite),
        allow_gpu_reuse=bool(args.allow_gpu_reuse),
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
