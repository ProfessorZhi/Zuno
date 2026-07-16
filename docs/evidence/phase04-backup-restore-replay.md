# PHASE04 Backup Restore Replay Evidence

phase_id: PHASE04
task_id: P04-T07
date: 2026-07-16
status: partial_implementation_available
postgres_backup: passed
postgres_restore: passed
object_manifest_restore: passed
checkpoint_table_restore: passed
outbox_inbox_watermark: passed
minio_restore_point: passed
projection_replay: partial_infra_rows_only
official_checkpointer_restore: not_yet_proven
pitr: not_yet_proven
runtime_restart_after_restore: not_yet_proven

## Boundary

Backup/Restore/Replay subset != PHASE04 completion.

This evidence proves a real recovery drill for the current PHASE04 primitive infrastructure rows and a real MinIO object restore point. It does not prove full product recovery, official LangGraph PostgreSQL Checkpointer restore, PITR, projection replay across domain modules, or runtime restart after restore.

## Environment

| Item | Value |
| --- | --- |
| PostgreSQL service | `zuno-postgres`, image `postgres:16` |
| Source DB | `zuno` |
| Restore DB | temporary `zuno_phase04_restore_<marker>` |
| Backup command | `docker exec zuno-postgres pg_dump -U postgres -d zuno -Fc -f /tmp/<restore-db>.dump` |
| Restore command | `docker exec zuno-postgres pg_restore -U postgres -d <restore-db> /tmp/<restore-db>.dump` |
| MinIO service | `zuno-minio`, image `minio/minio:RELEASE.2023-03-20T20-16-18Z` |
| Verification command | `python tools/scripts/verify_phase04_backup_restore_replay.py` |
| Integration test | `pytest -q tests/integration/test_phase04_backup_restore_replay.py -p no:cacheprovider` |

## Verified Behavior

- Writes unique PHASE04 recovery seed rows into real PostgreSQL infrastructure tables.
- Uses `infra_outbox_events` as the replay/outbox watermark and verifies restored status `published`.
- Uses `infra_inbox_messages` as the inbox dedup replay marker and verifies restored status `received`.
- Uses `infra_object_manifests` to verify the object manifest restore boundary.
- Uses `infra_checkpoints` to verify checkpoint primitive table restore.
- Creates a real MinIO object, restore point, delete, and restore cycle before database backup.
- Runs real `pg_dump` against the source database.
- Creates an isolated temporary restore database.
- Runs real `pg_restore` into the temporary restore database.
- Queries the restored database through `psycopg` and verifies marker/hash continuity.
- Drops the temporary restore database, removes the container dump file, and removes the temporary MinIO bucket.

## Commands And Results

```text
python tools/scripts/verify_phase04_backup_restore_replay.py
PHASE04 backup/restore/replay verification passed.
```

```text
pytest -q tests/integration/test_phase04_backup_restore_replay.py -p no:cacheprovider
1 passed
```

## Remaining Gap

- Official LangGraph PostgreSQL Checkpointer package/path is still not importable or proven.
- Checkpointer restore here covers only the primitive `infra_checkpoints` table, not the official checkpointer schema and runtime.
- PITR is not proven.
- Restore-after-runtime-restart is not proven.
- Projection replay across Product, Agent, Knowledge, Memory, Tool and Observability domains is not proven.
- Combined PostgreSQL/RabbitMQ/MinIO/Checkpointer dependency fault recovery remains missing.
- P04-T07 remains `ready`, not completed.
