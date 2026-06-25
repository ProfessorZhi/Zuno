# Near-Term Target Overview

## Purpose

Define the next-stage architecture target without letting long-term ideas take
over the current mainline.

## Current Evidence

- The current backend truth is `src/backend/zuno`.
- `src/backend/zuno/main.py` creates the FastAPI app, lifespan startup,
  middleware, and router registration.
- `src/backend/zuno/api/router.py` exposes the `/api/v1` route surface.
- `src/backend/zuno/core/graphs/domain_qa_graph.py` and the former
  `multi_agent_supervisor_graph.py` source have retired from current backend.
  The Domain Pack runtime service package has also retired; root Domain Pack
  assets, Docker references, and compat tests remain Blocked Legacy.
- `src/backend/zuno/services/retrieval/`, `services/rag/`, and
  `services/graphrag/` already contain the retrieval, RAG, and GraphRAG pieces.
- Frontend standard/enhanced product terms exist under `apps/web/src/utils/`
  and `apps/web/src/apis/`.

## Target Design

Zuno's near-term ideal architecture is:

```text
Frontend / Desktop
  -> FastAPI API Layer
  -> Application Service Layer
  -> LangGraph Orchestration Layer
  -> Retrieval / RAG / GraphRAG Layer
  -> LLM / LangChain / Tool Adapter Layer
  -> Persistence / Storage Layer
  -> Observability / Evaluation Layer
```

The goal is to make the current Python AI Runtime more explainable,
testable, and official-GraphRAG-aligned before reopening larger platform
questions.

## Near-Term Does

- clarify FastAPI route and service boundaries
- introduce GraphRAG Project as the target GraphRAG unit
- retire Domain Pack as the future mainline
- define Enhanced Mode as a query-method pipeline
- make Basic a strong BM25 + dense vector + fusion + rerank baseline
- normalize query methods to `auto/basic/local/global/drift`
- keep frontend product language simple while hiding old route names
- preserve trace, evidence, citation, index version, and fallback metadata

## Near-Term Does Not Do

- Java backend business layer implementation
- microservice extraction
- default multi-agent mode
- event bus architecture rollout
- independent GraphRAG service
- independent indexing service
- independent evaluation service

Those items live in `../future/`. They may influence adapter seams and trace
fields, but they are not near-term acceptance targets.

## Migration Notes

The next refactor should first turn existing behavior into explicit contracts.
Physical package moves or service extraction come later only if the contracts
are already stable.

## Acceptance Direction

Near-term success is proven by docs, route/service/graph contracts, focused
tests, and eval gates that show standard retrieval remains safe while Enhanced
Mode adds traceable GraphRAG capability.
