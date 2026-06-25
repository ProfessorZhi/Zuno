# Context Memory Agent Runtime V1

## Goal

Move Zuno toward the ideal single-Agent architecture documented in:

- `.agent/architecture/near-term/18-context-memory-ideal-architecture.md`

The program introduces a unified `GeneralAgent`, a Context Orchestrator, a
Memory & State Engine, dynamic capability selection, and a clean
`GraphRAGProjectSnapshot` boundary.

## Program Boundary

This is an Agent-side implementation plan, not current implementation truth.
Formal human-facing status still belongs in `docs/architecture/roadmap.md`.

Do not start destructive runtime replacement from this program until the current
`official-graphrag-cleanup-v1` Phase 11 Runtime Legacy Deletion dependency is
resolved or explicitly re-scoped.

## Source Design

Local design source:

- `C:\Users\Administrator\Downloads\zuno_ideal_architecture_with_context_memory.html`

Agent documentation source:

- `.agent/architecture/near-term/18-context-memory-ideal-architecture.md`

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
