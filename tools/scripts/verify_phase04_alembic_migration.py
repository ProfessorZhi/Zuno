from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine, text

REPO_ROOT = Path(__file__).resolve().parents[2]
ADMIN_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
DB_URL_TEMPLATE = "postgresql+psycopg://postgres:postgres@localhost:5432/{database}"
REQUIRED_INFRA_TABLES = {
    "infra_outbox_events",
    "infra_inbox_messages",
    "infra_idempotency_claims",
    "infra_worker_leases",
    "infra_object_manifests",
    "infra_checkpoints",
    "infra_outbox_sequences",
    "infra_delivery_watermarks",
    "infra_migration_backfills",
    "infra_migration_backfill_chunks",
}
EXPECTED_HEAD_REVISION = "20260717_08"
REQUIRED_TABLE_COLUMNS = {
    "infra_outbox_events": {
        "event_id",
        "aggregate_id",
        "topic",
        "payload",
        "payload_hash",
        "idempotency_key",
        "status",
        "claim_owner",
        "claimed_at",
        "published_at",
        "created_at",
        "tenant_id",
        "ordering_key",
        "ordering_sequence",
        "publish_attempts",
        "retry_count",
        "next_attempt_at",
        "last_error_code",
        "last_failed_at",
        "dead_lettered_at",
        "replay_count",
        "last_replay_owner",
        "replayed_at",
    },
    "infra_inbox_messages": {
        "consumer",
        "message_id",
        "payload_hash",
        "conflict_hash",
        "payload",
        "status",
        "received_at",
        "tenant_id",
        "ordering_key",
        "ordering_sequence",
    },
    "infra_idempotency_claims": {
        "claim_id",
        "tenant_id",
        "scope",
        "idempotency_key",
        "owner",
        "request_hash",
        "status",
        "generation",
        "result_ref",
        "expires_at",
        "completed_at",
        "created_at",
    },
    "infra_worker_leases": {"resource_id", "owner_id", "lease_id", "epoch", "expires_at", "updated_at"},
    "infra_object_manifests": {
        "object_ref",
        "owner",
        "content_hash",
        "conflict_hash",
        "size_bytes",
        "visibility",
        "created_at",
    },
    "infra_checkpoints": {
        "checkpoint_id",
        "thread_id",
        "generation",
        "owner",
        "state_hash",
        "state_payload",
        "created_at",
    },
    "infra_outbox_sequences": {
        "tenant_id",
        "ordering_key",
        "last_sequence",
        "updated_at",
    },
    "infra_delivery_watermarks": {
        "tenant_id",
        "consumer",
        "ordering_key",
        "contiguous_sequence",
        "max_seen_sequence",
        "updated_at",
    },
    "infra_migration_backfills": {
        "backfill_id",
        "module_owner",
        "source_ref",
        "target_ref",
        "transform_version",
        "state",
        "cursor",
        "cursor_hash",
        "source_watermark",
        "processed_count",
        "conflict_count",
        "chunk_size",
        "generation",
        "lease_owner",
        "lease_expires_at",
        "verification_hash",
        "error_code",
        "forward_fix_of",
        "created_at",
        "updated_at",
        "completed_at",
    },
    "infra_migration_backfill_chunks": {
        "backfill_id",
        "chunk_id",
        "start_cursor",
        "end_cursor",
        "start_cursor_hash",
        "end_cursor_hash",
        "payload_hash",
        "source_watermark",
        "row_count",
        "applied_generation",
        "applied_at",
    },
}
REQUIRED_CONSTRAINTS = {
    "ck_infra_outbox_events_status",
    "ck_infra_inbox_messages_status",
    "ck_infra_idempotency_claims_status",
    "ck_infra_object_manifests_visibility",
    "uq_infra_idempotency_claims_tenant_scope_key",
    "uq_infra_checkpoints_thread_generation",
    "ck_infra_outbox_sequences_positive",
    "ck_infra_outbox_events_ordering_pair",
    "uq_infra_outbox_events_tenant_ordering_sequence",
    "ck_infra_inbox_messages_ordering_pair",
    "uq_infra_inbox_messages_tenant_consumer_ordering_sequence",
    "ck_infra_delivery_watermarks_sequence",
    "ck_infra_outbox_events_delivery_counts",
    "ck_infra_outbox_events_claim_state",
    "ck_infra_outbox_events_dead_letter_state",
    "fk_infra_migration_backfills_forward_fix_of",
    "ck_infra_migration_backfills_state",
    "ck_infra_migration_backfills_counts",
    "ck_infra_migration_backfills_lease_state",
    "ck_infra_migration_backfills_completed_state",
    "fk_infra_migration_backfill_chunks_backfill",
    "pk_infra_migration_backfill_chunks",
    "ck_infra_migration_backfill_chunks_counts",
}
FORBIDDEN_CONSTRAINTS = {"uq_infra_idempotency_claims_scope_key"}
REQUIRED_INDEXES = {
    "ix_infra_outbox_events_pending",
    "ix_infra_outbox_events_idempotency_key",
    "ix_infra_checkpoints_thread_generation",
    "ix_infra_outbox_events_tenant_ordering",
    "ix_infra_inbox_messages_buffered",
    "ix_infra_outbox_events_delivery_ready",
    "ix_infra_migration_backfills_state_lease",
    "ix_infra_migration_backfills_owner",
    "ix_infra_migration_backfill_chunks_applied",
}


def _run_alembic(config_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["ZUNO_CONFIG"] = str(config_path)
    return subprocess.run(
        ["alembic", "-c", "infra/db/alembic.ini", *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
    )


def _create_database(database: str) -> None:
    engine = create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT", future=True)
    try:
        with engine.connect() as conn:
            conn.execute(text(f'CREATE DATABASE "{database}"'))
    finally:
        engine.dispose()


def _drop_database(database: str) -> None:
    engine = create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT", future=True)
    try:
        with engine.connect() as conn:
            conn.execute(
                text(
                    """
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = :database AND pid <> pg_backend_pid()
                    """
                ),
                {"database": database},
            )
            conn.execute(text(f'DROP DATABASE IF EXISTS "{database}"'))
    finally:
        engine.dispose()


def _write_config(path: Path, database_url: str) -> None:
    path.write_text(
        "\n".join(
            [
                "database:",
                f'  sync_endpoint: "{database_url}"',
                f'  async_endpoint: "{database_url.replace("+psycopg://", "+asyncpg://")}"',
                "  echo: false",
                "  pool_size: 2",
                "  max_overflow: 2",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _current_revision(database_url: str) -> str | None:
    engine = create_engine(database_url, future=True)
    try:
        with engine.connect() as conn:
            exists = conn.execute(
                text("SELECT to_regclass('public.alembic_version') IS NOT NULL")
            ).scalar_one()
            if not exists:
                return None
            return conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one_or_none()
    finally:
        engine.dispose()


def _table_names(database_url: str) -> set[str]:
    engine = create_engine(database_url, future=True)
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    """
                    SELECT tablename
                    FROM pg_tables
                    WHERE schemaname = 'public'
                    """
                )
            ).all()
            return {str(row.tablename) for row in rows}
    finally:
        engine.dispose()


def _schema_drift_errors(database_url: str) -> list[str]:
    engine = create_engine(database_url, future=True)
    errors: list[str] = []
    try:
        with engine.connect() as conn:
            column_rows = conn.execute(
                text(
                    """
                    SELECT table_name, column_name
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                    """
                )
            ).all()
            columns_by_table: dict[str, set[str]] = {}
            for row in column_rows:
                columns_by_table.setdefault(str(row.table_name), set()).add(str(row.column_name))
            for table_name, expected_columns in REQUIRED_TABLE_COLUMNS.items():
                actual_columns = columns_by_table.get(table_name, set())
                missing_columns = expected_columns - actual_columns
                extra_columns = actual_columns - expected_columns
                if missing_columns:
                    errors.append(f"{table_name} missing columns: {sorted(missing_columns)!r}")
                if extra_columns:
                    errors.append(f"{table_name} unexpected columns: {sorted(extra_columns)!r}")

            tenant_row = conn.execute(
                text(
                    """
                    SELECT is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND table_name = 'infra_idempotency_claims'
                      AND column_name = 'tenant_id'
                    """
                )
            ).first()
            if tenant_row is None:
                errors.append("infra_idempotency_claims.tenant_id column missing")
            elif str(tenant_row.is_nullable) != "NO" or tenant_row.column_default is not None:
                errors.append(
                    "infra_idempotency_claims.tenant_id must be NOT NULL without a persistent server default"
                )

            constraint_names = {
                str(row.conname)
                for row in conn.execute(
                    text(
                        """
                        SELECT conname
                        FROM pg_constraint
                        WHERE connamespace = 'public'::regnamespace
                        """
                    )
                ).all()
            }
            missing_constraints = REQUIRED_CONSTRAINTS - constraint_names
            forbidden_constraints = FORBIDDEN_CONSTRAINTS & constraint_names
            if missing_constraints:
                errors.append(f"missing schema constraints: {sorted(missing_constraints)!r}")
            if forbidden_constraints:
                errors.append(f"forbidden legacy constraints still present: {sorted(forbidden_constraints)!r}")

            index_names = {
                str(row.indexname)
                for row in conn.execute(
                    text(
                        """
                        SELECT indexname
                        FROM pg_indexes
                        WHERE schemaname = 'public'
                        """
                    )
                ).all()
            }
            missing_indexes = REQUIRED_INDEXES - index_names
            if missing_indexes:
                errors.append(f"missing schema indexes: {sorted(missing_indexes)!r}")
    finally:
        engine.dispose()
    return errors


def verify_phase04_alembic_migration() -> list[str]:
    errors: list[str] = []
    database = f"zuno_phase04_alembic_{uuid4().hex}"
    database_url = DB_URL_TEMPLATE.format(database=database)
    _create_database(database)
    try:
        with tempfile.TemporaryDirectory(prefix="zuno-phase04-alembic-") as tmp:
            config_path = Path(tmp) / "config.yaml"
            _write_config(config_path, database_url)

            upgrade = _run_alembic(config_path, "upgrade", "head")
            if upgrade.returncode != 0:
                errors.append("alembic upgrade head failed: " + (upgrade.stderr or upgrade.stdout).strip())
                return errors
            if _current_revision(database_url) != EXPECTED_HEAD_REVISION:
                errors.append(f"unexpected head revision after upgrade: {_current_revision(database_url)!r}")
            missing_tables = REQUIRED_INFRA_TABLES - _table_names(database_url)
            if missing_tables:
                errors.append(f"missing infra tables after upgrade: {sorted(missing_tables)!r}")
            errors.extend(_schema_drift_errors(database_url))

            repeated = _run_alembic(config_path, "upgrade", "head")
            if repeated.returncode != 0:
                errors.append("repeated alembic upgrade head failed: " + (repeated.stderr or repeated.stdout).strip())
            if _current_revision(database_url) != EXPECTED_HEAD_REVISION:
                errors.append(f"unexpected head revision after repeated upgrade: {_current_revision(database_url)!r}")

            downgrade = _run_alembic(config_path, "downgrade", "base")
            if downgrade.returncode != 0:
                errors.append("alembic downgrade base failed: " + (downgrade.stderr or downgrade.stdout).strip())
            remaining_after_downgrade = REQUIRED_INFRA_TABLES & _table_names(database_url)
            if remaining_after_downgrade:
                errors.append(f"infra tables remained after downgrade base: {sorted(remaining_after_downgrade)!r}")

            reupgrade = _run_alembic(config_path, "upgrade", "head")
            if reupgrade.returncode != 0:
                errors.append("alembic re-upgrade head failed: " + (reupgrade.stderr or reupgrade.stdout).strip())
            if _current_revision(database_url) != EXPECTED_HEAD_REVISION:
                errors.append(f"unexpected head revision after re-upgrade: {_current_revision(database_url)!r}")
            missing_after_reupgrade = REQUIRED_INFRA_TABLES - _table_names(database_url)
            if missing_after_reupgrade:
                errors.append(f"missing infra tables after re-upgrade: {sorted(missing_after_reupgrade)!r}")
    finally:
        _drop_database(database)
    return errors


def main() -> int:
    errors = verify_phase04_alembic_migration()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 Alembic migration verification failed.")
        return 1
    print("PHASE04 Alembic migration verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
