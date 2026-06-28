# 架构路线图

## 当前状态

Phase 0-6 架构收口仍是已完成的历史事实。

当前可执行 Agent 程序是：

- `.agent/programs/`

当前 active program 是 `zuno-repo-layout-cleanup-v1`，当前 phase 是 `.agent/programs/PHASE01_repo-layout-audit.md`。

`zuno-workflow-doc-system-v1` 和 `zuno-target-architecture-refresh-v1` 已完成并归档。上一轮 `zuno-architecture-surface-cleanup-v1` 的 PHASE01-06 已完成并归档。

## 短期四个改进目标

`zuno-architecture-surface-cleanup-v1` 已经把项目从恢复期推进到“可继续收口”的状态，但它不等于成熟项目封面已经完成。短期目标拆成五个 program 串行推进，每个 program 内部再拆 phase，并允许 phase 级多线程并行：

| 短期目标 | 为什么要做 | 当前不足 | 近期收口标准 |
| --- | --- | --- | --- |
| 本地文档系统和工作流自洽 | 让仓库能由 Agent 按入口、skills、program、templates、verifiers 自助维护，而不是靠临时提示词记忆。 | `AGENTS.md`、`.agent/programs`、`.agent/references`、verifier 已有第一版，但 program closure、history 归档、skill 更新和 docs drift 防线还需要继续收紧。 | 新 program 从 `PHASE01` 开始；旧 active 计划归档；`.agent/references` 保持 skill / lesson / playbook，不膨胀成索引；修改 docs / agent workflow 时有对应 verifier 和 repo tests。 |
| 目标架构继续升版 | 让 Zuno 从恢复期 GraphRAG / Domain Pack 叙事，继续靠近成熟 Agent / RAG / GraphRAG 工程架构。 | 目标架构已经分清 Current / Target，但完整 LangGraph runtime、生产级 Memory、动态 Capability、GraphRAG LLM entity extraction、知识库多配置和 frontend trace/evidence 闭环还没有成为 Current。 | 更新 `target-architecture.md` 和图示，把 API / Agent / Memory / Capability / Knowledge / Platform / Trace 的边界讲清；明确 GraphRAG 实体抽取优先 LLM extraction，而不是正则/规则匹配；仍不能把未实现能力写成 Current。 |
| 文件夹继续分门别类 | 让第一次看仓库的人能从目录名直接读出架构，而不是在 `core`、`services`、`rag`、`retrieval`、`graphrag` 之间拼图。 | 根目录仍能看到 `.codex`、`.local`、`.test-tmp`、`node_modules`、`reports`、`data` 等需要分类确认的目录；`src/backend` 顶层和 `src/backend/zuno` 还没有把六层目标表达得足够清楚。 | 先做目录 inventory 和迁移计划，再小步清理；根目录只保留必要入口和一等目录，`src/backend/zuno` 逐步靠近 `api / agent / memory / capability / knowledge / platform`；生成物和本地缓存不进入前台。 |
| Runtime 架构升级 | 在目标架构和目录边界稳定后，再把关键 runtime slice 往成熟形态推进。 | GraphRAG LLM entity extraction、knowledge extractor configs、memory/capability/trace hardening 仍是 Target，不是 Current。 | 只在 Program 2/3 边界清楚后实现；每个 runtime slice 必须有代码、测试、trace/eval 证据，不做大包式重构。 |
| 架构 HTML 重做清晰 | 让 GitHub 访问者和面试场景能快速看懂架构，而不是只靠长文本解释。 | HTML 展示已有第一版，但仍偏工具型，视觉和信息层级不够成熟；Mermaid 渲染依赖 CDN；页面还不能完全承担“项目封面图”的展示任务。 | 保持 `docs/architecture/diagrams.md` 为唯一 Mermaid 源；继续优化 `overview.html` 的布局、层级、色彩和说明；图只保留 Current Runtime、Target Runtime、Maintenance Workflow 三张核心图；HTML 不能成为第二套架构真相。 |

## 短期 Program 队列

当前 active program 只在 `.agent/programs/` 根目录平铺存在。当前 active phase 是 `PHASE01_repo-layout-audit.md`。后续 program 草案在 `.agent/architecture/future/programs/`，打开时必须迁入 `.agent/programs/` 并从 `PHASE01` 重新编号。

1. `zuno-workflow-doc-system-v1`：已完成，归档到 `docs/history/programs/zuno-workflow-doc-system-v1/`。
2. `zuno-target-architecture-refresh-v1`：已完成，归档到 `docs/history/programs/zuno-target-architecture-refresh-v1/`。
3. `zuno-repo-layout-cleanup-v1`：active。整理整个仓库目录、根目录必要入口、docs、`.agent`、tools/tests、生成物隔离和 `src/backend` 六层目标表达，先审计和计划，再小步迁移。
4. `zuno-runtime-architecture-upgrade-v1`：queued。只在 Program 2/3 边界清楚后推进 runtime slice，重点是 GraphRAG LLM entity extraction、knowledge extractor configs、memory/capability/trace hardening。
5. `zuno-architecture-visuals-v1`：queued。重做架构 HTML / Mermaid 展示面，保持图形展示不成为第二套架构真相。

已被替换的 V2 目标运行时材料归档在：

- `docs/history/programs/zuno-target-runtime-v2/`

已完成的 target architecture migration 程序归档在：

- `docs/history/programs/zuno-target-architecture-migration-v1/`

已完成的短期前两项 program 归档在：

- `docs/history/programs/zuno-workflow-doc-system-v1/`
- `docs/history/programs/zuno-target-architecture-refresh-v1/`

## 已完成状态

- Phase 01 到 Phase 10 已完成。
- Phase 11A：已完成。项目查询 runtime 已引入 `KnowledgeQueryService`、`GraphRAGQueryService`、`GraphRAGProjectSnapshot` 和 `KnowledgeQueryResult`。
- Phase 11B：已完成。知识查询已统一到 single `GeneralAgent` path，通过 `search_knowledge_base` 和 `KnowledgeQueryService` 执行。
- Phase 11C：active runtime cleanup 已完成。当前 FastAPI router 不再挂载 `/domain-packs`；Vue knowledge route/settings 不再打开 Domain Pack 页面；`AgentRuntime` facade、`MultiAgentSupervisorGraph`、`DomainQAGraph`、legacy graph states 和 `zuno.services.domain_pack` 已从当前主线退休。
- Phase 12：已通过 target migration closure evidence 关闭。full pytest、formal Contract Review eval、stackless eval baseline comparison、trace metadata、legacy grep classification 和 docs/evidence sync 已完成。

## 下一步

当前 `.agent/programs/` 已打开 `zuno-repo-layout-cleanup-v1`，从 `PHASE01_repo-layout-audit.md` 开始，不在 Program 1 或 Program 2 后追加 phase。

执行面是 `.agent/programs/implementation-roadmap.md` 和 `.agent/programs/PHASE01_repo-layout-audit.md`。后续 queued program 源是 `.agent/architecture/future/programs/`。

## 当前候选主线

`.agent/programs/` 是当前 program 平铺目录。当前 active phase 是 `PHASE01_repo-layout-audit.md`。它不能把成熟 Context Orchestrator、Memory Engine、Dynamic Capability Selector、GraphRAG LLM entity extraction、full LangGraph runtime、六层 facade 物理迁移或大文件轻拆写成 Current，直到代码和测试证明对应 slice。

当前架构图入口：

- `docs/architecture/diagrams.md`

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
- `.agent/programs/PHASE01_repo-layout-audit.md`
- `.agent/architecture/future/programs/`
- `docs/history/programs/zuno-target-runtime-v2/`
- `docs/history/programs/zuno-target-architecture-migration-v1/`
- `docs/history/programs/official-graphrag-cleanup-v1/`
