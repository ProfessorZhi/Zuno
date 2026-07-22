from __future__ import annotations

import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION = REPO_ROOT / "infra/db/alembic/versions/20260719_18_ingestion_source_lineage.py"
SCHEMA_REGISTRY = REPO_ROOT / "src/backend/zuno/platform/database/schema_registry.py"
PERSISTENCE = REPO_ROOT / "src/backend/zuno/platform/database/ingestion/persistence.py"

REVISION = "20260719_18"
DOWN_REVISION = "20260719_17"
EXPECTED_TABLES = {
    "ingestion_dead_letters",
    "ingestion_document_versions",
    "ingestion_indexable_document_snapshots",
    "ingestion_outbox_events",
    "ingestion_parse_attempts",
    "ingestion_parse_jobs",
    "ingestion_parse_plans",
    "ingestion_parse_snapshots",
    "ingestion_quality_gate_decisions",
    "ingestion_source_objects",
    "ingestion_source_spans",
}
REQUIRED_TERMS = [
    "source_sha256",
    "object_manifest_ref",
    "classification_ref",
    "security_epoch_ref",
    "document_version_id",
    "parse_plan_id",
    "parse_job_id",
    "parse_attempt_id",
    "fencing_token",
    "canonical_ir_ref",
    "canonical_ir_schema_ref",
    "source_span_id",
    "quality_decision_id",
    "indexable_snapshot_id",
    "handoff_envelope_hash",
    "ingestion_outbox_events",
    "ingestion_dead_letters",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _created_tables(migration_text: str) -> set[str]:
    tree = ast.parse(migration_text)
    tables: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr != "create_table":
            continue
        if not node.args or not isinstance(node.args[0], ast.Constant):
            continue
        tables.add(str(node.args[0].value))
    return tables


def verify_phase11_ingestion_source_lineage() -> list[str]:
    errors: list[str] = []
    if not MIGRATION.exists():
        return [f"missing migration: {MIGRATION.relative_to(REPO_ROOT)}"]
    if not PERSISTENCE.exists():
        return [f"missing persistence runtime: {PERSISTENCE.relative_to(REPO_ROOT)}"]

    migration = _read(MIGRATION)
    registry = _read(SCHEMA_REGISTRY)
    persistence = _read(PERSISTENCE)

    if f'revision = "{REVISION}"' not in migration:
        errors.append(f"migration missing revision {REVISION}")
    if f'down_revision = "{DOWN_REVISION}"' not in migration:
        errors.append(f"migration must chain after {DOWN_REVISION}")

    created = _created_tables(migration)
    if created != EXPECTED_TABLES:
        errors.append(f"migration table set mismatch: expected={sorted(EXPECTED_TABLES)!r} actual={sorted(created)!r}")

    for table in EXPECTED_TABLES:
        if f'"{table}": "Input / Document Ingestion"' not in registry:
            errors.append(f"schema registry missing Input owner for {table}")
        if f'op.drop_table(table_name)' not in migration:
            errors.append("migration downgrade must drop tables through reverse list")
            break

    if f'"{REVISION}": "Input / Document Ingestion"' not in registry:
        errors.append(f"schema registry missing revision owner for {REVISION}")

    for term in REQUIRED_TERMS:
        if term not in migration:
            errors.append(f"migration missing required ingestion lineage term: {term}")

    for forbidden in [
        "knowledge_chunks",
        "knowledge_versions",
        "entities",
        "relations",
        "vector_index",
        "bm25_index",
    ]:
        if forbidden in migration:
            errors.append(f"Input migration must not own Knowledge artifact: {forbidden}")

    for fk in [
        "fk_ingestion_document_versions_source",
        "fk_ingestion_parse_jobs_plan",
        "fk_ingestion_parse_attempts_job",
        "fk_ingestion_parse_snapshots_attempt",
        "fk_ingestion_source_spans_snapshot",
        "fk_ingestion_indexable_snapshots_quality",
    ]:
        if fk not in migration:
            errors.append(f"migration missing required foreign key: {fk}")

    for term in [
        "class IngestionUnitOfWork",
        "class IngestionRepository",
        "record_source_object",
        "record_document_version",
        "record_parse_plan",
        "record_parse_job",
        "record_parse_attempt",
        "record_parse_snapshot",
        "record_source_span",
        "record_quality_decision",
        "record_indexable_snapshot",
        "enqueue_outbox_event",
        "get_indexable_snapshot",
        "fencing_token",
        "quality_decision_id",
        "handoff_envelope_hash",
    ]:
        if term not in persistence:
            errors.append(f"persistence runtime missing term: {term}")

    return errors


def main() -> int:
    errors = verify_phase11_ingestion_source_lineage()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE11 ingestion source lineage verification failed.")
        return 1
    print("PHASE11 ingestion source lineage verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
