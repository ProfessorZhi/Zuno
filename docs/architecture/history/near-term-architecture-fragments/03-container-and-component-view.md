# Container And Component View

## Purpose

Show the near-term runtime containers and in-process components.

## Current Evidence

- `infra/docker/docker-compose.yml` defines local infrastructure including
  PostgreSQL and backend/frontend services.
- `src/backend/zuno/config.example.yaml` includes PostgreSQL, Neo4j, storage,
  model, and tool config.
- API routes live in `src/backend/zuno/api/v1/`.
- Route-adjacent services live in `src/backend/zuno/api/services/`.
- LangGraph graphs live in `src/backend/zuno/core/graphs/`.
- Retrieval, RAG, and GraphRAG modules live under `src/backend/zuno/services/`.

## Near-Term Containers

```text
Web Frontend
Desktop Shell
Python FastAPI AI Runtime
PostgreSQL
Vector Store
Neo4j Graph Store
Object/File Storage
Optional Cache
Local Evaluation Tooling
```

## Near-Term Components

```text
FastAPI API Layer
Application Services
LangGraph Graphs
Retrieval Planner / Orchestrator
RAG Retrievers
GraphRAG Project / Index / Query Services
LLM / Embedding / Rerank Adapters
Tool / MCP Adapters
Persistence DAOs and Storage Clients
Trace and Evaluation Helpers
```

## Non-Responsibilities

Near-term components should not pretend to be separately deployed services.
They may have service-ready interfaces, but they remain in-process until a later
program proves a split is worth the operational cost.

## Migration Notes

Name interfaces for boundaries that matter now. Avoid network-service naming
when the near-term reality is still a modular monolith.
