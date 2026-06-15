# Current Architecture

## Purpose

This file describes the current repo reality.
It does not describe the desired future state.

If this file and the code disagree, update this file.

## Current Reality

The repo is currently in a mixed and unstable transition state.

The visible codebase contains both:

```text
apps/
  web/
  desktop/

src/backend/zuno/
```

and an unfinished root-level migration attempt:

```text
services/
  api/

domain-packs/
```

That migration attempt is not currently the stable runtime baseline.

## Current Backend Truth

The stable backend package expected by the rest of the repo is still:

```text
src/backend/zuno/
```

The current `services/api/src/zuno/` tree should be treated as a paused migration surface, not as the confirmed runtime mainline.

In other words:

1. `apps/web` and `apps/desktop` remain valid top-level app shells
2. the Python backend still needs to recover to one stable `src/backend/zuno` runtime root
3. the root-level `services/` move is paused until the repo is stable again

## Current Execution Truth

The active execution priority is no longer:

```text
continue pushing the paused root-level service migration first
```

The active execution priority is now:

```text
recover one stable runnable backend baseline first
  -> then deepen LangGraph
  -> then deepen GraphRAG
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
What changed is the execution decision:

```text
stability first, repo-boundary migration later
```

## Current Documentation Rule

The front path under `docs/architecture/` should expose only:

1. the current repo reality
2. the latest recovery / execution plan
3. the target architecture expectation
4. the stable technical specs

Older migration-first execution materials should remain reachable only through `history/`.
