# Repository Ownership Matrix（兼容输入）

status: current-compatibility-reference
owner: Repository / Architecture Coordinator
human_entrypoint: AGENTS.md and docs/architecture/architecture.md

> 本文件保留给 `src/backend/zuno/**` 中尚未迁移的边界说明和工具读取路径。它不是新的项目故事、研究结论、架构正文或 ADR Owner；人类阅读入口是根目录 `AGENTS.md`、总体架构和 `docs/governance/operations/`。物理 Service Split 仍由证据门控。

## Documentation ownership

| Surface | Owner | 不拥有 |
| --- | --- | --- |
| `docs/project/` | 真实项目来源、发展、团队/个人参与 | Target 实现证明 |
| `docs/architecture/` | 唯一总体 Target Architecture | Current Evidence |
| `docs/modules/` | 当前 Target 的逻辑责任域设计 | 项目历史、模块数量永久冻结 |
| `docs/red-blue/` | Review method、Transcript、Findings、Round archive | Project/Architecture/Current truth |
| `docs/research/` | 研究谱系、法院背景、平台 baseline、Research→Engineering 输入 | Current / Target Architecture Truth |
| `docs/decisions/` | 长期 accepted decisions | 完整 Architecture Spec、Red/Blue 原始讨论 |
| `docs/evidence/` | Current Code/Test/Trace/Eval/Runtime Evidence | Target 设计 |
| `docs/governance/` | Provenance、Owner、Contract、文档/术语/workflow/operations/验收规则 | Human-first 项目故事、Target 业务设计 |

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

- Research Artifact、论文、Red/Blue Finding 和平台 feature 都不能绕过 Project / Architecture / Evidence Owner。
- API routes depend on application owners, not provider or database internals.
- Logical capability, module, Python package, worker, process, container, service and team are separate concepts.
- Physical Service Split must answer Why Service? Why not Library? Why not Worker? and must have measured scaling, failure, security, availability, lifecycle, cross-host contract or operational ownership evidence.
- A shared runtime engine may implement mechanics, but it is not an API facade or a second Domain execution path.
- Unknown external effects enter reconciliation; they are never silently retried as success.
- Current / Target / Research / History / Unknown / Not measured remain distinct in code, tests and docs.