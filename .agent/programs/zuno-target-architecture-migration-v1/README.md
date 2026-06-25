# Zuno Target Architecture Migration V1

## Purpose

This is the active end-to-end Agent program for moving Zuno from the current
runtime state to the near-term target architecture and repository layout.

It absorbs the old Context Memory candidate program and continues the unfinished
official GraphRAG cleanup work without pretending Phase 11C or Phase 12 are
complete.

## Current Truth

- Phase 11A is complete: GraphRAG Project query runtime exists.
- Phase 11B is complete: knowledge queries use the single `GeneralAgent` path.
- Phase 11C is in progress and still blocked overall. The current FastAPI
  router no longer mounts `/domain-packs`, and active Vue knowledge
  routes/pages no longer open Domain Pack entrypoints. Workspace knowledge
  prefetch/tools now use `KnowledgeQueryService`, not `AgentRuntime` or
  `_run_domain_pack_query`. The standalone `AgentRuntime` facade has been
  removed from current backend source and exports. The direct
  `DomainQAGraph` source, legacy graph state module, and
  `MultiAgentSupervisorGraph` source have also retired from current backend.
  `DomainQAGraph` and `MultiAgentSupervisorGraph` are no longer current core
  package public exports. `KnowledgeService.get_runtime_settings` preserves
  `domain_pack_id` without auto-loading `DomainPackLoader`. `GraphRetriever`
  uses explicit `query_policy` instead of loading Domain Pack policy from
  `domain_pack_id`. `GraphRetrieverAdapter` maps GraphRAG Project scope to the
  current legacy graph storage filter. Stackless local eval and the dedicated
  Contract Review eval can build from GraphRAG Project assets and call graph
  extractors with `project_payload=project_payload`. The
  `src/backend/zuno/services/domain_pack/` runtime service package is also
  retired from current backend source. Root Domain Pack assets are archived
  under `docs/architecture/history/domain-packs/root-contract-review/`, Docker
  no longer copies or mounts `/app/domain-packs`, and the former
  `tests/compat/` holding area is retired. Remaining migration compatibility
  coverage lives in root `tests/`. Domain Pack backend endpoint/API-service
  wrappers and frontend API/page files are retired from current source.
- Phase 12 is partial / not closed.
- Context Orchestrator and new Memory layering are Target, not Current.

## Target

The target is a Python/FastAPI modular monolith with:

- single `GeneralAgent`
- GraphRAG Project mainline
- Context & Memory Engine
- Capability System
- evidence, citation, trace, and eval closure
- repository layout governed by `.agent/architecture/near-term/`

## Execution Sources

- [Implementation Roadmap](implementation-roadmap.md)
- [Implementation Phases](implementation-phases/README.md)
- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
- `.agent/architecture/near-term/19-repository-layout-and-module-boundaries.md`

## Relationship To Other Programs

- `official-graphrag-cleanup-v1` remains referenced as the source program for
  completed GraphRAG cleanup phases and the still-blocked 11C/12 work.
- `context-memory-agent-runtime-v1` is archived under
  `docs/architecture/history/programs/context-memory-agent-runtime-v1/`; its
  useful design intent is folded into this program's Context/Memory phases.

## Non-Goals

This program does not authorize Java services, microservices, event workers,
database migrations, dependency upgrades, or product-level multi-agent mode
unless a later phase explicitly opens a separate future-direction program.
