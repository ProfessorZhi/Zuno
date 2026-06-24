# Deployment And Microservices View

## Purpose

Show deployment targets without claiming current service extraction.

## Current Evidence

- `infra/docker/docker-compose.yml` and `.dev.yml` provide local containerized
  dependencies and app services.
- `tools/launchers/windows/README.md` describes Windows startup scripts.
- The repo currently keeps the Python backend as `src/backend/zuno`, not a
  separate microservice tree.

## Target Deployment View

```text
Developer Machine
  Web Frontend
  Desktop Shell
  Python FastAPI AI Runtime
  PostgreSQL
  Neo4j
  Vector Store
  Object Storage

Future Server Deployment
  API Gateway
  Python AI Runtime
  Java Business Services
  Retrieval / GraphRAG Services
  Workers
  Observability Stack
```

## Deployment Principles

- Monorepo now, service-ready later.
- Runtime boundaries should be expressed in APIs, DTOs, settings, and trace
  fields before network boundaries are introduced.
- Split only when a component has independent scaling, failure isolation, data
  ownership, or team ownership needs.

## Failure / Fallback

If graph store, community reports, rerank, or Java service is unavailable, the
runtime should emit traceable fallback reasons and degrade to a safer basic path
instead of returning silent partial behavior.
