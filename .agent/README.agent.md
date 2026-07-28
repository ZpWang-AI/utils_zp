# utils_zp (UZP)

本文件用于帮助人或 agent 快速接手 `utils_zp`（下文简称 `UZP`）仓库：先找对入口，再按任务类型分流，最后进入对应模块和常用命令。

## 重要先读

- 工作区级 agent 注意事项：`/mnt/bn/motor-search2/wzp/repos/utils_zp/agent_zp/workspace/wzp/README.agent.md`
- workspace 通用协作约定：`/mnt/bn/motor-search2/wzp/repos/utils_zp/agent_zp/workspace/README.agent.md`
- 用户级通用 agent 规则：`/mnt/bn/motor-search2/wzp/repos/utils_zp/agent_zp/README.agent.md`
- 总结者约定：`/mnt/bn/motor-search2/wzp/repos/utils_zp/agent_zp/summarizer.agent.md`
- repo 内补充资料入口：`.agent/doc/README.agent.md`
- 正常开发记录：`.agent/PROGRESS.agent.md`
- issue 修复记录、待处理改进和已知限制：`.agent/ISSUE.agent.md`
- 重复性事件追踪：`.agent/ROUTINE.agent.md`
- 仓库命令入口：`README.md`、`pyproject.toml`
- CLI 代码入口：`src/utils_zp/cli/`
- CUDA 工具入口：`src/utils_zp/cuda/README.md`
- shell 配置入口：`shell/bashrc_zp.sh`

## 任务分流

1. 先按 `agent_zp/workspace/README.agent.md` 与 `agent_zp/workspace/wzp/README.agent.md` 理解通用协作规则、记录方式和环境边界
2. 再判断是“正常开发”还是“修 issue”：正常开发看 `.agent/PROGRESS.agent.md`，修 issue 看 `.agent/ISSUE.agent.md`
3. 最后按代码范围继续分流：CLI 相关基本在 `src/utils_zp/cli/`；GPU 工具相关基本在 `src/utils_zp/cuda/`；shell 初始化相关基本在 `shell/`
4. 不要一上来全仓库乱搜，先按“规则入口 + 任务类型 + 目录入口”分流
5. 如果用户要求“先记一下”某件事，但它不属于某个具体 repo 的代码 issue，而是通用协作提醒、跨 repo 待办或后续跟踪事项，统一补记到本仓 `.agent/ISSUE.agent.md`

## 项目概况

- `utils_zp` 当前定位是面向 agent / CLI 的轻量工具仓，优先提供简单直接的命令入口，而不是堆叠过多兼容层
- 当前已落地的 CLI 包括：
  - `zp`：展示包信息和命令列表
  - `zpbashrc`：把共享 shell 配置接入用户 `~/.bashrc`
  - `zpburn`：启动 GPU idle burn
  - `zprules`：输出当前 agent 规则入口路径和内容
- 当前已成型的代码模块主要有：
  - `src/utils_zp/cli/`：CLI 入口与交互逻辑
  - `src/utils_zp/cuda/`：GPU 查询、选卡、监控、占卡和压测工具
  - `shell/`：共享 bashrc 脚本
  - `agent_zp/`：用户级 / workspace 级 agent 规则
- 当前仓库优先保持小而清晰：能写成单一职责脚本或简单模块时，不要过早引入复杂抽象

## 主要目录

- `src/utils_zp/cli/`：CLI 命令实现
- `src/utils_zp/cuda/`：GPU 工具模块与说明文档
- `shell/`：shell 初始化脚本
- `agent_zp/`：用户级和 workspace 级 agent 规则入口
- `.agent/`：repo 级协作入口、进展、issue 和 routine 记录

## 常用入口

- 查看可用命令：`zp`
- 打印当前用户级规则：`zprules`
- 安装共享 bashrc：`zpbashrc`
- 启动 GPU idle burn：`zpburn <gpu_id>`
- 模块化执行规则打印：`python -m utils_zp.cli.zprules`
- 可编辑安装：`pip install -e .`
