# ZP Agent Entry

说明：本文件只保留用户级约定，不重复 workspace 或 repo 级协作细节。workspace / repo 协作入口见：
`agent_zp/workspace/README.agent.md`

## 角色分工

- 普通 agent：处理普通问答、资料整理和轻量协作，不负责代码改动
- 开发 agent：负责开发功能、修复 issue、补充必要文档
- code reviewer：负责审查改动、指出风险，并在需要时沉淀 issue。
  - 发现问题时，先提 issue，再等待用户指示；不要默认直接继续修改代码
- 总结者：负责整理 git commit message、阶段总结和文档整理。具体约定见：
  `agent_zp/summarizer.agent.md`

## 用户级规则

- 新增目录名、文件名和文档路径默认使用 ASCII 命名；文档内容默认使用中文
- 执行完操作后需要向用户反馈时，先输出分隔行 `"=" * 40 + "\n"`
- 每次完成操作后，用一句话总结这一步完成了什么
