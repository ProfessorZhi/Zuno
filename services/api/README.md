# API Service

`services/api` is currently a paused migration surface, not runtime truth.

## Boundary

- runtime truth remains `src/backend/zuno/`
- `services/api/src/zuno/` is kept in sync only where the repo still needs a migration-facing mirror
- compat-facing `agentchat` packages under this service exist only to keep old import surfaces alive
- those compat bridges are not runtime truth

## What This Directory Is Allowed To Do

- preserve a future service-root shape for later phases
- host migration-facing mirrors that are explicitly kept aligned with `src/backend/zuno/`
- expose temporary compat package bridges for `zuno` and compat-facing `agentchat`

## What This Directory Must Not Be Treated As

- the default backend startup root
- the primary place to add new GraphRAG behavior
- proof that the legacy import surface is still an active runtime dependency

If code, tests, scripts, or Docker need a backend truth decision today, use `src/backend/zuno/` unless a file is explicitly marked as compat-only.
