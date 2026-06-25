# Transition Strategy

## Goal

Keep the current execution path clear without creating another layer of false
current truth.

## Current Strategy

The completed recovery strategy was:

```text
Phase 0 first:
recover stable runtime

then:
resume deeper architecture work from that stable baseline
```

The earlier root-level `services/api` migration has been retired, and the placeholder `services/` root should not remain in the live repo.
Any future service-root move must reopen as a new phase with fresh verification and a newly created root.

The current active strategy is now the Zuno Target Architecture Migration V1
implementation program:

- `.agent/programs/zuno-target-architecture-migration-v1/implementation-roadmap.md`
- `.agent/programs/zuno-target-architecture-migration-v1/implementation-phases/`
- `.agent/programs/official-graphrag-cleanup-v1/implementation-roadmap.md`
- `.agent/programs/official-graphrag-cleanup-v1/implementation-phases/`
- `.agent/architecture/near-term/17-implementation-phase-map.md`

It first closes the unfinished Domain Pack / legacy runtime dependency gates,
then moves the front path toward GraphRAG Project, target repository layout,
Context/Memory, Capability System, and the single `GeneralAgent` runtime.

## Rules

### 1. Stability Before Boundary Motion

Do not keep moving backend package boundaries while the runtime import chain is not stable.

First recover:

- startup closure
- import closure
- focused runtime tests

Only after that should deeper architecture work continue.

### 2. Docs Truth First

The front path in docs must describe:

- the real current repo state
- the latest active execution plan
- the real target architecture expectation

Not the last attempted migration direction.

### 3. One Active Execution Path

Only one execution path should steer the repo at a time.

Right now that path is:

- `.agent/programs/zuno-target-architecture-migration-v1/implementation-roadmap.md`
- `.agent/programs/zuno-target-architecture-migration-v1/implementation-phases/`
- `.agent/programs/official-graphrag-cleanup-v1/implementation-roadmap.md`
- `.agent/programs/official-graphrag-cleanup-v1/implementation-phases/`
- `.agent/architecture/near-term/17-implementation-phase-map.md`

Older migration-first materials may remain available, but they must not steer current work.

### 4. Historical Docs Stay Reachable But Stop Steering Execution

Older refactor plans, phase checklists, readiness notes, and signoff surfaces may still be useful as historical evidence.

They should remain reachable through `history/`, but no longer sit on the default reading path.

### 5. Recover First, Then Deepen

The completed historical order was:

```text
recover runtime
  -> deepen LangGraph
  -> deepen GraphRAG
  -> formalize Domain Pack
  -> strengthen local eval
  -> sync README and architecture docs
```

The current implementation order starts by proving current state, then removing
Domain Pack active dependencies, migrating Contract Review assets, hardening
GraphRAG Project as the mainline, cleaning repository layout, implementing
Context/Memory and Capability boundaries, integrating them into the single
`GeneralAgent`, and closing with full tests, eval, trace, docs, and grep gates.
