# Target Architecture

## Purpose

This file states the high-level near-term target. It is desired direction, not
current implementation truth.

## Target

Zuno should remain:

```text
monorepo now, modular monolith, service-ready later
```

The stable target concepts are:

- Single `GeneralAgent`
- Context & Memory Engine
- Capability System
- GraphRAG Project
- Query methods: Basic, Local, Global, DRIFT
- Index / Update / Full Rebuild lifecycle
- Evidence / Citation / Trace / Eval
- FastAPI service boundary inside the current Python monorepo
- Vue web and Electron clients over typed API contracts

## Replacement Direction

```text
Domain Pack front path -> GraphRAG Project
domain_pack_id target name -> graphrag_project_id
rag_graph_deep -> Enhanced Mode plus query_method
local_graphrag -> local
community_global -> global
drift_like -> drift
```

## Not Near-Term

These are future direction, not current acceptance targets:

- Java business services
- microservice extraction
- event-driven workers
- product-level multi-agent mode
- Coding Agent mode
- independent GraphRAG or indexing services

## Detailed Design

Detailed design-stage material lives in:

- `.agent/architecture/near-term/`
- `.agent/architecture/future/`
- `.agent/architecture/decisions/`

The canonical Target / Proposed visual blueprint is:

- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`

Only implemented and verified conclusions should be promoted from `.agent/` to
formal `docs/`.
