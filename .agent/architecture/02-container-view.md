# Container View

## Purpose

Name target runtime containers and separate current from future containers.

## Current Evidence

- `infra/docker/docker-compose.yml` defines local infrastructure including
  PostgreSQL and backend/frontend containers.
- `infra/docker/README.md` describes Web, FastAPI backend, and PostgreSQL.
- `src/backend/zuno/config.example.yaml` contains PostgreSQL, Neo4j, storage,
  model, and tool configuration.
- `apps/desktop/main.cjs` and `apps/desktop/preload.cjs` form the desktop shell.

## Target Containers

```text
Web Frontend
Desktop Shell
Python AI Runtime / FastAPI
Java Business Services
LLM Gateway / Adapter
Retrieval Service
GraphRAG Service
Indexing Worker
Evaluation Worker
PostgreSQL
Vector Store
Graph Store
Object Storage
Cache
Observability Stack
```

## Current vs Target

| Container | Current Evidence | Target State |
| --- | --- | --- |
| Web Frontend | `apps/web` | Product UI and API client only |
| Desktop Shell | `apps/desktop` | Local desktop wrapper and bridge |
| Python AI Runtime | `src/backend/zuno` | AI, RAG, GraphRAG, Agent runtime |
| Java Business Services | none | Future extension, business truth |
| Retrieval Service | in-process Python modules | Module now, service-ready later |
| GraphRAG Service | in-process Python modules | Project/settings/prompt/index/query boundary |
| Indexing Worker | in-process service/task skeletons | Future async worker |
| Evaluation Worker | `tools/evals/zuno` | Regression and method comparison worker |
| PostgreSQL | SQLModel and Docker config | Application system of record |
| Vector Store | Milvus/Chroma adapters | Dense and multimodal index backend |
| Graph Store | Neo4j client | GraphRAG entity/relation/community store |
| Object Storage | storage config and clients | Original files and derived artifacts |
| Cache | config placeholder | LLM, retrieval, prompt tuning, job cache |

## Migration Notes

Keep the current modular monolith until API contracts and storage ownership are
clear. Do not split services only to mirror the target diagram.
