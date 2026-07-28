from __future__ import annotations

"""CLI entrypoint for GPU stress testing.

Run `zpburn <gpu_id>` to start the idle-burn controller on one physical GPU.
"""

import argparse

from tqdm import tqdm

from ..cuda.idle_burn import stress_gpu_to_target_usage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zpburn",
        description="Start idle_burn on one physical GPU.",
    )
    parser.add_argument(
        "gpu_id",
        type=int,
        help="Physical GPU index shown by nvidia-smi.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    progress = tqdm()
    try:
        stress_gpu_to_target_usage(
            gpu_id=args.gpu_id,
            progress_callback=progress.update,
        )
    except KeyboardInterrupt:
        print("\nStopped")
        return 130
    finally:
        progress.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
