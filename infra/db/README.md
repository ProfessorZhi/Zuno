# Database Migrations

`infra/db/` holds repository-level database migration assets.

Its current config follows the recovered backend runtime truth at `src/backend/zuno`.

Typical commands:

```powershell
alembic -c infra/db/alembic.ini upgrade head
alembic -c infra/db/alembic.ini downgrade -1
alembic -c infra/db/alembic.ini revision --autogenerate -m "describe change"
```

Notes:

- `prepend_sys_path = src/backend` reflects the current Alembic import path.
- `infra/db/alembic/env.py` now resolves metadata from `zuno.database.metadata`, not the legacy `agentchat` path.
- Runtime config resolution follows the same search order as `zuno.settings.resolve_app_config_path()`.
- Local overrides should stay in `.local/config/agentchat/config.local.yaml`.
