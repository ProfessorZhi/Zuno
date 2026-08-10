# Repository Ownership Matrix

状态：`current`

本文件只记录当前物理 owner，不记录已经删除的迁移路径、阶段计划或兼容表。

| Surface | Application owner | Domain / runtime owner | Evidence boundary |
| --- | --- | --- | --- |
| Product command / projection | `api/services/product/command_service.py` | Product domain repositories and Agent Core dispatch | command receipt is not run success |
| Product file / ingestion | `api/services/product/ingestion_service.py` | `knowledge/ingestion` and durable storage | hash, tenant and durable handoff are required |
| Product run lifecycle | `api/services/product/run_service.py` | `agent/runtime` canonical runtime | security, approval, budget, idempotency and recovery remain explicit |
| Product artifacts / feedback | `api/services/product/artifact_service.py` | durable ingestion store | authorization and citation access are separate |
| Product runtime observability | `api/services/product/observability_service.py` | projection and trace owners | measurement is not production readiness |
| Agent planning / execution | `agent/` | Agent Core single controller | no product multi-agent default |
| Knowledge / retrieval | `knowledge/` | Knowledge and GraphRAG owners | evidence and citation must be traceable |
| Capability / tools | `capability/` | Tool control plane and security | every effect is gated and audited |
| Persistence / infrastructure | `platform/database/`, `platform/storage/` | infrastructure owners | authoritative facts precede projections |

## Rules

- API routes depend on application owners, not provider or database internals.
- A shared runtime engine may implement mechanics, but it is not an API facade or
  a second production execution path.
- Unknown external effects enter reconciliation; they are never silently retried
  as success.
- Current/Target/Not measured must remain distinct in code, tests and docs.
