# Workspace Entry

说明：这里只放 workspace 层的通用协作规则；具体环境差异写到 `agent_zp/workspace/<workspace>/README.agent.md`。

## 先判断

- 先找当前 workspace 文档，再进入目标 repo 的 `.agent/README.agent.md`。
- 重要命令优先把 stdout / stderr 重定向到就近 `tmp/` 日志文件，再结合日志和实际产物判断结果。
- 临时文件、调试产物和命令日志优先放在当前目录或就近上层的 `tmp/` 中。

## 记录分流

- 正常开发：写目标 repo 的 `.agent/PROGRESS.agent.md`。
- 修 issue / review 发现问题：写目标 repo 的 `.agent/ISSUE.agent.md`。
- 跨 repo 的通用提醒或待办：写 `utils_zp/.agent/ISSUE.agent.md`。
- 已完成条目要补权威时间：issue 用 `解决时间`，progress 用 `实现时间`。

## 硬约束

- 修改代码后同步相关文档。
- 修 issue 时优先更新 `ISSUE.agent.md`，不要默认额外开 progress；只有确实需要同步过程状态时再补。
- 开发过程中发现明确问题，要及时从 `PROGRESS.agent.md` 转记到 `ISSUE.agent.md`。
- repo 根入口负责继续往下分流；子目录文档不重复回链上级。
