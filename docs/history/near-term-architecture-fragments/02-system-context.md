# System Context

## Purpose

Describe the near-term Zuno system boundary.

## Current Evidence

- `apps/web/` is the current Web frontend shell.
- `apps/desktop/` is the current Electron desktop shell.
- `src/backend/zuno/main.py` hosts FastAPI.
- `src/backend/zuno/settings.py` loads database, Neo4j, storage, model, tool,
  RAG, LangSmith, and other runtime settings.
- `tools/evals/zuno/` contains local evaluation tooling.

## Target Design

Near-term Zuno is one Python AI Runtime in a monorepo:

```text
User
  -> Web Frontend or Desktop Shell
  -> FastAPI API Runtime
  -> Application Services
  -> LangGraph AI Orchestration
  -> Retrieval / RAG / GraphRAG / Tool / LLM Adapter modules
  -> PostgreSQL, Vector Store, Neo4j, Object Storage
```

## Responsibilities

Zuno near-term owns:

- workspace UI and API contracts
- knowledge base lifecycle and query configuration
- LLM and tool adapter orchestration
- RAG and GraphRAG retrieval
- answer citation and trace metadata
- local evaluation and regression evidence

## Non-Responsibilities

The near-term system does not own Java enterprise business workflows,
microservice deployment boundaries, or default multi-agent task planning. Those
are future direction topics.

## Migration Notes

Do not make the frontend understand graph internals. The frontend should send
product-level settings and receive trace/evidence metadata from the backend.
