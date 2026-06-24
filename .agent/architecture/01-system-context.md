# System Context

## Purpose

Describe Zuno as a software system and its external actors.

## Current Evidence

- `apps/web/` is the current Web frontend shell.
- `apps/desktop/` is the Electron desktop shell.
- `src/backend/zuno/main.py` creates the FastAPI application, registers
  middleware, loads config, initializes database state, and mounts routes.
- `src/backend/zuno/api/router.py` exposes a `/api/v1` API surface and still
  includes `domain_packs`.
- `src/backend/zuno/settings.py` loads database, redis, rabbitmq, neo4j,
  langsmith, storage, rag, tool, and multi-model settings.
- `src/backend/zuno/services/graphrag/client.py` uses Neo4j for entities,
  relations, and community report nodes.
- There is no Java backend service in the current repo.

## Target Design

Zuno should be understood as an AI workspace system:

```text
User
  -> Web Frontend or Desktop Shell
  -> Python FastAPI AI Runtime
  -> Application Services
  -> LangGraph Orchestration
  -> Retrieval, RAG, GraphRAG, Tools, LLM Adapters
  -> PostgreSQL, Vector Store, Graph Store, Object Storage, Cache
```

External systems:

- LLM providers for chat, extraction, answer generation, and analysis.
- Embedding providers for text and visual indexes.
- Rerank providers for result ordering.
- PostgreSQL for application truth.
- Vector store for dense and image vectors.
- Neo4j or graph store for GraphRAG entities, relations, communities, and reports.
- Object or file storage for originals, parsed artifacts, and exports.
- MCP tools and local CLI tools for execution capabilities.
- Future Java business systems for rule-heavy enterprise workflows.

## Responsibilities

Zuno owns AI runtime, knowledge retrieval, GraphRAG query behavior, tool
execution orchestration, local evaluation, and workspace user flows.

## Non-Responsibilities

Zuno should not let the frontend understand graph internals. Future Java
business services should own strict business truth, transactions, permissions,
and audit consistency.

## Future Extension

Java business services may become a separate system called by Python through
HTTP, gRPC, or events. Multi-agent flows may use Java services through tool or
service adapters, but AI output must not bypass business rules.
