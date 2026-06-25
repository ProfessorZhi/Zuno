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

## Rule

Do not delete Blocked Legacy. Do not commit Generated or Local outputs.
