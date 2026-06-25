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

- Target Migration Phase 00 is ready.
- Phase 01 continues official cleanup 11C active dependency removal.
- Official cleanup Phase 11A and 11B are complete.
- Official cleanup Phase 11C remains blocked wherever Domain Pack runtime,
  `DomainQAGraph`, `MultiAgentSupervisorGraph`, launchers, evals,
  frontend/API, Docker, or `tests/compat/` still have active dependencies.
  Workspace knowledge prefetch/tools have been cut over to
  `KnowledgeQueryService`, and the standalone `AgentRuntime` facade has been
  removed from current backend source and exports. `DomainQAGraph` and
  `MultiAgentSupervisorGraph` are no longer current core package public
  exports.
- Official cleanup Phase 12 is partial / not closed.

## Detailed Sources

- `.agent/programs/current.md`
- `.agent/programs/zuno-target-architecture-migration-v1/implementation-roadmap.md`
- `.agent/programs/zuno-target-architecture-migration-v1/implementation-phases/`
- `.agent/programs/official-graphrag-cleanup-v1/implementation-roadmap.md`
- `.agent/programs/official-graphrag-cleanup-v1/implementation-phases/`
- `.agent/architecture/near-term/17-implementation-phase-map.md`

Do not use the implementation phases to pull Java, microservices,
event-driven workers, or default multi-agent mode into near-term acceptance.
