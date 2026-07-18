from __future__ import annotations

import re
import socket
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORK_PRODUCTS = REPO_ROOT / ".agent" / "programs" / "work-products"
PHASE04_READINESS = WORK_PRODUCTS / "phase04-readiness.yaml"
PHASE04_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-complete-infrastructure-blocker.md"
)
PARTIAL_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-postgres-foundation.md"
ALEMBIC_MIGRATION_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_alembic_migration.py"
)
ALEMBIC_MIGRATION_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-alembic-migration.md"
)
EXISTING_DATABASE_UPGRADE_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_existing_database_upgrade.py"
)
MIGRATION_CONTROL_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_migration_control.py"
)
MIGRATION_CONTROL_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-migration-control.md"
)
MIGRATION_RUNBOOK = (
    REPO_ROOT / "docs" / "governance" / "postgresql-migration-runbook.md"
)
POSTGRES_RUNTIME_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_postgres_runtime.py"
)
POSTGRES_RUNTIME_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-postgres-runtime.md"
)
POSTGRES_SESSION_RUNTIME_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_postgres_session_runtime.py"
)
POSTGRES_SESSION_RUNTIME_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-postgres-session-runtime.md"
)
DOMAIN_UOW_ADOPTION_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_domain_uow_adoption.py"
)
POSTGRES_DEADLOCK_RETRY_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_postgres_deadlock_retry.py"
)
POSTGRES_SERIALIZATION_RETRY_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_postgres_serialization_retry.py"
)
POSTGRES_POOL_EXHAUSTION_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_postgres_pool_exhaustion.py"
)
POSTGRES_CONNECTION_LOSS_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_postgres_connection_loss.py"
)
REAL_SERVICES_SMOKE = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_real_services_smoke.py"
)
RABBITMQ_TRANSPORT_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_rabbitmq_transport.py"
)
RABBITMQ_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-rabbitmq-transport.md"
RABBITMQ_BACKLOG_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_rabbitmq_backlog.py"
)
RABBITMQ_RETRY_EXHAUSTION_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_rabbitmq_retry_exhaustion.py"
)
OUTBOX_RABBITMQ_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_outbox_rabbitmq_publisher.py"
)
OUTBOX_RABBITMQ_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-outbox-rabbitmq-publisher.md"
)
DOMAIN_EVENT_ADOPTION_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_domain_event_adoption.py"
)
DOMAIN_EVENT_ADOPTION_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-domain-event-adoption.md"
)
OUTBOX_DELIVERY_POLICY_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_outbox_delivery_policy.py"
)
OUTBOX_DELIVERY_POLICY_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-outbox-delivery-policy.md"
)
RABBITMQ_OUT_OF_ORDER_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_rabbitmq_out_of_order.py"
)
RABBITMQ_OUT_OF_ORDER_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-rabbitmq-out-of-order.md"
)
RABBITMQ_RESTART_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_rabbitmq_broker_restart.py"
)
RABBITMQ_RESTART_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-rabbitmq-broker-restart.md"
)
RABBITMQ_PARTITION_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_rabbitmq_network_partition.py"
)
RABBITMQ_PARTITION_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-rabbitmq-network-partition.md"
)
MINIO_OBJECT_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_minio_object_store.py"
)
MINIO_OBJECT_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-minio-object-store.md"
)
MINIO_RESTART_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_minio_storage_restart.py"
)
MINIO_MANIFEST_ADOPTION_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_minio_manifest_adoption.py"
)
BACKUP_RESTORE_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_backup_restore_replay.py"
)
BACKUP_RESTORE_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-backup-restore-replay.md"
)
COMBINED_SERVICE_FAULT_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_combined_service_fault.py"
)
COMBINED_SERVICE_FAULT_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-combined-service-fault.md"
)
OPERATOR_READINESS_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_operator_readiness.py"
)
OPERATOR_READINESS_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-operator-readiness.md"
)
OPERATOR_RUNBOOK = (
    REPO_ROOT / "docs" / "governance" / "infrastructure-operations-runbook.md"
)
CAPACITY_ADMISSION_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_capacity_admission.py"
)
CAPACITY_ADMISSION_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-capacity-admission.md"
)
MANDATORY_AUDIT_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_mandatory_audit.py"
)
MANDATORY_AUDIT_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-mandatory-audit.md"
)
CUTOVER_SNAPSHOT_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_cutover_snapshot.py"
)
CUTOVER_SNAPSHOT_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-cutover-snapshot.md"
)
RECOVERY_WATERMARK_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_recovery_watermark.py"
)
RECOVERY_WATERMARK_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-recovery-watermark.md"
)
DR_PROFILE_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_dr_profile.py"
DR_PROFILE_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-dr-profile.md"
DR_PROFILE = REPO_ROOT / "docs" / "governance" / "infrastructure-dr-profile.yaml"
CAPABILITY_PROFILE_VERIFIER = (
    REPO_ROOT
    / "tools"
    / "scripts"
    / "verify_phase04_infrastructure_capability_profile.py"
)
CAPABILITY_PROFILE_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-infrastructure-capability-profile.md"
)
BACKUP_SERVICE_BOUNDARY_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_backup_service_boundaries.py"
)
BACKUP_SERVICE_BOUNDARY_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-backup-service-boundaries.md"
)
INFRASTRUCTURE_DOCS_GOVERNANCE_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_infrastructure_docs_governance.py"
)
INFRASTRUCTURE_DOCS_GOVERNANCE_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-infrastructure-docs-governance.md"
)
DOMAIN_BOUNDARY_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_infrastructure_domain_boundary.py"
)
DOMAIN_BOUNDARY_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-infrastructure-domain-boundary.md"
)
TYPED_PORTS_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_infrastructure_typed_ports.py"
)
TYPED_PORTS_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-infrastructure-typed-ports.md"
)
TENANT_ISOLATION_PROFILE_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_tenant_isolation_profiles.py"
)
TENANT_ISOLATION_PROFILE_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-tenant-isolation-profiles.md"
)
TENANT_PHYSICAL_CONSTRAINTS_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_tenant_physical_constraints.py"
)
TENANT_PHYSICAL_CONSTRAINTS_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-tenant-physical-constraints.md"
)
UPGRADE_COMPATIBILITY_PROFILE_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_upgrade_compatibility_profiles.py"
)
UPGRADE_COMPATIBILITY_PROFILE_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-upgrade-compatibility-profiles.md"
)
ADAPTER_CONFORMANCE_PROFILE_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_adapter_conformance_profiles.py"
)
ADAPTER_CONFORMANCE_PROFILE_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-adapter-conformance-profiles.md"
)
RELEASE_PROVENANCE_MANIFEST_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_release_provenance_manifest.py"
)
RELEASE_PROVENANCE_MANIFEST_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-release-provenance-manifest.md"
)
REDIS_OPTIONAL_BOUNDARY_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_redis_optional_boundary.py"
)
REDIS_OPTIONAL_BOUNDARY_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-redis-optional-boundary.md"
)
DERIVED_INDEX_BOUNDARY_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_derived_index_boundary.py"
)
DERIVED_INDEX_BOUNDARY_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-derived-index-boundary.md"
)
CONTRACT_OWNERSHIP_BOUNDARY_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_contract_ownership_boundaries.py"
)
CONTRACT_OWNERSHIP_BOUNDARY_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-contract-ownership-boundaries.md"
)
REQUIREMENT_LEDGER_EVIDENCE_GATE_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_requirement_ledger_evidence_gate.py"
)
REQUIREMENT_LEDGER_EVIDENCE_GATE_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-requirement-ledger-evidence-gate.md"
)
IDEMPOTENCY_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_idempotency_claim.py"
)
IDEMPOTENCY_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-idempotency-claim.md"
IDEMPOTENCY_OWNER_CRASH_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_idempotency_owner_crash.py"
)
IDEMPOTENCY_TENANT_ISOLATION_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_idempotency_tenant_isolation.py"
)
IDEMPOTENCY_SUPERVISION_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_idempotency_supervision.py"
)
LEASE_FENCING_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_lease_fencing.py"
)
LEASE_FENCING_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-lease-fencing.md"
LEASE_COORDINATION_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_lease_worker_coordination.py"
)
RECONCILER_SUPERVISION_BOUNDARY_VERIFIER = (
    REPO_ROOT
    / "tools"
    / "scripts"
    / "verify_phase04_reconciler_supervision_boundary.py"
)
RECONCILER_SUPERVISION_BOUNDARY_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-reconciler-supervision-boundary.md"
)
CHECKPOINT_BOUNDARY_VERSION_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_checkpoint_boundary_version.py"
)
CHECKPOINT_BOUNDARY_VERSION_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-checkpoint-boundary-version.md"
)

REQUIRED_REAL_SERVICES = {
    "PostgreSQL": ("localhost", 5432),
    "RabbitMQ": ("localhost", 5672),
    "MinIO/S3": ("localhost", 9000),
}

REQUIRED_EVIDENCE_PHRASES = [
    "RabbitMQ publisher confirm",
    "RabbitMQ redelivery",
    "RabbitMQ DLQ",
    "RabbitMQ network partition",
    "MinIO/S3 object staging",
    "MinIO/S3 restore",
    "Operator readiness",
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
        raise RuntimeError(
            f"cannot load verifier: {path.relative_to(REPO_ROOT).as_posix()}"
        )
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
        return [
            "missing PHASE04 readiness: .agent/programs/work-products/phase04-readiness.yaml"
        ]

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
            errors.append(
                f"PHASE04 Alembic migration verification failed: {alembic_error}"
            )

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
            "single_revision_chain: passed",
            "frozen_explicit_baseline: passed",
            "module_ownership_registry: passed",
            "schema_drift_detection: passed_full_domain_and_infra",
            "existing_database_upgrade: passed",
            "online_index_concurrently: passed",
            "online_constraint_validation: passed",
            "data_backfill_framework: passed",
            "online_migration_lock: passed",
            "forward_fix_lineage: passed",
            "p04_t02_completion: proven",
        ]:
            if phrase not in alembic_evidence:
                errors.append(
                    f"PHASE04 Alembic migration evidence missing phrase: {phrase}"
                )

    if not EXISTING_DATABASE_UPGRADE_VERIFIER.exists():
        errors.append("missing PHASE04 existing database upgrade verifier")
    else:
        existing_database_errors = _load_verifier(
            EXISTING_DATABASE_UPGRADE_VERIFIER,
            "verify_phase04_existing_database_upgrade",
            "verify_phase04_existing_database_upgrade",
        )()
        for existing_database_error in existing_database_errors:
            errors.append(
                "PHASE04 existing database upgrade verification failed: "
                f"{existing_database_error}"
            )

    if not MIGRATION_RUNBOOK.exists():
        errors.append("missing PostgreSQL migration runbook")
    else:
        migration_runbook = _read(MIGRATION_RUNBOOK)
        for phrase in [
            "Alembic revision 是服务器产品 Schema 的唯一变更入口",
            "发现 drift 时禁止 stamp",
            "CREATE INDEX CONCURRENTLY",
            "NOT VALID",
            "默认 forward-fix",
        ]:
            if phrase not in migration_runbook:
                errors.append(f"PostgreSQL migration runbook missing phrase: {phrase}")

    if not MIGRATION_CONTROL_VERIFIER.exists():
        errors.append("missing PHASE04 migration control verifier")
    else:
        migration_control_errors = _load_verifier(
            MIGRATION_CONTROL_VERIFIER,
            "verify_phase04_migration_control",
            "verify_phase04_migration_control",
        )()
        for migration_control_error in migration_control_errors:
            errors.append(
                f"PHASE04 migration control verification failed: {migration_control_error}"
            )

    if not MIGRATION_CONTROL_EVIDENCE.exists():
        errors.append("missing PHASE04 migration control evidence")
    else:
        migration_control_evidence = _read(MIGRATION_CONTROL_EVIDENCE)
        for phrase in [
            "migration_advisory_lock: passed",
            "parallel_deploy_fail_closed: passed",
            "lock_release_recovery: passed",
            "phase02_cutover_input_adoption: passed",
            "durable_backfill_ledger: passed",
            "chunk_idempotency: passed",
            "chunk_hash_conflict: passed_fail_closed",
            "pause_restart_resume: passed",
            "stale_generation_reject: passed",
            "forward_fix_lineage: passed",
            "migration_control_completion_input: proven",
        ]:
            if phrase not in migration_control_evidence:
                errors.append(
                    f"PHASE04 migration control evidence missing phrase: {phrase}"
                )

    if not POSTGRES_RUNTIME_VERIFIER.exists():
        errors.append("missing PHASE04 PostgreSQL runtime verifier")
    else:
        postgres_runtime_errors = _load_verifier(
            POSTGRES_RUNTIME_VERIFIER,
            "verify_phase04_postgres_runtime",
            "verify_phase04_postgres_runtime",
        )()
        for postgres_runtime_error in postgres_runtime_errors:
            errors.append(
                f"PHASE04 PostgreSQL runtime verification failed: {postgres_runtime_error}"
            )

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
                errors.append(
                    f"PHASE04 PostgreSQL runtime evidence missing phrase: {phrase}"
                )

    if not POSTGRES_SESSION_RUNTIME_VERIFIER.exists():
        errors.append("missing PHASE04 PostgreSQL session runtime verifier")
    else:
        session_runtime_errors = _load_verifier(
            POSTGRES_SESSION_RUNTIME_VERIFIER,
            "verify_phase04_postgres_session_runtime",
            "verify_phase04_postgres_session_runtime",
        )()
        for session_runtime_error in session_runtime_errors:
            errors.append(
                f"PHASE04 PostgreSQL session runtime verification failed: {session_runtime_error}"
            )

    if not POSTGRES_SESSION_RUNTIME_EVIDENCE.exists():
        errors.append("missing PHASE04 PostgreSQL session runtime evidence")
    else:
        session_runtime_evidence = _read(POSTGRES_SESSION_RUNTIME_EVIDENCE)
        for phrase in [
            "sync_session_factory: passed",
            "async_session_factory: passed",
            "explicit_transaction_scope: passed",
            "commit_rollback: passed",
            "nested_misuse_reject: passed",
            "failed_entry_connection_cleanup: passed",
            "tenant_concurrency_isolation: passed",
            "tenant_context_no_leak: passed",
            "read_only_transaction: passed",
            "transaction_isolation: passed",
            "async_statement_timeout: passed",
            "async_cancellation_recovery: passed",
            "async_connection_loss_recovery: passed",
            "connection_rotation: passed",
            "pool_health_metrics: passed",
            "default_runtime_owner: passed",
            "dao_uow_adoption: passed",
            "cross_repository_rollback: passed",
            "uow_owned_commit: passed",
            "async_task_isolation: passed",
            "p04_t01_completion: proven",
        ]:
            if phrase not in session_runtime_evidence:
                errors.append(
                    f"PHASE04 PostgreSQL session runtime evidence missing phrase: {phrase}"
                )

    if not DOMAIN_UOW_ADOPTION_VERIFIER.exists():
        errors.append("missing PHASE04 Domain UoW adoption verifier")
    else:
        domain_uow_errors = _load_verifier(
            DOMAIN_UOW_ADOPTION_VERIFIER,
            "verify_phase04_domain_uow_adoption",
            "verify_phase04_domain_uow_adoption",
        )()
        for domain_uow_error in domain_uow_errors:
            errors.append(
                f"PHASE04 Domain UoW adoption verification failed: {domain_uow_error}"
            )

    if not POSTGRES_DEADLOCK_RETRY_VERIFIER.exists():
        errors.append("missing PHASE04 PostgreSQL deadlock retry verifier")
    else:
        postgres_deadlock_errors = _load_verifier(
            POSTGRES_DEADLOCK_RETRY_VERIFIER,
            "verify_phase04_postgres_deadlock_retry",
            "verify_phase04_postgres_deadlock_retry",
        )()
        for postgres_deadlock_error in postgres_deadlock_errors:
            errors.append(
                f"PHASE04 PostgreSQL deadlock retry verification failed: {postgres_deadlock_error}"
            )

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
            errors.append(
                f"PHASE04 PostgreSQL pool exhaustion verification failed: {postgres_pool_error}"
            )

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
        errors.append(
            "official LangGraph PostgreSQL Checkpointer is not importable/proven"
        )

    if not RABBITMQ_TRANSPORT_VERIFIER.exists():
        errors.append("missing PHASE04 RabbitMQ transport verifier")
    else:
        rabbit_errors = _load_verifier(
            RABBITMQ_TRANSPORT_VERIFIER,
            "verify_phase04_rabbitmq_transport",
            "verify_phase04_rabbitmq_transport",
        )()
        for rabbit_error in rabbit_errors:
            errors.append(
                f"PHASE04 RabbitMQ transport verification failed: {rabbit_error}"
            )

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
                errors.append(
                    f"PHASE04 RabbitMQ transport evidence missing phrase: {phrase}"
                )

    if not RABBITMQ_BACKLOG_VERIFIER.exists():
        errors.append("missing PHASE04 RabbitMQ backlog verifier")
    else:
        backlog_errors = _load_verifier(
            RABBITMQ_BACKLOG_VERIFIER,
            "verify_phase04_rabbitmq_backlog",
            "verify_phase04_rabbitmq_backlog",
        )()
        for backlog_error in backlog_errors:
            errors.append(
                f"PHASE04 RabbitMQ backlog verification failed: {backlog_error}"
            )

    if not RABBITMQ_RETRY_EXHAUSTION_VERIFIER.exists():
        errors.append("missing PHASE04 RabbitMQ retry exhaustion verifier")
    else:
        retry_exhaustion_errors = _load_verifier(
            RABBITMQ_RETRY_EXHAUSTION_VERIFIER,
            "verify_phase04_rabbitmq_retry_exhaustion",
            "verify_phase04_rabbitmq_retry_exhaustion",
        )()
        for retry_exhaustion_error in retry_exhaustion_errors:
            errors.append(
                f"PHASE04 RabbitMQ retry exhaustion verification failed: {retry_exhaustion_error}"
            )

    if not OUTBOX_RABBITMQ_VERIFIER.exists():
        errors.append("missing PHASE04 outbox RabbitMQ publisher verifier")
    else:
        outbox_errors = _load_verifier(
            OUTBOX_RABBITMQ_VERIFIER,
            "verify_phase04_outbox_rabbitmq_publisher",
            "verify_phase04_outbox_rabbitmq_publisher",
        )()
        for outbox_error in outbox_errors:
            errors.append(
                f"PHASE04 outbox RabbitMQ publisher verification failed: {outbox_error}"
            )

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
            "confirm_unknown_reclaim_republish: passed",
            "consumer_crash_redelivery: passed",
            "inbox_first_seen_dedup: passed",
            "Queue ACK != Domain Success",
        ]:
            if phrase not in outbox_evidence:
                errors.append(
                    f"PHASE04 outbox RabbitMQ publisher evidence missing phrase: {phrase}"
                )

    if not DOMAIN_EVENT_ADOPTION_VERIFIER.exists():
        errors.append("missing PHASE04 domain event adoption verifier")
    else:
        domain_event_errors = _load_verifier(
            DOMAIN_EVENT_ADOPTION_VERIFIER,
            "verify_phase04_domain_event_adoption",
            "verify_phase04_domain_event_adoption",
        )()
        for domain_event_error in domain_event_errors:
            errors.append(
                f"PHASE04 domain event adoption verification failed: {domain_event_error}"
            )

    if not DOMAIN_EVENT_ADOPTION_EVIDENCE.exists():
        errors.append("missing PHASE04 domain event adoption evidence")
    else:
        domain_event_evidence = _read(DOMAIN_EVENT_ADOPTION_EVIDENCE)
        for phrase in [
            "domain_write_outbox_atomic: passed",
            "producer_precommit_crash_rollback: passed",
            "rabbitmq_consumer_redelivery: passed",
            "inbox_domain_write_atomic: passed",
            "consumer_precommit_crash_rollback: passed",
            "same_hash_duplicate_no_domain_reexecution: passed",
            "different_hash_quarantine: passed",
            "queue_ack_after_domain_commit: passed",
            "unknown_message_version_fail_closed: passed",
            "p04_t03_completion: proven",
        ]:
            if phrase not in domain_event_evidence:
                errors.append(
                    f"PHASE04 domain event adoption evidence missing phrase: {phrase}"
                )

    if not OUTBOX_DELIVERY_POLICY_VERIFIER.exists():
        errors.append("missing PHASE04 outbox delivery policy verifier")
    else:
        delivery_policy_errors = _load_verifier(
            OUTBOX_DELIVERY_POLICY_VERIFIER,
            "verify_phase04_outbox_delivery_policy",
            "verify_phase04_outbox_delivery_policy",
        )()
        for delivery_policy_error in delivery_policy_errors:
            errors.append(
                f"PHASE04 outbox delivery policy verification failed: {delivery_policy_error}"
            )

    if not OUTBOX_DELIVERY_POLICY_EVIDENCE.exists():
        errors.append("missing PHASE04 outbox delivery policy evidence")
    else:
        delivery_policy_evidence = _read(OUTBOX_DELIVERY_POLICY_EVIDENCE)
        for phrase in [
            "durable_backoff: passed",
            "retry_exhaustion_dead_letter: passed",
            "manual_replay_audit: passed",
            "broker_outage_recovery: passed",
            "outbox_backlog_visibility: passed",
            "delivery_attempt_headers: passed",
            "Queue ACK != Domain Success",
        ]:
            if phrase not in delivery_policy_evidence:
                errors.append(
                    f"PHASE04 outbox delivery policy evidence missing phrase: {phrase}"
                )

    if not RABBITMQ_OUT_OF_ORDER_VERIFIER.exists():
        errors.append("missing PHASE04 RabbitMQ out-of-order verifier")
    else:
        ordering_errors = _load_verifier(
            RABBITMQ_OUT_OF_ORDER_VERIFIER,
            "verify_phase04_rabbitmq_out_of_order",
            "verify_phase04_rabbitmq_out_of_order",
        )()
        for ordering_error in ordering_errors:
            errors.append(
                f"PHASE04 RabbitMQ out-of-order verification failed: {ordering_error}"
            )

    if not RABBITMQ_OUT_OF_ORDER_EVIDENCE.exists():
        errors.append("missing PHASE04 RabbitMQ out-of-order evidence")
    else:
        ordering_evidence = _read(RABBITMQ_OUT_OF_ORDER_EVIDENCE)
        for phrase in [
            "ordering_metadata_headers: passed",
            "out_of_order_buffered: passed",
            "delivery_watermark: passed",
            "restart_reconciliation: passed",
            "contiguous_release: passed",
            "duplicate_sequence_delivery: passed",
            "tenant_ordering_isolation: passed",
            "Queue ACK != Domain Success",
        ]:
            if phrase not in ordering_evidence:
                errors.append(
                    f"PHASE04 RabbitMQ out-of-order evidence missing phrase: {phrase}"
                )

    if not RABBITMQ_RESTART_VERIFIER.exists():
        errors.append("missing PHASE04 RabbitMQ broker restart verifier")
    else:
        restart_errors = _load_verifier(
            RABBITMQ_RESTART_VERIFIER,
            "verify_phase04_rabbitmq_broker_restart",
            "verify_phase04_rabbitmq_broker_restart",
        )()
        for restart_error in restart_errors:
            errors.append(
                f"PHASE04 RabbitMQ broker restart verification failed: {restart_error}"
            )

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
                errors.append(
                    f"PHASE04 RabbitMQ broker restart evidence missing phrase: {phrase}"
                )

    if not RABBITMQ_PARTITION_VERIFIER.exists():
        errors.append("missing PHASE04 RabbitMQ network partition verifier")
    else:
        partition_errors = _load_verifier(
            RABBITMQ_PARTITION_VERIFIER,
            "verify_phase04_rabbitmq_network_partition",
            "verify_phase04_rabbitmq_network_partition",
        )()
        for partition_error in partition_errors:
            errors.append(
                f"PHASE04 RabbitMQ network partition verification failed: {partition_error}"
            )

    if not RABBITMQ_PARTITION_EVIDENCE.exists():
        errors.append("missing PHASE04 RabbitMQ network partition evidence")
    else:
        partition_evidence = _read(RABBITMQ_PARTITION_EVIDENCE)
        for phrase in [
            "network_partition: passed",
            "partition_publish_fail_closed: passed",
            "partition_unknown_reconciled: passed",
            "transport_reconnect: passed",
            "pre_partition_persistent_delivery: passed",
            "post_recovery_confirmed_delivery: passed",
            "outbox_partition_confirm_unknown: passed",
            "outbox_reclaim_republish: passed",
            "outbox_inbox_dedup_after_partition: passed",
            "consumer_crash_before_transaction_commit: passed",
            "consumer_unacked_redelivery: passed",
            "consumer_inbox_first_seen: passed",
            "consumer_duplicate_no_followup_rewrite: passed",
            "Queue ACK != Domain Success",
        ]:
            if phrase not in partition_evidence:
                errors.append(
                    f"PHASE04 RabbitMQ network partition evidence missing phrase: {phrase}"
                )

    if not MINIO_OBJECT_VERIFIER.exists():
        errors.append("missing PHASE04 MinIO object store verifier")
    else:
        minio_errors = _load_verifier(
            MINIO_OBJECT_VERIFIER,
            "verify_phase04_minio_object_store",
            "verify_phase04_minio_object_store",
        )()
        for minio_error in minio_errors:
            errors.append(
                f"PHASE04 MinIO object store verification failed: {minio_error}"
            )

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
            "postgres_manifest_receipt_adoption: passed",
            "raw_content_sha256_reconciliation: passed",
            "domain_manifest_atomicity: passed",
            "post_physical_commit_crash_recovery: passed",
            "committed_read_gate: passed",
            "object_hash_quarantine: passed",
            "logical_delete_before_physical_purge: passed",
            "minio_subscope_completion: proven",
            "p04_t06_completion: blocked_official_checkpointer",
            "Object Commit != Domain Success",
        ]:
            if phrase not in minio_evidence:
                errors.append(
                    f"PHASE04 MinIO object store evidence missing phrase: {phrase}"
                )

    if not MINIO_RESTART_VERIFIER.exists():
        errors.append("missing PHASE04 MinIO storage restart verifier")
    else:
        minio_restart_errors = _load_verifier(
            MINIO_RESTART_VERIFIER,
            "verify_phase04_minio_storage_restart",
            "verify_phase04_minio_storage_restart",
        )()
        for minio_restart_error in minio_restart_errors:
            errors.append(
                f"PHASE04 MinIO storage restart verification failed: {minio_restart_error}"
            )

    if not MINIO_MANIFEST_ADOPTION_VERIFIER.exists():
        errors.append("missing PHASE04 MinIO manifest adoption verifier")
    else:
        minio_manifest_errors = _load_verifier(
            MINIO_MANIFEST_ADOPTION_VERIFIER,
            "verify_phase04_minio_manifest_adoption",
            "verify_phase04_minio_manifest_adoption",
        )()
        for minio_manifest_error in minio_manifest_errors:
            errors.append(
                "PHASE04 MinIO manifest adoption verification failed: "
                f"{minio_manifest_error}"
            )

    if not IDEMPOTENCY_VERIFIER.exists():
        errors.append("missing PHASE04 idempotency claim verifier")
    else:
        idempotency_errors = _load_verifier(
            IDEMPOTENCY_VERIFIER,
            "verify_phase04_idempotency_claim",
            "verify_phase04_idempotency_claim",
        )()
        for idempotency_error in idempotency_errors:
            errors.append(
                f"PHASE04 idempotency claim verification failed: {idempotency_error}"
            )

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
            "owner_generation_expiry_fencing: passed",
            "abort_reclaim: passed",
            "worker_heartbeat_supervision: passed",
            "effect_reconciliation_after_process_exit: passed",
            "lost_completion_no_reexecution: passed",
            "process_cancellation_propagates: passed",
            "Idempotency Claim != Domain Success",
            "P04-T04: completed",
        ]:
            if phrase not in idempotency_evidence:
                errors.append(
                    f"PHASE04 idempotency claim evidence missing phrase: {phrase}"
                )

    if not IDEMPOTENCY_OWNER_CRASH_VERIFIER.exists():
        errors.append("missing PHASE04 idempotency owner crash verifier")
    else:
        owner_crash_errors = _load_verifier(
            IDEMPOTENCY_OWNER_CRASH_VERIFIER,
            "verify_phase04_idempotency_owner_crash",
            "verify_phase04_idempotency_owner_crash",
        )()
        for owner_crash_error in owner_crash_errors:
            errors.append(
                f"PHASE04 idempotency owner crash verification failed: {owner_crash_error}"
            )

    if not IDEMPOTENCY_TENANT_ISOLATION_VERIFIER.exists():
        errors.append("missing PHASE04 idempotency tenant isolation verifier")
    else:
        tenant_isolation_errors = _load_verifier(
            IDEMPOTENCY_TENANT_ISOLATION_VERIFIER,
            "verify_phase04_idempotency_tenant_isolation",
            "verify_phase04_idempotency_tenant_isolation",
        )()
        for tenant_isolation_error in tenant_isolation_errors:
            errors.append(
                f"PHASE04 idempotency tenant isolation verification failed: {tenant_isolation_error}"
            )

    if not IDEMPOTENCY_SUPERVISION_VERIFIER.exists():
        errors.append("missing PHASE04 idempotency supervision verifier")
    else:
        supervision_errors = _load_verifier(
            IDEMPOTENCY_SUPERVISION_VERIFIER,
            "verify_phase04_idempotency_supervision",
            "verify_phase04_idempotency_supervision",
        )()
        for supervision_error in supervision_errors:
            errors.append(
                f"PHASE04 idempotency supervision verification failed: {supervision_error}"
            )

    if not BACKUP_RESTORE_VERIFIER.exists():
        errors.append("missing PHASE04 backup/restore/replay verifier")
    else:
        backup_errors = _load_verifier(
            BACKUP_RESTORE_VERIFIER,
            "verify_phase04_backup_restore_replay",
            "verify_phase04_backup_restore_replay",
        )()
        for backup_error in backup_errors:
            errors.append(
                f"PHASE04 backup/restore/replay verification failed: {backup_error}"
            )

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
            "runtime_restart_after_restore: passed",
            "Backup/Restore/Replay subset != PHASE04 completion",
        ]:
            if phrase not in backup_evidence:
                errors.append(
                    f"PHASE04 backup/restore/replay evidence missing phrase: {phrase}"
                )

    if not COMBINED_SERVICE_FAULT_VERIFIER.exists():
        errors.append("missing PHASE04 combined service fault verifier")
    else:
        combined_fault_errors = _load_verifier(
            COMBINED_SERVICE_FAULT_VERIFIER,
            "verify_phase04_combined_service_fault",
            "verify_phase04_combined_service_fault",
        )()
        for combined_fault_error in combined_fault_errors:
            errors.append(
                f"PHASE04 combined service fault verification failed: {combined_fault_error}"
            )

    if not COMBINED_SERVICE_FAULT_EVIDENCE.exists():
        errors.append("missing PHASE04 combined service fault evidence")
    else:
        combined_fault_evidence = _read(COMBINED_SERVICE_FAULT_EVIDENCE)
        for phrase in [
            "postgres_rabbitmq_minio_combined_outage: passed",
            "dependency_calls_fail_closed: passed",
            "durable_rabbitmq_message_recovered: passed",
            "outbox_to_inbox_after_restart: passed",
            "minio_hash_after_restart: passed",
            "new_postgres_runtime_after_restart: passed",
            "official_checkpointer_in_combined_fault: not_yet_proven",
            "不关闭 P04-T07",
        ]:
            if phrase not in combined_fault_evidence:
                errors.append(
                    f"PHASE04 combined service fault evidence missing phrase: {phrase}"
                )

    if not OPERATOR_READINESS_VERIFIER.exists():
        errors.append("missing PHASE04 operator readiness verifier")
    else:
        operator_errors = _load_verifier(
            OPERATOR_READINESS_VERIFIER,
            "verify_phase04_operator_readiness",
            "verify_phase04_operator_readiness",
        )()
        for operator_error in operator_errors:
            errors.append(
                f"PHASE04 operator readiness verification failed: {operator_error}"
            )

    if not OPERATOR_READINESS_EVIDENCE.exists():
        errors.append("missing PHASE04 operator readiness evidence")
    else:
        operator_evidence = _read(OPERATOR_READINESS_EVIDENCE)
        for phrase in [
            "operator_readiness_snapshot: passed",
            "postgres_health_readiness_metrics: passed",
            "rabbitmq_capacity_backlog_probe: passed",
            "minio_readiness_probe: passed",
            "structured_operator_log: passed",
            "trace_correlation: passed",
            "telemetry_not_eval_verdict: passed",
            "failure_owner_retry_recovery: passed",
            "p04_t07_operator_subscope: proven",
            "phase_completion: blocked_official_checkpointer_and_full_recovery_set",
        ]:
            if phrase not in operator_evidence:
                errors.append(
                    f"PHASE04 operator readiness evidence missing phrase: {phrase}"
                )

    if not OPERATOR_RUNBOOK.exists():
        errors.append("missing PHASE04 infrastructure operations runbook")
    else:
        operator_runbook = _read(OPERATOR_RUNBOOK)
        for phrase in [
            "Health 表示依赖可连接且基础操作成功",
            "Readiness 表示依赖可承接当前产品流量或恢复演练",
            "Capacity/Backlog 是运维指标，不是 Eval verdict",
            "Queue ACK、Object Commit、Checkpoint Commit、HTTP 2xx 和 Audit Receipt 都不能解释为领域成功",
            "缺少 owner、trace 或 evidence ref 的 snapshot 不能作为 PHASE04 evidence",
        ]:
            if phrase not in operator_runbook:
                errors.append(
                    f"PHASE04 infrastructure operations runbook missing phrase: {phrase}"
                )

    if not CAPACITY_ADMISSION_VERIFIER.exists():
        errors.append("missing PHASE04 capacity admission verifier")
    else:
        capacity_admission_errors = _load_verifier(
            CAPACITY_ADMISSION_VERIFIER,
            "verify_phase04_capacity_admission",
            "verify_phase04_capacity_admission",
        )()
        for capacity_admission_error in capacity_admission_errors:
            errors.append(
                "PHASE04 capacity admission verification failed: "
                f"{capacity_admission_error}"
            )

    if not CAPACITY_ADMISSION_EVIDENCE.exists():
        errors.append("missing PHASE04 capacity admission evidence")
    else:
        capacity_admission_evidence = _read(CAPACITY_ADMISSION_EVIDENCE)
        for phrase in [
            "capacity_admission_schema: passed",
            "drain_stops_new_admission: passed",
            "capacity_reservation_atomic_single_winner: passed",
            "capacity_release_restores_admission: passed",
            "capacity_exhaustion_backpressure: passed",
            "wrong_owner_release_rejected: passed",
            "phase_completion: blocked_official_checkpointer_and_full_recovery_set",
            "`ARCH-INFRA-031`、`ARCH-INFRA-032` 和 `ARCH-INFRA-033`",
        ]:
            if phrase not in capacity_admission_evidence:
                errors.append(
                    f"PHASE04 capacity admission evidence missing phrase: {phrase}"
                )

    if not MANDATORY_AUDIT_VERIFIER.exists():
        errors.append("missing PHASE04 mandatory audit verifier")
    else:
        mandatory_audit_errors = _load_verifier(
            MANDATORY_AUDIT_VERIFIER,
            "verify_phase04_mandatory_audit",
            "verify_phase04_mandatory_audit",
        )()
        for mandatory_audit_error in mandatory_audit_errors:
            errors.append(
                "PHASE04 mandatory audit verification failed: "
                f"{mandatory_audit_error}"
            )

    if not MANDATORY_AUDIT_EVIDENCE.exists():
        errors.append("missing PHASE04 mandatory audit evidence")
    else:
        mandatory_audit_evidence = _read(MANDATORY_AUDIT_EVIDENCE)
        for phrase in [
            "mandatory_audit_schema: passed",
            "durable_audit_before_effect: passed",
            "effect_without_durable_audit_rejected: passed",
            "audit_capacity_fail_closed: passed",
            "capacity_failed_audit_no_effect: passed",
            "audit_capacity_recovers_after_observed_effect: passed",
            "phase_completion: blocked_official_checkpointer_and_full_recovery_set",
            "`ARCH-INFRA-054` 和 `ARCH-INFRA-055`",
        ]:
            if phrase not in mandatory_audit_evidence:
                errors.append(
                    f"PHASE04 mandatory audit evidence missing phrase: {phrase}"
                )

    if not CUTOVER_SNAPSHOT_VERIFIER.exists():
        errors.append("missing PHASE04 cutover snapshot verifier")
    else:
        cutover_snapshot_errors = _load_verifier(
            CUTOVER_SNAPSHOT_VERIFIER,
            "verify_phase04_cutover_snapshot",
            "verify_phase04_cutover_snapshot",
        )()
        for cutover_snapshot_error in cutover_snapshot_errors:
            errors.append(
                "PHASE04 cutover snapshot verification failed: "
                f"{cutover_snapshot_error}"
            )

    if not CUTOVER_SNAPSHOT_EVIDENCE.exists():
        errors.append("missing PHASE04 cutover snapshot evidence")
    else:
        cutover_snapshot_evidence = _read(CUTOVER_SNAPSHOT_EVIDENCE)
        for phrase in [
            "cutover_snapshot_schema: passed",
            "cutover_generation_cas: passed",
            "stale_generation_rejected: passed",
            "active_snapshot_ref_acquired: passed",
            "active_snapshot_blocks_retirement: passed",
            "current_active_snapshot_retirement_rejected: passed",
            "released_snapshot_ref_allows_retirement: passed",
            "phase_completion: blocked_official_checkpointer_and_full_recovery_set",
            "`ARCH-INFRA-048` 和 `ARCH-INFRA-049`",
        ]:
            if phrase not in cutover_snapshot_evidence:
                errors.append(
                    f"PHASE04 cutover snapshot evidence missing phrase: {phrase}"
                )

    if not RECOVERY_WATERMARK_VERIFIER.exists():
        errors.append("missing PHASE04 recovery watermark verifier")
    else:
        recovery_watermark_errors = _load_verifier(
            RECOVERY_WATERMARK_VERIFIER,
            "verify_phase04_recovery_watermark",
            "verify_phase04_recovery_watermark",
        )()
        for recovery_watermark_error in recovery_watermark_errors:
            errors.append(
                "PHASE04 recovery watermark verification failed: "
                f"{recovery_watermark_error}"
            )

    if not RECOVERY_WATERMARK_EVIDENCE.exists():
        errors.append("missing PHASE04 recovery watermark evidence")
    else:
        recovery_watermark_evidence = _read(RECOVERY_WATERMARK_EVIDENCE)
        for phrase in [
            "recovery_watermark_schema: passed",
            "authoritative_watermarks_recorded: passed",
            "derived_watermarks_recorded: passed",
            "mismatched_derived_watermark_rejected: passed",
            "recovery_set_authoritative_and_derived_alignment: passed",
            "recovery_set_verification_hash: passed",
            "phase_completion: blocked_official_checkpointer_and_full_recovery_set",
            "`ARCH-INFRA-022` 和 `ARCH-INFRA-052`",
        ]:
            if phrase not in recovery_watermark_evidence:
                errors.append(
                    f"PHASE04 recovery watermark evidence missing phrase: {phrase}"
                )

    if not DR_PROFILE_VERIFIER.exists():
        errors.append("missing PHASE04 DR profile verifier")
    else:
        dr_profile_errors = _load_verifier(
            DR_PROFILE_VERIFIER,
            "verify_phase04_dr_profile",
            "verify_phase04_dr_profile",
        )()
        for dr_profile_error in dr_profile_errors:
            errors.append(f"PHASE04 DR profile verification failed: {dr_profile_error}")

    if not DR_PROFILE.exists():
        errors.append("missing PHASE04 infrastructure DR profile")
    else:
        dr_profile = _read(DR_PROFILE)
        for phrase in [
            "profile_id: zuno-server-product-dr-profile",
            "phase04_completion_claim: false",
            "phase05_ready: false",
            "component: langgraph_postgres_checkpointer",
            "current_status: blocked",
            "component: pitr",
            "current_status: target_not_current",
            "explicit_cutover_required: true",
            "cutover_allowed_by_default: false",
        ]:
            if phrase not in dr_profile:
                errors.append(
                    f"PHASE04 infrastructure DR profile missing phrase: {phrase}"
                )

    if not DR_PROFILE_EVIDENCE.exists():
        errors.append("missing PHASE04 DR profile evidence")
    else:
        dr_profile_evidence = _read(DR_PROFILE_EVIDENCE)
        for phrase in [
            "dr_profile_schema: passed",
            "rpo_rto_owner_coverage: passed",
            "explicit_cutover_policy: passed",
            "blocked_checkpointer_boundary: passed",
            "pitr_target_not_current_boundary: passed",
            "projection_replay_target_not_current_boundary: passed",
            "phase_completion: blocked_official_checkpointer_and_full_recovery_set",
            "It does not prove full Backup/Restore/PITR/Projection Replay",
        ]:
            if phrase not in dr_profile_evidence:
                errors.append(f"PHASE04 DR profile evidence missing phrase: {phrase}")

    if not CAPABILITY_PROFILE_VERIFIER.exists():
        errors.append("missing PHASE04 infrastructure capability profile verifier")
    else:
        capability_profile_errors = _load_verifier(
            CAPABILITY_PROFILE_VERIFIER,
            "verify_phase04_infrastructure_capability_profile",
            "verify_phase04_infrastructure_capability_profile",
        )()
        for capability_profile_error in capability_profile_errors:
            errors.append(
                "PHASE04 infrastructure capability profile verification failed: "
                f"{capability_profile_error}"
            )

    if not CAPABILITY_PROFILE_EVIDENCE.exists():
        errors.append("missing PHASE04 infrastructure capability profile evidence")
    else:
        capability_profile_evidence = _read(CAPABILITY_PROFILE_EVIDENCE)
        for phrase in [
            "infrastructure_capability_profile_contract: passed",
            "data_service_capability_contract: passed",
            "profile_immutable: passed",
            "profile_versioned_hash: passed",
            "invalid_content_hash_reject: passed",
            "developer_ci_and_server_product_share_typed_contract: passed",
            "derived_services_non_authoritative: passed",
            "unsupported_semantics_explicit: passed",
            "It does not prove official LangGraph PostgreSQL Checkpointer integration",
        ]:
            if phrase not in capability_profile_evidence:
                errors.append(
                    "PHASE04 infrastructure capability profile evidence missing phrase: "
                    f"{phrase}"
                )

    if not BACKUP_SERVICE_BOUNDARY_VERIFIER.exists():
        errors.append("missing PHASE04 backup/service boundary verifier")
    else:
        backup_service_boundary_errors = _load_verifier(
            BACKUP_SERVICE_BOUNDARY_VERIFIER,
            "verify_phase04_backup_service_boundaries",
            "verify_phase04_backup_service_boundaries",
        )()
        for backup_service_boundary_error in backup_service_boundary_errors:
            errors.append(
                "PHASE04 backup/service boundary verification failed: "
                f"{backup_service_boundary_error}"
            )

    if not BACKUP_SERVICE_BOUNDARY_EVIDENCE.exists():
        errors.append("missing PHASE04 backup/service boundary evidence")
    else:
        backup_service_boundary_evidence = _read(BACKUP_SERVICE_BOUNDARY_EVIDENCE)
        for phrase in [
            "backup_scope_profile: passed",
            "backup_rpo_source_coverage: passed",
            "backup_encryption_requirement_defined: passed",
            "service_boundary_profile: passed",
            "postgresql_rabbitmq_object_checkpoint_boundary: passed",
            "checkpoint_boundary_blocked_not_completed: passed",
            "不证明生产 encrypted backup、PITR、完整 RecoverySet 或 official Checkpointer restore",
        ]:
            if phrase not in backup_service_boundary_evidence:
                errors.append(
                    "PHASE04 backup/service boundary evidence missing phrase: "
                    f"{phrase}"
                )

    if not INFRASTRUCTURE_DOCS_GOVERNANCE_VERIFIER.exists():
        errors.append("missing PHASE04 infrastructure docs governance verifier")
    else:
        docs_governance_errors = _load_verifier(
            INFRASTRUCTURE_DOCS_GOVERNANCE_VERIFIER,
            "verify_phase04_infrastructure_docs_governance",
            "verify_phase04_infrastructure_docs_governance",
        )()
        for docs_governance_error in docs_governance_errors:
            errors.append(
                "PHASE04 infrastructure docs governance verification failed: "
                f"{docs_governance_error}"
            )

    if not INFRASTRUCTURE_DOCS_GOVERNANCE_EVIDENCE.exists():
        errors.append("missing PHASE04 infrastructure docs governance evidence")
    else:
        docs_governance_evidence = _read(INFRASTRUCTURE_DOCS_GOVERNANCE_EVIDENCE)
        for phrase in [
            "current_target_future_not_selected_layering: passed",
            "single_formal_infrastructure_target_document: passed",
            "agent_infrastructure_mirror_byte_identical: passed",
            "architecture_canonical_file_set: passed",
            "本证据不证明任何 runtime adapter",
        ]:
            if phrase not in docs_governance_evidence:
                errors.append(
                    "PHASE04 infrastructure docs governance evidence missing phrase: "
                    f"{phrase}"
                )

    if not DOMAIN_BOUNDARY_VERIFIER.exists():
        errors.append("missing PHASE04 infrastructure domain boundary verifier")
    else:
        domain_boundary_errors = _load_verifier(
            DOMAIN_BOUNDARY_VERIFIER,
            "verify_phase04_infrastructure_domain_boundary",
            "verify_phase04_infrastructure_domain_boundary",
        )()
        for domain_boundary_error in domain_boundary_errors:
            errors.append(
                "PHASE04 infrastructure domain boundary verification failed: "
                f"{domain_boundary_error}"
            )

    if not DOMAIN_BOUNDARY_EVIDENCE.exists():
        errors.append("missing PHASE04 infrastructure domain boundary evidence")
    else:
        domain_boundary_evidence = _read(DOMAIN_BOUNDARY_EVIDENCE)
        for phrase in [
            "infrastructure_receipt_contract_scan: passed",
            "queue_ack_not_domain_success: passed",
            "object_commit_not_domain_success: passed",
            "idempotency_claim_not_domain_success: passed",
            "operator_telemetry_not_domain_success: passed",
            "minio_manifest_domain_success_rollback_guard: passed",
            "Queue ACK, RabbitMQ delivery, Object Commit, Idempotency Claim, Object Manifest visibility and operator telemetry do not mean product/domain success",
        ]:
            if phrase not in domain_boundary_evidence:
                errors.append(
                    "PHASE04 infrastructure domain boundary evidence missing phrase: "
                    f"{phrase}"
                )

    if not TYPED_PORTS_VERIFIER.exists():
        errors.append("missing PHASE04 infrastructure typed ports verifier")
    else:
        typed_ports_errors = _load_verifier(
            TYPED_PORTS_VERIFIER,
            "verify_phase04_infrastructure_typed_ports",
            "verify_phase04_infrastructure_typed_ports",
        )()
        for typed_ports_error in typed_ports_errors:
            errors.append(
                f"PHASE04 infrastructure typed ports verification failed: {typed_ports_error}"
            )

    if not TYPED_PORTS_EVIDENCE.exists():
        errors.append("missing PHASE04 infrastructure typed ports evidence")
    else:
        typed_ports_evidence = _read(TYPED_PORTS_EVIDENCE)
        for phrase in [
            "local_server_same_profile_contract: passed",
            "data_service_capability_typed_fields: passed",
            "required_service_kind_coverage: passed",
            "local_server_service_kind_parity: passed",
            "unknown_service_kind_fail_closed: passed",
            "Developer CI and Server Product infrastructure profiles share the same typed",
            "It does not prove that every target adapter is implemented",
        ]:
            if phrase not in typed_ports_evidence:
                errors.append(
                    "PHASE04 infrastructure typed ports evidence missing phrase: "
                    f"{phrase}"
                )

    if not TENANT_ISOLATION_PROFILE_VERIFIER.exists():
        errors.append("missing PHASE04 tenant isolation profile verifier")
    else:
        tenant_profile_errors = _load_verifier(
            TENANT_ISOLATION_PROFILE_VERIFIER,
            "verify_phase04_tenant_isolation_profiles",
            "verify_phase04_tenant_isolation_profiles",
        )()
        for tenant_profile_error in tenant_profile_errors:
            errors.append(
                "PHASE04 tenant isolation profile verification failed: "
                f"{tenant_profile_error}"
            )

    if not TENANT_ISOLATION_PROFILE_EVIDENCE.exists():
        errors.append("missing PHASE04 tenant isolation profile evidence")
    else:
        tenant_profile_evidence = _read(TENANT_ISOLATION_PROFILE_EVIDENCE)
        for phrase in [
            "tenant_isolation_profile_contract: passed",
            "every_typed_service_has_profile: passed",
            "tenant_id_scope_required: passed",
            "application_end_filter_only_rejected: passed",
            "cross_tenant_hit_action_fail_closed: passed",
            "profile_evidence_refs_exist: passed",
            "It does not prove full runtime cross-tenant hit quarantine/fail-closed behavior",
        ]:
            if phrase not in tenant_profile_evidence:
                errors.append(
                    "PHASE04 tenant isolation profile evidence missing phrase: "
                    f"{phrase}"
                )

    if not TENANT_PHYSICAL_CONSTRAINTS_VERIFIER.exists():
        errors.append("missing PHASE04 tenant physical constraints verifier")
    else:
        tenant_physical_errors = _load_verifier(
            TENANT_PHYSICAL_CONSTRAINTS_VERIFIER,
            "verify_phase04_tenant_physical_constraints",
            "verify_phase04_tenant_physical_constraints",
        )()
        for tenant_physical_error in tenant_physical_errors:
            errors.append(
                "PHASE04 tenant physical constraints verification failed: "
                f"{tenant_physical_error}"
            )

    if not TENANT_PHYSICAL_CONSTRAINTS_EVIDENCE.exists():
        errors.append("missing PHASE04 tenant physical constraints evidence")
    else:
        tenant_physical_evidence = _read(TENANT_PHYSICAL_CONSTRAINTS_EVIDENCE)
        for phrase in [
            "relational_tenant_physical_constraint: passed",
            "queue_tenant_protocol_constraint: passed",
            "object_tenant_target_constraint: passed",
            "trace_audit_tenant_snapshot_constraint: passed",
            "target_only_services_not_promoted: passed",
            "Cross-tenant hit quarantine/fail-closed",
        ]:
            if phrase not in tenant_physical_evidence:
                errors.append(
                    "PHASE04 tenant physical constraints evidence missing phrase: "
                    f"{phrase}"
                )

    if not UPGRADE_COMPATIBILITY_PROFILE_VERIFIER.exists():
        errors.append("missing PHASE04 upgrade compatibility profile verifier")
    else:
        upgrade_profile_errors = _load_verifier(
            UPGRADE_COMPATIBILITY_PROFILE_VERIFIER,
            "verify_phase04_upgrade_compatibility_profiles",
            "verify_phase04_upgrade_compatibility_profiles",
        )()
        for upgrade_profile_error in upgrade_profile_errors:
            errors.append(
                "PHASE04 upgrade compatibility profile verification failed: "
                f"{upgrade_profile_error}"
            )

    if not UPGRADE_COMPATIBILITY_PROFILE_EVIDENCE.exists():
        errors.append("missing PHASE04 upgrade compatibility profile evidence")
    else:
        upgrade_profile_evidence = _read(UPGRADE_COMPATIBILITY_PROFILE_EVIDENCE)
        for phrase in [
            "upgrade_compatibility_profile_contract: passed",
            "every_typed_service_has_upgrade_profile: passed",
            "adapter_and_schema_versions_explicit: passed",
            "read_write_rollback_windows_explicit: passed",
            "unknown_version_fail_closed: passed",
            "profile_version_hash_changes: passed",
            "It does not prove live rolling upgrade, official Checkpointer integration, or full recovery replay",
        ]:
            if phrase not in upgrade_profile_evidence:
                errors.append(
                    "PHASE04 upgrade compatibility profile evidence missing phrase: "
                    f"{phrase}"
                )

    if not ADAPTER_CONFORMANCE_PROFILE_VERIFIER.exists():
        errors.append("missing PHASE04 adapter conformance profile verifier")
    else:
        conformance_profile_errors = _load_verifier(
            ADAPTER_CONFORMANCE_PROFILE_VERIFIER,
            "verify_phase04_adapter_conformance_profiles",
            "verify_phase04_adapter_conformance_profiles",
        )()
        for conformance_profile_error in conformance_profile_errors:
            errors.append(
                "PHASE04 adapter conformance profile verification failed: "
                f"{conformance_profile_error}"
            )

    if not ADAPTER_CONFORMANCE_PROFILE_EVIDENCE.exists():
        errors.append("missing PHASE04 adapter conformance profile evidence")
    else:
        conformance_profile_evidence = _read(ADAPTER_CONFORMANCE_PROFILE_EVIDENCE)
        for phrase in [
            "adapter_conformance_profile_contract: passed",
            "developer_ci_server_product_same_suite: passed",
            "service_kind_coverage_parity: passed",
            "unsupported_local_semantic_fail_fast: passed",
            "conformance_suite_version_hash_changes: passed",
            "It does not prove that every future enterprise adapter is implemented",
        ]:
            if phrase not in conformance_profile_evidence:
                errors.append(
                    "PHASE04 adapter conformance profile evidence missing phrase: "
                    f"{phrase}"
                )

    if not RELEASE_PROVENANCE_MANIFEST_VERIFIER.exists():
        errors.append("missing PHASE04 release provenance manifest verifier")
    else:
        release_provenance_errors = _load_verifier(
            RELEASE_PROVENANCE_MANIFEST_VERIFIER,
            "verify_phase04_release_provenance_manifest",
            "verify_phase04_release_provenance_manifest",
        )()
        for release_provenance_error in release_provenance_errors:
            errors.append(
                "PHASE04 release provenance manifest verification failed: "
                f"{release_provenance_error}"
            )

    if not RELEASE_PROVENANCE_MANIFEST_EVIDENCE.exists():
        errors.append("missing PHASE04 release provenance manifest evidence")
    else:
        release_provenance_evidence = _read(RELEASE_PROVENANCE_MANIFEST_EVIDENCE)
        for phrase in [
            "release_manifest_contract: passed",
            "source_commit_bound: passed",
            "running_image_digest_bound: passed",
            "compose_network_refs_bound: passed",
            "compatibility_evidence_bound: passed",
            "rollback_ref_self_rejected: passed",
            "It does not prove a production application image release",
        ]:
            if phrase not in release_provenance_evidence:
                errors.append(
                    "PHASE04 release provenance manifest evidence missing phrase: "
                    f"{phrase}"
                )

    if not REDIS_OPTIONAL_BOUNDARY_VERIFIER.exists():
        errors.append("missing PHASE04 Redis optional boundary verifier")
    else:
        redis_optional_errors = _load_verifier(
            REDIS_OPTIONAL_BOUNDARY_VERIFIER,
            "verify_phase04_redis_optional_boundary",
            "verify_phase04_redis_optional_boundary",
        )()
        for redis_optional_error in redis_optional_errors:
            errors.append(
                "PHASE04 Redis optional boundary verification failed: "
                f"{redis_optional_error}"
            )

    if not REDIS_OPTIONAL_BOUNDARY_EVIDENCE.exists():
        errors.append("missing PHASE04 Redis optional boundary evidence")
    else:
        redis_optional_evidence = _read(REDIS_OPTIONAL_BOUNDARY_EVIDENCE)
        for phrase in [
            "redis_cache_capability_present: passed",
            "redis_cache_non_authoritative: passed",
            "redis_cache_rebuildable: passed",
            "redis_not_required_real_service: passed",
            "redis_not_required_release_adapter: passed",
            "It does not prove Redis high availability",
        ]:
            if phrase not in redis_optional_evidence:
                errors.append(
                    "PHASE04 Redis optional boundary evidence missing phrase: "
                    f"{phrase}"
                )

    if not DERIVED_INDEX_BOUNDARY_VERIFIER.exists():
        errors.append("missing PHASE04 derived index boundary verifier")
    else:
        derived_index_errors = _load_verifier(
            DERIVED_INDEX_BOUNDARY_VERIFIER,
            "verify_phase04_derived_index_boundary",
            "verify_phase04_derived_index_boundary",
        )()
        for derived_index_error in derived_index_errors:
            errors.append(
                "PHASE04 derived index boundary verification failed: "
                f"{derived_index_error}"
            )

    if not DERIVED_INDEX_BOUNDARY_EVIDENCE.exists():
        errors.append("missing PHASE04 derived index boundary evidence")
    else:
        derived_index_evidence = _read(DERIVED_INDEX_BOUNDARY_EVIDENCE)
        for phrase in [
            "vector_index_rebuildable_non_authoritative: passed",
            "graph_index_rebuildable_non_authoritative: passed",
            "lexical_index_rebuildable_non_authoritative: passed",
            "derived_index_versioned_semantics: passed",
            "derived_indexes_not_required_release_adapters: passed",
            "It does not prove current server adapters for Milvus",
        ]:
            if phrase not in derived_index_evidence:
                errors.append(
                    "PHASE04 derived index boundary evidence missing phrase: "
                    f"{phrase}"
                )

    if not CONTRACT_OWNERSHIP_BOUNDARY_VERIFIER.exists():
        errors.append("missing PHASE04 contract ownership boundary verifier")
    else:
        contract_ownership_errors = _load_verifier(
            CONTRACT_OWNERSHIP_BOUNDARY_VERIFIER,
            "verify_phase04_contract_ownership_boundaries",
            "verify_phase04_contract_ownership_boundaries",
        )()
        for contract_ownership_error in contract_ownership_errors:
            errors.append(
                "PHASE04 contract ownership boundary verification failed: "
                f"{contract_ownership_error}"
            )

    if not CONTRACT_OWNERSHIP_BOUNDARY_EVIDENCE.exists():
        errors.append("missing PHASE04 contract ownership boundary evidence")
    else:
        contract_ownership_evidence = _read(CONTRACT_OWNERSHIP_BOUNDARY_EVIDENCE)
        for phrase in [
            "index_write_visibility_contract_layering: passed",
            "index_manifest_acceptance_domain_owner: passed",
            "write_receipt_not_domain_acceptance: passed",
            "prepared_tool_action_owner_distinct: passed",
            "prepared_tool_action_canonical_hash_fail_closed: passed",
            "本证据不证明 Milvus、Neo4j、BM25/Search 当前 server adapter",
        ]:
            if phrase not in contract_ownership_evidence:
                errors.append(
                    "PHASE04 contract ownership boundary evidence missing phrase: "
                    f"{phrase}"
                )

    if not REQUIREMENT_LEDGER_EVIDENCE_GATE_VERIFIER.exists():
        errors.append("missing requirement ledger evidence gate verifier")
    else:
        ledger_gate_errors = _load_verifier(
            REQUIREMENT_LEDGER_EVIDENCE_GATE_VERIFIER,
            "verify_requirement_ledger_evidence_gate",
            "verify_requirement_ledger_evidence_gate",
        )()
        for ledger_gate_error in ledger_gate_errors:
            errors.append(
                f"Requirement ledger evidence gate verification failed: {ledger_gate_error}"
            )

    if not REQUIREMENT_LEDGER_EVIDENCE_GATE_EVIDENCE.exists():
        errors.append("missing PHASE04 requirement ledger evidence gate evidence")
    else:
        ledger_gate_evidence = _read(REQUIREMENT_LEDGER_EVIDENCE_GATE_EVIDENCE)
        for phrase in [
            "target_to_current_evidence_gate: passed",
            "current_status_count_reconciliation: passed",
            "current_path_existence: passed",
            "current_test_path_existence: passed",
            "current_evidence_path_existence: passed",
            "reverse_trace_completeness: passed",
            "placeholder_evidence_reject: passed",
            "This evidence only proves the Requirement Ledger promotion gate",
        ]:
            if phrase not in ledger_gate_evidence:
                errors.append(
                    f"PHASE04 requirement ledger evidence gate evidence missing phrase: {phrase}"
                )

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

    if not LEASE_COORDINATION_VERIFIER.exists():
        errors.append("missing PHASE04 lease worker coordination verifier")
    else:
        coordination_errors = _load_verifier(
            LEASE_COORDINATION_VERIFIER,
            "verify_phase04_lease_worker_coordination",
            "verify_phase04_lease_worker_coordination",
        )()
        for coordination_error in coordination_errors:
            errors.append(
                f"PHASE04 lease worker coordination verification failed: {coordination_error}"
            )

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
            "database_clock_deadline: passed",
            "same_owner_idempotent_acquire: passed",
            "explicit_transfer: passed",
            "fenced_commit_same_transaction: passed",
            "worker_heartbeat_scheduler: passed",
            "crash_handoff: passed",
            "network_partition_heartbeat_loss: passed",
            "pause_gc_delay: passed",
            "cancel_transfer_race: passed",
            "clock_tolerance: passed",
            "不能代表领域结果成功",
            "P04-T05: completed",
        ]:
            if phrase not in lease_evidence:
                errors.append(
                    f"PHASE04 lease/fencing evidence missing phrase: {phrase}"
                )

    if not RECONCILER_SUPERVISION_BOUNDARY_VERIFIER.exists():
        errors.append("missing PHASE04 reconciler supervision boundary verifier")
    else:
        reconciler_boundary_errors = _load_verifier(
            RECONCILER_SUPERVISION_BOUNDARY_VERIFIER,
            "verify_phase04_reconciler_supervision_boundary",
            "verify_phase04_reconciler_supervision_boundary",
        )()
        for reconciler_boundary_error in reconciler_boundary_errors:
            errors.append(
                "PHASE04 reconciler supervision boundary verification failed: "
                f"{reconciler_boundary_error}"
            )

    if not RECONCILER_SUPERVISION_BOUNDARY_EVIDENCE.exists():
        errors.append("missing PHASE04 reconciler supervision boundary evidence")
    else:
        reconciler_boundary_evidence = _read(RECONCILER_SUPERVISION_BOUNDARY_EVIDENCE)
        for phrase in [
            "reconciler_supervision_boundary: passed",
            "idempotency_reconcile_no_reexecution: passed",
            "lease_fencing_supervision: passed",
            "postgres_partition_fail_closed: passed",
            "不证明所有产品 Reconciler 已接入",
        ]:
            if phrase not in reconciler_boundary_evidence:
                errors.append(
                    "PHASE04 reconciler supervision boundary evidence missing phrase: "
                    f"{phrase}"
                )

    if not CHECKPOINT_BOUNDARY_VERSION_VERIFIER.exists():
        errors.append("missing PHASE04 checkpoint boundary/version verifier")
    else:
        checkpoint_boundary_errors = _load_verifier(
            CHECKPOINT_BOUNDARY_VERSION_VERIFIER,
            "verify_phase04_checkpoint_boundary_version",
            "verify_phase04_checkpoint_boundary_version",
        )()
        for checkpoint_boundary_error in checkpoint_boundary_errors:
            errors.append(
                "PHASE04 checkpoint boundary/version verification failed: "
                f"{checkpoint_boundary_error}"
            )

    if not CHECKPOINT_BOUNDARY_VERSION_EVIDENCE.exists():
        errors.append("missing PHASE04 checkpoint boundary/version evidence")
    else:
        checkpoint_boundary_evidence = _read(CHECKPOINT_BOUNDARY_VERSION_EVIDENCE)
        for phrase in [
            "checkpoint_domain_fact_separation: passed",
            "checkpoint_version_fail_closed: passed",
            "official_checkpointer_blocked_boundary: passed",
            "不证明 official LangGraph PostgreSQL Checkpointer runtime 已安装或可恢复",
        ]:
            if phrase not in checkpoint_boundary_evidence:
                errors.append(
                    "PHASE04 checkpoint boundary/version evidence missing phrase: "
                    f"{phrase}"
                )

    if not PARTIAL_EVIDENCE.exists():
        errors.append(
            "missing partial PHASE04 evidence: docs/evidence/phase04-postgres-foundation.md"
        )
    else:
        partial = _read(PARTIAL_EVIDENCE)
        for phrase in [
            "partial_implementation_available",
            "phase_completion: `withdrawn`",
        ]:
            if phrase not in partial:
                errors.append(
                    f"partial PHASE04 evidence missing boundary phrase: {phrase}"
                )

    if not PHASE04_EVIDENCE.exists():
        errors.append("missing PHASE04 complete infrastructure evidence/blocker file")
    else:
        evidence = _read(PHASE04_EVIDENCE)
        for phrase in REQUIRED_EVIDENCE_PHRASES:
            if phrase not in evidence:
                errors.append(
                    f"PHASE04 evidence missing required real dependency proof: {phrase}"
                )
        for marker in REQUIRED_COMPLETION_PROOF_MARKERS:
            if marker not in evidence:
                errors.append(
                    f"PHASE04 evidence missing completion proof marker: {marker}"
                )
        if (
            "status: blocked" not in evidence
            and "coordinator_decision: approved" not in evidence
        ):
            errors.append(
                "PHASE04 evidence must explicitly record blocked status or approved closure"
            )
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
