# Program3 Directory Closure Target Mode Prompt

> 用法：把本文完整内容用于当前主线程的真正 Codex UI 目标模式。不是多线程 coordinator，不创建或复用子线程；在主线程内部默认开启多 agent 模式，并保证不同 agent 写入范围不重叠。

## 目标

你正在 `F:\internship-work\resume&resume project\02_projects\Zuno` 执行 Program 3：`zuno-repo-layout-cleanup-v1` 的目录结构收口。一次性完成 `.agent/programs/PHASE01` 到 `PHASE06`，最终让 `src/backend/zuno` 顶层目录只剩：

```text
api/
agent/
memory/
capability/
knowledge/
platform/
```

允许的顶层文件只有 `__init__.py`、`main.py` 和明确受控的 `.py` alias module。`compatibility/`、`resources/`、`config/`、`database/`、`schema/`、`tools/`、`utils/`、`services/`、`core/` 不能继续作为 Program3 完成态顶层目录存在。

## 工作模式

- 必须使用当前主线程的真正 Codex UI 目标模式。
- 主线程自己端到端完成计划、实现、验证、提交和推送。
- 默认开启主线程内多 agent 模式。
- 不创建或复用 Codex 子线程，不写子线程提示词，不走多线程 coordinator 流程。
- 多 agent 只能处理互相独立的子任务，不能同时编辑同一批文件。
- 建议按以下写入范围在主线程内部拆分多 agent：
  - Agent A：`platform/` 下沉迁移和旧 import alias。
  - Agent B：`schema/`、`tools/`、`resources/` 收口。
  - Agent C：`services/` 低风险小模块迁移。
  - Agent D：`core/` 变薄和 `agent/` facade。
  - Agent E：verifier、tests、docs、Program closure。
- 主线程必须最终统一审查所有 agent 的 diff、跑集成验证、提交、推送。

## 必读顺序

先读：

1. `AGENTS.md`
2. `src/backend/zuno/AGENTS.md`
3. `.agent/programs/current.md`
4. `.agent/programs/PHASE01_directory-closure-master-plan.md`
5. `.agent/programs/PHASE02_platform-foundation-directory-migration.md`
6. `.agent/programs/PHASE03_schema-tools-resources-directory-migration.md`
7. `.agent/programs/PHASE04_services-thinning-directory-migration.md`
8. `.agent/programs/PHASE05_core-agent-runtime-directory-migration.md`
9. `.agent/programs/PHASE06_final-six-layer-guard-and-closure.md`
10. `src/backend/zuno/DIRECTORY_MAP.md`
11. `.agent/references/zuno-repo-hygiene.md`
12. `tools/scripts/verify_repo_structure.py`
13. `tests/repo/test_repo_structure_consistency.py`
14. `tests/legacy_guards/test_zuno_alias_imports.py`

再读待迁移目录的 imports、tests 和 README。不要只凭文档推断 runtime 行为。

## 执行要求

### PHASE01：总控计划确认

- 确认 `.agent/programs/` 只有 PHASE01-06 active files。
- 确认 Program4 / Program5 仍是 queued / not active。
- 确认 `DIRECTORY_MAP.md` 的最终目标是六层顶层目录。

### PHASE02：Platform foundation migration

目标：

- `config/` 下沉到 `platform/config/` 或 `platform/config.py`。
- `database/` 下沉到 `platform/database/`。
- `compatibility/` 下沉到 `platform/compatibility/`。

要求：

- 保留旧 `zuno.config.*`、`zuno.database.*`、`zuno.compatibility.*` import path。
- 旧路径只能是 alias module 或 compatibility facade，不能恢复顶层目录。
- 不改 DB schema，不改 API 行为。

### PHASE03：Schema / tools / resources migration

目标：

- `schema/` 拆到 `api/dto/` 和各层 `contracts.py`。
- runtime 可调用工具进入 `capability/tools/`。
- 维护脚本迁出 runtime 包，进入仓库根 `tools/`。
- runtime packaged resources 进入 `platform/resources/`，示例或文档资源迁出到 `examples/` 或 `docs/`。

要求：

- 旧 import path 必须有 alias guard。
- 不改 API 字段语义，不改 eval baseline。

### PHASE04：Services thinning

目标：

- `services/` 不再作为 active 架构入口。
- 先迁移低风险小模块到 `memory/`、`capability/`、`knowledge/`、`platform/`。
- 高风险 orchestrator / fusion / graph runtime 只做 facade 或明确暂缓，不做大重写。

要求：

- 新代码不得继续写入泛 `services/` 主线。
- 旧 `zuno.services.*` import path 继续可用。
- 不改变 retrieval / GraphRAG / eval 语义。

### PHASE05：Core agent runtime thinning

目标：

- `core/` 不再作为 active 架构入口。
- Agent 主入口进入 `agent/`。
- 模型网关或 provider 管理按边界进入 `platform/`。

要求：

- 不重写 Agent 主循环行为。
- 不混入 Program4 runtime architecture upgrade。
- 不改 streaming contract。
- 旧 `zuno.core.*` import path 继续可用。

### PHASE06：Final six-layer guard and closure

目标：

- `src/backend/zuno` 顶层目录只剩六层：
  - `api`
  - `agent`
  - `memory`
  - `capability`
  - `knowledge`
  - `platform`
- `verify_repo_structure.py` 收紧 backend top-level directory allowlist 到六层。
- `DIRECTORY_MAP.md` 从迁移地图更新为 closure summary。
- `.agent/programs/` 移除 PHASE01-06 active files，并把 Program3 完整归档到 `docs/history/programs/zuno-repo-layout-cleanup-v1/`。
- `AGENTS.md`、`.agent/references/current-program.md`、`docs/architecture/roadmap.md` 改为 Program3 completed；Program4 仍 queued / not active。

## 禁止事项

- 禁止一次性无测试大搬 `services/` 或 `core/`。
- 禁止改 public API、DB schema、eval baseline、frontend 行为。
- 禁止把 Program4 runtime architecture upgrade 混入 Program3。
- 禁止恢复 `mcp_servers/`、`middleware/`、`evals/` 顶层目录。
- 禁止新增未经 `DIRECTORY_MAP.md` 和 verifier 登记的 `src/backend/zuno` 顶层目录。

## 验证要求

每个独立迁移切片至少跑对应 focused tests。最终收口必须跑：

```powershell
git diff --check
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
python tools/scripts/verify_docs_entrypoints.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q --durations=50 -p no:cacheprovider
```

如 full pytest 生成 `.local/`、`.test-tmp/`、`.pytest_cache/` 或 `__pycache__/`，清理后重跑 `python tools/scripts/verify_repo_structure.py` 和 `python .agent/scripts/verify_repo_hygiene.py`。

## Git 收尾

- 每个 PR / phase 可以单独提交。
- 整个 Program3 结束时必须提交并推送。
- 不要 force push。
- 如果推送失败，报告具体错误和本地 commit hash。
