# Target Architecture

## Purpose

This file states the near-term target. It is desired direction, not current
implementation truth.

## Target

Zuno should remain:

```text
monorepo now, service-ready later
```

The near-term target is:

```text
apps/web + apps/desktop
  -> src/backend/zuno
  -> FastAPI service boundary
  -> LangGraph runtime
  -> Basic RAG: BM25 + dense vector + fusion + rerank
  -> GraphRAG Project settings
  -> query_method: auto/basic/local/global/drift
  -> Prompt Registry and prompt versions
  -> index/update/version boundaries
  -> Enhanced Mode pipeline
  -> evidence bundle, citation, and trace
  -> local eval proof
```

## Not Near-Term

These are future direction, not current acceptance targets:

- Java business services
- microservice extraction
- event-driven workers
- default multi-agent QA mode
- independent GraphRAG or indexing services

## Replacement Direction

```text
Domain Pack front path -> GraphRAG Project
domain_pack_id target name -> graphrag_project_id
rag_graph_deep -> Enhanced Mode plus query_method
local_graphrag -> local
community_global -> global
drift_like -> drift
```

## Detailed Design

Detailed design-stage material lives in:

- `.agent/architecture/near-term/`
- `.agent/architecture/future/`
- `.agent/architecture/decisions/`

Only implemented and verified conclusions should be promoted from `.agent/` to
formal `docs/`.
