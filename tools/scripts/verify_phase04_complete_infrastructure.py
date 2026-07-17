from __future__ import annotations

import re
import socket
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORK_PRODUCTS = REPO_ROOT / ".agent" / "programs" / "work-products"
PHASE04_READINESS = WORK_PRODUCTS / "phase04-readiness.yaml"
PHASE04_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-complete-infrastructure-blocker.md"
PARTIAL_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-postgres-foundation.md"
ALEMBIC_MIGRATION_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_alembic_migration.py"
ALEMBIC_MIGRATION_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-alembic-migration.md"
POSTGRES_RUNTIME_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_postgres_runtime.py"
POSTGRES_RUNTIME_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-postgres-runtime.md"
POSTGRES_DEADLOCK_RETRY_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_postgres_deadlock_retry.py"
POSTGRES_SERIALIZATION_RETRY_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_postgres_serialization_retry.py"
POSTGRES_POOL_EXHAUSTION_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_postgres_pool_exhaustion.py"
POSTGRES_CONNECTION_LOSS_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_postgres_connection_loss.py"
REAL_SERVICES_SMOKE = REPO_ROOT / "tools" / "scripts" / "verify_phase04_real_services_smoke.py"
RABBITMQ_TRANSPORT_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_rabbitmq_transport.py"
RABBITMQ_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-rabbitmq-transport.md"
RABBITMQ_BACKLOG_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_rabbitmq_backlog.py"
RABBITMQ_RETRY_EXHAUSTION_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_rabbitmq_retry_exhaustion.py"
OUTBOX_RABBITMQ_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_outbox_rabbitmq_publisher.py"
OUTBOX_RABBITMQ_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-outbox-rabbitmq-publisher.md"
RABBITMQ_RESTART_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_rabbitmq_broker_restart.py"
RABBITMQ_RESTART_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-rabbitmq-broker-restart.md"
MINIO_OBJECT_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_minio_object_store.py"
MINIO_OBJECT_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-minio-object-store.md"
MINIO_RESTART_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_minio_storage_restart.py"
BACKUP_RESTORE_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_backup_restore_replay.py"
BACKUP_RESTORE_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-backup-restore-replay.md"
IDEMPOTENCY_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_idempotency_claim.py"
IDEMPOTENCY_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-idempotency-claim.md"
IDEMPOTENCY_OWNER_CRASH_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_idempotency_owner_crash.py"
IDEMPOTENCY_TENANT_ISOLATION_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_idempotency_tenant_isolation.py"
LEASE_FENCING_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_lease_fencing.py"
LEASE_FENCING_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-lease-fencing.md"

REQUIRED_REAL_SERVICES = {
    "PostgreSQL": ("localhost", 5432),
    "RabbitMQ": ("localhost", 5672),
    "MinIO/S3": ("localhost", 9000),
}

REQUIRED_EVIDENCE_PHRASES = [
    "RabbitMQ publisher confirm",
    "RabbitMQ redelivery",
    "RabbitMQ DLQ",
    "MinIO/S3 object staging",
    "MinIO/S3 restore",
    "LangGraph PostgreSQL Checkpointer",
    "Backup/Restore/Replay",
    "PITR",
    "combined dependency fault",
]

REQUIRED_COMPLETION_PROOF_MARKERS = [
    "real_services_smoke: passed",
    "langgraph_postgres_checkpointer: proven",
    "backup_restore_replay: proven",
    "rabbitmq_fault_evidence: proven",
    "minio_restore_evidence: proven",
    "combined_dependency_fault: proven",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _tcp_open(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _load_verifier(path: Path, module_name: str, function_name: str):
    spec = spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load verifier: {path.relative_to(REPO_ROOT).as_posix()}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, function_name)


def _official_langgraph_postgres_checkpointer_available() -> bool:
    return (
        find_spec("langgraph.checkpoint.postgres") is not None
        or find_spec("langgraph_checkpoint_postgres") is not None
    )


def verify_phase04_complete_infrastructure() -> list[str]:
    errors: list[str] = []
    if not PHASE04_READINESS.exists():
        return ["missing PHASE04 readiness: .agent/programs/work-products/phase04-readiness.yaml"]

    readiness = _read(PHASE04_READINESS)
    for task_id in [f"P04-T{index:02d}" for index in range(1, 8)]:
        if re.search(rf"(?s){task_id}:\s*\n\s+state:\s+completed\b", readiness) is None:
            errors.append(f"{task_id} is not completed in phase04-readiness.yaml")
    if "coordinator_approval: approved" not in readiness:
        errors.append("PHASE04 coordinator approval is not approved")
    if "may_start_phase05_after_validation: true" not in readiness:
        errors.append("PHASE05 start gate remains closed")

    for label, (host, port) in REQUIRED_REAL_SERVICES.items():
        if not _tcp_open(host, port):
            errors.append(f"{label} real service is not reachable at {host}:{port}")

    if not REAL_SERVICES_SMOKE.exists():
        errors.append("missing PHASE04 real services smoke verifier")
    else:
        smoke_errors = _load_verifier(
            REAL_SERVICES_SMOKE,
            "verify_phase04_real_services_smoke",
            "verify_phase04_real_services_smoke",
        )()
        for smoke_error in smoke_errors:
            errors.append(f"PHASE04 real service smoke failed: {smoke_error}")

    if not ALEMBIC_MIGRATION_VERIFIER.exists():
        errors.append("missing PHASE04 Alembic migration verifier")
    else:
        alembic_errors = _load_verifier(
            ALEMBIC_MIGRATION_VERIFIER,
            "verify_phase04_alembic_migration",
            "verify_phase04_alembic_migration",
        )()
        for alembic_error in alembic_errors:
            errors.append(f"PHASE04 Alembic migration verification failed: {alembic_error}")

    if not ALEMBIC_MIGRATION_EVIDENCE.exists():
        errors.append("missing PHASE04 Alembic migration evidence")
    else:
        alembic_evidence = _read(ALEMBIC_MIGRATION_EVIDENCE)
        for phrase in [
            "temporary_database_upgrade_head: passed",
            "repeated_upgrade_head: passed",
            "downgrade_base: passed",
            "reupgrade_head: passed",
            "infra_table_roundtrip: passed",
            "schema_drift_detection: passed_infra_schema_subset",
            "不关闭 P04-T02",
        ]:
            if phrase not in alembic_evidence:
                errors.append(f"PHASE04 Alembic migration evidence missing phrase: {phrase}")

    if not POSTGRES_RUNTIME_VERIFIER.exists():
        errors.append("missing PHASE04 PostgreSQL runtime verifier")
    else:
        postgres_runtime_errors = _load_verifier(
            POSTGRES_RUNTIME_VERIFIER,
            "verify_phase04_postgres_runtime",
            "verify_phase04_postgres_runtime",
        )()
        for postgres_runtime_error in postgres_runtime_errors:
            errors.append(f"PHASE04 PostgreSQL runtime verification failed: {postgres_runtime_error}")

    if not POSTGRES_RUNTIME_EVIDENCE.exists():
        errors.append("missing PHASE04 PostgreSQL runtime evidence")
    else:
        postgres_runtime_evidence = _read(POSTGRES_RUNTIME_EVIDENCE)
        for phrase in [
            "readiness: passed",
            "tenant_context: passed",
            "tenant_context_no_leak: passed",
            "statement_timeout: passed",
            "lock_timeout: passed",
            "connection_loss_recovery: passed",
            "deadlock_retry_boundary: passed",
            "serialization_retry_boundary: passed",
            "pool_exhaustion: passed",
            "不关闭 P04-T01",
        ]:
            if phrase not in postgres_runtime_evidence:
                errors.append(f"PHASE04 PostgreSQL runtime evidence missing phrase: {phrase}")

    if not POSTGRES_DEADLOCK_RETRY_VERIFIER.exists():
        errors.append("missing PHASE04 PostgreSQL deadlock retry verifier")
    else:
        postgres_deadlock_errors = _load_verifier(
            POSTGRES_DEADLOCK_RETRY_VERIFIER,
            "verify_phase04_postgres_deadlock_retry",
            "verify_phase04_postgres_deadlock_retry",
        )()
        for postgres_deadlock_error in postgres_deadlock_errors:
            errors.append(f"PHASE04 PostgreSQL deadlock retry verification failed: {postgres_deadlock_error}")

    if not POSTGRES_SERIALIZATION_RETRY_VERIFIER.exists():
        errors.append("missing PHASE04 PostgreSQL serialization retry verifier")
    else:
        postgres_serialization_errors = _load_verifier(
            POSTGRES_SERIALIZATION_RETRY_VERIFIER,
            "verify_phase04_postgres_serialization_retry",
            "verify_phase04_postgres_serialization_retry",
        )()
        for postgres_serialization_error in postgres_serialization_errors:
            errors.append(
                f"PHASE04 PostgreSQL serialization retry verification failed: {postgres_serialization_error}"
            )

    if not POSTGRES_POOL_EXHAUSTION_VERIFIER.exists():
        errors.append("missing PHASE04 PostgreSQL pool exhaustion verifier")
    else:
        postgres_pool_errors = _load_verifier(
            POSTGRES_POOL_EXHAUSTION_VERIFIER,
            "verify_phase04_postgres_pool_exhaustion",
            "verify_phase04_postgres_pool_exhaustion",
        )()
        for postgres_pool_error in postgres_pool_errors:
            errors.append(f"PHASE04 PostgreSQL pool exhaustion verification failed: {postgres_pool_error}")

    if not POSTGRES_CONNECTION_LOSS_VERIFIER.exists():
        errors.append("missing PHASE04 PostgreSQL connection loss verifier")
    else:
        postgres_connection_loss_errors = _load_verifier(
            POSTGRES_CONNECTION_LOSS_VERIFIER,
            "verify_phase04_postgres_connection_loss",
            "verify_phase04_postgres_connection_loss",
        )()
        for postgres_connection_loss_error in postgres_connection_loss_errors:
            errors.append(
                f"PHASE04 PostgreSQL connection loss verification failed: {postgres_connection_loss_error}"
            )

    if not _official_langgraph_postgres_checkpointer_available():
        errors.append("official LangGraph PostgreSQL Checkpointer is not importable/proven")

    if not RABBITMQ_TRANSPORT_VERIFIER.exists():
        errors.append("missing PHASE04 RabbitMQ transport verifier")
    else:
        rabbit_errors = _load_verifier(
            RABBITMQ_TRANSPORT_VERIFIER,
            "verify_phase04_rabbitmq_transport",
            "verify_phase04_rabbitmq_transport",
        )()
        for rabbit_error in rabbit_errors:
            errors.append(f"PHASE04 RabbitMQ transport verification failed: {rabbit_error}")

    if not RABBITMQ_EVIDENCE.exists():
        errors.append("missing PHASE04 RabbitMQ transport evidence")
    else:
        rabbit_evidence = _read(RABBITMQ_EVIDENCE)
        for phrase in [
            "publisher_confirm: passed",
            "redelivery: passed",
            "dlq: passed",
            "dlq_replay: passed",
            "backlog_depth: passed",
            "retry_exhaustion: passed",
            "Queue ACK != Domain Success",
        ]:
            if phrase not in rabbit_evidence:
                errors.append(f"PHASE04 RabbitMQ transport evidence missing phrase: {phrase}")

    if not RABBITMQ_BACKLOG_VERIFIER.exists():
        errors.append("missing PHASE04 RabbitMQ backlog verifier")
    else:
        backlog_errors = _load_verifier(
            RABBITMQ_BACKLOG_VERIFIER,
            "verify_phase04_rabbitmq_backlog",
            "verify_phase04_rabbitmq_backlog",
        )()
        for backlog_error in backlog_errors:
            errors.append(f"PHASE04 RabbitMQ backlog verification failed: {backlog_error}")

    if not RABBITMQ_RETRY_EXHAUSTION_VERIFIER.exists():
        errors.append("missing PHASE04 RabbitMQ retry exhaustion verifier")
    else:
        retry_exhaustion_errors = _load_verifier(
            RABBITMQ_RETRY_EXHAUSTION_VERIFIER,
            "verify_phase04_rabbitmq_retry_exhaustion",
            "verify_phase04_rabbitmq_retry_exhaustion",
        )()
        for retry_exhaustion_error in retry_exhaustion_errors:
            errors.append(f"PHASE04 RabbitMQ retry exhaustion verification failed: {retry_exhaustion_error}")

    if not OUTBOX_RABBITMQ_VERIFIER.exists():
        errors.append("missing PHASE04 outbox RabbitMQ publisher verifier")
    else:
        outbox_errors = _load_verifier(
            OUTBOX_RABBITMQ_VERIFIER,
            "verify_phase04_outbox_rabbitmq_publisher",
            "verify_phase04_outbox_rabbitmq_publisher",
        )()
        for outbox_error in outbox_errors:
            errors.append(f"PHASE04 outbox RabbitMQ publisher verification failed: {outbox_error}")

    if not OUTBOX_RABBITMQ_EVIDENCE.exists():
        errors.append("missing PHASE04 outbox RabbitMQ publisher evidence")
    else:
        outbox_evidence = _read(OUTBOX_RABBITMQ_EVIDENCE)
        for phrase in [
            "outbox_claim: passed",
            "rabbitmq_publish_confirm: passed",
            "outbox_published_receipt: passed",
            "inbox_dedup_receipt: passed",
            "commit_after_publish_before_complete_crash: passed",
            "Queue ACK != Domain Success",
        ]:
            if phrase not in outbox_evidence:
                errors.append(f"PHASE04 outbox RabbitMQ publisher evidence missing phrase: {phrase}")

    if not RABBITMQ_RESTART_VERIFIER.exists():
        errors.append("missing PHASE04 RabbitMQ broker restart verifier")
    else:
        restart_errors = _load_verifier(
            RABBITMQ_RESTART_VERIFIER,
            "verify_phase04_rabbitmq_broker_restart",
            "verify_phase04_rabbitmq_broker_restart",
        )()
        for restart_error in restart_errors:
            errors.append(f"PHASE04 RabbitMQ broker restart verification failed: {restart_error}")

    if not RABBITMQ_RESTART_EVIDENCE.exists():
        errors.append("missing PHASE04 RabbitMQ broker restart evidence")
    else:
        restart_evidence = _read(RABBITMQ_RESTART_EVIDENCE)
        for phrase in [
            "broker_restart: passed",
            "durable_topology: passed",
            "persistent_message_survived_restart: passed",
            "Queue ACK != Domain Success",
        ]:
            if phrase not in restart_evidence:
                errors.append(f"PHASE04 RabbitMQ broker restart evidence missing phrase: {phrase}")

    if not MINIO_OBJECT_VERIFIER.exists():
        errors.append("missing PHASE04 MinIO object store verifier")
    else:
        minio_errors = _load_verifier(
            MINIO_OBJECT_VERIFIER,
            "verify_phase04_minio_object_store",
            "verify_phase04_minio_object_store",
        )()
        for minio_error in minio_errors:
            errors.append(f"PHASE04 MinIO object store verification failed: {minio_error}")

    if not MINIO_OBJECT_EVIDENCE.exists():
        errors.append("missing PHASE04 MinIO object store evidence")
    else:
        minio_evidence = _read(MINIO_OBJECT_EVIDENCE)
        for phrase in [
            "object_staging: passed",
            "visibility_lag: passed",
            "duplicate_upload: passed",
            "multipart_upload: passed",
            "partial_upload_abort: passed",
            "lost_response_reconciliation: passed",
            "duplicate_complete_reconciliation: passed",
            "orphan_reconciliation: passed",
            "hash_mismatch_fail_closed: passed",
            "missing_object: passed",
            "delete: passed",
            "restore: passed",
            "storage_restart: passed",
            "authorization_hook: passed_fail_closed",
            "permission_deny: passed",
            "retention: passed_governance",
            "legal_hold: passed",
            "lifecycle: passed_staging_expiration",
            "Object Commit != Domain Success",
        ]:
            if phrase not in minio_evidence:
                errors.append(f"PHASE04 MinIO object store evidence missing phrase: {phrase}")

    if not MINIO_RESTART_VERIFIER.exists():
        errors.append("missing PHASE04 MinIO storage restart verifier")
    else:
        minio_restart_errors = _load_verifier(
            MINIO_RESTART_VERIFIER,
            "verify_phase04_minio_storage_restart",
            "verify_phase04_minio_storage_restart",
        )()
        for minio_restart_error in minio_restart_errors:
            errors.append(f"PHASE04 MinIO storage restart verification failed: {minio_restart_error}")

    if not IDEMPOTENCY_VERIFIER.exists():
        errors.append("missing PHASE04 idempotency claim verifier")
    else:
        idempotency_errors = _load_verifier(
            IDEMPOTENCY_VERIFIER,
            "verify_phase04_idempotency_claim",
            "verify_phase04_idempotency_claim",
        )()
        for idempotency_error in idempotency_errors:
            errors.append(f"PHASE04 idempotency claim verification failed: {idempotency_error}")

    if not IDEMPOTENCY_EVIDENCE.exists():
        errors.append("missing PHASE04 idempotency claim evidence")
    else:
        idempotency_evidence = _read(IDEMPOTENCY_EVIDENCE)
        for phrase in [
            "same_key_same_hash: passed",
            "same_key_different_hash: passed",
            "renew: passed",
            "expiry: passed",
            "stale_generation_reject: passed",
            "result_replay: passed",
            "owner_crash: passed_process_exit_reclaim",
            "tenant_isolation: passed",
            "high_concurrency_single_winner: passed",
            "Idempotency Claim != Domain Success",
        ]:
            if phrase not in idempotency_evidence:
                errors.append(f"PHASE04 idempotency claim evidence missing phrase: {phrase}")

    if not IDEMPOTENCY_OWNER_CRASH_VERIFIER.exists():
        errors.append("missing PHASE04 idempotency owner crash verifier")
    else:
        owner_crash_errors = _load_verifier(
            IDEMPOTENCY_OWNER_CRASH_VERIFIER,
            "verify_phase04_idempotency_owner_crash",
            "verify_phase04_idempotency_owner_crash",
        )()
        for owner_crash_error in owner_crash_errors:
            errors.append(f"PHASE04 idempotency owner crash verification failed: {owner_crash_error}")

    if not IDEMPOTENCY_TENANT_ISOLATION_VERIFIER.exists():
        errors.append("missing PHASE04 idempotency tenant isolation verifier")
    else:
        tenant_isolation_errors = _load_verifier(
            IDEMPOTENCY_TENANT_ISOLATION_VERIFIER,
            "verify_phase04_idempotency_tenant_isolation",
            "verify_phase04_idempotency_tenant_isolation",
        )()
        for tenant_isolation_error in tenant_isolation_errors:
            errors.append(f"PHASE04 idempotency tenant isolation verification failed: {tenant_isolation_error}")

    if not BACKUP_RESTORE_VERIFIER.exists():
        errors.append("missing PHASE04 backup/restore/replay verifier")
    else:
        backup_errors = _load_verifier(
            BACKUP_RESTORE_VERIFIER,
            "verify_phase04_backup_restore_replay",
            "verify_phase04_backup_restore_replay",
        )()
        for backup_error in backup_errors:
            errors.append(f"PHASE04 backup/restore/replay verification failed: {backup_error}")

    if not BACKUP_RESTORE_EVIDENCE.exists():
        errors.append("missing PHASE04 backup/restore/replay evidence")
    else:
        backup_evidence = _read(BACKUP_RESTORE_EVIDENCE)
        for phrase in [
            "postgres_backup: passed",
            "postgres_restore: passed",
            "object_manifest_restore: passed",
            "checkpoint_table_restore: passed",
            "outbox_inbox_watermark: passed",
            "Backup/Restore/Replay subset != PHASE04 completion",
        ]:
            if phrase not in backup_evidence:
                errors.append(f"PHASE04 backup/restore/replay evidence missing phrase: {phrase}")

    if not LEASE_FENCING_VERIFIER.exists():
        errors.append("missing PHASE04 lease/fencing verifier")
    else:
        lease_errors = _load_verifier(
            LEASE_FENCING_VERIFIER,
            "verify_phase04_lease_fencing",
            "verify_phase04_lease_fencing",
        )()
        for lease_error in lease_errors:
            errors.append(f"PHASE04 lease/fencing verification failed: {lease_error}")

    if not LEASE_FENCING_EVIDENCE.exists():
        errors.append("missing PHASE04 lease/fencing evidence")
    else:
        lease_evidence = _read(LEASE_FENCING_EVIDENCE)
        for phrase in [
            "lease_acquire: passed",
            "heartbeat_renew: passed",
            "duplicate_worker_reject: passed",
            "expiry_transfer: passed",
            "cancel_transfer: passed",
            "late_fencing_token_reject: passed",
            "不能代表领域结果成功",
        ]:
            if phrase not in lease_evidence:
                errors.append(f"PHASE04 lease/fencing evidence missing phrase: {phrase}")

    if not PARTIAL_EVIDENCE.exists():
        errors.append("missing partial PHASE04 evidence: docs/evidence/phase04-postgres-foundation.md")
    else:
        partial = _read(PARTIAL_EVIDENCE)
        for phrase in ["partial_implementation_available", "phase_completion: `withdrawn`"]:
            if phrase not in partial:
                errors.append(f"partial PHASE04 evidence missing boundary phrase: {phrase}")

    if not PHASE04_EVIDENCE.exists():
        errors.append("missing PHASE04 complete infrastructure evidence/blocker file")
    else:
        evidence = _read(PHASE04_EVIDENCE)
        for phrase in REQUIRED_EVIDENCE_PHRASES:
            if phrase not in evidence:
                errors.append(f"PHASE04 evidence missing required real dependency proof: {phrase}")
        for marker in REQUIRED_COMPLETION_PROOF_MARKERS:
            if marker not in evidence:
                errors.append(f"PHASE04 evidence missing completion proof marker: {marker}")
        if "status: blocked" not in evidence and "coordinator_decision: approved" not in evidence:
            errors.append("PHASE04 evidence must explicitly record blocked status or approved closure")
    return errors


def main() -> int:
    errors = verify_phase04_complete_infrastructure()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 complete infrastructure verification failed.")
        return 1
    print("PHASE04 complete infrastructure verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
