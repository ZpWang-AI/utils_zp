# Utils_zp

Utilities used by zpwang.

main(v1) branch: old version, last updated in 2026-7-28.
v2 branch: new version, based on LLM agents.

Current CLI commands:
- `zp`: show package name, version, and available commands
- `zpbashrc`: install shared bashrc hooks into `~/.bashrc`, including shared tmux shell defaults
- `zpburn`: start GPU idle burn on a physical GPU, requires `torch`
- `zpdata`: show marked datasets from `data/dataset_versions.md`; use `zpdata 7` to print one dataset detail
- `zpexp`: show marked experiments from `exp/exp_versions.md`; use `zpexp 4` to print one experiment detail
- `zpjobs`: show a concise list of agent jobs; use `zpjobs 4` to print one job section, or `zpjobs --full` for the full document
- `zppremodel` / `zppremodels`: show marked pretrained models from `pretrained_models/model_versions.md`; use `zppremodel 3` to print one model detail
- `zprules`: print the full path of `agent_zp/README.agent.md`, then print its content

Optional runtime dependencies:
- plotting monitor logs with `utils_zp.plot_monitor_log()` requires `matplotlib`
- running `zpburn` requires `torch`

## Install

This repo currently supports **editable install only**.

Reason:
- `zpbashrc` reads `shell/bashrc_zp.sh`
- `zpjobs` reads `agent_zp/jobs.agent.md`
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

# print current user agent jobs
zpjobs

# print one dataset detail
zpdata 7

# print one experiment detail
zpexp 4

# print one job and its description
zpjobs 4

# print one pretrained model detail
zppremodels 3

# print the full jobs document when needed
zpjobs --full

# print current user agent rules
zprules
~~~

## Feishu docs

For Feishu doc/wiki reading and writing, use the authenticated `lark-cli` workflow as the default path. Keep `utils_zp` focused on local CLI helpers and do not route Feishu sync through browser automation prechecks in this repo.
