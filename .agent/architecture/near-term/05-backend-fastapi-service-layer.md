# Backend FastAPI Service Layer

## Purpose

Define near-term FastAPI and service responsibilities.

## Current Evidence

- `src/backend/zuno/main.py` creates the FastAPI app through `create_app()`.
- `lifespan()` calls config initialization, database initialization, router
  registration, and startup tasks.
- `register_middleware()` adds trace id, whitelist, and CORS middleware.
- `src/backend/zuno/api/router.py` mounts `/api/v1` and includes current routes,
  including legacy-facing `domain_packs`.
- `src/backend/zuno/api/services/` contains application service modules.

## Target Design

```text
FastAPI Route
  -> parse request
  -> auth / permission boundary
  -> validate DTO
  -> call Application Service
  -> return response envelope or stream

Application Service
  -> resolve runtime context
  -> enforce use-case rules
  -> map DTO to graph command
  -> invoke LangGraph or retrieval service
  -> normalize domain errors
  -> return app-level result
```

## API Layer Responsibilities

- route registration
- request and response DTOs
- auth/JWT boundary
- permission guard calls
- trace id propagation
- response envelope shape
- streaming connection boundary
- background job enqueue or trigger

## API Layer Non-Responsibilities

- choosing query method
- choosing retrievers
- rendering prompts
- writing graph store data directly
- deciding full rebuild vs update

## Service Layer Responsibilities

- use case orchestration
- runtime settings lookup
- knowledge/project config normalization
- validation that depends on current data
- transaction boundary
- LangGraph invocation
- index/reindex action coordination
- error normalization for routes

## Service Layer Non-Responsibilities

- frontend layout logic
- provider-specific request bodies
- low-level SQL or Cypher in route methods
- direct dependency on future Java services

## Migration Notes

Start by making current routes thin. Then introduce GraphRAG Project commands
behind services. Avoid changing `src/backend/zuno/` behavior until each service
contract has tests.

## Acceptance Direction

Near-term implementation is ready when API tests can prove routes delegate to
services and service tests can prove use-case behavior without requiring the
frontend or real provider clients.
