# Zuno 2026-06 Architecture Upgrade Design

## Purpose

This spec defines the current architecture-upgrade program after the service-migration-first path was paused.

It answers four questions:

1. what stable shape Zuno is trying to recover first
2. why the previous migration-first execution path was paused
3. how `spec / phase / workflow / history` should now be separated
4. what sequence should govern the next rounds of architecture work

This is not a historical archive.
Historical materials belong in `../history/`.

## Problem Statement

The repo accumulated three kinds of drift at the same time:

1. documentation drift
   - old execution phases, current expectations, and historical notes were mixed together
2. structure drift
   - `apps/` became visible, but backend boundaries and runtime entrypoints no longer told one clear story
3. workflow drift
   - docs, implementation, validation, and public explanations could move out of sync

The main problem is not naming.
The main problem is that the repo stopped having one stable current truth.

## Current Upgrade Decision

The active decision is now:

```text
stability first, migration later
```

More concretely:

```text
recover one stable runnable baseline
  -> let the user try it
  -> then continue deeper runtime and architecture upgrades
```

The earlier `services/api` migration attempt remains useful as context, but it is not the current execution mainline.

## Target Shape For This Round

The next stable shape is:

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

This target is intentionally conservative.
It favors one explainable, runnable monorepo baseline over a partially migrated service layout.

## Runtime Mainline

The runtime thesis remains:

```text
Domain Pack
  -> LangGraph Runtime
  -> Retrieval Planning
  -> Vector / BM25 / Graph Retrieval
  -> Evidence Fusion
  -> Answer + Citation Check
  -> Evaluation + Proof
```

What changed is not the runtime thesis.
What changed is the execution order used to stabilize it.

## Documentation Layering

The front path should expose only four kinds of current-truth material:

1. `current`
2. `plan / phase`
3. `spec`
4. `decision`

Everything else belongs in history or support docs.

Recommended split:

```text
docs/architecture/
  README.md
  current-architecture.md
  target-architecture.md
  transition-strategy.md
  phases/
  specs/
  decisions/
  history/
```

## Current Phase Program

The active phase program is now:

1. Phase 0: Stable Runtime Recovery
2. Phase 1: LangGraph Runtime Deepening
3. Phase 2: GraphRAG Mainline Deepening
4. Phase 3: Domain Pack Formalization
5. Phase 4: Local Eval Strengthening
6. Phase 5: Docs And Public Explanation Sync

This replaces the paused migration-first phase story as the current execution truth.

## Workflow Rule

For any structure-level or runtime-level change, use:

```text
spec update
  -> phase alignment
  -> implementation slice
  -> minimal targeted verification
  -> docs sync
```

Two hard rules follow from this:

1. if a change alters structure or public explanation, docs must move with it
2. if a change cannot be minimally verified, it is not ready to claim as current truth

## Migration Rule

Do not treat directory movement as success by itself.

If the repo ever reopens a root-level service migration, it must move together with:

- imports
- startup entrypoints
- Docker and launcher paths
- eval scripts
- test expectations
- README and architecture docs

Otherwise the repo only gains a second root and loses explainability.

## Acceptance Criteria

This architecture-upgrade round is in a healthy state only when all of the following are true:

1. the repo has one stable runnable baseline
2. the user has personally tried that recovered runtime
3. front-path docs expose only the latest plan, latest phase model, and latest architecture truth
4. older migration-first materials live only in `history/` or explicit historical context
5. deeper LangGraph, GraphRAG, Domain Pack, and eval work can continue without reopening doc ambiguity first

## Summary

The shortest correct path is:

```text
recover a stable baseline
  -> verify it
  -> let the user experience it
  -> then deepen the architecture
```

That is the current architecture-upgrade design truth for Zuno.
