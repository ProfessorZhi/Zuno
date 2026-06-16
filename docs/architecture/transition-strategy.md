# Transition Strategy

## Goal

Move from the current unstable mixed state to a stable runtime baseline without creating another layer of false current truth.

## Current Strategy

The current strategy is:

```text
Phase 0 first:
recover stable runtime

then:
resume deeper architecture work from that stable baseline
```

The earlier root-level `services/api` migration has been retired, and the placeholder `services/` root should not remain in the live repo.
Any future service-root move must reopen as a new phase with fresh verification and a newly created root.

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

- `docs/architecture/plans/stable-baseline-recovery-and-runtime-deepening-plan.md`

Older migration-first materials may remain available, but they must not steer current work.

### 4. Historical Docs Stay Reachable But Stop Steering Execution

Older refactor plans, phase checklists, readiness notes, and signoff surfaces may still be useful as historical evidence.

They should remain reachable through `history/`, but no longer sit on the default reading path.

### 5. Recover First, Then Deepen

The intended order is:

```text
recover runtime
  -> deepen LangGraph
  -> deepen GraphRAG
  -> formalize Domain Pack
  -> strengthen local eval
  -> sync README and architecture docs
```
