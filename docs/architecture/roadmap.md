# Architecture Roadmap

## Current

The completed Phase 0-6 architecture closure is historical truth.

There is no active executable Agent program after the target architecture
migration closure. The completed program is archived under
`docs/architecture/history/programs/zuno-target-architecture-migration-v1/`.

Phase 01 through Phase 10 are complete. Those phases cover contract, loader,
prompt registry, index versioning, query router, Enhanced Mode, and frontend API
migration stages.

## Phase Status

- Phase 11A: complete. Commit `24abdd9` introduced the project query runtime:
  `KnowledgeQueryService`, `GraphRAGQueryService`,
  `GraphRAGProjectSnapshot`, and `KnowledgeQueryResult`.
- Phase 11B: complete. Commit `b160c4b` unified knowledge queries under the
  single `GeneralAgent` path through `search_knowledge_base` and
  `KnowledgeQueryService`.
- Phase 11C: active runtime cleanup complete. The current FastAPI router no longer mounts
  `/domain-packs`, and the active Vue knowledge route/settings entrypoints no
  longer open Domain Pack pages. Workspace knowledge prefetch/tools no longer
  use `AgentRuntime` or `_run_domain_pack_query`; they use
  `KnowledgeQueryService`. The standalone `AgentRuntime` facade has been
  removed from current backend source and exports. The direct
  `MultiAgentSupervisorGraph` source has also been removed. `DomainQAGraph`
  and `MultiAgentSupervisorGraph` are no longer exported from current core
  package public surfaces. The `/knowledge/search` API service path now routes
  through `KnowledgeQueryService` instead of the legacy `RagHandler` search
  path. `KnowledgeService.get_runtime_settings` preserves
  `domain_pack_id` as a migration field but no longer loads
  `DomainPackLoader` from it. Runtime payload output is project-named as
  `project_payload`, while legacy `domain_pack` payload input remains only as
  a migration fallback. `GraphRetriever` no longer loads retrieval policy from
  a bare `domain_pack_id`; explicit `query_policy` now carries the
  GraphRAG Project policy data. Agent and Knowledge public DTOs now prefer
  `graphrag_project_id`, and frontend knowledge config patches no longer send
  `domain_pack_id`; old `domain_pack_id` input is migration compatibility only.
  Graph writer/client/retriever paths now write and query
  `graphrag_project_id` as the primary graph scope while dual-reading legacy
  graph properties until the dry-run-first Neo4j backfill is applied.
  Stackless local eval and the dedicated Contract Review eval can build from
  GraphRAG Project assets without loading `DomainPackLoader`. Root Phase 11C tests now guard retired runtime imports
  for `DomainQAGraph`, `MultiAgentSupervisorGraph`, `AgentRuntime`, legacy
  graph states, and `zuno.services.domain_pack`. Root `domain-packs/` assets are archived under
  `docs/architecture/history/domain-packs/root-contract-review/`, Docker no
  longer copies or mounts `/app/domain-packs`, and the former `tests/compat/`
  holding area is retired. Bounded migration compatibility evidence remains
  in root `tests/` for storage/eval/DB aliases. The direct `DomainQAGraph` source, its legacy
  graph state module, and `src/backend/zuno/services/domain_pack/` runtime
  service package have also been retired from current backend source. Domain
  Pack backend endpoint/API-service wrappers and frontend API/page files are
  retired from current source.
- Phase 12: closed through the target migration closure evidence. full pytest,
  formal Contract Review eval, stackless eval baseline comparison, trace
  metadata, legacy grep classification, and docs/evidence sync are complete.

## Next Actions

1. Open a new executable program only if the next requirement needs one.

Contract Review asset migration has completed its asset-only slice: the Target
example copy lives at `examples/graphrag-projects/contract_review/`, and the
dedicated Contract Review eval now reads its GraphRAG Project compatibility
payload and eval fixture from that copy. Root Domain Pack assets are archived
and Docker Domain Pack mounts are retired.

## Next Candidate

Context Memory Agent Runtime V1 is the next candidate / design-ready program.
It is not active Current implementation. Phase 00 must wait for 11C/12 closure
or explicitly re-verify dependencies before implementation starts.

## Blocked Legacy

These surfaces are confirmed legacy directionally, but still current or blocked
by active dependencies:

- remaining `domain_pack_id` references are bounded migration aliases,
  existing Agent database-column compatibility, eval CLI compatibility, and
  retirement/history tests under root `tests/`

Retired evidence kept for verification, not active source:

- retired root `domain-packs/` archive at
  `docs/architecture/history/domain-packs/root-contract-review/`
- retired Docker `/app/domain-packs` copy and mounts
- root Phase 11C retired-import guards for `src/backend/zuno/services/domain_pack/`,
  `DomainQAGraph`, `MultiAgentSupervisorGraph`, `AgentRuntime`, and legacy
  graph states

Current foundation closures:

- Phase 05 Context Contract foundation is current code under
  `src/backend/zuno/services/application/context/`.
- Phase 06 Memory Layer foundation is current code under
  `src/backend/zuno/services/memory/layers.py`.
- Phase 07 Capability System foundation is current code under
  `src/backend/zuno/services/application/capabilities/`, with the existing
  capability search service exposing unified metadata for tools, skills, MCP
  servers, and MCP tools.
- Phase 08 GeneralAgent runtime integration is current code in
  `src/backend/zuno/core/agents/general_agent.py`: it prepares context,
  passes trace metadata into the single React loop, and commits scoped memory
  raw events and task summaries after a turn when memory is enabled.

## Non-Goals

The active roadmap does not implement Java services, split microservices,
event workers, database migrations, dependency upgrades, or default multi-agent
mode.

## Agent Execution Sources

Archived implementation planning lives in:

- `.agent/programs/current.md`
- `docs/architecture/history/programs/zuno-target-architecture-migration-v1/`
- `docs/architecture/history/programs/official-graphrag-cleanup-v1/`
- `.agent/architecture/near-term/17-implementation-phase-map.md`
