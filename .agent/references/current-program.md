# Current Program

The active executable Agent program is:

- `.agent/programs/zuno-target-architecture-migration-v1/`

Formal human-facing status is summarized in:

- `docs/architecture/roadmap.md`

## Why This Program Exists

The previous Phase 0-6 closure is complete and historical.

The current work moves from the proven 11A/11B runtime state toward the target
architecture and target repository layout. It continues official GraphRAG
cleanup 11C/12 work before Context/Memory and Capability implementation.

## Current Implementation Status

- Target Migration Phase 00 is complete.
- Phase 01 active runtime cleanup is complete.
- Official cleanup Phase 11A and 11B are complete.
- Official cleanup Phase 11C active runtime cleanup is closed. Bounded
  migration aliases remain where tests name storage/eval/DB compatibility
  roles. The former `tests/compat/` holding area is retired. Root `domain-packs/` assets are
  archived under `docs/architecture/history/domain-packs/root-contract-review/`,
  and Docker no longer copies or mounts `/app/domain-packs`.
  Workspace knowledge prefetch/tools have been cut over to
  `KnowledgeQueryService`, and the standalone `AgentRuntime` facade has been
  removed from current backend source and exports. The direct
  `DomainQAGraph` source, legacy graph state module,
  `MultiAgentSupervisorGraph` source, and
  `src/backend/zuno/services/domain_pack/` runtime service package have also
  retired from current backend.
  `DomainQAGraph` and `MultiAgentSupervisorGraph` are no longer current core
  package public exports.
- Phase 02 is complete. Contract Review target assets live under
  `examples/graphrag-projects/contract_review/`, with root Domain
  Pack assets archived under
  `docs/architecture/history/domain-packs/root-contract-review/`.
- Phase 03 is complete for the public GraphRAG Project mainline:
  `/knowledge/search` routes through `KnowledgeQueryService`, Contract Review
  project assets expose `to_project_payload()`, graph scope uses
  `graphrag_project_id`, and stackless eval entrypoints prefer
  `graphrag_project_id` / `--graphrag-project-id` while retaining legacy
  compatibility aliases only where explicitly tested.
- Phase 04 is complete: retired Domain Pack UI capture and
  responsive-check scripts are archived under
  `docs/architecture/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/`.
- Official cleanup Phase 12 is partial / not closed.

## Detailed Sources

- `.agent/programs/current.md`
- `.agent/programs/zuno-target-architecture-migration-v1/implementation-roadmap.md`
- `.agent/programs/zuno-target-architecture-migration-v1/implementation-phases/`
- `docs/architecture/history/programs/official-graphrag-cleanup-v1/implementation-roadmap.md`
- `docs/architecture/history/programs/official-graphrag-cleanup-v1/implementation-phases/`
  as archived cleanup evidence, not active executable program material
- `.agent/architecture/near-term/17-implementation-phase-map.md`

Do not use the implementation phases to pull Java, microservices,
event-driven workers, or default multi-agent mode into near-term acceptance.
