# Workflow Map

## Purpose

Map task types to Agent workflows.

## Current Paths

- `.agent/workflows/read-only-audit.md`
- `.agent/workflows/docs-maintenance.md`
- `.agent/workflows/repo-hygiene.md`
- `.agent/workflows/frontend-change.md`
- `.agent/workflows/backend-change.md`
- `.agent/workflows/api-contract-change.md`
- `.agent/workflows/architecture-refactor.md`
- `.agent/workflows/eval-change.md`
- `.agent/workflows/bugfix-root-cause.md`
- `.agent/workflows/task-closure.md`

## Routing

- unclear scope -> read-only audit
- docs or `.agent` -> docs maintenance
- directory move, delete, archive, ignore, generated/local cleanup -> repo hygiene
- `apps/web` -> frontend change
- `src/backend/zuno` -> backend change
- API, DTO, request/response, frontend/backend contract -> API contract change
- architecture replacement -> architecture refactor
- eval data, metrics, profiles, reports -> eval change
- failure or regression -> bugfix root cause
- before finishing any modification -> task closure

## Update Triggers

Update this map when adding, removing, or renaming workflows or skills.

## Active Program

The active executable Agent program is:

- `.agent/programs/zuno-target-runtime-v2/`

The completed V1 target architecture migration is archived at:

- `docs/architecture/history/programs/zuno-target-architecture-migration-v1/`
## Required Target Blueprint

Architecture replacement, directory moves, Context/Memory, GraphRAG boundary,
and repository hygiene workflows must read:

- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`

Treat it as Target / Proposed visual reference only.
