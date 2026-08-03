# Agent Progress

本文件用途：记录正常开发场景下多个 agent 协同工作时需要同步的阶段性进展、特殊变动、临时约定和交接信息。

## 使用约定

- 适用场景是正常开发，不是 issue 排查或 issue 修复；后者统一走 `.agent/ISSUE.agent.md`
- 只记录需要跨 agent 同步的关键信息，不重复复制各目录 `README` 或 `README.agent.md` 的稳定说明
- 记录临时变更、特殊处理、已完成事项、待确认事项和交接提示
- 所有事项统一记录在 `当前进展` 下，使用 `1. 2. 3.` 编号列表，不使用 `-` 列表
- progress 条目推荐格式为：`1. 标题（状态）`，下面固定写 `标签：`、`说明：`、`涉及文件：`、`实现时间：`
- `标签：` 统一写成 `优先级=P0/P1/P2/P3；问题类型=...`；`问题类型` 优先用简短中文短语，例如 `功能开发`、`文档同步`、`流程规范`、`可维护性`
- 如果某项内容已经沉淀为稳定结论，应回写到对应目录文档，再从这里删除或简化
- 正常开发开始修改时，在当前进展底部先写入一条新进展并在标题后标注 `（进行中）`；结束后改成 `（已完成）`
- 如果 progress 实现过程中发现了需要持续跟踪、排查或修复的明确问题，应新增或更新 `.agent/ISSUE.agent.md` 对应条目，不要把这类问题留在 `PROGRESS.agent.md`
- 修 issue 时不要默认新增 progress 进行中记录，应先更新 `.agent/ISSUE.agent.md` 中对应 issue 的状态；只有需要跨 agent 同步过程状态、临时约定或交接信息时，才额外在这里追加 progress
- 如果用户明确要求归档，或主文档已明显过长，已完成且不再活跃的进展可移动到 `.agent/progress_archive/`
- 已完成 progress 必须填写精确到秒的 `实现时间：YYYY-MM-DD HH:MM:SS`
- progress 归档按日期组织；归档文件名统一使用条目 `实现时间` 所属日期，格式为 `YYYY-MM-DD.md`
- 如需归档，归档文件中的条目序号保持原号，主 `PROGRESS.agent.md` 里剩余条目也保持原号，不因归档而重排

## 当前上下文

- 当前已创建 progress 记录文档，后续正常开发可直接追加到本文件
- 已根据用户要求将 `1` 到 `3` 号已完成进展按 `实现时间` 所属日期归档到 `.agent/progress_archive/2026-07-28.md`，并将 `4` 到 `7` 号已完成进展归档到 `.agent/progress_archive/2026-07-29.md`
- 由于仓库可能存在多 agent 协同修改，进展记录需要注意对应的代码状态和文档状态是否一致
- 当前已使用过的最新进展序号是 `7`；后续新增进展统一从 `8` 开始顺延编号
- 主文档当前无未完成或仍需跟踪的 progress 事项；如有新任务，直接从 `8` 号开始追加

## 当前进展

8. 新增 `zpckpt` 命令（已完成）
标签：优先级=P1；问题类型=功能开发
说明：新增 `zpckpt` CLI，用固定注册表打印当前支持的 checkpoint，并补充入口、测试和 README 说明；当前收敛了 `线上模型` 与 `Qwen3.5 teacher` 两个 checkpoint。
涉及文件：`src/utils_zp/cli/zpckpt.py`、`src/utils_zp/setting.py`、`src/utils_zp/cli/main.py`、`pyproject.toml`、`tests/test_zpckpt.py`、`tests/test_main.py`、`README.md`
实现时间：2026-07-31 15:48:07

9. 将 `zpckpt` / `zpdata` / `zpexp` / `zppremodel` 索引切到 YAML（已完成）
标签：优先级=P1；问题类型=功能开发
说明：为四个 CLI 新增统一 YAML 索引读取逻辑，把原先 Markdown 里的详细说明并入 `detail_markdown` 字段，同时把真实索引文件迁移为 `checkpoint_versions.yaml`、`dataset_versions.yaml`、`exp_versions.yaml`、`model_versions.yaml`。
涉及文件：`src/utils_zp/cli/_yaml_index.py`、`src/utils_zp/cli/zpckpt.py`、`src/utils_zp/cli/zpdata.py`、`src/utils_zp/cli/zpexp.py`、`src/utils_zp/cli/zppremodel.py`、`src/utils_zp/setting.py`、`tests/test_zpckpt.py`、`tests/test_zpdata.py`、`tests/test_zpexp.py`、`tests/test_zppremodel.py`、`tests/test_main.py`、`README.md`、`pyproject.toml`、`/mnt/bn/motor-search2/wzp/repos/motor_search_relevance/model/checkpoint_versions.yaml`、`/mnt/bn/motor-search2/wzp/repos/motor_search_relevance/data/dataset_versions.yaml`、`/mnt/bn/motor-search2/wzp/repos/motor_search_relevance/exp/exp_versions.yaml`、`/mnt/bn/motor-search2/wzp/pretrained_models/model_versions.yaml`
实现时间：2026-07-31 16:25:00

10. 统一 versions YAML 结构与 CLI 输出口径（已完成）
标签：优先级=P1；问题类型=功能开发
说明：四个命令的索引列表统一改为 `versions`，`id` 全部按无前导零数字口径处理，所有记录补齐相对 `target_path`，`zpckpt` 对齐 `zppremodel` 的 `参数量 + 简要说明` 输出，并为四个命令都增加了 `--full`。
涉及文件：`src/utils_zp/cli/_yaml_index.py`、`src/utils_zp/cli/zpckpt.py`、`src/utils_zp/cli/zpdata.py`、`src/utils_zp/cli/zpexp.py`、`src/utils_zp/cli/zppremodel.py`、`tests/test_zpckpt.py`、`tests/test_zpdata.py`、`tests/test_zpexp.py`、`tests/test_zppremodel.py`、`README.md`、`/mnt/bn/motor-search2/wzp/repos/motor_search_relevance/model/checkpoint_versions.yaml`、`/mnt/bn/motor-search2/wzp/repos/motor_search_relevance/data/dataset_versions.yaml`、`/mnt/bn/motor-search2/wzp/repos/motor_search_relevance/exp/exp_versions.yaml`、`/mnt/bn/motor-search2/wzp/pretrained_models/model_versions.yaml`
实现时间：2026-07-31 16:40:00
