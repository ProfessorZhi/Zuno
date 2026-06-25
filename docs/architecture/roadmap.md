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
  package public surfaces. `KnowledgeService.get_runtime_settings` preserves
  `domain_pack_id` as a migration field but no longer loads
  `DomainPackLoader` from it. `GraphRetriever` no longer loads retrieval
  policy from a bare `domain_pack_id`; explicit `query_policy` now carries the
  GraphRAG Project policy data. Stackless local eval and the dedicated
  Contract Review eval can build from GraphRAG Project assets without loading
  `DomainPackLoader`. Active dependencies still remain in `domain-packs/`,
  Domain Pack runtime services, Docker surfaces, and `tests/compat/`. The
  direct `DomainQAGraph` source and its legacy graph state module have also
  been retired from current backend source.
  Domain Pack backend endpoint/API-service wrappers and frontend API/page
  files are retired from current source.
- Phase 12: partial / not closed. Focused tests exist, but final full `pytest`
  and formal Eval baseline comparison are not complete.

## Next Actions

1. 11C active dependency removal
2. Contract Review asset migration
3. full pytest
4. eval baseline comparison
5. program closure

Contract Review asset migration has started: the Target example copy lives at
`examples/graphrag-projects/contract_review/`, and the dedicated Contract
Review eval now reads its GraphRAG Project compatibility payload and eval
fixture from that copy. This does not close Phase 02 or 11C because Domain
Pack services/assets/Docker/compat surfaces remain.

## Next Candidate

Context Memory Agent Runtime V1 is the next candidate / design-ready program.
It is not active Current implementation. Phase 00 must wait for 11C/12 closure
or explicitly re-verify dependencies before implementation starts.

## Blocked Legacy

These surfaces are confirmed legacy directionally, but still current or blocked
by active dependencies:

- `domain-packs/`
- `src/backend/zuno/services/domain_pack/`
- retired `DomainQAGraph` compatibility evidence
- retained `MultiAgentSupervisorGraph` compat retirement evidence
- `tests/compat/`

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
