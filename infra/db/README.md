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
- `infra/db/alembic/env.py` resolves metadata from `zuno.database.metadata`.
- Runtime config resolution follows the same search order as `zuno.settings.resolve_app_config_path()`.
- Local overrides should stay in `.local/config/zuno/config.local.yaml`.
- Online Alembic commands acquire the PostgreSQL session advisory lock
  `zuno:alembic:migration:v1`; set `ZUNO_ALEMBIC_LOCK_TIMEOUT_SECONDS` to a
  positive number to change the default 30-second wait.
- Long-running data copies must use `PostgresBackfillController` instead of a
  single revision transaction. Its durable ledger owns chunk idempotency,
  cursor/watermark progress, pause/resume, generation fencing and forward-fix
  lineage; it does not own domain cutover success.
- A lock timeout is fail-closed. Confirm the current revision and the active
  deploy owner before retrying; do not bypass the advisory lock.
