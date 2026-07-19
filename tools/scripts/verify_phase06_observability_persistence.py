from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from zuno.platform.database.schema_registry import OBSERVABILITY_TABLE_OWNERS

REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION_PATH = (
    REPO_ROOT
    / "infra"
    / "db"
    / "alembic"
    / "versions"
    / "20260719_17_observability_black_box.py"
)
EXPECTED_REVISION = "20260719_17"
EXPECTED_DOWN_REVISION = "20260719_16"
FORBIDDEN_COLUMNS = {
    "prompt",
    "hidden_reasoning",
    "chain_of_thought",
    "secret",
    "secret_material",
    "access_token",
    "refresh_token",
    "api_key",
    "password",
}
REQUIRED_COLUMNS = {
    "observability_ingest_envelopes": {
        "envelope_id",
        "tenant_id",
        "workspace_id",
        "trace_id",
        "schema_ref",
        "schema_version",
        "producer",
        "scope_ref",
        "effective_security_epoch_ref",
        "payload_hash",
        "redaction_hash",
        "payload",
        "status",
        "quarantine_reason",
        "accepted_at",
    },
    "observability_traces": {
        "trace_id",
        "tenant_id",
        "workspace_id",
        "root_run_id",
        "lifecycle_state",
        "terminal",
        "trace_hash",
        "started_at",
        "completed_at",
    },
    "observability_spans": {
        "span_id",
        "trace_id",
        "tenant_id",
        "parent_span_id",
        "causation_id",
        "span_kind",
        "name",
        "status",
        "span_hash",
        "started_at",
        "ended_at",
    },
    "observability_runtime_events": {
        "event_id",
        "tenant_id",
        "trace_id",
        "span_id",
        "stream_id",
        "sequence",
        "event_type",
        "payload_hash",
        "redacted_payload",
        "status",
        "accepted_at",
    },
    "observability_audit_records": {
        "audit_id",
        "tenant_id",
        "trace_id",
        "sequence",
        "previous_hash",
        "audit_hash",
        "payload_hash",
        "redacted_payload",
        "accepted",
        "accepted_at",
    },
    "observability_projection_watermarks": {
        "watermark_id",
        "tenant_id",
        "projection_id",
        "stream_id",
        "contiguous_sequence",
        "max_seen_sequence",
        "freshness_status",
        "updated_at",
    },
    "observability_gaps": {
        "gap_id",
        "tenant_id",
        "stream_id",
        "missing_after_sequence",
        "missing_before_sequence",
        "status",
        "detected_at",
        "filled_at",
    },
    "observability_dead_letters": {
        "dead_letter_id",
        "tenant_id",
        "source_ref",
        "reason_code",
        "payload_hash",
        "redacted_payload",
        "status",
        "created_at",
    },
    "observability_projection_rebuilds": {
        "rebuild_id",
        "tenant_id",
        "projection_id",
        "claim_owner",
        "fencing_token",
        "replay_from_sequence",
        "status",
        "started_at",
        "completed_at",
    },
}


class OpRecorder:
    def __init__(self) -> None:
        self.tables: dict[str, set[str]] = {}
        self.indexes: set[str] = set()
        self.dropped_tables: list[str] = []

    def create_table(self, name: str, *objects: Any, **_: Any) -> None:
        self.tables[name] = {
            str(item.name)
            for item in objects
            if item.__class__.__name__ == "Column" and getattr(item, "name", None)
        }

    def create_index(self, name: str, *_: Any, **__: Any) -> None:
        self.indexes.add(name)

    def drop_index(self, *_: Any, **__: Any) -> None:
        return None

    def drop_table(self, name: str) -> None:
        self.dropped_tables.append(name)


def _load_migration():
    spec = importlib.util.spec_from_file_location("phase06_observability_migration", MIGRATION_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load PHASE06 observability migration")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_with_recorder(function: str) -> OpRecorder:
    module = _load_migration()
    recorder = OpRecorder()
    original_op = module.op
    module.op = recorder
    try:
        getattr(module, function)()
    finally:
        module.op = original_op
    return recorder


def verify_phase06_observability_persistence() -> list[str]:
    errors: list[str] = []
    if not MIGRATION_PATH.exists():
        return ["missing PHASE06 observability black box migration"]
    module = _load_migration()
    if module.revision != EXPECTED_REVISION:
        errors.append(f"unexpected PHASE06 observability revision: {module.revision!r}")
    if module.down_revision != EXPECTED_DOWN_REVISION:
        errors.append(
            f"PHASE06 observability migration must follow {EXPECTED_DOWN_REVISION}, found {module.down_revision!r}"
        )
    if set(OBSERVABILITY_TABLE_OWNERS) != set(REQUIRED_COLUMNS):
        errors.append("OBSERVABILITY_TABLE_OWNERS does not match required observability tables")

    upgrade = _run_with_recorder("upgrade")
    missing_tables = set(REQUIRED_COLUMNS) - set(upgrade.tables)
    if missing_tables:
        errors.append(f"observability migration missing tables: {sorted(missing_tables)!r}")
    extra_tables = set(upgrade.tables) - set(REQUIRED_COLUMNS)
    if extra_tables:
        errors.append(f"observability migration has unexpected tables: {sorted(extra_tables)!r}")
    for table, required_columns in REQUIRED_COLUMNS.items():
        actual_columns = upgrade.tables.get(table, set())
        missing_columns = required_columns - actual_columns
        if missing_columns:
            errors.append(f"{table} missing columns: {sorted(missing_columns)!r}")
        forbidden = FORBIDDEN_COLUMNS & actual_columns
        if forbidden:
            errors.append(f"{table} has forbidden raw sensitive columns: {sorted(forbidden)!r}")
        if "tenant_id" not in actual_columns:
            errors.append(f"{table} missing tenant_id boundary column")

    source = MIGRATION_PATH.read_text(encoding="utf-8")
    for phrase in [
        "effective_security_epoch_ref",
        "redaction_hash",
        "quarantine_reason",
        "previous_hash",
        "audit_hash",
        "freshness_status",
        "dead_letter",
        "fencing_token",
    ]:
        if phrase not in source:
            errors.append(f"observability migration missing target phrase: {phrase}")
    for forbidden in ["create_all(", "drop_all(", "hidden_reasoning", "chain_of_thought", "access_token", "api_key", "password"]:
        if forbidden in source:
            errors.append(f"observability migration contains forbidden phrase: {forbidden}")

    repository = (
        REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "observability" / "persistence.py"
    ).read_text(encoding="utf-8")
    for phrase in [
        "class ObservabilityUnitOfWork",
        "class ObservabilityRepository",
        "class PostgresObservabilityRuntimeAdapter",
        "ingest_envelope",
        "record_trace",
        "record_span",
        "record_runtime_event",
        "record_audit",
        "update_watermark",
        "record_gap",
        "record_dead_letter",
        "record_security_audit",
        "trace_timeline",
        "projection_freshness",
        "dead_letters",
        "ObservabilityFreshnessRecord",
        "duplicate_sequence_payload_mismatch",
        "redact_sensitive_payload",
    ]:
        if phrase not in repository:
            errors.append(f"observability persistence repository missing phrase: {phrase}")
    for forbidden in ["hidden_reasoning", "chain_of_thought", "access_token", "api_key", "password"]:
        if forbidden in repository:
            errors.append(f"observability persistence repository contains forbidden phrase: {forbidden}")

    downgrade = _run_with_recorder("downgrade")
    if set(downgrade.dropped_tables) != set(REQUIRED_COLUMNS):
        errors.append(
            "observability migration downgrade does not drop the same table set: "
            f"{sorted(downgrade.dropped_tables)!r}"
        )
    return errors


def main() -> int:
    errors = verify_phase06_observability_persistence()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE06 observability persistence verification failed.")
        return 1
    print("PHASE06 observability persistence verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
