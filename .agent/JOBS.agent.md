# Repo Jobs Notes

说明：这里只补本仓相对用户级 `jobs` 的特殊口径和长期记录点；通用规则以 `agent_zp/jobs.agent.md` 为准。

- 本文件每个 job 默认只更新两件事：`做了什么：` 和 `最近一次时间：`。

## 当前工作
1. code review（待持续更新）
标签：`优先级=P2；问题类型=质量巡检`
做了什么：按用户级 `jobs 2` 对当前 staged 代码改动做 review，范围限定为源码、测试、CLI 入口和配置；本轮重点检查新增 `zpdata` / `zpexp` / `zppremodel` / `zpjobs` 编号选择能力、`setting.py` 的索引路径绑定，以及 `__init__.py` 的 lazy import 改动；执行 `PYTHONPATH=src python -m unittest discover -s tests`，43 个测试通过，未发现明确 correctness 问题。
最近一次时间：2026-07-31 10:25:01
