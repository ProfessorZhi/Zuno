# Context Memory Agent Runtime V1

## Status

Candidate / Design-ready. This is not active Current implementation.

Phase 00 must wait for `official-graphrag-cleanup-v1` Phase 11C / Phase 12
closure, or explicitly re-verify active dependencies before implementation
starts.

## Goal

Move Zuno toward the ideal single-Agent architecture documented in:

- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
- `.agent/architecture/near-term/18-context-memory-ideal-architecture.md`

The program introduces a unified `GeneralAgent`, a Context Orchestrator, a
Memory & State Engine, dynamic capability selection, and clean separation among
Agent Context, `GraphRAGProjectSnapshot`, and Knowledge Evidence.

## Program Boundary

This is an Agent-side implementation plan, not current implementation truth.
Formal human-facing status still belongs in `docs/architecture/roadmap.md`.

Do not start destructive runtime replacement from this program until the current
`official-graphrag-cleanup-v1` Phase 11C / Phase 12 dependency is resolved or
explicitly re-scoped.

`GraphRAGProjectSnapshot` and `GraphRAGQueryService` have partially landed in
the cleanup program. That does not mean this program's Phase 06 is complete.
Future work must reuse those results instead of implementing a second snapshot
or query service.

## Execution Source

Use these files when executing the program:

- [Implementation Plan](implementation-plan.md)
- [Implementation Phases](implementation-phases/README.md)

## Phase Rule

Each phase must define:

- goal
- dependency
- scope
- files to change
- files not to change
- acceptance gates
- verification commands
- evidence to return
