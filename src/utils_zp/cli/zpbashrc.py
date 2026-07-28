from __future__ import annotations

"""Interactive installer for utils_zp shell config.

This command prints the target paths, asks whether to update, and then
ensures `~/.bashrc` sources both `bashrc_zp.sh` and `bashrc_zp.local.sh`.
"""

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SHELL_DIR = REPO_ROOT / "shell"
BASHRC_ZP_PATH = SHELL_DIR / "bashrc_zp.sh"
BASHRC_ZP_LOCAL_PATH = SHELL_DIR / "bashrc_zp.local.sh"
HOME_BASHRC_PATH = Path.home() / ".bashrc"

def main() -> int:
    print("=== Bashrc Updater ===")
    print("Add utils_zp shell config to a bashrc file.")
    print(f"target bashrc: {HOME_BASHRC_PATH}")
    print(f"source script: {BASHRC_ZP_PATH}")
    print(f"local script:  {BASHRC_ZP_LOCAL_PATH}")
    print()

    if sys.platform != "linux":
        print(f"unsupported platform: {sys.platform}")
        return 1

    if not BASHRC_ZP_PATH.exists():
        print(f"missing shell script: {BASHRC_ZP_PATH}")
        return 1

    while True:
        confirm = input("Update the bashrc file now? (y/n): ").strip().lower()
        if confirm in {"y", "yes"}:
            break
        if confirm in {"n", "no"}:
            print("Operation cancelled")
            return 0
        print("Please enter 'y' or 'n'")

    changed = update_bashrc(HOME_BASHRC_PATH)
    if changed:
        print("Successfully updated")
    else:
        print("Already updated")

    print()
    print("Run this command to apply changes:")
    print(f"  source {HOME_BASHRC_PATH}")
    return 0


def update_bashrc(bashrc_path: Path) -> bool:
    BASHRC_ZP_LOCAL_PATH.touch(exist_ok=True)

    try:
        lines = bashrc_path.read_text(encoding="utf-8").splitlines(keepends=True)
    except FileNotFoundError:
        lines = []

    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    elif not lines:
        lines = ["\n"]

    source_line_a = f". {BASHRC_ZP_PATH}\n"
    source_line_b = f". {BASHRC_ZP_LOCAL_PATH}\n"

    changed_a = _upsert_source_line(lines, "bashrc_zp.sh", source_line_a)
    changed_b = _upsert_source_line(lines, "bashrc_zp.local.sh", source_line_b)

    bashrc_path.parent.mkdir(parents=True, exist_ok=True)
    bashrc_path.write_text("".join(lines), encoding="utf-8")
    return changed_a or changed_b


def _upsert_source_line(lines: list[str], marker: str, new_line: str) -> bool:
    for index, line in enumerate(lines):
        if marker in line:
            if line != new_line:
                lines[index] = new_line
                return True
            return False

    lines.append(new_line)
    return True


if __name__ == "__main__":
    raise SystemExit(main())
