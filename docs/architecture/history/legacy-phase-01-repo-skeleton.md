# Phase 1: Repo Skeleton

## Goal

Define and expose the new top-level project skeleton:

```text
apps / services / domain-packs / infra / tools / tests / docs
```

## Why This Phase Exists

The current repo already has a strong application split, but its top-level shape does not yet fully express the intended service boundary.

This phase makes the public repo skeleton legible before deeper migration work begins.

## What Changes Here

- docs entrypoints
- README structure explanation
- publish-boundary language
- new architecture and phase surfaces
- directory placeholders where needed

## Closure Gate

- the new repo skeleton is documented as the active target
- current docs stop presenting stale phase truth as current
- current-vs-history boundaries are explicit
- structure verification still passes
