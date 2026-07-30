# Repo Jobs Notes

说明：这里只补本仓相对用户级 `jobs` 的特殊口径和长期记录点；通用规则以 `agent_zp/jobs.agent.md` 为准。

- 本文件每个 job 默认只更新两件事：`做了什么：` 和 `最近一次时间：`。

## 当前工作
1. code review（待持续更新）
标签：`优先级=P2；问题类型=质量巡检`
做了什么：按用户级 `jobs 8` 对当前 staged 代码改动做 review，范围限定为源码、脚本、测试和配置，跳过纯 Markdown；重点检查 `zpjobs` CLI、`CUDA_VISIBLE_DEVICES` 物理卡到 torch 逻辑卡映射、`leave_free_mb` 多卡目标值、缺 matplotlib 报错口径和 bashrc tmux 初始化，未发现明确 correctness 问题；执行 `PYTHONPATH=src python -m unittest discover -s tests`，21 个测试通过。
最近一次时间：2026-07-29 20:32:05
