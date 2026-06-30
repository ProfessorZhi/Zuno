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
- Agent 层：`src/backend/zuno/agent/`
- Memory 层：`src/backend/zuno/memory/`
- Capability 层：`src/backend/zuno/capability/`
- Knowledge 层：`src/backend/zuno/knowledge/`
- Platform 层：`src/backend/zuno/platform/`
- 旧 `core`、`services`、`database`、`schema`、`tools`、`utils`、`config`、`resources`、`compatibility` import path 由 `src/backend/zuno/platform/compatibility/legacy_aliases.py` 注册兼容，真实实现位于六层内部。
- MCP server implementations：`src/backend/zuno/capability/mcp/servers/`，旧 `zuno.mcp_servers.*` 由 legacy alias registry 承接。
- HTTP middleware implementations：`src/backend/zuno/platform/middleware/`，旧 `zuno.middleware.*` 由 legacy alias registry 承接。
- Runtime 资源：`src/backend/zuno/platform/resources/`
- 兼容边界：`src/backend/zuno/platform/compatibility/`
- Eval 和维护工具：`tools/evals/zuno/`、`tools/scripts/`；旧 `zuno.evals.*` 由 legacy alias registry 指向 `tools/evals/zuno/`。

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
- PHASE04 Query Router foundation：`CompletionReq`、`AgentConfig`、`KnowledgeQueryService`、`GraphRAGQueryService`、`RetrievalRequest`、`RetrievalPlan`、`RetrievalPlanner` 和 `RetrievalOrchestrator` 已经贯通 `product_mode = normal | enhanced | auto` 与 `query_method = auto | basic | local | global | drift` 的请求/路由/trace 基础。`auto` 在 trace 中表示 router；`resolved_query_method` 只落到 `basic | local | global | drift`。当前 trace metadata 已包含 requested/resolved product mode、requested/resolved query method、router decision、fallback reason、budget policy、fallback policy、evidence coverage 和 retrievers used。
- PHASE08 GraphRAG Knowledge Runtime foundation：`GraphRAGExtractorConfig`、`GraphRAGProjectSnapshot.extractor_config`、`query_method_contract`、`citation_contract` 和 `retrieval_fusion_contract` 已经进入当前 query trace。`KnowledgeQueryService` 会从现有 `knowledge_config` JSON 组装 LLM-first extractor config 与 rule fallback 信息，`RetrievalPlanner` 会把显式 `global` 路径约束为 `community_global`，不再与 vector / BM25 chunk-level retrievers 扁平混榜；`GeneralAgent` 知识库工具返回文本会暴露 `query_method_contract`。这些事实由 PHASE08 focused tests 和 legacy import guard 证明。

Workspace knowledge prefetch、Workspace `search_knowledge_base` tool 和 `/knowledge/search` API service path 现在都通过 `KnowledgeQueryService`。

上面的调用链是当前 runtime 事实。目标架构图见：

- [architecture.md](../architecture.md)
- [architecture.html](../architecture.html)

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

- Typed Context Contract models 和 minimal pre-call `ContextOrchestrator`：当前经 `zuno.services.application.context` 兼容入口访问，物理位于 `src/backend/zuno/platform/services/application/context/`。PHASE05 已证明 `ContextPackPolicy`、`ModelContextPacket.context_policy`、source id coverage trace 和缺失 source id 检查这组 foundation contract。
- Memory layer foundation contracts：当前可经 `zuno.memory.contracts`、`zuno.memory.store`、`zuno.memory.policy`、`zuno.memory.review`、`zuno.memory.retrieval`、`zuno.memory.rendering` 和 `zuno.memory.engine` 这些目标层薄入口访问；旧 `zuno.services.memory.layers` 兼容入口仍保留。物理实现位于 `src/backend/zuno/platform/services/memory/layers.py`。PHASE05 已证明五类 Agent memory taxonomy、structured memory pending review、approval / rejection decision、policy serialization 和 source id 要求。
- Capability System foundation contracts：当前可经 `zuno.capability.contracts`、`zuno.capability.registry`、`zuno.capability.selector`、`zuno.capability.policy`、`zuno.capability.execution`、`zuno.capability.trace` 和 `zuno.capability.retrieval` 这些目标层薄入口访问；旧 `zuno.services.application.capabilities` 和 `zuno.services.capability_registry` 兼容入口仍保留。物理实现位于 `src/backend/zuno/platform/services/application/capabilities/` 和 `src/backend/zuno/platform/services/capability_registry.py`。PHASE06 已证明 ToolCard compact metadata、Native BM25 ToolCard retrieval、type / health / permission / side-effect / cost filters、selection trace 和 GeneralAgent internal trace bridge 这组 foundation contract。
- Knowledge foundation thin surfaces：当前可经 `zuno.knowledge.contracts`、`zuno.knowledge.query_service`、`zuno.knowledge.evidence`、`zuno.knowledge.citation`、`zuno.knowledge.trace`、`zuno.knowledge.retrieval`、`zuno.knowledge.fusion` 和 `zuno.knowledge.graphrag` 访问。`zuno.knowledge.retrieval` 暴露 PHASE04 的 product mode / query method contract 常量和 `normalize_product_mode`。真实 query / retrieval / GraphRAG 行为仍在既有 services owner 中。
- Hooks / Evidence / Trace / Artifact foundation contracts：PHASE07 已证明 `HookPoint`、`RuntimeTraceEvent`、`RuntimeTraceBuilder`、`EvidenceChecker`、`EvidenceVerdict` 和 `TraceArtifactManifest` 这组 trace artifact contract。`GraphRAGQueryService` 会在 query result trace metadata 中生成 runtime trace events、evidence verdict 和 artifact manifest；`GeneralAgent` 知识库工具会通过既有 custom event 通道发出 additive trace payload，并把低置信 evidence status 写入工具返回文本；tool middleware 会在既有 START / END / ERROR payload 内添加 pre-tool / post-tool trace event。Multihop eval diagnostics 已能读取这些 trace 字段。
- GraphRAG Knowledge Runtime foundation contracts：PHASE08 已证明 Knowledge config 可以保留 LLM-first extractor refs、prompt / schema / policy / eval refs 和 rule fallback；GraphRAG snapshot、orchestrator metadata 和 query result trace 会携带 extractor config、query method contract、citation contract 与 retrieval fusion contract；global route 当前是 community-only prior，缺少 chunk/span grounding 时 citation contract 明确为 `missing`；local route 当前可证明 vector / BM25 / graph baseline-preserving fusion trace 和 rerank-used 标记。
- Runtime Upgrade Integration foundation contracts：PHASE09 已证明 `RuntimeTurnLedger`、当前轮 knowledge/tool trace reset、`prepare_context -> capability_selection -> agent_loop -> knowledge_retrieval_trace -> tool_trace -> post_turn_commit` 的最小证据链、post-turn memory evidence payload、六层目标入口 import guard 和 eval diagnostics。
- Agent boundary thin surfaces：当前可经 `zuno.agent.runtime`、`zuno.agent.context`、`zuno.agent.post_turn`、`zuno.agent.state`、`zuno.agent.streaming` 和 `zuno.agent.tool_bridge` 访问。`GeneralAgent` 主循环仍由既有 runtime owner 承担，但 foundation contracts 已优先经 `zuno.agent` / `zuno.capability` / `zuno.knowledge` / `zuno.memory` 目标层入口引用。
- Platform foundation thin surfaces：当前可经 `zuno.platform.model_gateway`、`zuno.platform.security`、`zuno.platform.observability` 和 `zuno.platform.storage` 访问。这些只是边界入口，不改变 provider、storage、settings 或 DB 默认行为。
- `GeneralAgent.astream()` 的 minimal runtime integration：准备 `ModelContextPacket`、传递 `context_trace` / `model_context_packet`、选择有限 capability schema、保留 knowledge/tool trace、并在 memory enabled 时提交 scoped raw event、task summary 和 runtime evidence payload。PHASE09 只证明当前轮 foundation ledger，不是成熟 memory retrieval runtime 或完整 model-visible context injection。
- Program 3 backend layout cleanup：顶层 `src/backend/fastapi_jwt_auth/` 已退休；`src/backend/zuno` 顶层目录只保留 `api / agent / memory / capability / knowledge / platform`；旧 runtime 顶层目录已下沉到六层内部；根级 alias `.py` 文件退休；旧 public import path 由 legacy alias registry 兼容；repo structure verifier 和 repo tests 固定该完成态。
- Program `zuno-six-layer-internalization-v1` 已完成并归档；这只表示六层内部第一批 import surface 更清楚，不表示 Runtime Architecture Upgrade 已经完成。

## 不属于 Current

以下仍是 Target，不是当前成熟事实：

- production-grade memory extraction / retrieval / consolidation
- mature Context Orchestrator product behavior
- product-level dynamic capability orchestration
- 完整产品级 `prepare_context -> agent_loop -> post_turn_commit` LangGraph runtime，包括成熟 model-visible context injection、动态工具编排和跨前后端 trace UI
- production-grade Memory DB
- 完整 frontend trace 面板
- 完整 artifact storage / download flow
- production-grade hooks governance / middleware policy
- 产品 UI 的三模式完整改名和所有前端入口统一
- production-grade ToolCard retrieval、optional vector capability search 和完整 runtime tool filtering
- multi-query / multi-retriever / RRF / optional rerank 的完整 retrieval fusion
- GraphRAG LLM-first entity / relation extraction 的生产实现
- 可由知识库选择的多套 extractor / config 治理、生产级 extractor orchestration 和 schema-constrained LLM 抽取执行
- API / Agent / Memory / Capability / Knowledge / Platform 六个主层的成熟 runtime 内聚；当前完成的是目录表层收口、兼容 alias、第一批六层 foundation thin surfaces 和 PHASE09 最小 runtime ledger，不等于 Runtime Architecture Upgrade 已完成。

## 历史完成事实

Phase 0-6 architecture closure 是历史完成事实，不应被重写成未完成。

## 文档边界

- `docs/`：正式人类文档。
- `.agent/`：Agent 工作流库和目标设计工作集。
- `docs/history/`：完成、过时或被替换的历史材料。
