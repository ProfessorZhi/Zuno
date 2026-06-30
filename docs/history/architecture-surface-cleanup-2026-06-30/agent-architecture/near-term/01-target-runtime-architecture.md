# 目标运行架构

## 用途

定义 Zuno 近期目标 runtime。本文是 Target / Proposed，不是 Current truth。Current 必须回到 `docs/architecture/current-architecture.md` 和代码/测试证明。

## 目标摘要

```text
Local-first Agent Workspace
= Single Controller Agent
+ Context Builder
+ Agentic RAG Controller
+ GraphRAG Knowledge Base
+ ToolCard / MCP Tool Layer
+ Hooks / Policy / Budget / Fallback
+ Evidence / Citation / Trace / Eval
+ Session Workspace / Artifact Flow
```

Zuno 近期保持 Python/FastAPI modular monolith。目标不是机械增加目录，而是让每个概念有 owner、每个 runtime 决策有 trace、每个答案能回到 evidence。

## 主链路

```text
User Query
  -> Session Manager
  -> Context Builder
  -> Single Controller Agent
  -> Product Mode Policy: normal / enhanced / auto
  -> Router Decision: direct / normal_basic / enhanced_basic|local|global|drift
  -> Retrieval: basic / local / global / drift
  -> Evidence Check
  -> Answer Synthesizer
  -> Citation Builder
  -> Trace / Eval / Memory Write
  -> Answer / Report / Artifact
```

DeepSearchAgents 值得吸收的是任务闭环表达、session workspace、上传附件、artifact delivery、长任务事件流和 README 展示方式。Zuno 不吸收它的固定一主三从默认 runtime。

## 产品层三模式

```text
普通模式 = low-budget basic path
增强模式 = controlled Agentic RAG path
自动模式 = router decides direct / basic / enhanced
```

普通用户默认走自动模式。高级用户和调试场景可以手动指定内部 `query_method`。

Trace / eval 中必须分开记录：

- `requested_product_mode` / `resolved_product_mode`：产品模式。
- `router_decision`：`normal_basic` 或 `enhanced_basic|local|global|drift` 等路由解释。
- `requested_query_method` / `resolved_query_method`：requested 可为 `auto`，resolved 只能是 `basic / local / global / drift`。
- `fallback_reason`、`budget_policy`、`fallback_policy`、`citation_coverage`：解释降级、预算和证据覆盖。

## 内部四方法

```text
query_method = basic | local | global | drift
```

`auto` 是 router，不是第五种 query method。

- `basic`：Native BM25 + Dense Vector + RRF + optional rerank。
- `local`：entity / relation / graph neighborhood / source chunks。
- `global`：community reports / global summaries / map-reduce style synthesis。
- `drift`：global primer -> follow-up questions -> local/basic evidence loop。

## 六个主层与横切治理

```text
1. API Layer
   FastAPI routes / DTO / Application Services
   task / session / upload / artifact list-download
   SSE or WebSocket event stream

2. Agent Layer
   Single Controller Agent
   prepare_context -> agent_loop -> post_turn_commit
   Plan + ReAct + gated Reflection

3. Memory Layer
   short-term state
   working memory
   semantic memory
   episodic memory
   procedural memory
   Raw Event Log

4. Capability Layer
   ToolCard Registry
   keyword / alias search
   Native BM25 over ToolCard
   optional vector tool search
   permission / health / cost filter
   MCP / connector adapter

5. Knowledge Layer
   KnowledgeQueryService
   GraphRAGQueryService
   GraphRAGProjectSnapshot
   LLM-first entity / relation extraction
   basic / local / global / drift
   retrieval / fusion / evidence

6. Platform Layer
   PostgreSQL / Redis / RabbitMQ / MinIO
   Milvus / Neo4j / optional Elasticsearch adapter
   model gateway / session workspace / artifact store / background jobs

Cross-cutting Governance
   Evidence / Citation / Trace / Eval / Policy
   latency / cost / permission / fallback metadata
```

Product clients live in `apps/web` and `apps/desktop`. They are entry surfaces over API, not backend ownership layers.

## Context Builder

The model should not receive the raw repository, raw memory, raw retrieval output, and all tools at once. Target context preparation is:

```text
system rules
+ user settings
+ session state
+ task state
+ selected memory
+ selected evidence
+ selected ToolCards
+ uploaded file summaries
-> Context Pack
```

Context Builder owns context selection, compression, eviction reasons, and trace metadata. It does not own retrieval semantics or final answer generation.

## Hooks / Middleware

Hooks are runtime governance points, not just logging:

- before agent: inject thread metadata, route policy, budget.
- before model: trim context, choose model, limit tool surface.
- around tool: permission, cache, metering, fallback, result normalization.
- before final answer: citation coverage, evidence coverage, output shape.
- post turn: trace write, memory candidate, artifact event, eval metadata.

## Multi-source Evidence Channel

Zuno 的目标等价于 DeepSearchAgents 的 Tavily / MySQL / RAGFlow / uploaded-file 分工，但边界必须 provider-neutral：

| Source channel | Zuno owner | Runtime output |
| --- | --- | --- |
| Public web | Web Search Capability | URL-backed evidence and trace |
| Structured business data | Structured Data Capability | table / row evidence and permission trace |
| Internal documents | Knowledge / GraphRAG or external RAG adapter | document evidence and citations |
| Uploaded files | File Capability + Session Workspace | extracted file evidence and hash/path trace |
| Generated reports | Artifact Capability + Platform storage | artifact id, download path, artifact_created event |

All channels return evidence to Agent Context. None become Agent Memory without Raw Event Log, Summary Compression, Structured Extraction, source ids, and permission checks.

## Runtime events

Target event stream covers:

- `task_started`
- `workspace_created`
- `capability_selected`
- `tool_call_started`
- `evidence_ready`
- `artifact_created`
- `fallback_applied`
- `task_cancelled`
- `error`

The transport may be SSE or WebSocket. This is Trace / Observability presentation, not a new business layer.

## Current / Target / Future

- Current: single GeneralAgent mainline, GraphRAG Project query runtime, KnowledgeQueryService, minimal ContextOrchestrator, context/memory/capability foundations.
- Target: mature Context Builder, ToolCard retrieval, dynamic capability selection, full `prepare_context -> agent_loop -> post_turn_commit`, retrieval/fusion/evidence trace closure.
- Future: Java business services, microservices, event workers, product-level multi-agent mode, Coding Agent mode, default tree-search reasoning.

Do not promote Target or Future behavior to Current until code, tests, verifiers, and evidence prove it.
