# Phase 0: Stable Runtime Recovery

## Goal

Recover one stable, runnable backend baseline before any further architecture deepening.

## Status

Closed.

## Focus

- preserve the paused `services/` migration attempt as history or WIP
- restore `src/backend/zuno` as the stable backend runtime root
- restore startup closure
- restore import closure
- restore focused runtime verification

## Closure Gate

- `src/backend/zuno/main.py` is the real backend entry again
- `uvicorn --app-dir src/backend zuno.main:app` is the shared startup path
- core runtime imports work again
- focused runtime and entrypoint tests pass
- the user has personally tried the recovered runtime before Phase 2 begins
