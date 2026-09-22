# utils_zp (简称 UZP)

说明：这里只放仓库级入口，负责导航、任务分流和少量硬约束；专题说明与背景继续下沉到 `.agent/doc/` 或代码目录文档。

## 先看哪里

- 用户级规则：`../agent_zp/README.agent.md`
- workspace 规则：`../agent_zp/workspace/README.agent.md`、`../agent_zp/workspace/wzp/README.agent.md`
- 仓库协作主文档：`ISSUE.agent.md`、`PROGRESS.agent.md`、`JOBS.agent.md`
- repo 内专题入口：`doc/README.agent.md`
- 代码入口：`../src/utils_zp/cli/`、`../src/utils_zp/cuda/README.md`、`../shell/bashrc_zp.sh`
- 安装与公开说明：`../README.md`、`../pyproject.toml`

## 任务分流

1. 先确认 workspace 规则、环境边界和记录方式。
2. 再按任务类型分流：正常开发看 `PROGRESS.agent.md`，修 issue 看 `ISSUE.agent.md`，重复性工作先按用户级 `jobs` 分流，再看 `JOBS.agent.md` 中的本仓补充约定。
3. 再按代码范围下钻：CLI 相关看 `../src/utils_zp/cli/`，GPU 工具相关看 `../src/utils_zp/cuda/`，shell 初始化相关看 `../shell/`。
4. 跨 repo 的协作提醒、后续待办或不落在具体代码 issue 上的事项，统一补记到本仓 `ISSUE.agent.md`。

## 仓库定位

- `utils_zp` 是面向 agent / CLI 的轻量工具仓，优先提供直接可用的命令入口。
- 当前主要范围：CLI、CUDA 工具、共享 shell 配置，以及 `agent_zp/` 下的规则文档。
- 设计上优先保持小而清晰；能写成单一职责脚本或简单模块时，不提前堆复杂抽象。

## 硬约束

- 仓库级入口优先做“导航 + 分流 + 硬约束”；专题背景、历史过程和实现细节不要重新堆回本文件。
- 仓库内文档路径优先写相对路径，避免把绝对路径扩散到 repo 级入口。
- 执行重要命令时，优先把 stdout / stderr 重定向到就近 `tmp/` 日志文件，再结合日志和实际产物核对结果，不只看 Terminal 输出。
- 依赖 GPU 的压测、占卡和实验命令不要在当前环境直接执行；先整理命令、参数和预期产物，再放到对应 GPU 环境运行。
- 默认示例优先给源码入口；如果涉及安装方式或 repo 相对资源约束，以 `../README.md` 中的 editable-only 说明为准。
- 涉及飞书 doc/wiki 同步时，默认走已认证的 `lark-cli`；说明里聚焦认证、scope 和读写结果，不再引导到浏览器自动化前置检查。

## 最小命令索引

- 查看可用命令：`zp`
- 打印当前用户级 jobs：`zpjobs`
- 打印当前用户级规则：`zprules`
- 打印当前支持的 checkpoint：`zpckpt`
- 安装共享 bashrc：`zpbashrc`
- 启动 GPU idle burn：`zpburn <gpu_id>`
- 模块化执行 jobs 打印：`python -m utils_zp.cli.zpjobs`
- 生成并行任务 shell：`zppshell --output tmp/run_parallel.sh --task 'demo|0|echo hello'`
- 模块化执行规则打印：`python -m utils_zp.cli.zprules`
