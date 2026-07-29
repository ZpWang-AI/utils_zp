# ZP Agent Entry

说明：这里只放用户级总入口，负责导航、分流和少量硬约束；workspace 细节看 `agent_zp/workspace/`，repo 细节看各仓库自己的 `.agent/README.agent.md`

## 角色分工

- 普通 agent：处理普通问答、资料整理和轻量协作，不负责代码改动。
- 开发 agent：负责开发功能、修复 issue、补充必要文档。
  - 修复 bug 时，不只改表层调用点；要尽量把语义收敛到合适层次，例如把路径解析收敛到配置构造层，而不是散落在 CLI、脚本和运行时重复处理。
  - 遇到“文本字段 vs 数值字段”“业务缺失值 vs 库默认行为”这类边界问题时，要同时检查读入层、归一化层和端到端产物，避免只修一半。
  - 修完后补最小回归测试，并同步必要文档。

## jobs

- 需要结构化分流的专项工作，统一看 `agent_zp/jobs.agent.md`。
- 需要快速查看当前支持的 jobs 时，可直接运行 `zpjobs`。
- 当前 jobs 覆盖：`commit message`、`agent 文档归档`、`项目文档整理`、`history 总结`、`阶段总结 / 交接`、`查看运行状态`、`清理无用文件`、`code review`。

## 触发词

- `zprules`：必须实际执行 `zprules`，按命令输出刷新规则理解。
- `zpjobs`：可直接执行 `zpjobs` 查看当前 jobs 清单和说明。
- `jobs`：进入 `agent_zp/jobs.agent.md` 分流，先列举支持的工作，再让用户选一个交给 agent 做。
- `history`：把本轮整理后的上下文输出到 `agent_zp/history/`。

## 用户级规则

- 规则按层级拆开写：用户级看这里，workspace 级看 `agent_zp/workspace/README.agent.md`，repo 级看各仓库 `.agent/README.agent.md`。
- 新增目录名、文件名和文档路径默认使用 ASCII；文档内容默认使用中文。
- 根入口文档默认收敛成“导航 + 分流 + 硬约束”，不要把背景、过程和实现细节重新堆回入口。
- 涉及规则来源判断时，以 `zprules` 实际输出为准，不用旧记忆覆盖当前规则。
- 涉及飞书 doc/wiki 写入时，默认走已认证的 `lark-cli`；失败时直接说明没写成，并同步认证、scope 或接口侧的真实阻塞点。
- 清理 `outputs/` 或其他运行入口目录前，先确认是否仍有程序依赖原路径，优先保入口可用。
- 对用户反馈直接回答；结束时补一句话总结，不输出分隔线或固定装饰。
