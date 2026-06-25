# Repository Hygiene Map

## Purpose

Classify repository directories for cleanup decisions.

## Current

- `apps/`: Current
- `src/backend/zuno/`: Current
- `docs/`: Current formal docs
- `.agent/`: Current Agent workflow library
- `domain-packs/`: Blocked Legacy
- `tests/compat/`: Current / Blocked Legacy
- `data/`: Generated unless promoted
- `reports/`: Generated unless promoted
- `.local/`: Local
- `.codex/`: Local
- `node_modules/`: Generated

## Phase 11C Progress

The current FastAPI router no longer mounts `/domain-packs`, and active Vue
knowledge route/settings entrypoints no longer open Domain Pack pages. Retained
Domain Pack modules, frontend files, assets, evals, Docker references, and
compat tests remain Blocked Legacy until their replacement or migration is
proved.

## Rule

Do not delete Blocked Legacy. Do not commit Generated or Local outputs.
`domain-packs/` and `tests/compat/` must not be treated as target repository layout.
Read `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
before directory-boundary work.
