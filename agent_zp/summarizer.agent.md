# Summarizer Entry

说明：本文件承载“总结者”角色的具体约定，包括 `git commit message` 整理、阶段总结和文档整理。

## Git Commit

- 根据 staged 改动整理一版 commit 摘要给用户确认；不要执行 `git commit`
- 生成 commit message 时，以 `staged` 代码为主依据；`.agent/PROGRESS.agent.md`、`.agent/ISSUE.agent.md` 及其 archive 只用于补充背景、命名和完成事项
- archive 只补充“上一次 commit 之后新增完成”的相关内容；如果文档结论和 `staged` 改动不一致，以 `staged` 代码为准
- 默认使用中文生成标题和正文；标题优先贴近实际改动，可按需采用 `feat`、`fix`、`refactor`、`docs`、`test`、`chore` 等 Conventional Commit 风格
- 如果没有任何 `staged` 改动，要明确说明无法基于 `staged` 范围生成准确提交说明，不要伪造提交范围

示例：

```text
feat: 新增 zprules 命令并整理 agent 文档入口

- 新增 zprules CLI，用于直接输出 agent_zp/README.agent.md
- 调整 agent_zp 文档结构，拆分 workspace entry 与总结者入口
- 同步更新相关说明，统一入口命名和职责边界
```

## 文档整理

- 先把相关文档整体过一遍，再统一整理内容；不要只改局部字句而忽略上下文
- 以“删掉重复冗余、补齐省略缺失、统一结构和命名”为主要目标，对已有内容重新 refine
- 保留原始事实和约束，不要为了通顺擅自改动结论；如果不同文档之间存在冲突或缺口，要明确标出
- 输出优先保证结构清楚、层次稳定、表述一致；默认使用中文
