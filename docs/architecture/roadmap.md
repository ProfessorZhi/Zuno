# 架构路线图

## 当前状态

Phase 0-6 架构收口仍是已完成的历史事实。

当前可执行 Agent 程序是：

- `.agent/programs/`

当前 active program 是 `zuno-repo-layout-cleanup-v1`。用户反馈指出 Program 3 原 Definition of Done 过窄：PHASE01-05 虽然完成了 root/docs hygiene、backend 六层迁移计划、六层 README 边界说明、repo hygiene verifier 和 repo tests 收口，但 `src/backend` 在 VS Code / Explorer 里仍然拥挤。因此 Program 3 重新打开为 continuation，从 PHASE06 继续做 backend physical layout cleanup。

已完成并归档：

- `zuno-architecture-surface-cleanup-v1`
- `zuno-workflow-doc-system-v1`
- `zuno-target-architecture-refresh-v1`
- `zuno-repo-layout-cleanup-v1` first slice

## 短期五个改进目标

`zuno-architecture-surface-cleanup-v1` 已经把项目从恢复期推进到“可继续收口”的状态，但它不等于成熟项目封面已经完成。短期目标拆成五个 program 串行推进，每个 program 内部再拆 phase，并允许 phase 级多线程并行：

| 短期目标 | 状态 | 为什么要做 | 近期收口标准 |
| --- | --- | --- | --- |
| 本地文档系统和工作流自洽 | completed / archived | 让仓库能由 Agent 按入口、skills、program、templates、verifiers 自助维护，而不是靠临时提示词记忆。 | 新 program 从 `PHASE01` 开始；旧 active 计划归档；修改 docs / agent workflow 时有对应 verifier 和 repo tests。 |
| 目标架构继续升版 | completed / archived | 让 Zuno 从恢复期 GraphRAG / Domain Pack 叙事，继续靠近成熟 Agent / RAG / GraphRAG 工程架构。 | 更新 `target-architecture.md` 和图示，把 API / Agent / Memory / Capability / Knowledge / Platform / Trace 的边界讲清；仍不能把未实现能力写成 Current。 |
| 文件夹继续分门别类 | active / definition revised | 让第一次看仓库的人能从目录名直接读出架构，而不是在 `core`、`services`、`rag`、`retrieval`、`graphrag` 之间拼图。 | PHASE01-05 已完成第一轮文档和 guardrails；PHASE06 起继续处理 `src/backend` 视觉拥挤、`fastapi_jwt_auth` 兼容壳和后端物理目录切片。 |
| Runtime 架构升级 | queued / not active | 在目标架构和目录边界稳定后，再把关键 runtime slice 往成熟形态推进。 | 只在 Program 2/3 边界清楚后实现；每个 runtime slice 必须有代码、测试、trace/eval 证据，不做大包式重构。 |
| 架构 HTML 重做清晰 | queued / not active | 让 GitHub 访问者和面试场景能快速看懂架构，而不是只靠长文本解释。 | 保持 `docs/architecture/diagrams.md` 为唯一 Mermaid 源；优化 `overview.html`；HTML 不能成为第二套架构真相。 |

## 短期 Program 队列

当前 active program 只在 `.agent/programs/` 根目录平铺存在。后续 program 草案在 `.agent/architecture/future/programs/`。queued 只表示候选顺序，不表示 active。

1. `zuno-workflow-doc-system-v1`：已完成，归档到 `docs/history/programs/zuno-workflow-doc-system-v1/`。
2. `zuno-target-architecture-refresh-v1`：已完成，归档到 `docs/history/programs/zuno-target-architecture-refresh-v1/`。
3. `zuno-repo-layout-cleanup-v1`：active / definition revised。PHASE01-05 first slice 已归档到 `docs/history/programs/zuno-repo-layout-cleanup-v1/`；当前从 PHASE06 继续处理 backend physical layout cleanup。
4. `zuno-runtime-architecture-upgrade-v1`：queued / not active。只在 Program 2/3 边界清楚后推进 runtime slice，重点是 GraphRAG LLM entity extraction、knowledge extractor configs、memory/capability/trace hardening。
5. `zuno-architecture-visuals-v1`：queued / not active。重做架构 HTML / Mermaid 展示面，保持图形展示不成为第二套架构真相。

已被替换的 V2 目标运行时材料归档在：

- `docs/history/programs/zuno-target-runtime-v2/`

已完成的 target architecture migration 程序归档在：

- `docs/history/programs/zuno-target-architecture-migration-v1/`

已完成的 GraphRAG 清理程序归档在：

- `docs/history/programs/official-graphrag-cleanup-v1/`

## Program 3 当前焦点

Program 3 first slice 已归档到：

- `docs/history/programs/zuno-repo-layout-cleanup-v1/`

Program 3 当前 continuation 仍不实施业务 runtime feature、API 行为、DB schema、frontend 或 eval baseline 修改；但允许在有测试保护的前提下做后端目录清理、兼容壳降噪、facade-first 小切片和 generated/local 清理。

Program 3 已完成的边界：

- `docs/architecture/README.md` 只作为架构入口和正式文档导航。
- `docs/architecture/target-architecture.md` 只写目标架构、设计边界和非近期目标。
- `docs/architecture/roadmap.md` 承担正式人类状态入口。
- `.agent/templates/goal-mode-prompt.md` 只保留目标模式提示骨架。
- `data/` / `reports/` 使用白名单语义：正式证据进 `docs/evidence/`，示例输入进 `examples/` 或 `tools/evals/`，运行生成物保持 ignored/local。
- `src/backend/zuno` 已形成六层 facade-first 迁移计划，不做 runtime 大搬家。
- `src/backend/zuno/api|agent|memory|capability|knowledge|platform/README.md` 已说明当前角色、目标角色、允许新增和禁止事项。
- 生成物/cache/local path、`data/` / `reports/` 白名单、`tools/` / `tests/` / `examples/` / `infra/` 子目录职责已进入 verifier 和 repo tests。

Program 3 当前继续处理：

- PHASE06：盘点 `src/backend` 和 `src/backend/zuno` 顶层目录，输出 current role / target bucket / action / risk / tests / rollback。
- PHASE07：处理 `src/backend/fastapi_jwt_auth` 兼容壳，明确为什么存在、如何降噪、何时退休。
- PHASE08：把后端物理清理拆成可验证小切片，避免一次性移动 `services/`、`core/`、`database/` 等高风险目录。

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

- V2 Context Contract foundation：`src/backend/zuno/services/application/context/`
- V2 Memory Layer foundation：`src/backend/zuno/services/memory/layers.py`
- V2 Capability System foundation：`src/backend/zuno/services/application/capabilities/`
- V2 GeneralAgent runtime integration：`src/backend/zuno/core/agents/general_agent.py`

这些是 foundation，不等于成熟产品能力。

## 已归档执行阶段

- `zuno-architecture-surface-cleanup-v1` PHASE01-06 已完成并归档。
- `zuno-workflow-doc-system-v1` PHASE01-05 已完成并归档。
- `zuno-target-architecture-refresh-v1` PHASE01-05 已完成并归档。
- `zuno-repo-layout-cleanup-v1` PHASE01-05 first slice 已完成并归档；PHASE06-08 当前 active。
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
- `.agent/programs/PHASE06_backend-directory-clarity-audit.md`
- `.agent/programs/PHASE07_fastapi-jwt-auth-compat-retirement-plan.md`
- `.agent/programs/PHASE08_backend-physical-cleanup-slices.md`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/`
- `.agent/architecture/future/programs/`
- `docs/architecture/diagrams.md`
- `docs/history/programs/zuno-target-runtime-v2/`
- `docs/history/programs/zuno-target-architecture-migration-v1/`
- `docs/history/programs/official-graphrag-cleanup-v1/`
