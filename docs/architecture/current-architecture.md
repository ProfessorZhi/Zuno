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
```

and a paused future-facing migration surface:

```text
services/
  api/

domain-packs/
```

That migration surface is not the active runtime baseline.

## Current Backend Truth

The stable backend package expected by the rest of the repo is now:

```text
src/backend/zuno/
```

The current `services/api/src/zuno/` tree should be treated as a paused migration surface, not as the confirmed runtime mainline.

In other words:

1. `apps/web` and `apps/desktop` remain valid top-level app shells
2. the Python backend runtime truth is `src/backend/zuno`
3. the root-level `services/` move remains paused until a later architecture phase reopens it

## Legacy Boundary

The repo still contains:

```text
src/backend/zuno/legacy/agentchat/
```

That tree is now `compatibility-only`.

It may still exist to support:

- compat import surfaces named `agentchat`
- paused migration bridges under `services/api`
- explicit compatibility tests

It is not runtime truth.

Current mainline runtime work must not add new retrieval, GraphRAG, Docker, launcher, or default test dependencies on `src/backend/zuno/legacy/agentchat/`.

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
the repo is in a legacy boundary hardening checkpoint before Phase 3
```

## Current Documentation Rule

The front path under `docs/architecture/` should expose only:

1. the current repo reality
2. the latest recovery / execution plan
3. the target architecture expectation
4. the stable technical specs

Older migration-first execution materials should remain reachable only through `history/`.
