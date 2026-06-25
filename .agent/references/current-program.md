# Current Program

The active executable Agent program is:

- `.agent/programs/official-graphrag-cleanup-v1/`

Formal human-facing status is summarized in:

- `docs/architecture/roadmap.md`

## Why This Program Exists

The previous Phase 0-6 closure is complete and historical.

The current work standardizes `docs/`, `AGENTS.md`, `.agent/`, repository
hygiene, and history while aligning GraphRAG work with GraphRAG Project, Prompt
Tuning, Query Method, Enhanced Mode, and trace/evidence concepts.

## Current Implementation Status

- Phase 01 through Phase 10 are complete.
- Phase 11 Runtime Legacy Deletion is next.
- Phase 11 remains blocked wherever Domain Pack runtime, `DomainQAGraph`,
  launchers, evals, or `tests/compat/` still have active dependencies.

## Detailed Sources

- `.agent/programs/current.md`
- `.agent/programs/official-graphrag-cleanup-v1/implementation-roadmap.md`
- `.agent/programs/official-graphrag-cleanup-v1/implementation-phases/`
- `.agent/architecture/near-term/17-implementation-phase-map.md`

Do not use the implementation phases to pull Java, microservices,
event-driven workers, or default multi-agent mode into near-term acceptance.
