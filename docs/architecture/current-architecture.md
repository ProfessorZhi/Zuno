# Current Architecture

## Purpose

This file states current repository reality. It does not describe the desired
future state.

## Current

Zuno is a monorepo with these active runtime boundaries:

```text
apps/web
apps/desktop
src/backend/zuno
infra
tools
tests
```

`src/backend/zuno` is the only active Python backend runtime boundary. There is
no active root-level `services/` backend tree and no active `src/frontend`
workspace.

## Current Backend Shape

- FastAPI entrypoint: `src/backend/zuno/main.py`
- API layer: `src/backend/zuno/api/`
- Runtime/core layer: `src/backend/zuno/core/`
- Service layer: `src/backend/zuno/services/`
- Persistence and settings: `src/backend/zuno/database/`,
  `src/backend/zuno/settings.py`
- Eval and maintenance tooling: `tools/evals/zuno/`, `tools/scripts/`

## Current GraphRAG And Agent State

Current code and focused tests prove this mainline:

```text
Completion API
  -> CompletionService
  -> GeneralAgent single loop
  -> search_knowledge_base
  -> KnowledgeQueryService
  -> GraphRAGQueryService
  -> RetrievalPlanner / RetrievalOrchestrator
  -> Evidence / Citation / Trace
  -> GeneralAgent answer
```

Phase 11A is complete. The current code contains `KnowledgeQueryService`,
`GraphRAGQueryService`, `GraphRAGProjectSnapshot`, and `KnowledgeQueryResult`.
This is the current GraphRAG Project Query Runtime boundary.

Phase 11B is complete. `GeneralAgent.astream()` uses the single current session
path, `search_knowledge_base` calls `KnowledgeQueryService`, and
`DomainQAGraph` no longer owns the `GeneralAgent` conversation path.

Workspace knowledge prefetch and the Workspace `search_knowledge_base` tool
also use `KnowledgeQueryService` now. `WorkSpaceSimpleAgent` no longer imports
`AgentRuntime`, exposes `domain_qa_runtime`, or calls `_run_domain_pack_query`.
The `/knowledge/search` API service path also routes through
`KnowledgeQueryService` and returns evidence/citation/trace-oriented query
metadata while preserving compatibility fields such as `content` and
`final_mode`.
The standalone `src/backend/zuno/core/runtime/agent_runtime.py` facade and the
direct `src/backend/zuno/core/graphs/multi_agent_supervisor_graph.py` source
have also been removed from current backend source and exports. The direct
`src/backend/zuno/core/graphs/domain_qa_graph.py` source and its legacy
`states.py` graph state module have also been removed from current backend
source. The `src/backend/zuno/services/domain_pack/` runtime service package
has also been retired from current backend source.
`DomainQAGraph` and `MultiAgentSupervisorGraph` are no longer exported from
the `zuno.core` or `zuno.core.graphs` public package surfaces.

Agent and Knowledge public DTOs now prefer `graphrag_project_id`. Legacy
`domain_pack_id` is accepted only as migration input and mapped to existing
storage boundaries where required; it is not the target public field.

`KnowledgeService.get_runtime_settings` now preserves `domain_pack_id` without
auto-loading `DomainPackLoader` from that field. It emits GraphRAG Project
runtime payloads under `project_payload`; legacy `domain_pack` runtime payload
input is accepted only as a migration fallback. The current project identity
still comes from `graphrag_project_id` and compatibility `domain_pack_id`
where existing contracts require it.

`GraphRetriever` no longer loads Domain Pack retrieval policy from
`domain_pack_id`. Contract Review graph policy now resolves through explicit
`query_policy` data, including the GraphRAG Project `retrieval_policy.yaml`
copy under `examples/graphrag-projects/contract_review/`.
`GraphRetrieverAdapter`, `GraphRetriever`, `GraphWriter`, structured graph
extraction, pipeline graph indexing, and the Neo4j client now use
`graphrag_project_id` as the primary graph scope for new graph writes and
project-scoped graph retrieval. Neo4j queries still dual-read legacy
`domain_pack_id` properties with `COALESCE` so old graph data remains readable
until the backfill is applied. A dry-run-first migration helper exists under
`tools/migrations/` to backfill `graphrag_project_id` from legacy graph
properties. Explicit legacy `domain_pack_id` remains a bounded migration input,
not the target API or graph-write shape.

Stackless local eval and the dedicated Contract Review eval can build their
Contract Review graph/eval payloads from GraphRAG Project assets. The dedicated
Contract Review eval no longer loads `DomainPackLoader` or executes through
`DomainQAGraph`. Stackless local eval no longer has a generic Domain Pack
loader fallback; when an id is provided, it must resolve to GraphRAG Project
assets. Their graph extraction paths, the active pipeline graph extraction
path, and the extractor contract tests now call extractors with
`project_payload=project_payload`; the graph extractor `domain_pack=` payload
alias is retired from active extractor APIs.

GraphRAG Project Contract Review assets now expose `to_project_payload()` as
the project-named compatibility payload API. The legacy
`to_domain_pack_payload()` wrapper is retired from the active project loader.
Stackless compare/local embedding evals prefer `graphrag_project_id` /
`--graphrag-project-id` while retaining `domain_pack_id` only as a migration
alias where current contracts still require it.
Stackless and real-runtime local eval runtime registries now expose GraphRAG
Project payload state through `project_payload`, not `domain_pack`.

## Migration Compatibility

Phase 11C active runtime cleanup is closed for current source paths. Remaining
compatibility evidence exists because older stored data, eval fixtures, and
migration tests still mention Domain Pack-era names:

- remaining migration compatibility fields and tests that still mention Domain
  Pack-era names

Retired evidence is kept for verification, not active source:

- Contract Review eval has moved to a GraphRAG Project local eval flow without
  `DomainPackLoader` or `DomainQAGraph`
- Root `domain-packs/` assets are archived under
  `docs/architecture/history/domain-packs/root-contract-review/`. Docker no longer copies or mounts `/app/domain-packs`
- The former `tests/compat/` holding area is retired; remaining migration
  compatibility coverage now lives in root `tests/`
- Domain Pack backend endpoint/API-service wrappers are retired from current source; `/api/v1/domain-packs` is not mounted on the current FastAPI router
- Domain Pack frontend API/page files are retired from `apps/web/src/`; Domain
  Pack pages are not active knowledge routes or settings-shell pages
- root Phase 11C tests guard retired `DomainQAGraph`,
  `MultiAgentSupervisorGraph`, `AgentRuntime`, legacy graph states, and Domain
  Pack runtime service imports

These surfaces are not the future front-path architecture, but remaining compat
tests and migration fields still require explicit replacement or retirement
proof before final Phase 09 grep closure.

## Not Current

Typed Context Contract models are current code under
`src/backend/zuno/services/application/context/`.

Context Orchestrator and new Memory layering are Target, not Current.

The near-term Context & Memory orchestration design is documented under
`.agent/`; it is not implemented as the current runtime. Do not describe
short/medium/long memory, Context Orchestrator, Dynamic Capability Selector, or
the Post-turn Pipeline as current behavior until code and tests prove them.

Phase 12 is partial / not closed. The repository has focused tests for recent
changes, but final full `pytest` and formal Eval baseline comparison have not
been completed.

## Historical Completion Truth

Phase 0-6 is complete and historical. Do not rewrite those phase files as
incomplete to carry new work.

## Documentation Boundary

`docs/` is formal documentation. `.agent/` is the Agent workflow library.
Historical materials live under `docs/architecture/history/`.
