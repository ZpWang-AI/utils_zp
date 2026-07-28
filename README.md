# Utils_zp

Utilities used by zpwang.

main(v1) branch: old version, last updated in 2026-7-28.
v2 branch: new version, based on LLM agents.

Current CLI commands:
- `zp`: show package name, version, and available commands
- `zpbashrc`: install shared bashrc hooks into `~/.bashrc`
- `zpburn`: start GPU idle burn on a physical GPU, requires `torch`
- `zprules`: print the full path of `agent_zp/README.agent.md`, then print its content

## Install

This repo currently supports **editable install only**.

Reason:
- `zpbashrc` reads `shell/bashrc_zp.sh`
- `zprules` reads `agent_zp/README.agent.md`
- these commands currently depend on repo-relative resources, so non-editable install is not supported

Use:

~~~sh
# git clone repo
git clone -b v2 --single-branch --depth 1 git@ssh.github.com:ZpWang-AI/utils_zp.git
# or
git clone -b v2 --single-branch --depth 1 https://github.com/ZpWang-AI/utils_zp.git

# install (editable only)
pip install -e utils_zp

# show new cmds
zp

# print current user agent rules
zprules
~~~
