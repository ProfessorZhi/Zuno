from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path
from uuid import uuid4

import psycopg
from sqlalchemy import text

from zuno.platform.database.foundation import (
    InfrastructureUnitOfWork,
    create_foundation_engine,
)
from zuno.platform.database.runtime import PostgresRuntime, PostgresRuntimeConfig
from zuno.platform.storage import MinioObjectStore

REPO_ROOT = Path(__file__).resolve().parents[2]
POSTGRES_SQLALCHEMY_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/zuno"
POSTGRES_BASE_DSN = "postgresql://postgres:postgres@localhost:5432"
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=False)


def _insert_recovery_seed(marker: str, object_ref: str, object_hash: str) -> dict[str, str]:
    engine = create_foundation_engine(POSTGRES_SQLALCHEMY_URL)
    try:
        uow = InfrastructureUnitOfWork(engine)
        with uow as repo:
            event_id = repo.enqueue_outbox(
                aggregate_id=f"phase04-recovery-{marker}",
                topic="phase04.recovery",
                payload={"marker": marker, "object_ref": object_ref, "object_hash": object_hash},
                idempotency_key=f"phase04-recovery-{marker}",
            )
            claimed = repo.claim_outbox(worker_id=f"publisher-{marker}", limit=1)
            if event_id in claimed:
                repo.complete_outbox(event_id=event_id, worker_id=f"publisher-{marker}")
            inbox_hash = repo.record_inbox(
                consumer="phase04-replay",
                message_id=f"message-{marker}",
                payload={"marker": marker, "event_id": event_id},
            )
            repo.put_object_manifest(
                object_ref=object_ref,
                content=object_hash.encode("ascii"),
                owner="phase04-backup-restore",
                visibility="restored",
            )
            repo.save_checkpoint(
                thread_id=f"thread-{marker}",
                checkpoint_id=f"checkpoint-{marker}",
                generation=1,
                state={"marker": marker, "event_id": event_id, "object_ref": object_ref},
                owner="phase04-backup-restore",
            )
        return {"event_id": event_id, "inbox_hash": inbox_hash}
    finally:
        engine.dispose()


def _query_restore_database(database_name: str, marker: str, event_id: str, object_ref: str) -> list[str]:
    errors: list[str] = []
    dsn = f"{POSTGRES_BASE_DSN}/{database_name}"
    with psycopg.connect(dsn, connect_timeout=5) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT status, payload->>'marker'
                FROM infra_outbox_events
                WHERE event_id = %s
                """,
                (event_id,),
            )
            outbox = cur.fetchone()
            if outbox != ("published", marker):
                errors.append(f"restored outbox row mismatch: {outbox!r}")

            cur.execute(
                """
                SELECT status, payload->>'marker'
                FROM infra_inbox_messages
                WHERE consumer = 'phase04-replay' AND message_id = %s
                """,
                (f"message-{marker}",),
            )
            inbox = cur.fetchone()
            if inbox != ("received", marker):
                errors.append(f"restored inbox row mismatch: {inbox!r}")

            cur.execute(
                """
                SELECT visibility, owner
                FROM infra_object_manifests
                WHERE object_ref = %s
                """,
                (object_ref,),
            )
            manifest = cur.fetchone()
            if manifest != ("restored", "phase04-backup-restore"):
                errors.append(f"restored object manifest mismatch: {manifest!r}")

            cur.execute(
                """
                SELECT checkpoint_id, generation, state_payload->>'marker'
                FROM infra_checkpoints
                WHERE thread_id = %s
                """,
                (f"thread-{marker}",),
            )
            checkpoint = cur.fetchone()
            if checkpoint != (f"checkpoint-{marker}", 1, marker):
                errors.append(f"restored checkpoint row mismatch: {checkpoint!r}")
    return errors


def _cleanup_recovery_seed(marker: str, event_id: str, object_ref: str) -> None:
    engine = create_foundation_engine(POSTGRES_SQLALCHEMY_URL)
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "DELETE FROM infra_inbox_messages "
                    "WHERE consumer = 'phase04-replay' AND message_id = :message_id"
                ),
                {"message_id": f"message-{marker}"},
            )
            connection.execute(
                text("DELETE FROM infra_outbox_events WHERE event_id = :event_id"),
                {"event_id": event_id},
            )
            connection.execute(
                text("DELETE FROM infra_object_manifests WHERE object_ref = :object_ref"),
                {"object_ref": object_ref},
            )
            connection.execute(
                text("DELETE FROM infra_checkpoints WHERE thread_id = :thread_id"),
                {"thread_id": f"thread-{marker}"},
            )
    finally:
        engine.dispose()


async def _verify_restored_runtime(
    database_name: str,
    marker: str,
    event_id: str,
    object_ref: str,
) -> list[str]:
    errors: list[str] = []
    runtime = PostgresRuntime(
        PostgresRuntimeConfig(
            sync_url=f"postgresql+psycopg://postgres:postgres@localhost:5432/{database_name}",
            async_url=f"postgresql+asyncpg://postgres:postgres@localhost:5432/{database_name}",
            pool_size=1,
            max_overflow=0,
            pool_timeout_seconds=2,
            statement_timeout_ms=5_000,
            lock_timeout_ms=1_000,
        )
    )
    try:
        sync_health = runtime.sync_health()
        async_health = await runtime.async_health()
        if not sync_health.ready or not async_health.ready:
            errors.append("restored database was not ready through a rebuilt sync/async PostgresRuntime")

        with runtime.sync_uow(read_only=True) as session:
            outbox = session.execute(
                text(
                    """
                    SELECT status, payload->>'marker'
                    FROM infra_outbox_events
                    WHERE event_id = :event_id
                    """
                ),
                {"event_id": event_id},
            ).one_or_none()
            manifest = session.execute(
                text(
                    """
                    SELECT visibility, owner
                    FROM infra_object_manifests
                    WHERE object_ref = :object_ref
                    """
                ),
                {"object_ref": object_ref},
            ).one_or_none()
        if outbox is None or tuple(outbox) != ("published", marker):
            errors.append(f"rebuilt sync Runtime read the wrong restored outbox row: {outbox!r}")
        if manifest is None or tuple(manifest) != ("restored", "phase04-backup-restore"):
            errors.append(f"rebuilt sync Runtime read the wrong restored manifest: {manifest!r}")

        async with runtime.async_uow(read_only=True) as session:
            inbox = (
                await session.execute(
                    text(
                        """
                        SELECT status, payload->>'marker'
                        FROM infra_inbox_messages
                        WHERE consumer = 'phase04-replay' AND message_id = :message_id
                        """
                    ),
                    {"message_id": f"message-{marker}"},
                )
            ).one_or_none()
            checkpoint = (
                await session.execute(
                    text(
                        """
                        SELECT checkpoint_id, generation, state_payload->>'marker'
                        FROM infra_checkpoints
                        WHERE thread_id = :thread_id
                        """
                    ),
                    {"thread_id": f"thread-{marker}"},
                )
            ).one_or_none()
        if inbox is None or tuple(inbox) != ("received", marker):
            errors.append(f"rebuilt async Runtime read the wrong restored inbox row: {inbox!r}")
        expected_checkpoint = (f"checkpoint-{marker}", 1, marker)
        if checkpoint is None or tuple(checkpoint) != expected_checkpoint:
            errors.append(
                f"rebuilt async Runtime read the wrong restored checkpoint primitive: {checkpoint!r}"
            )
    finally:
        await runtime.close()
    return errors


def verify_phase04_backup_restore_replay() -> list[str]:
    marker = uuid4().hex
    database_name = f"zuno_phase04_restore_{marker[:16]}"
    dump_path = f"/tmp/{database_name}.dump"
    bucket = f"phase04-recovery-{marker}"
    object_name = "committed/recovery.txt"
    restore_point_name = "_restore/recovery.txt"
    object_ref = f"s3://{bucket}/{object_name}"
    errors: list[str] = []
    seed: dict[str, str] | None = None

    store = MinioObjectStore(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
    )
    try:
        staged = store.stage_object(bucket=bucket, object_name=object_name, content=f"phase04:{marker}".encode("utf-8"))
        committed = store.commit_object(
            bucket=bucket,
            staged_object_name=staged.object_name,
            committed_object_name=object_name,
            expected_hash=staged.content_hash,
        )
        restore_point = store.create_restore_point(
            bucket=bucket,
            object_name=committed.object_name,
            restore_point_name=restore_point_name,
        )
        store.delete_object(bucket=bucket, object_name=committed.object_name)
        restored = store.restore_object(
            bucket=bucket,
            restore_point_name=restore_point.object_name,
            restored_object_name=object_name,
        )
        if restored.content_hash != committed.content_hash:
            errors.append("MinIO restore point hash changed during recovery drill")

        seed = _insert_recovery_seed(marker, object_ref, restored.content_hash)
        dump = _run(["docker", "exec", "zuno-postgres", "pg_dump", "-U", "postgres", "-d", "zuno", "-Fc", "-f", dump_path])
        if dump.returncode != 0:
            return [f"PostgreSQL pg_dump failed: {dump.stderr.strip()}"]

        create_db = _run(["docker", "exec", "zuno-postgres", "createdb", "-U", "postgres", database_name])
        if create_db.returncode != 0:
            return [f"PostgreSQL restore database create failed: {create_db.stderr.strip()}"]

        restore = _run(["docker", "exec", "zuno-postgres", "pg_restore", "-U", "postgres", "-d", database_name, dump_path])
        if restore.returncode != 0:
            errors.append(f"PostgreSQL pg_restore failed: {restore.stderr.strip()}")
        else:
            errors.extend(_query_restore_database(database_name, marker, seed["event_id"], object_ref))
            errors.extend(
                asyncio.run(
                    _verify_restored_runtime(
                        database_name,
                        marker,
                        seed["event_id"],
                        object_ref,
                    )
                )
            )
    finally:
        _run(["docker", "exec", "zuno-postgres", "dropdb", "-U", "postgres", "--if-exists", database_name])
        _run(["docker", "exec", "zuno-postgres", "rm", "-f", dump_path])
        if seed is not None:
            _cleanup_recovery_seed(marker, seed["event_id"], object_ref)
        store.remove_bucket_tree(bucket)
    return errors


def main() -> int:
    errors = verify_phase04_backup_restore_replay()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 backup/restore/replay verification failed.")
        return 1
    print("PHASE04 backup/restore/replay verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
