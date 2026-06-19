# Current Architecture

## Purpose

This file describes the current repo reality.
It does not describe the desired future state.

If this file and the code disagree, update this file.

## Current Reality

The repo has recovered one stable backend runtime baseline.

The visible codebase contains:

```text
apps/
  web/
  desktop/

src/backend/zuno/
domain-packs/
```

There is no active root-level `services/` tree in current truth.

## Current Backend Truth

The stable backend package expected by the rest of the repo is now:

```text
src/backend/zuno/
```

In other words:

1. `apps/web` and `apps/desktop` remain valid top-level app shells
2. the Python backend runtime truth is `src/backend/zuno`
3. any future root-level `services/` move must be reopened explicitly as a new architecture phase

## Runtime Boundary

There is no active compatibility namespace in current truth.

The only backend runtime boundary is:

```text
src/backend/zuno/
```

Current mainline runtime work must not reintroduce retired alias packages, duplicate backend roots, or compatibility-only import trees.

## Current Execution Truth

The active execution priority is no longer:

```text
continue pushing the paused root-level service migration first
```

The active execution priority is now:

```text
stabilize the recovered runtime baseline
  -> then deepen GraphRAG mainline
  -> then strengthen Domain Pack and local eval
```

The current execution plan for that is:

- `docs/architecture/plans/stable-baseline-recovery-and-runtime-deepening-plan.md`

Any future attempt to move the backend into a root-level `services/` subtree must be treated as a new architecture phase that recreates that root from scratch, not as a continuation of the removed `services/api` path.

## Current Runtime Line

The backend runtime thesis is still the same:

```text
Domain Pack
  -> LangGraph runtime
  -> retrieval orchestration
  -> vector / BM25 / Local GraphRAG retrieval
  -> later Community GraphRAG global summary
  -> answer generation
  -> citation / evidence checks
  -> local evaluation surfaces
```

What changed is not the thesis.
What changed is the current stage:

```text
Phase 0 stable runtime recovery is closed
Phase 1 LangGraph runtime deepening is closed
Phase 2 GraphRAG mainline deepening is closed
Phase 2.5 legacy boundary hardening is closed
Phase 3 Domain Pack formalization is closed
Phase 4 Knowledge Config V2 + Local Eval strengthening is closed
Phase 5 docs and public explanation sync is closed
Phase 6 Agent GraphRAG pluginization boundary is closed
```

## Current Documentation Rule

The front path under `docs/architecture/` should expose only:

1. the current repo reality
2. the latest recovery / execution plan
3. the target architecture expectation
4. the stable technical specs

Older migration-first execution materials should remain reachable only through `history/`.
