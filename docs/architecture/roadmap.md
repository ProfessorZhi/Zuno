# 架构路线图

## 当前状态

Phase 0-6 架构收口仍是已完成的历史事实。

当前可执行 Agent 程序是：

- `.agent/programs/`

当前没有 active program。`zuno-repo-layout-cleanup-v1` / Program 3 final alias surface closure 已完成并归档：`src/backend/zuno` 顶层目录只保留 `api / agent / memory / capability / knowledge / platform`，根级 alias `.py` 文件已收口到 `platform/compatibility/legacy_aliases.py`。`zuno-six-layer-internalization-v1` / Program 4 也已完成并归档：六层内部已有第一批无副作用薄入口、README、focused tests 和 verifier guard。

已完成并归档：

- `zuno-architecture-surface-cleanup-v1`
- `zuno-workflow-doc-system-v1`
- `zuno-target-architecture-refresh-v1`
- `zuno-repo-layout-cleanup-v1`
- `zuno-six-layer-internalization-v1`

## 短期五个改进目标

`zuno-architecture-surface-cleanup-v1` 已经把项目从恢复期推进到“可继续收口”的状态，但它不等于成熟项目封面已经完成。短期目标拆成五个 program 串行推进，每个 program 内部再拆 phase，并允许 phase 级多线程并行：

| 短期目标 | 状态 | 为什么要做 | 近期收口标准 |
| --- | --- | --- | --- |
| 本地文档系统和工作流自洽 | completed / archived | 让仓库能由 Agent 按入口、skills、program、templates、verifiers 自助维护，而不是靠临时提示词记忆。 | 新 program 从 `PHASE01` 开始；旧 active 计划归档；修改 docs / agent workflow 时有对应 verifier 和 repo tests。 |
| 目标架构继续升版 | completed / archived | 让 Zuno 从恢复期 GraphRAG / Domain Pack 叙事，继续靠近成熟 Agent / RAG / GraphRAG 工程架构。 | 更新 `target-architecture.md` 和图示，把 API / Agent / Memory / Capability / Knowledge / Platform / Trace 的边界讲清；仍不能把未实现能力写成 Current。 |
| 文件夹继续分门别类 | completed / archived | 让第一次看仓库的人能从目录名直接读出架构，而不是在 `core`、`services`、`rag`、`retrieval`、`graphrag` 之间拼图。 | `src/backend/zuno` 顶层目录已收敛到六层；根级 alias `.py` 文件收口到 legacy alias registry；verifier 和 repo tests 固定完成态。 |
| 六层内部入口成熟化 | completed / archived | Program 3 只完成顶层封口；六层内部还需要从 facade 逐步长成可解释、可测试的目标层入口。 | 已完成 agent / memory / capability / knowledge / platform 的第一批无副作用薄入口，并证明新旧 import 边界和 no-eager-load 约束。 |
| Runtime 架构升级 | queued / not active | 在目标架构和目录边界稳定后，再把关键 runtime slice 往成熟形态推进。 | 只在 internalization 边界清楚后实现；每个 runtime slice 必须有代码、测试、trace/eval 证据，不做大包式重构。 |
| 架构 HTML 重做清晰 | target blueprint refreshed / queued follow-up | 让 GitHub 访问者和面试场景能快速看懂架构，而不是只靠长文本解释。 | `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html` 已改成任务到交付物主链路；`overview.html` / Mermaid 生成页仍保持 queued follow-up；HTML 不能成为第二套架构真相。 |

## 短期 Program 队列

当前没有 active program。后续 program 草案在 `.agent/architecture/future/programs/`。queued 只表示候选顺序，不表示 active。

1. `zuno-workflow-doc-system-v1`：已完成，归档到 `docs/history/programs/zuno-workflow-doc-system-v1/`。
2. `zuno-target-architecture-refresh-v1`：已完成，归档到 `docs/history/programs/zuno-target-architecture-refresh-v1/`。
3. `zuno-repo-layout-cleanup-v1`：已完成，归档到 `docs/history/programs/zuno-repo-layout-cleanup-v1/`；final alias surface closure 作为 PHASE10-15 保存。
4. `zuno-six-layer-internalization-v1`：已完成，归档到 `docs/history/programs/zuno-six-layer-internalization-v1/`。六层内部已拥有第一批可解释、可测试、无副作用的目标层薄入口。
5. `zuno-runtime-architecture-upgrade-v1`：queued / not active。只在 Program 2/3 和 internalization 边界清楚后推进 runtime slice，重点是 GraphRAG LLM entity extraction、knowledge extractor configs、memory/capability/trace hardening。
6. `zuno-architecture-visuals-v1`：target blueprint refreshed / queued follow-up。目标架构 HTML 已吸收任务到交付物主链路；后续仍可重做 `docs/architecture/overview.html` / Mermaid 生成展示面，保持图形展示不成为第二套架构真相。

已被替换的 V2 目标运行时材料归档在：

- `docs/history/programs/zuno-target-runtime-v2/`

已完成的 target architecture migration 程序归档在：

- `docs/history/programs/zuno-target-architecture-migration-v1/`

已完成的 GraphRAG 清理程序归档在：

- `docs/history/programs/official-graphrag-cleanup-v1/`

## Program 3 完成状态

Program 3 PHASE01-09 归档到：

- `docs/history/programs/zuno-repo-layout-cleanup-v1/`

Program 3 不实施业务 runtime feature、API 行为、DB schema、frontend 或 eval baseline 修改；它继续做后端目录清理、兼容壳降噪、facade-first 小切片和 generated/local 清理。

Program 3 已完成的边界：

- `docs/architecture/README.md` 只作为架构入口和正式文档导航。
- `docs/architecture/target-architecture.md` 只写目标架构、设计边界和非近期目标。
- `docs/architecture/roadmap.md` 承担正式人类状态入口。
- `.agent/templates/goal-mode-prompt.md` 只保留目标模式提示骨架。
- `data/` / `reports/` 使用白名单语义：正式证据进 `docs/evidence/`，示例输入进 `examples/` 或 `tools/evals/`，运行生成物保持 ignored/local。
- `src/backend/zuno` 顶层目录已收敛到六层：`api / agent / memory / capability / knowledge / platform`。
- 旧 runtime 顶层目录已下沉到六层内部，旧 import path 由 legacy alias registry 保留。
- `src/backend/zuno/api|agent|memory|capability|knowledge|platform/README.md` 已说明当前角色、目标角色、允许新增和禁止事项。
- 生成物/cache/local path、`data/` / `reports/` 白名单、`tools/` / `tests/` / `examples/` / `infra/` 子目录职责已进入 verifier 和 repo tests。
- `src/backend/fastapi_jwt_auth/` 顶层 shell 已退休。
- `resources/` 与 `compatibility/` 已完成物理收敛。
- MCP server implementations 已迁入 `src/backend/zuno/capability/mcp/servers/`。
- HTTP middleware implementations 已迁入 `src/backend/zuno/platform/middleware/`。
- 旧 `mcp_servers/`、`middleware/`、`evals/` 顶层目录和根级 alias 文件已退休，兼容由 `platform/compatibility/legacy_aliases.py` 承接。
- repo structure verifier 和 repo tests 已禁止旧 runtime 顶层目录和非 alias 顶层文件回流。

## 已完成状态

- Phase 01 到 Phase 10 已完成。
- Phase 11A：已完成。项目查询 runtime 已引入 `KnowledgeQueryService`、`GraphRAGQueryService`、`GraphRAGProjectSnapshot` 和 `KnowledgeQueryResult`。
- Phase 11B：已完成。知识查询已统一到 single `GeneralAgent` path，通过 `search_knowledge_base` 和 `KnowledgeQueryService` 执行。
- Phase 11C：active runtime cleanup 已完成。当前 FastAPI router 不再挂载 `/domain-packs`；Vue knowledge route/settings 不再打开 Domain Pack 页面；`AgentRuntime` facade、`MultiAgentSupervisorGraph`、`DomainQAGraph`、legacy graph states 和 `zuno.services.domain_pack` 已从当前主线退休。
- Phase 12：已通过 target migration closure evidence 关闭。full pytest、formal Contract Review eval、stackless eval baseline comparison、trace metadata、legacy grep classification 和 docs/evidence sync 已完成。

## 受限历史兼容

这些内容是兼容保留，不是目标方向：

- 剩余 `domain_pack_id` references 只属于 migration aliases、existing Agent database-column compatibility、eval CLI compatibility 和 retirement/history tests。
- root `domain-packs/` archive 保留在 `docs/history/domain-packs/root-contract-review/`。
- root Phase 11C retired-import guards 保留用于防回归。

## 当前基础切片收口

- V2 Context Contract foundation：`zuno.services.application.context` 兼容入口，物理位于 `src/backend/zuno/platform/services/application/context/`
- V2 Memory Layer foundation：`zuno.memory.contracts` / `store` / `policy` / `review` / `retrieval` / `rendering` / `engine` 目标层薄入口，加上旧 `zuno.services.memory.layers` 兼容入口；物理位于 `src/backend/zuno/platform/services/memory/layers.py`
- V2 Capability System foundation：`zuno.capability.contracts` / `registry` / `selector` / `policy` / `execution` / `trace` 目标层薄入口，加上旧 `zuno.services.application.capabilities` 兼容入口；物理位于 `src/backend/zuno/platform/services/application/capabilities/`
- V2 Knowledge Layer foundation：`zuno.knowledge.contracts` / `query_service` / `evidence` / `citation` / `trace` / `retrieval` / `fusion` / `graphrag` 目标层薄入口。
- V2 Agent Layer foundation：`zuno.agent.runtime` / `context` / `post_turn` / `state` / `streaming` / `tool_bridge` 目标层薄入口。
- V2 Platform Layer foundation：`zuno.platform.model_gateway` / `security` / `observability` / `storage` 目标层薄入口。
- V2 GeneralAgent runtime integration：`zuno.core.agents.general_agent` 兼容入口，物理位于 `src/backend/zuno/agent/core/agents/general_agent.py`

这些是 foundation，不等于成熟产品能力。

## 已归档执行阶段

- `zuno-architecture-surface-cleanup-v1` PHASE01-06 已完成并归档。
- `zuno-workflow-doc-system-v1` PHASE01-05 已完成并归档。
- `zuno-target-architecture-refresh-v1` PHASE01-05 已完成并归档。
- `zuno-repo-layout-cleanup-v1` PHASE01-09 和 Directory Surface Alignment PHASE01-06 已归档。
- `zuno-six-layer-internalization-v1` PHASE01-07 已完成并归档。
- 旧 V2 target runtime 材料已归档到 `docs/history/programs/zuno-target-runtime-v2/`。

## 非目标

当前路线图不实施：

- Java services
- split microservices
- event workers
- database migrations
- dependency upgrades
- product/runtime default multi-agent mode

## Agent 执行来源

- `.agent/programs/current.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `docs/history/programs/zuno-six-layer-internalization-v1/`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/`
- `.agent/architecture/future/programs/`
- `docs/architecture/diagrams.md`
- `docs/history/programs/zuno-target-runtime-v2/`
- `docs/history/programs/zuno-target-architecture-migration-v1/`
- `docs/history/programs/official-graphrag-cleanup-v1/`
