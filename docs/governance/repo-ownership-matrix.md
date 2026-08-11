# Repository Ownership Matrix

状态：`current`（物理代码）；服务拆分为 `target`

本文件只记录当前物理 owner 和已接受的 Target 服务 Owner，不记录已经删除的迁移路径或未批准的阶段计划。

| Surface | Current code owner | Target logical / service owner | Evidence boundary |
| --- | --- | --- | --- |
| External HTTP / SSE | `src/backend/zuno/main.py`, `zuno/api/` | `edge-api` | correlation receipt is not business success |
| Matter / Domain state | `zuno/api/`, `zuno/platform/` | `platform-domain-service` + Domain Owner | accepted state requires provenance, permission and version |
| Agent planning / execution | `zuno/agent/` | `agent-runtime-service` | runtime checkpoint is not Domain Fact |
| Ingestion / retrieval | `zuno/knowledge/`, `zuno/platform/services/rag/` | `knowledge-service` + workers | candidates and citations require lineage |
| Capability / tool execution | `zuno/capability/`, `zuno/platform/services/` | `tool-sandbox-service` | every external effect has receipt or UNKNOWN reconciliation |
| Model / Legal Intelligence | provider adapters across `zuno/agent/`, `knowledge/`, `capability/` | provider layer; service split is evidence-gated | provider output is Proposal/Observation, never Owner Commit |
| Eval / observability | `zuno/platform/`, `tools/evals/` | batch worker and audit/trace sinks | measurement is not Production Readiness |
| Persistence / infrastructure | `zuno/platform/database/`, `platform/storage/`, `infra/` | Data and Deployment Owners | authoritative facts precede projections |

## Rules

- API routes depend on application owners, not provider or database internals.
- Logical capability, service, process, container and team are separate concepts;
  one Python image may host multiple Target service roles without merging their
  ownership or recovery contracts.
- A shared runtime engine may implement mechanics, but it is not an API facade or
  a second Domain execution path.
- Unknown external effects enter reconciliation; they are never silently retried
  as success.
- Current/Target/Not measured must remain distinct in code, tests and docs.
