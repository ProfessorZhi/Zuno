# 架构路线图

## 当前状态

Phase 0-6 架构收口仍是已完成的历史事实。

当前可执行 Agent 程序是：

- `.agent/programs/`

它接在 Target Architecture Migration V1 收口之后，当前职责是按小 phase 落地目标 runtime。已完成的 V2 Phase 00-04 详细文件和证据归档在：

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

按当前 active `.agent/programs/` 平铺计划线性执行：

1. Phase 05：记忆引擎
2. Phase 06 Capability / Tool Retrieval
3. Phase 07 GraphRAG LLM Entity Extraction / Knowledge Retrieval / Fusion
4. Phase 08 GeneralAgent LangGraph Runtime
5. Phase 09：产品边界、Trace 与 Eval 收口

执行源是 `.agent/architecture/near-term/` 和 `.agent/programs/implementation-roadmap.md`。

## 当前候选主线

`.agent/programs/` 是当前 active program 平铺目录。它不能把成熟 Context Orchestrator、Memory Engine、Dynamic Capability Selector、GraphRAG LLM entity extraction 或 full LangGraph runtime 写成 Current，直到代码和测试证明对应 slice。

## 受限历史兼容

这些内容是兼容保留，不是目标方向：

- 剩余 `domain_pack_id` references 只属于 migration aliases、existing Agent database-column compatibility、eval CLI compatibility 和 retirement/history tests。
- root `domain-packs/` archive 保留在 `docs/history/domain-packs/root-contract-review/`。
- root Phase 11C retired-import guards 保留用于防回归。

## 当前基础切片收口

- Phase 05 Context Contract foundation：`src/backend/zuno/services/application/context/`
- Phase 06 Memory Layer foundation：`src/backend/zuno/services/memory/layers.py`
- Phase 07 Capability System foundation：`src/backend/zuno/services/application/capabilities/`
- Phase 08 GeneralAgent runtime integration：`src/backend/zuno/core/agents/general_agent.py`

这些是 foundation，不等于成熟产品能力。

## 未来执行阶段

- Phase 05: mature Memory Engine around Raw Event Log、Summary Compression、Structured Extraction、`source_event_ids` 和 ContextTrace。
- Phase 06: mature Capability / Tool Retrieval around ToolCard Registry、Native BM25 capability search、filters 和 `CapabilitySelectionTrace`。
- Phase 07: mature Knowledge Retrieval / Fusion around LLM-first GraphRAG entity extraction、Native BM25、multi-query、multi-retriever recall、RRF `k=60`、optional rerank、evidence、citation 和 trace。
- Phase 08: explicit `prepare_context -> agent_loop -> post_turn_commit` LangGraph runtime，同时保持 single `GeneralAgent` path。
- Phase 09：产品 / API 边界、前端可见状态、trace / eval 收口、`docs/` 与 `.agent/` 前台路径瘦身、临时产物清理和历史归档卫生。

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
- `.agent/programs/phase-*.md`
- `.agent/programs/closure-checklist.md`
- `docs/history/programs/zuno-target-runtime-v2/`
- `docs/history/programs/zuno-target-architecture-migration-v1/`
- `docs/history/programs/official-graphrag-cleanup-v1/`
