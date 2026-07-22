from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from uuid import uuid4

from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text

from zuno.platform.database.metadata import metadata
from zuno.platform.database.schema_registry import (
    DOMAIN_TABLE_OWNERS,
    INFRASTRUCTURE_TABLES,
    ONLINE_SCHEMA_OBJECTS,
    REVISION_OWNERS,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
ADMIN_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
DB_URL_TEMPLATE = "postgresql+psycopg://postgres:postgres@localhost:5432/{database}"
REQUIRED_INFRA_TABLES = INFRASTRUCTURE_TABLES
REQUIRED_DOMAIN_TABLES = set(DOMAIN_TABLE_OWNERS)
EXPECTED_HEAD_REVISION = "20260718_15"
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
    "infra_worker_leases": {
        "resource_id",
        "owner_id",
        "lease_id",
        "epoch",
        "expires_at",
        "updated_at",
    },
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
    "infra_capacity_admissions": {
        "resource_id",
        "capacity_limit",
        "drained",
        "generation",
        "updated_by",
        "updated_at",
    },
    "infra_capacity_reservations": {
        "reservation_id",
        "resource_id",
        "owner_id",
        "amount",
        "generation",
        "status",
        "expires_at",
        "released_at",
        "created_at",
    },
    "infra_audit_channels": {
        "channel_id",
        "capacity_limit",
        "fail_mode",
        "drained",
        "generation",
        "updated_by",
        "updated_at",
    },
    "infra_mandatory_audit_events": {
        "audit_id",
        "channel_id",
        "effect_id",
        "owner_id",
        "payload_hash",
        "payload",
        "status",
        "generation",
        "created_at",
        "effect_observed_at",
    },
    "infra_cutover_targets": {
        "target_id",
        "active_snapshot_id",
        "active_generation",
        "updated_by",
        "updated_at",
    },
    "infra_cutover_snapshots": {
        "snapshot_id",
        "target_id",
        "owner_id",
        "payload_hash",
        "payload",
        "status",
        "activated_generation",
        "created_at",
        "activated_at",
        "superseded_at",
        "retired_at",
        "retired_by",
    },
    "infra_active_snapshot_refs": {
        "ref_id",
        "target_id",
        "snapshot_id",
        "generation",
        "owner_id",
        "status",
        "created_at",
        "released_at",
    },
    "infra_recovery_watermarks": {
        "component_id",
        "service_kind",
        "authority",
        "watermark",
        "payload_hash",
        "payload",
        "owner_id",
        "updated_at",
    },
    "infra_recovery_sets": {
        "recovery_set_id",
        "recovery_point",
        "status",
        "verification_hash",
        "owner_id",
        "created_at",
    },
    "infra_recovery_set_members": {
        "recovery_set_id",
        "component_id",
        "service_kind",
        "authority",
        "watermark",
        "payload_hash",
    },
    "infra_secret_versions": {
        "secret_ref",
        "version",
        "tenant_id",
        "kms_key_ref",
        "config_hash",
        "payload_hash",
        "payload",
        "status",
        "owner_id",
        "created_at",
        "activated_at",
        "retired_at",
    },
    "infra_secret_rotation_heads": {
        "secret_ref",
        "tenant_id",
        "active_version",
        "previous_version",
        "generation",
        "status",
        "owner_id",
        "updated_at",
    },
    "infra_secret_leases": {
        "lease_id",
        "secret_ref",
        "tenant_id",
        "version",
        "generation",
        "owner_id",
        "payload_hash",
        "issued_at",
        "expires_at",
    },
    "infra_cross_tenant_hits": {
        "hit_id",
        "service_kind",
        "resource_ref",
        "expected_tenant_id",
        "observed_tenant_id",
        "action",
        "status",
        "payload_hash",
        "payload",
        "owner_id",
        "created_at",
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
    "ck_infra_migration_backfills_owner_nonempty",
    "fk_infra_capacity_reservations_admission",
    "ck_infra_capacity_admissions_limit_positive",
    "ck_infra_capacity_admissions_generation_positive",
    "ck_infra_capacity_reservations_amount_positive",
    "ck_infra_capacity_reservations_generation_positive",
    "ck_infra_capacity_reservations_status",
    "fk_infra_mandatory_audit_events_channel",
    "uq_infra_mandatory_audit_events_effect",
    "ck_infra_audit_channels_limit_positive",
    "ck_infra_audit_channels_generation_positive",
    "ck_infra_audit_channels_fail_mode",
    "ck_infra_mandatory_audit_events_generation_positive",
    "ck_infra_mandatory_audit_events_status",
    "ck_infra_mandatory_audit_events_payload_hash",
    "fk_infra_cutover_snapshots_target",
    "fk_infra_cutover_targets_active_snapshot",
    "fk_infra_active_snapshot_refs_target",
    "fk_infra_active_snapshot_refs_snapshot",
    "ck_infra_cutover_targets_generation_positive",
    "ck_infra_cutover_snapshots_payload_hash",
    "ck_infra_cutover_snapshots_status",
    "ck_infra_cutover_snapshots_generation_positive",
    "ck_infra_active_snapshot_refs_generation_positive",
    "ck_infra_active_snapshot_refs_status",
    "fk_infra_recovery_set_members_set",
    "fk_infra_recovery_set_members_watermark",
    "pk_infra_recovery_set_members",
    "ck_infra_recovery_watermarks_authority",
    "ck_infra_recovery_watermarks_payload_hash",
    "ck_infra_recovery_sets_status",
    "ck_infra_recovery_sets_verification_hash",
    "ck_infra_recovery_set_members_authority",
    "ck_infra_recovery_set_members_payload_hash",
    "pk_infra_secret_versions",
    "fk_infra_secret_rotation_heads_active",
    "fk_infra_secret_rotation_heads_previous",
    "fk_infra_secret_leases_version",
    "ck_infra_secret_versions_version",
    "ck_infra_secret_versions_config_hash",
    "ck_infra_secret_versions_payload_hash",
    "ck_infra_secret_versions_status",
    "ck_infra_secret_rotation_heads_generation",
    "ck_infra_secret_rotation_heads_active_version",
    "ck_infra_secret_rotation_heads_previous_version",
    "ck_infra_secret_rotation_heads_status",
    "ck_infra_secret_leases_version",
    "ck_infra_secret_leases_generation",
    "ck_infra_secret_leases_payload_hash",
    "ck_infra_cross_tenant_hits_mismatch",
    "ck_infra_cross_tenant_hits_action",
    "ck_infra_cross_tenant_hits_status",
    "ck_infra_cross_tenant_hits_payload_hash",
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
    "ix_infra_capacity_reservations_resource_active",
    "ix_infra_mandatory_audit_events_channel_status",
    "ix_infra_active_snapshot_refs_snapshot_active",
    "ix_infra_cutover_snapshots_target_status",
    "ix_infra_recovery_watermarks_kind_watermark",
    "ix_infra_recovery_sets_recovery_point",
    "ix_infra_secret_versions_tenant_status",
    "ix_infra_secret_leases_secret_generation",
    "ix_infra_cross_tenant_hits_resource",
    "ix_workspace_session_user_update_time",
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
                text("""
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = :database AND pid <> pg_backend_pid()
                    """),
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
            return conn.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one_or_none()
    finally:
        engine.dispose()


def _table_names(database_url: str) -> set[str]:
    engine = create_engine(database_url, future=True)
    try:
        with engine.connect() as conn:
            rows = conn.execute(text("""
                    SELECT tablename
                    FROM pg_tables
                    WHERE schemaname = 'public'
                    """)).all()
            return {str(row.tablename) for row in rows}
    finally:
        engine.dispose()


def _schema_drift_errors(database_url: str) -> list[str]:
    engine = create_engine(database_url, future=True)
    errors: list[str] = []
    try:
        with engine.connect() as conn:
            column_rows = conn.execute(text("""
                    SELECT table_name, column_name
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                    """)).all()
            columns_by_table: dict[str, set[str]] = {}
            for row in column_rows:
                columns_by_table.setdefault(str(row.table_name), set()).add(
                    str(row.column_name)
                )
            for table_name, expected_columns in REQUIRED_TABLE_COLUMNS.items():
                actual_columns = columns_by_table.get(table_name, set())
                missing_columns = expected_columns - actual_columns
                extra_columns = actual_columns - expected_columns
                if missing_columns:
                    errors.append(
                        f"{table_name} missing columns: {sorted(missing_columns)!r}"
                    )
                if extra_columns:
                    errors.append(
                        f"{table_name} unexpected columns: {sorted(extra_columns)!r}"
                    )

            tenant_row = conn.execute(text("""
                    SELECT is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND table_name = 'infra_idempotency_claims'
                      AND column_name = 'tenant_id'
                    """)).first()
            if tenant_row is None:
                errors.append("infra_idempotency_claims.tenant_id column missing")
            elif (
                str(tenant_row.is_nullable) != "NO"
                or tenant_row.column_default is not None
            ):
                errors.append(
                    "infra_idempotency_claims.tenant_id must be NOT NULL without a persistent server default"
                )

            constraint_names = {str(row.conname) for row in conn.execute(text("""
                        SELECT conname
                        FROM pg_constraint
                        WHERE connamespace = 'public'::regnamespace
                        """)).all()}
            missing_constraints = REQUIRED_CONSTRAINTS - constraint_names
            forbidden_constraints = FORBIDDEN_CONSTRAINTS & constraint_names
            if missing_constraints:
                errors.append(
                    f"missing schema constraints: {sorted(missing_constraints)!r}"
                )
            if forbidden_constraints:
                errors.append(
                    f"forbidden legacy constraints still present: {sorted(forbidden_constraints)!r}"
                )

            index_names = {str(row.indexname) for row in conn.execute(text("""
                        SELECT indexname
                        FROM pg_indexes
                        WHERE schemaname = 'public'
                        """)).all()}
            missing_indexes = REQUIRED_INDEXES - index_names
            if missing_indexes:
                errors.append(f"missing schema indexes: {sorted(missing_indexes)!r}")
    finally:
        engine.dispose()
    return errors


def _domain_schema_drift_errors(database_url: str) -> list[str]:
    def include_object(obj, name, type_, reflected, compare_to):
        if type_ == "table":
            return name in REQUIRED_DOMAIN_TABLES
        table = getattr(obj, "table", None)
        table_name = getattr(table, "name", None)
        if table_name not in REQUIRED_DOMAIN_TABLES:
            return False
        if type_ in {"index", "unique_constraint", "check_constraint"}:
            return name not in ONLINE_SCHEMA_OBJECTS
        return True

    engine = create_engine(database_url, future=True)
    try:
        with engine.connect() as connection:
            context = MigrationContext.configure(
                connection,
                opts={
                    "compare_type": True,
                    "compare_server_default": True,
                    "include_object": include_object,
                },
            )
            differences = compare_metadata(context, metadata)
    finally:
        engine.dispose()
    return [f"domain schema drift: {difference!r}" for difference in differences]


def _revision_chain_errors() -> list[str]:
    errors: list[str] = []
    config = Config(str(REPO_ROOT / "infra" / "db" / "alembic.ini"))
    script = ScriptDirectory.from_config(config)
    if script.get_revision(EXPECTED_HEAD_REVISION) is None:
        errors.append(f"PHASE04 expected revision is missing: {EXPECTED_HEAD_REVISION}")
        return errors
    revisions = list(script.walk_revisions(base="base", head=EXPECTED_HEAD_REVISION))
    revision_ids = {str(item.revision) for item in revisions}
    expected_phase04_revisions = {
        revision
        for revision, owner in REVISION_OWNERS.items()
        if owner in {"Cross-module frozen baseline", "Infrastructure", "Product Surface"}
    }
    if revision_ids != expected_phase04_revisions:
        errors.append(
            "revision ownership registry mismatch: "
            f"chain={sorted(revision_ids)!r}, registry={sorted(expected_phase04_revisions)!r}"
        )
    if set(metadata.tables) != REQUIRED_DOMAIN_TABLES:
        errors.append(
            "domain table ownership registry does not match SQLModel metadata"
        )
    for item in revisions:
        source = Path(item.path).read_text(encoding="utf-8")
        if "create_all(" in source or "drop_all(" in source:
            errors.append(
                f"revision {item.revision} uses runtime metadata create_all/drop_all"
            )
        if item.branch_labels:
            errors.append(
                f"revision {item.revision} introduces an unsupported branch label"
            )
    return errors


def _online_schema_errors(database_url: str) -> list[str]:
    engine = create_engine(database_url, future=True)
    errors: list[str] = []
    try:
        with engine.connect() as connection:
            index_row = connection.execute(text("""
                    SELECT i.indisready, i.indisvalid
                    FROM pg_index i
                    JOIN pg_class c ON c.oid = i.indexrelid
                    WHERE c.relname = 'ix_workspace_session_user_update_time'
                    """)).first()
            if (
                index_row is None
                or not index_row.indisready
                or not index_row.indisvalid
            ):
                errors.append(
                    "concurrent workspace session index is missing or invalid"
                )
            constraint_row = connection.execute(text("""
                    SELECT convalidated
                    FROM pg_constraint
                    WHERE conname = 'ck_infra_migration_backfills_owner_nonempty'
                    """)).first()
            if constraint_row is None or not constraint_row.convalidated:
                errors.append(
                    "online backfill owner constraint is missing or not validated"
                )
    finally:
        engine.dispose()
    revision_09 = (
        REPO_ROOT
        / "infra"
        / "db"
        / "alembic"
        / "versions"
        / "20260717_09_workspace_session_online_index.py"
    ).read_text(encoding="utf-8")
    revision_10 = (
        REPO_ROOT
        / "infra"
        / "db"
        / "alembic"
        / "versions"
        / "20260717_10_backfill_owner_online_constraint.py"
    ).read_text(encoding="utf-8")
    if (
        "CREATE INDEX CONCURRENTLY" not in revision_09
        or "autocommit_block" not in revision_09
    ):
        errors.append(
            "workspace session index revision does not use concurrent autocommit DDL"
        )
    if "NOT VALID" not in revision_10 or "VALIDATE CONSTRAINT" not in revision_10:
        errors.append(
            "backfill owner constraint revision does not use add-then-validate DDL"
        )
    return errors


def verify_phase04_alembic_migration() -> list[str]:
    errors = _revision_chain_errors()
    database = f"zuno_phase04_alembic_{uuid4().hex}"
    database_url = DB_URL_TEMPLATE.format(database=database)
    _create_database(database)
    try:
        with tempfile.TemporaryDirectory(prefix="zuno-phase04-alembic-") as tmp:
            config_path = Path(tmp) / "config.yaml"
            _write_config(config_path, database_url)

            upgrade = _run_alembic(config_path, "upgrade", EXPECTED_HEAD_REVISION)
            if upgrade.returncode != 0:
                errors.append(
                    f"alembic upgrade {EXPECTED_HEAD_REVISION} failed: "
                    + (upgrade.stderr or upgrade.stdout).strip()
                )
                return errors
            if _current_revision(database_url) != EXPECTED_HEAD_REVISION:
                errors.append(
                    f"unexpected head revision after upgrade: {_current_revision(database_url)!r}"
                )
            missing_tables = REQUIRED_INFRA_TABLES - _table_names(database_url)
            if missing_tables:
                errors.append(
                    f"missing infra tables after upgrade: {sorted(missing_tables)!r}"
                )
            errors.extend(_schema_drift_errors(database_url))
            missing_domain_tables = REQUIRED_DOMAIN_TABLES - _table_names(database_url)
            if missing_domain_tables:
                errors.append(
                    f"missing domain tables after upgrade: {sorted(missing_domain_tables)!r}"
                )
            errors.extend(_domain_schema_drift_errors(database_url))
            errors.extend(_online_schema_errors(database_url))

            repeated = _run_alembic(config_path, "upgrade", EXPECTED_HEAD_REVISION)
            if repeated.returncode != 0:
                errors.append(
                    f"repeated alembic upgrade {EXPECTED_HEAD_REVISION} failed: "
                    + (repeated.stderr or repeated.stdout).strip()
                )
            if _current_revision(database_url) != EXPECTED_HEAD_REVISION:
                errors.append(
                    f"unexpected head revision after repeated upgrade: {_current_revision(database_url)!r}"
                )

            downgrade = _run_alembic(config_path, "downgrade", "base")
            if downgrade.returncode != 0:
                errors.append(
                    "alembic downgrade base failed: "
                    + (downgrade.stderr or downgrade.stdout).strip()
                )
            remaining_after_downgrade = (
                REQUIRED_INFRA_TABLES | REQUIRED_DOMAIN_TABLES
            ) & _table_names(database_url)
            if remaining_after_downgrade:
                errors.append(
                    f"managed tables remained after downgrade base: {sorted(remaining_after_downgrade)!r}"
                )

            reupgrade = _run_alembic(config_path, "upgrade", EXPECTED_HEAD_REVISION)
            if reupgrade.returncode != 0:
                errors.append(
                    f"alembic re-upgrade {EXPECTED_HEAD_REVISION} failed: "
                    + (reupgrade.stderr or reupgrade.stdout).strip()
                )
            if _current_revision(database_url) != EXPECTED_HEAD_REVISION:
                errors.append(
                    f"unexpected head revision after re-upgrade: {_current_revision(database_url)!r}"
                )
            missing_after_reupgrade = REQUIRED_INFRA_TABLES - _table_names(database_url)
            if missing_after_reupgrade:
                errors.append(
                    f"missing infra tables after re-upgrade: {sorted(missing_after_reupgrade)!r}"
                )
            missing_domain_after_reupgrade = REQUIRED_DOMAIN_TABLES - _table_names(
                database_url
            )
            if missing_domain_after_reupgrade:
                errors.append(
                    "missing domain tables after re-upgrade: "
                    f"{sorted(missing_domain_after_reupgrade)!r}"
                )
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
