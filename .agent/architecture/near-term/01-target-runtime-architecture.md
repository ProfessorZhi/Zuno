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

DeepSearchAgents is useful as a product-closure reference, not as a replacement
identity. Zuno should absorb its clear task flow, session workspace, uploaded
file handling, artifact delivery, and observable long-running execution. Zuno
should not absorb its fixed one-main-three-worker runtime as the default
architecture.

Target task-to-artifact flow:

```text
User Task
  -> Typed API task / session
  -> Session Workspace
  -> Single GeneralAgent
  -> Capability Selector
  -> Web / structured data / GraphRAG-RAG adapter / uploaded file capabilities
  -> Evidence / Citation / Trace
  -> Answer / Markdown / PDF / Artifact
  -> SSE or WebSocket event stream
```

## 六个主层与横切治理

```text
1. API Layer
   FastAPI routes / DTO / Application Services
   task / session / upload / artifact list-download
   SSE or WebSocket event stream

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
   Web search / structured data / GraphRAG-RAG adapter / file / artifact tools

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
   Multi-source evidence normalization

6. Platform Layer
   PostgreSQL / Redis / RabbitMQ / MinIO
   Milvus / Neo4j / Elasticsearch optional adapter
   model gateway / session workspace / artifact store / storage / background jobs

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
- research task creation, cancellation, and progress state
- upload handoff into session workspace
- artifact list and download boundaries
- knowledge query orchestration
- project, memory, and capability commands
- indexing job creation
- DTO-to-runtime command mapping
- transaction and permission checks

Routes should call exactly one use-case boundary. They should not import
concrete retrievers, GraphRAG traversal code, provider clients, or runtime graph
internals.

## 多来源 Evidence Channel

Zuno's target equivalent of DeepSearchAgents' Tavily / MySQL / RAGFlow /
uploaded-file split is provider-neutral:

| Source channel | Zuno owner | Runtime output |
| --- | --- | --- |
| Public web | Web Search Capability | URL-backed evidence and trace |
| Structured business data | Structured Data Capability | table / row evidence and permission trace |
| Internal documents | Knowledge / GraphRAG or external RAG adapter | document evidence and citations |
| Uploaded files | File Capability + Session Workspace | extracted file evidence and hash/path trace |
| Generated reports | Artifact Capability + Platform storage | artifact id, download path, artifact_created event |

All channels return evidence to the Agent. None of them become Agent Memory
without Raw Event Log, Summary Compression, Structured Extraction, source ids,
and permission checks.

## 会话工作区与运行事件

The target session workspace binds task id, session id, uploaded files,
intermediate files, generated artifacts, event index, and trace id. A concrete
implementation may use local filesystem storage, object storage, database rows,
or a hybrid. `session_dir` and `ContextVar` are implementation options, not
the architecture identity.

Long tasks need a typed runtime event stream. The transport may be SSE or
WebSocket. The event contract should cover at least:

- `task_started`
- `workspace_created`
- `capability_selected`
- `tool_call_started`
- `evidence_ready`
- `artifact_created`
- `fallback_applied`
- `task_cancelled`
- `error`

This stream is a Trace / Observability presentation boundary. It is not a new
business layer and does not replace durable trace evidence.

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
