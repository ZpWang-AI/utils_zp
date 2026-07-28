from __future__ import annotations

"""Print the current user-level agent rules file."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
RULES_PATH = REPO_ROOT / "agent_zp" / "README.agent.md"


def main() -> int:
    if not RULES_PATH.exists():
        print(f"missing rules file: {RULES_PATH}")
        return 1

    print(f'Agent Entry Path: {RULES_PATH}\n')
    print(RULES_PATH.read_text(encoding="utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
