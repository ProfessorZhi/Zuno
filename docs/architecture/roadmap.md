# 架构路线图

## 当前状态

Phase 0-6 架构收口仍是已完成的历史事实。

当前可执行 Agent 程序是：

- `.agent/programs/`

当前 program 是 `zuno-architecture-surface-cleanup-v1`。它接在目标运行时第一轮 slice 之后，当前职责不是继续堆 feature，而是把 Zuno 收口成成熟项目外形：README、docs、`.agent`、目录蓝图、tools/tests 和架构图都能一眼讲清。

本 program 的 PHASE01 只做公开封面与架构叙事收口：README、`docs/architecture/*` 和 Mermaid 图。它不修改 runtime、API、DTO、DB schema、依赖、Docker 或 eval baseline。

已被替换的 V2 目标运行时材料归档在：

- `docs/history/programs/zuno-target-runtime-v2/`

已完成的 target architecture migration 程序归档在：

- `docs/history/programs/zuno-target-architecture-migration-v1/`

## 已完成状态

- Phase 01 到 Phase 10 已完成。
- Phase 11A：已完成。项目查询 runtime 已引入 `KnowledgeQueryService`、`GraphRAGQueryService`、`GraphRAGProjectSnapshot` 和 `KnowledgeQueryResult`。
- Phase 11B：已完成。知识查询已统一到 single `GeneralAgent` path，通过 `search_knowledge_base` 和 `KnowledgeQueryService` 执行。
- Phase 11C：active runtime cleanup 已完成。当前 FastAPI router 不再挂载 `/domain-packs`；Vue knowledge route/settings 不再打开 Domain Pack 页面；`AgentRuntime` facade、`MultiAgentSupervisorGraph`、`DomainQAGraph`、legacy graph states 和 `zuno.services.domain_pack` 已从当前主线退休。
- Phase 12：已通过 target migration closure evidence 关闭。full pytest、formal Contract Review eval、stackless eval baseline comparison、trace metadata、legacy grep classification 和 docs/evidence sync 已完成。

## 下一步

按当前 active `.agent/programs/` 平铺计划线性执行。每个新 program 都从 `PHASE01` 开始，旧 phase 文件从当前前台移除：

1. PHASE01：公开封面与架构叙事收口
2. PHASE02：本地 Agent Skill System 收口
3. PHASE03：tools / tests 工作流防回归
4. PHASE04：后端六层 facade 分层
5. PHASE05：大文件轻拆
6. PHASE06：架构图与 HTML 展示页

执行源是 `.agent/architecture/near-term/` 和 `.agent/programs/implementation-roadmap.md`。

## 当前候选主线

`.agent/programs/` 是当前 active program 平铺目录。它不能把成熟 Context Orchestrator、Memory Engine、Dynamic Capability Selector、GraphRAG LLM entity extraction、full LangGraph runtime、六层 facade 物理迁移或大文件轻拆写成 Current，直到代码和测试证明对应 slice。

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

## 未来执行阶段

- PHASE01: README、docs/architecture、Mermaid 三图和公开叙事收口。
- PHASE02: `.agent` 本地 Skill System，包含 `system.yaml`、references skills 和 templates 边界。
- PHASE03: tools / tests 防回归，确保 program 平铺、PHASE01 编号、docs drift 和 skill 文件结构不会漂移。
- PHASE04: backend 六层 facade，先 re-export，不改 runtime 行为。
- PHASE05: `general_agent.py`、capabilities、retrieval orchestrator、fusion 的大文件轻拆。
- PHASE06: 架构图 HTML 展示页和 Mermaid 源同步规则。

## 非目标

当前路线图不实施：

- Java services
- split microservices
- event workers
- database migrations
- dependency upgrades
- default multi-agent mode

## Agent 执行来源

- `.agent/programs/current.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/PHASE*.md`
- `.agent/programs/closure-checklist.md`
- `docs/history/programs/zuno-target-runtime-v2/`
- `docs/history/programs/zuno-target-architecture-migration-v1/`
- `docs/history/programs/official-graphrag-cleanup-v1/`
