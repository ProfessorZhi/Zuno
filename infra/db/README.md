# Database Migrations

`infra/db/` holds repository-level database migration assets.

Its current config still tracks the repo's mixed runtime surface, but that does not redefine the active architecture goal.

Typical commands:

```powershell
alembic -c infra/db/alembic.ini upgrade head
alembic -c infra/db/alembic.ini downgrade -1
alembic -c infra/db/alembic.ini revision --autogenerate -m "describe change"
```

Notes:

- `prepend_sys_path = services/api/src` reflects the current Alembic import path used by the repo's mixed runtime surface.
- `infra/db/alembic/env.py` now resolves metadata from `zuno.database.metadata`, not the legacy `agentchat` path.
- Runtime config resolution follows the same search order as `zuno.settings.resolve_app_config_path()`.
- Local overrides should stay in `.local/config/agentchat/config.local.yaml`.
