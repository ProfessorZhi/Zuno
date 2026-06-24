# Component View

## Purpose

Map the target components inside the Python AI Runtime.

## Current Evidence

- API routes live in `src/backend/zuno/api/v1/`.
- Route-adjacent services live in `src/backend/zuno/api/services/`.
- LangGraph graphs live in `src/backend/zuno/core/graphs/`.
- General agents live in `src/backend/zuno/core/agents/`.
- Retrieval planning, adapters, orchestration, and fusion live in
  `src/backend/zuno/services/retrieval/`.
- RAG vector/BM25/rerank behavior lives in `src/backend/zuno/services/rag/`.
- GraphRAG extraction, graph storage, retrieval, and community reports live in
  `src/backend/zuno/services/graphrag/`.
- Domain Pack modules still exist in `src/backend/zuno/services/domain_pack/`
  and `src/backend/zuno/domain_packs/`.

## Target Components

```text
API Layer
  -> Application Service Layer
  -> LangGraph Orchestration Layer
  -> Retrieval / RAG / GraphRAG Layer
  -> LLM / LangChain / Tool Adapter Layer
  -> Persistence / Storage Layer
  -> Observability / Evaluation Layer
```

## Responsibilities

- API Layer: request parsing, auth boundary, validation, response envelopes,
  streaming boundary.
- Application Service Layer: use cases, transaction boundaries, command mapping,
  calls into LangGraph or future Java services.
- LangGraph Orchestration Layer: state, nodes, routing, fallback, evidence
  aggregation, specialist handoff.
- Retrieval/RAG/GraphRAG Layer: query planning, retrievers, fusion, rerank,
  evidence checks, GraphRAG project/index/query method behavior.
- LLM/Tool Adapter Layer: provider isolation, prompt rendering, embeddings,
  rerank calls, MCP and local tool adapters.
- Persistence Layer: SQLModel/PostgreSQL, vector stores, graph store, object
  storage, cache.
- Observability Layer: trace, cost, evaluation fixtures, regression reports.

## Non-Responsibilities

Routes should not contain complex retrieval decisions. LangGraph should not own
provider-specific client details. Frontend code should not know internal graph
route names.

## Migration Notes

Current files may stay where they are during v0.1 design. The migration goal is
clearer contracts first, physical extraction later.
