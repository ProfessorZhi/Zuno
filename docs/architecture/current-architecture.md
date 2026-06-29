# 当前架构

## 用途

这份文档只描述当前仓库已经由代码和测试证明的事实，不描述尚未实现的目标状态。

当前一句话：

```text
Zuno current = monorepo + FastAPI backend + Single GeneralAgent Runtime + Knowledge / GraphRAG query path + evidence / citation / trace foundation
```

## 当前仓库边界

Zuno 当前是一个 monorepo，主要前台边界是：

```text
apps/web
apps/desktop
src/backend/zuno
infra
tools
tests
docs
.agent
```

`src/backend/zuno` 是唯一当前 Python 后端 runtime 边界。当前事实中没有 active root-level `services/` 后端树，也没有 active `src/frontend` workspace。

## 当前后端形态

- FastAPI 入口：`src/backend/zuno/main.py`
- API 层：`src/backend/zuno/api/`
- Runtime / core 层：`src/backend/zuno/core/`
- Service 层：`src/backend/zuno/services/`
- 持久化和设置：`src/backend/zuno/database/`、`src/backend/zuno/settings.py`
- MCP server implementations：`src/backend/zuno/capability/mcp/servers/`，旧 `zuno.mcp_servers.*` 只作为 compatibility shell。
- HTTP middleware implementations：`src/backend/zuno/platform/middleware/`，旧 `zuno.middleware.*` 只作为 compatibility shell。
- Runtime 资源：`src/backend/zuno/resources/`
- 兼容边界：`src/backend/zuno/compatibility/`
- Eval 和维护工具：`tools/evals/zuno/`、`tools/scripts/`

## 当前 GraphRAG 与 Agent 主线

当前代码和聚焦测试证明的主线是：

```text
Completion API
  -> CompletionService
  -> GeneralAgent single loop
  -> search_knowledge_base
  -> KnowledgeQueryService
  -> GraphRAGQueryService
  -> RetrievalPlanner / RetrievalOrchestrator
  -> Evidence / Citation / Trace
  -> GeneralAgent answer
```

已证明的当前事实：

- Phase 11A：已完成。当前代码包含 `KnowledgeQueryService`、`GraphRAGQueryService`、`GraphRAGProjectSnapshot` 和 `KnowledgeQueryResult`。
- Phase 11B：已完成。`GeneralAgent.astream()` 使用单一会话路径，`search_knowledge_base` 调用 `KnowledgeQueryService`。
- Phase 11C：active runtime cleanup 已完成。`DomainQAGraph`、`MultiAgentSupervisorGraph`、`AgentRuntime`、legacy graph states 和 `zuno.services.domain_pack` 不再是当前后端主线。
- Phase 12：已通过 target migration closure evidence 关闭。full pytest、Contract Review eval、stackless baseline comparison、trace metadata、legacy grep classification 和 docs/evidence sync 已完成。

Workspace knowledge prefetch、Workspace `search_knowledge_base` tool 和 `/knowledge/search` API service path 现在都通过 `KnowledgeQueryService`。

当前 runtime 图见：

- [diagrams.md](diagrams.md)

## 当前兼容边界

`graphrag_project_id` 是 Agent 和 Knowledge public DTO 的目标身份字段。

`domain_pack_id` 仍可能出现在：

- migration alias
- 旧数据库兼容字段
- eval CLI 兼容
- retirement / history tests

它不是 active mainline，也不是新的目标公开字段。

旧 root `domain-packs/` 已归档到：

- `docs/history/domain-packs/root-contract-review/`

Docker 不再复制或挂载 `/app/domain-packs`。

## 当前基础切片

这些是当前已经存在的基础切片，但不能写成成熟产品能力：

- Typed Context Contract models 和 minimal pre-call `ContextOrchestrator`：`src/backend/zuno/services/application/context/`
- Memory layer foundation contracts：`src/backend/zuno/services/memory/layers.py`
- Capability System foundation contracts：`src/backend/zuno/services/application/capabilities/`
- `GeneralAgent.astream()` 的 minimal runtime integration：准备 `ModelContextPacket`、传递 `context_trace`、选择有限 capability schema，并在 memory enabled 时提交 scoped raw event 与 task summary。
- Program 3 backend layout cleanup：顶层 `src/backend/fastapi_jwt_auth/` 已退休；prompt、fixture、system skill 资源已进入 `src/backend/zuno/resources/`；legacy / vendor 兼容材料已进入 `src/backend/zuno/compatibility/`；MCP server implementations 已进入 `src/backend/zuno/capability/mcp/servers/`；HTTP middleware implementations 已进入 `src/backend/zuno/platform/middleware/`；仍保留的旧 runtime 顶层目录已由 README 和 repo structure verifier 固定分类。

## 不属于 Current

以下仍是 Target，不是当前成熟事实：

- production-grade memory extraction / retrieval / consolidation
- mature Context Orchestrator product behavior
- product-level dynamic capability orchestration
- 完整 `prepare_context -> agent_loop -> post_turn_commit` LangGraph runtime
- production-grade Memory DB
- 完整 frontend trace 面板
- Native BM25 capability search
- multi-query / multi-retriever / RRF / optional rerank 的完整 retrieval fusion
- GraphRAG LLM-first entity / relation extraction 的生产实现
- 可由知识库选择的多套 extractor / config 治理
- API / Agent / Memory / Capability / Knowledge / Platform 六个主层的完整物理迁移；当前只完成资源、兼容目录、MCP server implementations 和 HTTP middleware implementations 的低风险物理收敛

## 历史完成事实

Phase 0-6 architecture closure 是历史完成事实，不应被重写成未完成。

## 文档边界

- `docs/`：正式人类文档。
- `.agent/`：Agent 工作流库和目标设计工作集。
- `docs/history/`：完成、过时或被替换的历史材料。
