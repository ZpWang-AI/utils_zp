# Utils_zp

Utilities used by zpwang.

main(v1) branch: old version, last updated in 2026-7-28.
v2 branch: new version, based on LLM agents.

Current CLI commands:
- `zp`: show package name, version, and available commands
- `zpbashrc`: install shared bashrc hooks into `~/.bashrc`
- `zpburn`: start GPU idle burn on a physical GPU
- `zprules`: print `agent_zp/README.agent.md`

~~~sh
# git clone repo
git clone -b v2 --single-branch --depth 1 git@ssh.github.com:ZpWang-AI/utils_zp.git
# or
git clone -b v2 --single-branch --depth 1 https://github.com/ZpWang-AI/utils_zp.git

# install
pip install -e utils_zp

# show new cmds
zp

# print current user agent rules
zprules
~~~
