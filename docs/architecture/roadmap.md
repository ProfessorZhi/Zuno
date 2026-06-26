# Architecture Roadmap

## Current

The completed Phase 0-6 architecture closure is historical truth.

The active program is target architecture migration. It continues the unfinished
official GraphRAG cleanup 11C/12 gates and then proceeds through repository
layout, Context/Memory, Capability System, and single `GeneralAgent`
integration phases.

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
- Phase 11C: blocked. The current FastAPI router no longer mounts
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
  A dry-run-first Neo4j graph backfill helper exists, but the graph property
  migration has not been applied. Stackless local eval and the dedicated
  Contract Review eval can build from GraphRAG Project assets without loading
  `DomainPackLoader`. Root Phase 11C tests now guard retired runtime imports
  for `DomainQAGraph`, `MultiAgentSupervisorGraph`, `AgentRuntime`, legacy
  graph states, and `zuno.services.domain_pack`. Root `domain-packs/` assets are archived under
  `docs/architecture/history/domain-packs/root-contract-review/`, Docker no
  longer copies or mounts `/app/domain-packs`, and the former `tests/compat/`
  holding area is retired. Active migration compatibility dependencies remain
  in root `tests/`. The direct `DomainQAGraph` source, its legacy
  graph state module, and `src/backend/zuno/services/domain_pack/` runtime
  service package have also been retired from current backend source. Domain
  Pack backend endpoint/API-service wrappers and frontend API/page files are
  retired from current source.
- Phase 12: partial / not closed. Focused tests exist, but final full `pytest`
  and formal Eval baseline comparison are not complete.

## Next Actions

1. finish 11C active dependency removal through compatibility dependency
   reduction and formal Phase 02 closure proof
2. continue Phase 03 GraphRAG Project mainline hardening from safe prework
3. continue Phase 04 repository layout cleanup from safe prework
4. full pytest
5. eval baseline comparison
6. program closure

Contract Review asset migration has completed its asset-only slice: the Target
example copy lives at `examples/graphrag-projects/contract_review/`, and the
dedicated Contract Review eval now reads its GraphRAG Project compatibility
payload and eval fixture from that copy. Root Domain Pack assets are archived
and Docker Domain Pack mounts are retired, but this does not close 11C because
compat surfaces remain.

## Next Candidate

Context Memory Agent Runtime V1 is the next candidate / design-ready program.
It is not active Current implementation. Phase 00 must wait for 11C/12 closure
or explicitly re-verify dependencies before implementation starts.

## Blocked Legacy

These surfaces are confirmed legacy directionally, but still current or blocked
by active dependencies:

- remaining `domain_pack_id` and Domain Pack-era migration compatibility tests
  under root `tests/`

Retired evidence kept for verification, not active source:

- retired root `domain-packs/` archive at
  `docs/architecture/history/domain-packs/root-contract-review/`
- retired Docker `/app/domain-packs` copy and mounts
- root Phase 11C retired-import guards for `src/backend/zuno/services/domain_pack/`,
  `DomainQAGraph`, `MultiAgentSupervisorGraph`, `AgentRuntime`, and legacy
  graph states

## Non-Goals

The active roadmap does not implement Java services, split microservices,
event workers, database migrations, dependency upgrades, or default multi-agent
mode.

## Agent Execution Sources

Detailed implementation planning lives in:

- `.agent/programs/current.md`
- `.agent/programs/zuno-target-architecture-migration-v1/`
- `.agent/programs/official-graphrag-cleanup-v1/`
- `.agent/architecture/near-term/17-implementation-phase-map.md`
