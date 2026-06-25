# Layered Architecture

## Purpose

Define the near-term dependency direction and responsibilities.

## Target Stack

```text
Frontend / Desktop
  -> API Client
  -> FastAPI API Layer
  -> Application Service Layer
  -> LangGraph Orchestration Layer
  -> Retrieval / RAG / GraphRAG Layer
  -> LLM / LangChain / Tool Adapter Layer
  -> Persistence / Storage Layer
  -> Observability / Evaluation Layer
```

## Frontend / Desktop

Responsibilities: product mode, user flows, settings display, evidence/citation
display, trace display.

Non-Responsibilities: internal graph route names, provider clients, graph query
planning, storage version writes.

Current Evidence: `apps/web/src/apis/`, `apps/web/src/utils/retrieval.ts`,
`apps/web/src/utils/knowledge-config.ts`, and `apps/desktop/`.

Target Design: expose Standard Mode, Enhanced Mode, and optional advanced query
method controls without leaking old names like `local_graphrag`.

Migration Notes: migrate UI/API payloads from `domain_pack_id` and
`rag_graph_deep` toward `graphrag_project_id` and query methods.

## FastAPI API Layer

Responsibilities: route registration, request parsing, auth boundary,
validation, response envelopes, streaming boundary, trace id propagation.

Non-Responsibilities: retrieval strategy, graph traversal, rerank policy,
prompt tuning, durable business decisions.

Current Evidence: `src/backend/zuno/main.py`, `src/backend/zuno/api/router.py`,
and `src/backend/zuno/api/v1/`.

Target Design: routes call application services with typed command/DTO shapes.

Migration Notes: keep `/api/v1` stable while retiring old surfaces behind
versioned replacements.

## Application Service Layer

Responsibilities: use cases, runtime setting resolution, transaction boundary,
permission checks, command mapping, LangGraph invocation.

Non-Responsibilities: provider-specific LLM calls, graph-store query strings,
frontend display text.

Current Evidence: `src/backend/zuno/api/services/`.

Target Design: services become the boundary between API routes and AI runtime
graphs.

Migration Notes: move complex route behavior into services before graph or
retrieval changes.

## LangGraph Orchestration Layer

Responsibilities: graph state, node order, fallback decisions, evidence
assembly, citation check, final trace.

Non-Responsibilities: SQL, Neo4j Cypher, provider configuration, frontend
contracts.

Current Evidence: `DomainQAGraph`. Historical evidence:
`MultiAgentSupervisorGraph` existed but has retired from current backend source.

Target Design: `GraphRAGQAGraph` becomes the near-term primary QA graph.

Migration Notes: migrate from `DomainQAGraph` terminology without changing
runtime behavior blindly.

## Retrieval / RAG / GraphRAG Layer

Responsibilities: query method routing, BM25/vector/graph recall, fusion/RRF,
rerank, evidence checks, GraphRAG project/index/query semantics.

Current Evidence: `services/retrieval`, `services/rag`, `services/graphrag`.

Target Design: Basic, Local, Global, and DRIFT are query methods; retrievers are
recall channels.

Migration Notes: first normalize names and trace contracts, then change storage
fields.

## LLM / LangChain / Tool Adapter Layer

Responsibilities: model/provider isolation, prompt rendering, tool schema,
MCP/local tool adapters, embedding and rerank adapters.

Current Evidence: `core/models`, `services/llm`, `services/embedding`,
`services/mcp`, `services/mcp_openai`, `tools`, `prompts`, `rag/rerank.py`.

Target Design: providers do not leak into service or graph contracts.

## Persistence / Storage Layer

Responsibilities: PostgreSQL, vector store, graph store, object storage, cache,
version fields, task state.

Current Evidence: `database/`, `services/rag/vector_db/`,
`services/graphrag/client.py`, storage config.

Target Design: `graphrag_project_id`, `prompt_version`, `index_version`,
`document_hash`, `chunk_hash`, `community_version`.

## Observability / Evaluation Layer

Responsibilities: trace ids, route metadata, cost, latency, eval fixtures,
regression reports.

Current Evidence: `middleware/trace_id_middleware.py`, graph trace metadata,
retrieval orchestrator metadata, `tools/evals/zuno/`.

Target Design: every query explains requested method, resolved method,
retrievers used, fallback reason, evidence, citation coverage, and index
versions.

## Acceptance Direction

A later implementation phase should prove each layer can be tested or inspected
without relying on unrelated layers.
