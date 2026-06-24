# Target Layered Architecture

## Purpose

Define the target dependency direction and layer responsibilities.

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

## Current Evidence

- Frontend API clients live in `apps/web/src/apis/`.
- Backend routes and services live in `src/backend/zuno/api/`.
- LangGraph orchestration exists in `src/backend/zuno/core/graphs/`.
- Retrieval logic exists in `src/backend/zuno/services/retrieval/`.
- RAG and GraphRAG implementation exists under `src/backend/zuno/services/rag/`
  and `src/backend/zuno/services/graphrag/`.
- Persistence uses `src/backend/zuno/database/` plus vector, graph, and storage
  service clients.

## Target Dependency Rules

- Frontend expresses product mode and display needs only.
- API routes parse requests and map responses; they do not plan retrieval.
- Services express use cases and transactions.
- LangGraph orchestrates states, nodes, fallback, and specialist handoff.
- Retrieval/GraphRAG modules own recall, query method routing, fusion, rerank,
  and evidence building.
- Provider adapters isolate LLM, embedding, rerank, MCP, and tools.
- Persistence modules own database and storage access.
- Observability records traces across all layers.

## Migration Notes

Retire old names from front-path contracts in this order: `agentchat`,
`legacy`, `compat`, `Domain Pack`, `domain_pack_id`, `rag_graph_deep`,
`local_graphrag`, `community_global`, and `drift_like`. Keep temporary mappings
only inside migration code until replacement contracts are accepted.
