# Workspace Entry

说明：这是 workspace 层级的总入口，负责承载跨 workspace 复用的通用协作约定，不索引具体 workspace entry。

## 通用约定

- 具体 workspace 使用 `agent_zp/workspace/<workspace>/README.agent.md` 这一目录结构读写入口文档；`example` 为示例 workspace
- 执行重要命令时，优先将 stdout/stderr 重定向到就近 `tmp/` 下的日志文件，再读取日志，不要只依赖 Terminal 输出
- 临时文件、调试产物和一次性中间结果优先放到当前操作目录或就近上层目录的 `tmp/` 中，方便排查和清理
- 命令日志也优先放在当前层级或就近上层目录的 `tmp/` 中，避免和正式产物混放
- 如果目录里还没有 `tmp/`，可以按需临时创建

## 文档约定

- **修改完具体代码后同步相关文档！**
- repo 内总入口统一放在各自仓库的 agent 入口文档，例如 `.agent/README.agent.md`
- 正常开发相关的过程记录、协同状态和交接信息统一写在 repo 内 `.agent/PROGRESS.agent.md`
- 正常开发相关的历史归档统一放在 repo 内 `.agent/progress_archive/`，按条目 `实现时间` 所属日期归档；文件名使用 `YYYY-MM-DD.md`
- issue 和 TODO 统一写在 repo 内 `.agent/ISSUE.agent.md`
- issue 历史归档统一放在 repo 内 `.agent/issue_archive/`，按条目 `解决时间` 所属日期归档；文件名使用 `YYYY-MM-DD.md`
- `progress` 和 `issue` 条目统一补 `标签：` 字段，格式为 `优先级=P0/P1/P2/P3；问题类型=...`
- 已完成 issue 统一补 `解决时间：YYYY-MM-DD HH:MM:SS`；已完成 progress 统一补 `实现时间：YYYY-MM-DD HH:MM:SS`
- 开始处理任务时，先按任务类型更新对应主文档：修 issue 优先把 `.agent/ISSUE.agent.md` 对应条目标成 `（进行中）`；正常开发再写 `.agent/PROGRESS.agent.md` 的 `（进行中）` 记录
- 只有当修 issue 过程中确实需要跨 agent 同步过程状态、临时约定或交接信息时，才额外新增对应的 `PROGRESS` 进行中记录；不要把“所有 issue 都先开一条 progress”当成默认动作
- 如果正常开发过程中暴露出明确问题、阻塞或待修复项，应及时转记到 repo 内 `.agent/ISSUE.agent.md`，不要把问题本身长期留在 `.agent/PROGRESS.agent.md`
- 如果处理的是与 repo 无关的特殊任务，不往 repo 内 `PROGRESS.agent.md` 或 `ISSUE.agent.md` 里补记录；这类任务通常直接在 `/tmp` 中运行，按一次性任务处理
- 如果被改动的是和当前任务无关的 `progress` 或 `issue`，不要因此停下来
- repo 根文档或 repo 内 `.agent/README.agent.md` 负责往 `src/`、`data_process/`、`.agent/` 或其他需要关注的子文件夹分发入口；子目录文档不额外回链上级目录
