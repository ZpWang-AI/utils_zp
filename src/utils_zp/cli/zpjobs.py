from __future__ import annotations

"""Print the current user-level jobs entry summary."""

import argparse
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[3]
JOBS_PATH = REPO_ROOT / "agent_zp" / "jobs.agent.md"
JOB_HEADER_RE = re.compile(r"^##\s+(\d+)\.\s+(.+?)\s*$")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zpjobs",
        description="Show a concise summary of agent jobs.",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Print the full jobs.agent.md content instead of the concise summary.",
    )
    return parser


def extract_job_titles(content: str) -> list[tuple[int, str]]:
    jobs: list[tuple[int, str]] = []
    for line in content.splitlines():
        match = JOB_HEADER_RE.match(line)
        if match:
            jobs.append((int(match.group(1)), match.group(2)))
    return jobs


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not JOBS_PATH.exists():
        print(f"missing jobs file: {JOBS_PATH}")
        return 1

    content = JOBS_PATH.read_text(encoding="utf-8")
    if args.full:
        print(f"Jobs Entry Path: {JOBS_PATH}\n")
        print(content, end="")
        return 0

    jobs = extract_job_titles(content)
    print("Agent jobs:")
    for index, title in jobs:
        print(f"{index}. {title}")
    print(f"\nFull doc: {JOBS_PATH}")
    print("Use `zpjobs --full` to print the full document.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
