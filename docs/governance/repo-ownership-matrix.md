# Repository Ownership Matrix（兼容输入）

status: current-compatibility-reference
owner: Repository / Architecture Coordinator
human_entrypoint: AGENTS.md and docs/architecture/architecture.md

> 本文件保留给 `src/backend/zuno/**` 中尚未迁移的边界说明和工具读取路径。它不是新的项目故事、研究结论、架构正文或 ADR Owner；人类阅读入口是根目录 `AGENTS.md`、总体架构和 `docs/maintenance/operations/`。物理 Service Split 仍由证据门控。

## Documentation ownership

| Surface | Owner | 不拥有 |
| --- | --- | --- |
| `docs/project/` | 真实项目来源、发展、团队/个人参与 | Target 实现证明 |
| `docs/research/` | 研究谱系、外部平台 baseline、Research→Engineering 推导 | Current / Target Architecture Truth |
| `docs/architecture/` | 唯一总体 Target Architecture | Current Evidence |
| `docs/modules/` | 九个逻辑责任域设计 | 项目历史 |
| `docs/decisions/` | 长期 accepted decisions | Red/Blue 原始讨论 |
| `docs/evidence/` | Current Code/Test/Trace/Eval/Runtime Evidence | Target 设计 |
| `docs/governance/` | Provenance、Owner、Contract、文档/验收规则 | Human-first 项目故事 |
| `docs/maintenance/` | Runbook、Agent workflow、历史审查 | Current/Target truth |

## Runtime / code ownership

| Surface | Current code owner | Target logical owner / optional physical boundary | Evidence boundary |
| --- | --- | --- | --- |
| External HTTP / SSE | `src/backend/zuno/main.py`, `zuno/api/` | Product / Application Surface Owner | correlation receipt is not business success |
| Matter / Domain state | `zuno/api/`, `zuno/platform/` | Domain Owner；physical split requires Evidence Gate | accepted state requires provenance, permission and version |
| Agent planning / execution | `zuno/agent/` | Agent Runtime Owner；Worker or Service only when justified | runtime checkpoint is not Domain Fact |
| Ingestion / retrieval | `zuno/knowledge/`, `zuno/platform/services/rag/` | Knowledge Owner；Worker or Service only when justified | candidates and citations require lineage |
| Capability / tool execution | `zuno/capability/`, `zuno/platform/services/` | Tool / Security Owner；isolated boundary requires Evidence Gate | every external effect has receipt or UNKNOWN reconciliation |
| Model / Legal Intelligence | provider adapters across `zuno/agent/`, `knowledge/`, `capability/` | provider layer; service split is evidence-gated | provider output is Proposal/Observation, never Owner Commit |
| Eval / observability | `zuno/platform/`, `tools/evals/` | batch worker and audit/trace sinks | measurement is not Production Readiness |
| Persistence / infrastructure | `zuno/platform/database/`, `platform/storage/`, `infra/` | Data and Deployment Owners | authoritative facts precede projections |

## Rules

- Research Artifact、论文和平台 feature 都不能绕过 Project / Architecture / Evidence Owner。
- API routes depend on application owners, not provider or database internals.
- Logical capability, service, process, container and team are separate concepts；one Python image may host multiple logical responsibilities without creating a pre-committed Network Service topology.
- Physical Service Split must record Why Service? Why not Library? Why not Worker? Independent Scaling, Failure, Security, Availability, Lifecycle, Cross-host Contract or Data / Operational Ownership evidence is required.
- A shared runtime engine may implement mechanics, but it is not an API facade or a second Domain execution path.
- Unknown external effects enter reconciliation；they are never silently retried as success.
- Current / Target / Research / History / Not measured must remain distinct in code, tests and docs.
