# Target Architecture

## Purpose

This file describes the target shape for the current architecture direction.
It is the desired structure, not the current state.

## Target Shape Now

The next target is not immediate root-level service extraction.

The next target is:

```text
one stable, explainable monorepo baseline
  -> apps/web
  -> apps/desktop
  -> src/backend/zuno
  -> strong LangGraph runtime
  -> strong GraphRAG and Domain Pack contracts
  -> strong local evaluation proof
```

## Target Repository Shape

```text
Zuno/
  apps/
    web/
    desktop/
  src/
    backend/
      zuno/
  infra/
  tools/
  tests/
  docs/
```

## Target Directory Meaning

```text
apps              = user-facing application shells
src/backend/zuno  = stable Python backend package
infra             = deployment and environment infrastructure
tools             = scripts, launchers, eval tooling, migration helpers
tests             = repo-level verification and end-to-end checks
docs              = current truth, plans, specs, workflow, history
```

## Target Runtime Mainline

The backend should be easy to explain as:

```text
Domain Pack
  -> LangGraph runtime
  -> retrieval planning
  -> vector / BM25 / graph retrieval
  -> evidence fusion
  -> answer + citation check
  -> evaluation + proof
```

## Target Evolution Rule

The repo should remain:

```text
monorepo now, service-ready later
```

That means:

1. recover and stabilize `src/backend/zuno` first
2. deepen runtime quality second
3. only reopen repo-boundary migration after the runtime is stable and testable

## Target Documentation Rule

The docs system should expose only these current-truth layers on the front path:

1. `current`
2. `plan`
3. `spec`
4. `decision`

Everything older belongs in:

- `history`
- `reference`
- `development`
