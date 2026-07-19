from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from sqlalchemy import exc, text

from zuno.platform.database.foundation import create_foundation_engine
from zuno.platform.database.ingestion import IngestionPersistenceError, IngestionUnitOfWork


REPO_ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno",
)
HEX_64 = "b" * 64


@pytest.fixture(scope="session", autouse=True)
def migrated_postgres() -> None:
    result = subprocess.run(
        ["alembic", "-c", "infra/db/alembic.ini", "upgrade", "head"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.fixture()
def engine(migrated_postgres):
    engine = create_foundation_engine(DATABASE_URL)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                TRUNCATE
                    ingestion_dead_letters,
                    ingestion_outbox_events,
                    ingestion_indexable_document_snapshots,
                    ingestion_quality_gate_decisions,
                    ingestion_source_spans,
                    ingestion_parse_snapshots,
                    ingestion_parse_attempts,
                    ingestion_parse_jobs,
                    ingestion_parse_plans,
                    ingestion_document_versions,
                    ingestion_source_objects
                RESTART IDENTITY
                """
            )
        )
    try:
        yield engine
    finally:
        engine.dispose()


def test_ingestion_uow_persists_source_to_indexable_snapshot_handoff(engine) -> None:
    with IngestionUnitOfWork(engine) as repo:
        source = repo.record_source_object(
            source_object_id="source:phase11:1",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            filename="policy.md",
            mime_type="text/markdown",
            declared_format="markdown",
            storage_uri="s3://bucket/workspace-a/policy.md",
            object_manifest_ref="manifest:source:phase11:1",
            source_sha256=HEX_64,
            size_bytes=42,
            classification_ref="classification:internal",
            security_epoch_ref="security-epoch:phase11",
        )
        document = repo.record_document_version(
            document_version_id="document-version:phase11:1",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            source_object_id=source.ref,
            version_no=1,
            content_hash=HEX_64,
            metadata={"filename": "policy.md", "mime_type": "text/markdown"},
            immutability_ref="immutability:document-version:phase11:1",
        )
        plan = repo.record_parse_plan(
            parse_plan_id="parse-plan:phase11:1",
            tenant_id="tenant-a",
            document_version_id=document.ref,
            parser_route={"primary": "native_markdown"},
            parser_policy_ref="parser-policy:phase11",
            parser_bundle={"parser": "native_markdown", "version": "v1"},
            quality_policy_ref="quality-policy:phase11",
            security_decision_ref="security-decision:phase11",
        )
        job = repo.record_parse_job(
            parse_job_id="parse-job:phase11:1",
            tenant_id="tenant-a",
            parse_plan_id=plan.ref,
            document_version_id=document.ref,
            idempotency_key="parse:tenant-a:policy-md:v1",
        )
        attempt = repo.record_parse_attempt(
            parse_attempt_id="parse-attempt:phase11:1",
            tenant_id="tenant-a",
            parse_job_id=job.ref,
            attempt_no=1,
            worker_id="worker:phase11",
            lease_ref="lease:phase11:1",
            fencing_token=1,
        )
        snapshot = repo.record_parse_snapshot(
            parse_snapshot_id="parse-snapshot:phase11:1",
            tenant_id="tenant-a",
            parse_job_id=job.ref,
            parse_attempt_id=attempt.ref,
            document_version_id=document.ref,
            canonical_ir={"blocks": [{"block_id": "block:1", "text": "Policy text"}]},
            canonical_ir_ref="canonical-ir:phase11:1",
            canonical_ir_schema_ref="CanonicalDocumentIR:v1",
            parser_id="native_markdown",
            parser_version="v1",
        )
        repo.record_source_span(
            source_span_id="source-span:phase11:1",
            tenant_id="tenant-a",
            parse_snapshot_id=snapshot.ref,
            document_version_id=document.ref,
            block_id="block:1",
            page_no=1,
            coordinate_ref={"line_start": 1, "line_end": 1},
        )
        quality = repo.record_quality_decision(
            quality_decision_id="quality:phase11:1",
            tenant_id="tenant-a",
            parse_snapshot_id=snapshot.ref,
            coverage_score=1.0,
            confidence_score=0.98,
            decision="publish",
        )
        indexable = repo.record_indexable_snapshot(
            indexable_snapshot_id="indexable:phase11:1",
            tenant_id="tenant-a",
            parse_snapshot_id=snapshot.ref,
            document_version_id=document.ref,
            quality_decision_id=quality.ref,
            visibility_ref="visibility:workspace-a:active",
            payload={"source_spans": ["source-span:phase11:1"], "blocks": ["block:1"]},
        )
        outbox = repo.enqueue_outbox_event(
            outbox_event_id="outbox:phase11:1",
            tenant_id="tenant-a",
            aggregate_ref=indexable.ref,
            event_type="ingestion.indexable_snapshot.ready",
            payload={"indexable_snapshot_id": indexable.ref},
        )
        restored = repo.get_indexable_snapshot(indexable.ref)

    assert restored["quality_decision_id"] == quality.ref
    assert restored["knowledge_handoff_status"] == "pending"
    assert outbox.status == "pending"
    with engine.connect() as conn:
        for table in [
            "ingestion_source_objects",
            "ingestion_document_versions",
            "ingestion_parse_plans",
            "ingestion_parse_jobs",
            "ingestion_parse_attempts",
            "ingestion_parse_snapshots",
            "ingestion_source_spans",
            "ingestion_quality_gate_decisions",
            "ingestion_indexable_document_snapshots",
            "ingestion_outbox_events",
        ]:
            assert conn.execute(text(f"SELECT count(*) FROM {table}")).scalar_one() == 1


def test_ingestion_indexable_snapshot_requires_quality_gate(engine) -> None:
    with pytest.raises(exc.IntegrityError):
        with IngestionUnitOfWork(engine) as repo:
            repo.record_indexable_snapshot(
                indexable_snapshot_id="indexable:missing-quality",
                tenant_id="tenant-a",
                parse_snapshot_id="parse-snapshot:missing",
                document_version_id="document-version:missing",
                quality_decision_id="quality:missing",
                visibility_ref="visibility:workspace-a:active",
                payload={"blocks": []},
            )

    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM ingestion_indexable_document_snapshots")).scalar_one() == 0


def test_ingestion_rejects_malformed_source_hash(engine) -> None:
    with pytest.raises(IngestionPersistenceError):
        with IngestionUnitOfWork(engine) as repo:
            repo.record_source_object(
                source_object_id="source:bad-hash",
                tenant_id="tenant-a",
                workspace_id="workspace-a",
                filename="bad.md",
                mime_type="text/markdown",
                storage_uri="s3://bucket/bad.md",
                object_manifest_ref="manifest:bad",
                source_sha256="not-a-sha",
                size_bytes=1,
                classification_ref="classification:internal",
                security_epoch_ref="security-epoch:phase11",
            )
