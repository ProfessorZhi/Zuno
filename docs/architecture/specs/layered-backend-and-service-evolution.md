# Layered Backend And Service Evolution

## Goal

This spec defines the backend layering Zuno should follow now, and how that layering keeps the repo ready for deeper evolution later.

The question is not:

- how to split microservices immediately
- how to make the tree look modern at any cost

The real question is:

```text
while Zuno is still a local-first monorepo,
how do we keep backend boundaries clear enough
that later runtime deepening or service extraction does not require a reset
```

## Core Direction

The correct near-term direction is still:

```text
monorepo now, service-ready later
```

In the current repo, that means:

```text
recover one stable backend root first
  -> keep internal layering clean
  -> only then reconsider larger boundary moves
```

## Current Structure Assumption

For current architecture and placement decisions, treat this as the recovery baseline:

```text
Zuno/
  src/
    backend/
      zuno/
        api/
        core/
        database/
        services/
  apps/
    web/
    desktop/
  docs/
  infra/
  tools/
  tests/
```

If migration-era code still exists elsewhere, that is transitional debt, not the architecture default.

## Recommended Backend Layers

The backend should keep at least four clear layers:

1. control layer
2. service layer
3. DAO layer
4. infrastructure layer

These layers are not ceremony.
They are how we keep the code explainable, changeable, and later splittable.

## Directory Semantics

Current recommended meaning:

- `src/backend/zuno/api/`
  - control-layer entrypoints
- `src/backend/zuno/core/`
  - runtime state, graph contracts, core orchestration primitives
- `src/backend/zuno/database/`
  - models, metadata, session, DAO
- `src/backend/zuno/services/`
  - business orchestration, retrieval, GraphRAG, Domain Pack, provider adapters

Repo-level meaning:

- `apps/web/`
  - web frontend
- `apps/desktop/`
  - desktop shell
- `docs/`
  - current truth, plans, specs, workflow, history
- `infra/`
  - Docker, deployment, environment orchestration
- `tools/`
  - scripts, evals, helper tooling
- `tests/`
  - repo-level verification and cross-surface checks

## Layer Responsibilities

### Control Layer

Typical location:

- `src/backend/zuno/api/*`

Responsibilities:

- handle HTTP request and response flow
- validate parameters
- map DTOs into service calls

Rules:

- keep controllers thin
- do not bury workflow logic here
- do not let the control layer own provider orchestration

### Service Layer

Typical location:

- `src/backend/zuno/core/*`
- `src/backend/zuno/services/*`

Responsibilities:

- business orchestration
- retrieval orchestration
- GraphRAG Project and knowledge-query runtime orchestration
- LangGraph runtime composition
- multi-agent coordination

Rules:

- service-layer code owns business meaning
- it may coordinate multiple DAOs and infrastructure adapters
- it is the first candidate boundary if the repo later extracts a service

### DAO Layer

Typical location:

- `src/backend/zuno/database/dao/*`

Responsibilities:

- persistence access
- database queries and transaction-facing operations
- mapping storage records into backend models

Rules:

- DAO code does not own workflow orchestration
- DAO code does not own HTTP, queue, or storage process logic
- DAO interfaces should stay stable enough for future extraction

### Infrastructure Layer

Typical location:

- `src/backend/zuno/services/redis.py`
- `src/backend/zuno/services/queue/*`
- `src/backend/zuno/services/storage/*`
- `src/backend/zuno/services/rag/vector_db/*`
- `src/backend/zuno/services/graphrag/*`

Responsibilities:

- Redis
- queue and message integration
- object storage
- vector stores
- graph stores
- trace and observability adapters

Rules:

- provider-specific logic stays here
- infrastructure code does not own business decisions
- upper layers should be able to swap providers without rewriting the main business line

## What Not To Do

Avoid:

- putting orchestration into controllers
- turning DAO code into a workflow manager
- letting infrastructure adapters own business policy
- using migration-era alternate roots as the default placement rule
- creating more bridges just to preserve a mixed-root state

## Evolution Space

This layering keeps space for:

1. stronger LangGraph and retrieval runtime workflows
2. deeper GraphRAG and Domain Pack contracts
3. possible queue-worker or service extraction later
4. possible non-Python backend integration later

The point is not to overbuild now.
The point is to avoid painting the repo into a corner.

## Summary

Zuno does not need premature service splitting.
It needs one stable backend root, clean internal layering, and explicit runtime boundaries.
