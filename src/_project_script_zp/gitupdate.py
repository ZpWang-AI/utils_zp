import sys
from pathlib import Path
from utils_zp import git_update


def gitupdate_cmd():
    """
    Command line interface for gitupdate.
    
    Behavior:
    - If no argument: print help and exit
    - If argument provided: silently execute git_update with that repo_path
    """
    
    # Define help information (only shown when no arguments)
    if len(sys.argv) == 1:
        help_text = f"""=== gitupdate ===
Update repository: pull from and push to remotes (branch main)
Ignore remote if remote name starts with '_'

Usage:
  gitupdate REPO_PATH

Examples:
  gitupdate .
  gitupdate ./abc
"""
        print(help_text)
        return
    
    # Execute silently when argument is provided
    repo_path = sys.argv[1]
    git_update(repo_path)


if __name__ == "__main__":
    gitupdate_cmd()