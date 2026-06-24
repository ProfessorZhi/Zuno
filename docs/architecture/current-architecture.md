# Current Architecture

## Purpose

This file describes the current repo reality. It does not describe the desired future state.

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

The stable backend package expected by the rest of the repo is:

```text
src/backend/zuno/
```

In other words:

1. `apps/web` and `apps/desktop` remain valid top-level app shells.
2. the Python backend runtime truth is `src/backend/zuno`.
3. any future root-level `services/` move must be reopened explicitly as a new architecture phase.

## Current Runtime Boundary

There is no active compatibility namespace in current truth.

The only backend runtime boundary is:

```text
src/backend/zuno/
```

Current mainline runtime work must not reintroduce retired alias packages, duplicate backend roots, or compatibility-only import trees.

## Completed Closure Truth

The previous architecture closure remains complete:

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

Do not rewrite these files as incomplete to carry new work.

## Current New Program

The current new execution program is:

- `docs/architecture/programs/official-graphrag-cleanup-v1/`

This program starts a separate cleanup and alignment round for:

1. docs and Agent workflow boundaries
2. legacy front-path cleanup
3. official GraphRAG Project settings
4. Prompt Tuning and indexing
5. Query Method routing
6. storage versioning
7. frontend/API surface alignment
8. tests, evals, and closure

## Current Documentation Rule

The front path under `docs/architecture/` should expose:

1. the current repo reality
2. the active independent program
3. the target architecture expectation
4. the stable technical specs

Older migration-first execution materials and superseded programs should remain reachable only through `history/`.

`AGENTS.md` is the Agent entrypoint. `.agent/` is the Agent workflow library. Neither replaces `docs/architecture/` as formal truth.
