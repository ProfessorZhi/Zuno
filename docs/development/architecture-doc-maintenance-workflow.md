# Architecture Doc Maintenance Workflow

## Purpose

This is the current maintainer workflow for keeping architecture docs aligned with the repo.

Use it after any significant change to:

- repo structure
- backend service boundary
- runtime workflow
- GraphRAG Project / migration compatibility contracts
- evaluation surface
- README public explanation path

## Required Sequence

```text
spec update
  -> active phase update
  -> implementation
  -> targeted verification
  -> docs sync
  -> GitHub node
```

## What Must Be Reviewed

At minimum, review:

1. `README.md`
2. `docs/architecture/README.md`
3. `docs/architecture/current-architecture.md`
4. `docs/architecture/target-architecture.md`
5. the active file in `docs/architecture/history/phases/`
6. affected specs in `docs/architecture/specs/`
7. `docs/development/README.md`

## Update Checklist

For every large architecture or runtime change:

1. remove solved problems from architecture docs
2. update the current phase if the repo has crossed a phase boundary
3. downgrade stale readiness or temperature notes from the main path
4. make sure README and architecture docs describe the same repo shape
5. keep historical materials reachable, but not on the first-read path

## Anti-Pattern

Do not let a completed operational checklist continue acting like a current workflow entrypoint.

Examples:

- prestage notes
- ready-check notes
- one-off signoff surfaces
- phase-completion temperature docs

These may be useful history, but they should not remain in the main workflow path once the underlying operation is complete.
