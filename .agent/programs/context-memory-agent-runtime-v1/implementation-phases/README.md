# Implementation Phases

These phases split Context Memory Agent Runtime V1 into executable units.

Read first:

1. `../implementation-plan.md`
2. `../../current.md`
3. `../../official-graphrag-cleanup-v1/implementation-roadmap.md`
4. `../../../architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
5. `../../../architecture/near-term/18-context-memory-ideal-architecture.md`
6. `../../../../docs/architecture/current-architecture.md`
7. `../../../../docs/architecture/target-architecture.md`

## Status

Candidate / Design-ready. Phase 00 must wait for 11C/12 closure or explicitly
re-verify dependencies before implementation starts.

## Phase List

1. [Phase 00: Dependency Gate And Design Alignment](phase-00-dependency-gate-and-design-alignment.md)
2. [Phase 01: Context Contract Foundation](phase-01-context-contract-foundation.md)
3. [Phase 02: Short-term State And Raw Event Log](phase-02-short-term-state-and-raw-event-log.md)
4. [Phase 03: Compaction And Task Memory](phase-03-compaction-and-task-memory.md)
5. [Phase 04: Long-term Memory Stores](phase-04-long-term-memory-stores.md)
6. [Phase 05: Dynamic Context And Capability Selection](phase-05-dynamic-context-and-capability-selection.md)
7. [Phase 06: GraphRAG Snapshot Query Boundary](phase-06-graphrag-snapshot-query-boundary.md)
8. [Phase 07: GeneralAgent Runtime Integration](phase-07-generalagent-runtime-integration.md)
9. [Phase 08: Context Memory Eval Closure](phase-08-context-memory-eval-closure.md)

## Rule

Do not skip phase evidence. If a later phase looks easy, first prove the
dependency phase is complete from the current worktree.
