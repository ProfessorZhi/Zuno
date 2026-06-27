# 目标运行架构

## 用途

Define the canonical near-term Zuno target runtime without claiming it is fully
current. This file replaces the old fragmented overview, system context,
container/component, layering, FastAPI service, LangGraph, LangChain adapter,
and observability notes.

## 目标摘要

```text
Local-first Agent Workspace
= Single GeneralAgent Runtime
+ Context / Memory Engine
+ Capability / Tool Retrieval
+ Knowledge / GraphRAG Retrieval
+ Evidence / Citation / Trace / Eval
+ Typed API + Web/Desktop
```

Zuno stays a Python/FastAPI modular monolith now and remains service-ready
later. The goal is not to create more directories mechanically. The goal is to
make every concept have one owner, every file have one home, and every runtime
path be explainable through tests and traces.

## 六个主层与横切治理

```text
1. API Layer
   FastAPI routes / DTO / Application Services

2. Agent Layer
   Single GeneralAgent Runtime
   prepare_context -> agent_loop -> post_turn_commit

3. Memory Layer
   L0 Working Context
   L1 Recent Interaction Window
   L2 Task Summary Memory
   L3 Structured Long-term Memory
   L4 External Knowledge
   Raw Event Log

4. Capability Layer
   ToolCard Registry
   Keyword / alias search
   Native BM25 over ToolCard
   Optional vector tool search
   Permission / health / cost filter
   Capability selection trace

5. Knowledge Layer
   KnowledgeQueryService
   GraphRAGQueryService
   GraphRAGProjectSnapshot
   LLM-first entity / relation extraction
   basic / local / global / drift
   auto router
   Query variants
   Native BM25
   Dense vector
   Graph local
   Community global
   Deduplication
   RRF fusion
   Optional rerank
   Evidence check
   Citation

6. Platform Layer
   PostgreSQL / Redis / RabbitMQ / MinIO
   Milvus / Neo4j / Elasticsearch optional adapter
   model gateway / storage / background jobs

Cross-cutting Governance
   Evidence / Citation / Trace / Eval / Policy
   latency / cost / permission / fallback metadata
```

Product clients live in `apps/web` and `apps/desktop`. They are entry surfaces
over the API layer, not a separate backend ownership layer.

## 产品层

`apps/web` and `apps/desktop` own product interaction. They display chats,
knowledge projects, GraphRAG Project settings, capability state, memory
surfaces, evidence, citations, and trace summaries.

They must not own graph traversal, provider calls, rerank policy, prompt
versioning, database writes, or migration-only fields such as active public
`domain_pack_id`.

## API 与应用层

FastAPI routes own HTTP boundaries only:

- route registration
- request/response DTOs
- auth and permission boundary
- validation
- streaming/SSE boundary
- request/trace id propagation
- error mapping

Application services own use cases:

- chat session creation and recovery
- knowledge query orchestration
- project, memory, and capability commands
- indexing job creation
- DTO-to-runtime command mapping
- transaction and permission checks

Routes should call exactly one use-case boundary. They should not import
concrete retrievers, GraphRAG traversal code, provider clients, or runtime graph
internals.

## 单一 GeneralAgent 运行时

All conversational requests enter one `GeneralAgent` mainline:

```text
prepare_context
  -> agent_loop
  -> post_turn_commit
```

The current code already has the single GeneralAgent path, minimal
`ContextOrchestrator`, `ModelContextPacket`, capability foundation, and memory
foundation. The target is the mature form:

- `prepare_context`: builds model-visible context from pinned instructions,
  recent window, task summaries, structured memories, knowledge evidence, tool
  results, and selected ToolCards.
- `agent_loop`: executes the LangGraph/LangChain model and tool loop through
  one runtime, not through parallel conversational agents.
- `post_turn_commit`: appends raw events, writes checkpoints, updates task
  summaries, extracts structured memory candidates, records traces, and schedules
  async work when needed.

## LangChain 与 LangGraph 的职责

LangChain provides provider/model/tool/message abstractions:

- model adapter
- message adapter
- tool schema and invocation adapter
- structured output adapter
- prompt rendering adapter

LangGraph provides stateful runtime control:

- state loop
- checkpoint and resume
- interrupt and recovery
- conditional routing
- step trace

LangGraph should orchestrate the single GeneralAgent runtime. It should not
restore a second chat agent, `DomainQAGraph`, or a default multi-agent runtime.

## 可观测性与 Eval

Every important query path should be explainable through:

- `trace_id`
- requested and resolved query method
- selected capabilities
- context selection and eviction reasons
- retrievers used
- fusion and optional rerank trace
- evidence bundle
- citation coverage
- prompt and query prompt version
- index and community version
- latency and cost metadata when available

Eval and benchmark surfaces live under `tools/evals/zuno/` and curated evidence
under `docs/evidence/`. Generated local reports stay out of the front path until
explicitly promoted.

## 当前、基础、目标与未来边界

- Current: single GeneralAgent mainline, GraphRAG Project query runtime,
  KnowledgeQueryService, minimal ContextOrchestrator, context/memory/capability
  foundations.
- Target: mature Context & Memory Engine, ToolCard retrieval, dynamic
  capability selection, full `prepare_context -> agent_loop -> post_turn_commit`
  LangGraph runtime, retrieval/fusion/evidence trace closure.
- Future: Java business services, microservices, event workers, product-level
  multi-agent mode, and Coding Agent mode.

Do not promote Target or Future behavior to Current until code, tests,
verifiers, and evidence prove it.
