# Database Migrations

`infra/db/` holds repository-level database migration assets so `src/backend/` can stay focused on importable source packages.

Typical commands:

```powershell
alembic -c infra/db/alembic.ini upgrade head
alembic -c infra/db/alembic.ini downgrade -1
alembic -c infra/db/alembic.ini revision --autogenerate -m "describe change"
```

Notes:

- `prepend_sys_path = src/backend` keeps backend packages importable during migrations.
- Runtime config resolution follows the same search order as `zuno.settings.resolve_app_config_path()`.
- Local overrides should stay in `.local/config/agentchat/config.local.yaml`.
