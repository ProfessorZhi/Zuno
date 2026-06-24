# Backend FastAPI And Service Layer

## Purpose

Define FastAPI and service-layer boundaries.

## Current Evidence

- `src/backend/zuno/main.py` creates `FastAPI`, registers `TraceIDMiddleware`,
  `WhitelistMiddleware`, and CORS, initializes config, database, MCP server
  metadata, and avatars during lifespan startup.
- `src/backend/zuno/api/router.py` creates an `/api/v1` router and includes
  config, completion, dialog, domain packs, message, agent, history, user, tool,
  LLM, knowledge, MCP, workspace, usage, upload, agent skill, and capability
  routers.
- `src/backend/zuno/api/services/` contains route-adjacent application services.

## Target API Layer

FastAPI should own:

- request parsing
- auth and permission boundary
- validation
- response envelopes
- streaming boundary
- trace id propagation
- background task submission
- error normalization

## Target Application Service Layer

Application services should own:

- use case orchestration
- transaction boundary
- DTO to command mapping
- calls to LangGraph or future Java services
- runtime setting resolution
- user and tenant context propagation

## Non-Responsibilities

Routes should not choose retrievers, graph paths, or prompt versions. Services
should not directly embed provider-specific LLM details.

## Java Boundary

Future Java services should expose business capability APIs. Python services
may call Java before, during, or after LangGraph execution, but Java remains the
source of strict business validation and audit consistency.
