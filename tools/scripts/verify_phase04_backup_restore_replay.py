from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path
from uuid import uuid4

import psycopg
from psycopg.types.json import Jsonb
from sqlalchemy import text

from zuno.platform.contracts import canonical_sha256
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
            manifest_hash = repo.put_object_manifest(
                object_ref=object_ref,
                content=object_hash.encode("ascii"),
                owner="phase04-backup-restore",
                visibility="restored",
            )
            product_source_payload = {
                "marker": marker,
                "runtime_request_ref": f"runtime-request:{marker}",
                "source_fact_ref": f"product-command:{marker}",
                "source_partition": f"workspace-task:{marker}",
                "source_watermark": 1,
                "object_ref": object_ref,
                "object_hash": object_hash,
                "manifest_hash": manifest_hash,
                "projection_schema_version": "product-projection-v1",
                "authorized_view_ref": f"authorized-view:{marker}",
            }
            product_event_id = repo.enqueue_outbox(
                aggregate_id=f"product-projection-{marker}",
                topic="product.projection.source_fact",
                payload=product_source_payload,
                idempotency_key=f"phase04-product-projection-{marker}",
                tenant_id="tenant-phase04",
                ordering_key=f"product-projection-{marker}",
            )
            product_claimed = repo.claim_outbox(
                worker_id=f"product-projector-{marker}",
                limit=10,
            )
            if product_event_id in product_claimed:
                repo.complete_outbox(
                    event_id=product_event_id,
                    worker_id=f"product-projector-{marker}",
                )
            repo.save_checkpoint(
                thread_id=f"thread-{marker}",
                checkpoint_id=f"checkpoint-{marker}",
                generation=1,
                state={"marker": marker, "event_id": event_id, "object_ref": object_ref},
                owner="phase04-backup-restore",
            )
        return {
            "event_id": event_id,
            "inbox_hash": inbox_hash,
            "product_event_id": product_event_id,
            "product_source_hash": canonical_sha256(product_source_payload),
        }
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


def _replay_product_projection_from_restore(
    database_name: str,
    marker: str,
    product_event_id: str,
    expected_source_hash: str,
    object_ref: str,
) -> list[str]:
    errors: list[str] = []
    dsn = f"{POSTGRES_BASE_DSN}/{database_name}"
    recovery_point = f"product-source:{product_event_id}"
    authoritative_component_id = f"product-authoritative-{marker}"
    projection_component_id = f"product-projection-{marker}"
    recovery_set_id = f"product-recovery-set-{marker}"
    with psycopg.connect(dsn, connect_timeout=5) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT count(*)
                FROM infra_recovery_watermarks
                WHERE component_id = %s
                """,
                (projection_component_id,),
            )
            if cur.fetchone() != (0,):
                errors.append("derived product projection watermark existed before replay")

            cur.execute(
                """
                SELECT event_id, aggregate_id, payload, payload_hash, ordering_sequence, status
                FROM infra_outbox_events
                WHERE event_id = %s
                  AND topic = 'product.projection.source_fact'
                  AND tenant_id = 'tenant-phase04'
                """,
                (product_event_id,),
            )
            source = cur.fetchone()
            if source is None:
                return [f"restored product source fact missing: {product_event_id}"]
            (
                restored_event_id,
                aggregate_id,
                source_payload,
                restored_source_hash,
                ordering_sequence,
                status,
            ) = source
            source_payload = dict(source_payload)
            if restored_source_hash != expected_source_hash:
                errors.append(
                    "restored product source fact hash mismatch: "
                    f"{restored_source_hash!r}"
                )
            if canonical_sha256(source_payload) != restored_source_hash:
                errors.append("restored product source payload failed canonical hash verification")
            if status != "published":
                errors.append(f"restored product source fact was not published: {status!r}")
            if int(ordering_sequence or 0) != 1:
                errors.append(
                    f"restored product source ordering watermark mismatch: {ordering_sequence!r}"
                )

            cur.execute(
                """
                SELECT content_hash, visibility, owner
                FROM infra_object_manifests
                WHERE object_ref = %s
                """,
                (object_ref,),
            )
            manifest = cur.fetchone()
            if manifest is None:
                return [f"restored object manifest missing for projection replay: {object_ref}"]
            manifest_hash, visibility, owner = manifest
            if manifest_hash != source_payload["manifest_hash"]:
                errors.append("projection replay rejected mismatched restored object manifest hash")
            if visibility != "restored" or owner != "phase04-backup-restore":
                errors.append(f"projection replay saw wrong manifest state: {manifest!r}")

            projection_payload = {
                "projection_id": f"projection:{marker}",
                "source_fact_ref": restored_event_id,
                "source_event_id": restored_event_id,
                "source_partition": aggregate_id,
                "source_watermark": int(ordering_sequence or 0),
                "schema_version": source_payload["projection_schema_version"],
                "authorized_view_ref": source_payload["authorized_view_ref"],
                "object_ref": source_payload["object_ref"],
                "object_hash": manifest_hash,
                "restored_object_hash": source_payload["object_hash"],
                "rebuildable": True,
            }
            projection_hash = canonical_sha256(projection_payload)
            if projection_hash == restored_source_hash:
                errors.append("derived product projection hash must not replace source fact hash")

            cur.execute(
                """
                INSERT INTO infra_recovery_watermarks(
                    component_id, service_kind, authority, watermark, payload_hash,
                    payload, owner_id
                ) VALUES (
                    %s, 'PRODUCT', 'authoritative', %s, %s, %s,
                    'phase04-product-replay'
                )
                """,
                (
                    authoritative_component_id,
                    recovery_point,
                    restored_source_hash,
                    Jsonb(source_payload),
                ),
            )
            cur.execute(
                """
                INSERT INTO infra_recovery_watermarks(
                    component_id, service_kind, authority, watermark, payload_hash,
                    payload, owner_id
                ) VALUES (
                    %s, 'PRODUCT_PROJECTION', 'derived', %s, %s, %s,
                    'phase04-product-replay'
                )
                """,
                (
                    projection_component_id,
                    recovery_point,
                    projection_hash,
                    Jsonb(projection_payload),
                ),
            )
            verification_hash = canonical_sha256(
                {
                    "recovery_point": recovery_point,
                    "components": [
                        {
                            "component_id": authoritative_component_id,
                            "service_kind": "PRODUCT",
                            "authority": "authoritative",
                            "watermark": recovery_point,
                            "payload_hash": restored_source_hash,
                        },
                        {
                            "component_id": projection_component_id,
                            "service_kind": "PRODUCT_PROJECTION",
                            "authority": "derived",
                            "watermark": recovery_point,
                            "payload_hash": projection_hash,
                        },
                    ],
                }
            )
            cur.execute(
                """
                INSERT INTO infra_recovery_sets(
                    recovery_set_id, recovery_point, status, verification_hash, owner_id
                ) VALUES (%s, %s, 'verified', %s, 'phase04-product-replay')
                """,
                (recovery_set_id, recovery_point, verification_hash),
            )
            for component_id, service_kind, authority, payload_hash in (
                (
                    authoritative_component_id,
                    "PRODUCT",
                    "authoritative",
                    restored_source_hash,
                ),
                (
                    projection_component_id,
                    "PRODUCT_PROJECTION",
                    "derived",
                    projection_hash,
                ),
            ):
                cur.execute(
                    """
                    INSERT INTO infra_recovery_set_members(
                        recovery_set_id, component_id, service_kind, authority,
                        watermark, payload_hash
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        recovery_set_id,
                        component_id,
                        service_kind,
                        authority,
                        recovery_point,
                        payload_hash,
                    ),
                )
            conn.commit()

            cur.execute(
                """
                SELECT status, verification_hash
                FROM infra_recovery_sets
                WHERE recovery_set_id = %s
                """,
                (recovery_set_id,),
            )
            recovery_set = cur.fetchone()
            if recovery_set != ("verified", verification_hash):
                errors.append(f"product projection RecoverySet mismatch: {recovery_set!r}")

            cur.execute(
                """
                SELECT authority, watermark, payload_hash, payload->>'source_fact_ref',
                       payload->>'rebuildable'
                FROM infra_recovery_watermarks
                WHERE component_id = %s
                """,
                (projection_component_id,),
            )
            projection_watermark = cur.fetchone()
            expected_projection_watermark = (
                "derived",
                recovery_point,
                projection_hash,
                product_event_id,
                "true",
            )
            if projection_watermark != expected_projection_watermark:
                errors.append(
                    f"product projection replay watermark mismatch: {projection_watermark!r}"
                )
    return errors


def _cleanup_recovery_seed(marker: str, event_id: str, object_ref: str, product_event_id: str) -> None:
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
                text("DELETE FROM infra_outbox_events WHERE event_id = :event_id"),
                {"event_id": product_event_id},
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
                _replay_product_projection_from_restore(
                    database_name,
                    marker,
                    seed["product_event_id"],
                    seed["product_source_hash"],
                    object_ref,
                )
            )
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
            _cleanup_recovery_seed(
                marker,
                seed["event_id"],
                object_ref,
                seed["product_event_id"],
            )
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
