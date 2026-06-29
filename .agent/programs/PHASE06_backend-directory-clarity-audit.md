# PHASE06：Backend Directory Clarity Audit

> 状态：active。目标是把 `src/backend` 和 `src/backend/zuno` 的真实目录拥挤点审清楚，形成可执行分类表。

> 更新：PHASE07 / PHASE08 已推进部分审计结论。`src/backend/fastapi_jwt_auth/` 已退休；`prompts/`、`fixtures/`、`system_skills/` 已迁入 `resources/`；`legacy/`、`vendor/` 已迁入 `compatibility/`。本文件保留原始盘点和风险判断。

## 目标

回答一个问题：

```text
为什么 VS Code 里看起来还是乱？
```

本 phase 不是写泛泛计划，而是输出每个顶层目录的处理动作。

## 必须审计

- `src/backend/fastapi_jwt_auth/`
- `src/backend/zuno/api/`
- `src/backend/zuno/agent/`
- `src/backend/zuno/capability/`
- `src/backend/zuno/config/`
- `src/backend/zuno/core/`
- `src/backend/zuno/database/`
- `src/backend/zuno/evals/`
- `src/backend/zuno/fixtures/`
- `src/backend/zuno/knowledge/`
- `src/backend/zuno/legacy/`
- `src/backend/zuno/mcp_servers/`
- `src/backend/zuno/memory/`
- `src/backend/zuno/middleware/`
- `src/backend/zuno/platform/`
- `src/backend/zuno/prompts/`
- `src/backend/zuno/schema/`
- `src/backend/zuno/services/`
- `src/backend/zuno/system_skills/`
- `src/backend/zuno/tools/`
- `src/backend/zuno/utils/`
- `src/backend/zuno/vendor/`

## 分类标签

每个目录必须归到一个主标签：

| 标签 | 含义 |
| --- | --- |
| target-layer | 已经是目标六层之一。 |
| compatibility-shell | 为 public import / vendor 兼容暂留。 |
| migration-source | 当前 runtime 来源，将来应迁入六层。 |
| infrastructure | DB、settings、middleware、vendor 等底座目录。 |
| app-resource | prompts、fixtures、system skills 等资源。 |
| generated-local | 本地产物，应清理或 ignored。 |
| retirement-candidate | 可退休，但需要验证。 |

## 输出

本轮审计采用 deep research report 的口径：根目录不是最大问题，真正阻塞成熟封面的是 `src/backend` 和 `src/backend/zuno` 的中层目录没有把六层架构表达出来。

| path | current role | target bucket | action | risk | tests | rollback |
| --- | --- | --- | --- | --- | --- | --- |
| `src/backend/fastapi_jwt_auth/` | 旧 public import 的 compatibility shell，转接到 `zuno/vendor/fastapi_jwt_auth`。 | compatibility-shell | 进入 PHASE07，先说明存在原因，再评估替换 import 和退休路径。 | 直接删除会破坏 `from zuno.compatibility.vendor.fastapi_jwt_auth import AuthJWT`。 | `pytest -q tests/api/test_fastapi_jwt_auth_compat.py -p no:cacheprovider` | 保留 shell 和现有兼容测试。 |
| `src/backend/zuno/api/` | HTTP route、API service、DTO 入口。 | target-layer | 保留为六层之一，后续只整理内部 DTO / service 边界。 | API import 和前端契约漂移。 | API focused tests。 | 恢复旧 route / schema import。 |
| `src/backend/zuno/agent/` | 新目标 agent facade 层。 | target-layer | 保留；未来承接 `core/agents` 的 runtime facade。 | 过早搬 runtime 会影响 streaming / memory commit。 | agent runtime tests。 | 旧 `core/agents` 继续作为来源。 |
| `src/backend/zuno/capability/` | 新目标 capability facade 层。 | target-layer | 保留；未来承接 ToolCard / MCP / execution policy。 | ToolCard public import 变化。 | capability / toolcard tests。 | 旧 `services/application/capabilities` 继续 re-export。 |
| `src/backend/zuno/config/` | 配置相关目录，和 `platform/`、`settings.py` 叙事重叠。 | infrastructure | PHASE08 Slice A 判断保留为 compat 还是收敛到 platform/config。 | 配置加载路径变动会影响测试收集。 | settings / repo structure tests。 | 恢复旧 config import path。 |
| `src/backend/zuno/core/` | legacy runtime 来源，含旧 Agent 主线。 | migration-source | 不一次性移动；未来把 `general_agent.py` 拆向 `agent/runtime.py` 等。 | 主循环、streaming、memory commit 回归风险高。 | agent focused tests + full pytest。 | 保持 `core` 为 runtime source。 |
| `src/backend/zuno/database/` | DB session、models、storage 底座。 | infrastructure | 暂留；未来归入 `platform/database/` 前必须做 import audit。 | DB URL / test collection 失败。 | storage / db tests。 | 保留 `zuno.database.*` public path。 |
| `src/backend/zuno/evals/` | runtime/eval 辅助逻辑。 | infrastructure | 判断是否保留为 runtime eval package，或迁到 `tools/evals` 只保留 API。 | eval runner import 漂移。 | eval focused tests。 | 保留当前 package。 |
| `src/backend/zuno/fixtures/` | runtime 或测试资源混合风险。 | app-resource | 审计是否应转入 `tests/fixtures`、`examples` 或 runtime resources。 | 测试数据路径丢失。 | fixture consumers grep + tests。 | 恢复原目录。 |
| `src/backend/zuno/knowledge/` | 新目标 Knowledge / RAG / GraphRAG facade 层。 | target-layer | 保留；未来承接 retrieval、rag、graphrag facade。 | retrieval trace / evidence 语义漂移。 | retrieval focused tests。 | 旧 `services/rag`、`services/retrieval`、`services/graphrag` 继续可用。 |
| `src/backend/zuno/legacy/` | retired alias / legacy guard。 | retirement-candidate | 只删除 grep 和 tests 证明无引用的文件。 | 历史兼容测试破坏。 | legacy guard tests。 | 恢复 legacy alias。 |
| `src/backend/zuno/mcp_servers/` | MCP server adapters。 | migration-source | 未来映射到 `capability/mcp.py` 或 capability 子包。 | MCP tool discovery 失效。 | MCP / capability tests。 | 保留现路径。 |
| `src/backend/zuno/memory/` | 新目标 Memory facade 层。 | target-layer | 保留；未来承接 `services/memory` contracts/store/review。 | memory approval / snapshot 行为漂移。 | memory focused tests。 | 旧 `services/memory` 继续作为来源。 |
| `src/backend/zuno/middleware/` | HTTP/runtime middleware。 | infrastructure | 判断归 `api/` 还是 `platform/security`。 | 请求链和鉴权行为变化。 | API middleware tests。 | 保留现路径。 |
| `src/backend/zuno/platform/` | 新目标 platform 层。 | target-layer | 保留；未来承接 config/database/model gateway/observability。 | 与 `config`、`database` 双头。 | repo + settings tests。 | 保留旧路径。 |
| `src/backend/zuno/prompts/` | Prompt 资源。 | app-resource | 加 README 或后续迁入 agent/knowledge resource 边界。 | prompt path 破坏。 | prompt consumers grep。 | 保留现路径。 |
| `src/backend/zuno/schema/` | 旧 DTO / schema 来源。 | migration-source | PHASE08 Slice B 判断逐步迁入 `api/dto`，或保留 compat source。 | API contract 破坏。 | API schema tests。 | 保留 `zuno.schema.*`。 |
| `src/backend/zuno/services/` | 最大 legacy service source，含 memory/capability/retrieval/graphrag 等。 | migration-source | 不一次性移动；只允许 facade-first 和小切片迁移。 | 大面积 import / behavior 回归。 | focused tests + repo tests。 | 保持 services 为实现来源。 |
| `src/backend/zuno/system_skills/` | runtime skill resource / system prompt 资源。 | app-resource | 判断归 capability skill、agent resources，还是保留 runtime resource。 | skill loading 失败。 | skill/tool tests。 | 保留现路径。 |
| `src/backend/zuno/tools/` | runtime tools 或内部 helper。 | migration-source | PHASE08 Slice D 区分 runtime tools 和 repo maintenance tools。 | 工具注册和执行 trace 回归。 | tool / capability tests。 | 保留现路径。 |
| `src/backend/zuno/utils/` | 通用 helper 聚合。 | migration-source | 只迁移有明确目标层归属的小 helper。 | 隐式依赖多，容易漏 import。 | grep + focused tests。 | 保留 utils。 |
| `src/backend/zuno/vendor/` | vendored dependency source。 | compatibility-shell | 保留；必须解释和测试 compat shell。 | vendored import 破坏。 | `tests/api/test_fastapi_jwt_auth_compat.py` | 恢复 vendor package。 |

## 当前判断

- 可以马上清理的是 untracked generated cache，例如 `__pycache__`。
- 不能为了视觉清爽直接删 `fastapi_jwt_auth`、`core`、`services`、`database` 或 `schema`。
- 真正的下一步不是继续写泛泛目标，而是按 PHASE07 / PHASE08 对 compatibility shell 和 migration-source 做小切片。

## 禁止

- 不移动 runtime 文件。
- 不删除 tracked 文件。
- 不改 public import。
- 只允许清理 untracked generated cache，例如 `__pycache__`。

## 验证

```powershell
git diff --check
python .agent/scripts/verify_agent_system.py
python tools/scripts/verify_repo_structure.py
pytest -q tests/repo/test_repo_structure_consistency.py tests/repo/test_backend_facade_layers.py -p no:cacheprovider
```
