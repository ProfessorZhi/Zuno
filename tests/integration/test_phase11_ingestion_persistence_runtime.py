from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from minio.error import S3Error
import pytest
from sqlalchemy import exc, text

from zuno.knowledge.ingestion import (
    DeleteLifecycleCommand,
    DeleteRestoreRuntime,
    HumanReviewRuntime,
    PackageAProductionIngestionRuntime,
    PersistentDeleteRestoreCoordinator,
    ReviewDecisionReceipt,
    ReviewTask,
    StaticRestoreAuthorizationPort,
)
from zuno.knowledge.ingestion.delete_restore import DeleteLifecycleReceipt
from zuno.platform.database.foundation import create_foundation_engine
from zuno.platform.database.ingestion import IngestionPersistenceError, IngestionUnitOfWork
from zuno.platform.storage import DurableMinioObjectStore, MinioObjectStore


REPO_ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno?connect_timeout=5",
)
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
HEX_64 = "b" * 64


@pytest.fixture(scope="session", autouse=True)
def migrated_postgres() -> None:
    env = {
        **os.environ,
        "PGCONNECT_TIMEOUT": os.environ.get("PGCONNECT_TIMEOUT", "5"),
        "ZUNO_ALEMBIC_LOCK_TIMEOUT_SECONDS": os.environ.get("ZUNO_ALEMBIC_LOCK_TIMEOUT_SECONDS", "5"),
    }
    result = subprocess.run(
        ["alembic", "-c", "infra/db/alembic.ini", "upgrade", "head"],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
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
                    ingestion_delete_lifecycles,
                    ingestion_review_decision_receipts,
                    ingestion_review_tasks,
                    ingestion_dead_letters,
                    ingestion_outbox_events,
                    ingestion_indexable_document_snapshots,
                    ingestion_quality_gate_decisions,
                    ingestion_source_spans,
                    ingestion_parse_snapshots,
                    ingestion_parse_leases,
                    ingestion_parse_attempts,
                    ingestion_parse_jobs,
                    ingestion_parse_plans,
                    ingestion_document_versions,
                    ingestion_source_objects,
                    infra_outbox_events,
                    infra_outbox_sequences,
                    infra_object_manifests
                RESTART IDENTITY
                """
            )
        )
    try:
        yield engine
    finally:
        engine.dispose()


def test_ingestion_uow_persists_source_to_indexable_snapshot_handoff(engine) -> None:
    from zuno.knowledge.ingestion import DeleteRestoreRuntime

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
        review_task = repo.record_review_task(
            review_task_id="review-task:phase11:1",
            tenant_id="tenant-a",
            parse_snapshot_id=snapshot.ref,
            quality_decision_id=quality.ref,
            document_version_id=document.ref,
            workspace_id="workspace-a",
            reviewer_scope="workspace_reviewer",
            security_epoch_ref="security-epoch:phase11",
            status="pending",
            reason="quality_review_required",
            decision_hash=HEX_64,
            expires_at=1893456000.0,
        )
        review_receipt = repo.record_review_decision_receipt(
            decision_id="review-decision:phase11:1",
            tenant_id="tenant-a",
            review_task_id=review_task.ref,
            status="approved",
            reviewer_id="reviewer:phase11",
            reviewer_scope="workspace_reviewer",
            security_epoch_ref="security-epoch:phase11",
            reason="review_decision_recorded",
            decision_hash=HEX_64,
            decided_at=1893456001.0,
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
        delete_receipt = DeleteRestoreRuntime().verify_delete(
            DeleteRestoreRuntime().mark_physical_delete(
                DeleteRestoreRuntime().confirm_knowledge_cleanup(
                    DeleteRestoreRuntime().request_cleanup(
                        DeleteRestoreRuntime().request_delete_after_snapshot(
                            indexable_snapshot_id=indexable.ref,
                            handoff_outbox_event_id=outbox.ref,
                            visibility_ref="visibility:workspace-a:active",
                            projection_cleanup_ref=f"projection-cleanup:{indexable.ref}",
                        )
                    )
                )
            )
        )
        delete = repo.record_delete_lifecycle(
            tenant_id="tenant-a",
            **delete_receipt.model_dump(),
        )
        restored = repo.get_indexable_snapshot(indexable.ref)
        restored_review_task = repo.get_review_task(review_task.ref)
        restored_review_receipt = repo.get_review_decision_receipt(review_receipt.ref)
        restored_delete = repo.get_delete_lifecycle(delete.ref)

    assert restored["quality_decision_id"] == quality.ref
    assert restored["knowledge_handoff_status"] == "pending"
    assert restored_review_task["quality_decision_id"] == quality.ref
    assert restored_review_task["status"] == "approved"
    assert restored_review_receipt["review_task_id"] == review_task.ref
    assert restored_review_receipt["status"] == "approved"
    assert restored_delete["indexable_snapshot_id"] == indexable.ref
    assert restored_delete["state"] == "verified"
    assert restored_delete["cleanup_verified"] is True
    assert restored_delete["physical_delete_verified"] is True
    assert restored_delete["history"][-1] == "verified"
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
            "ingestion_review_tasks",
            "ingestion_review_decision_receipts",
            "ingestion_indexable_document_snapshots",
            "ingestion_outbox_events",
            "ingestion_delete_lifecycles",
        ]:
            assert conn.execute(text(f"SELECT count(*) FROM {table}")).scalar_one() == 1


def test_ingestion_delete_lifecycle_legal_hold_blocks_physical_delete_ref(engine) -> None:
    from zuno.knowledge.ingestion import DeleteRestoreRuntime

    held = DeleteRestoreRuntime().request_delete(
        snapshot_ref="snapshot:legal-hold",
        visibility_ref="visibility:workspace-a:legal-hold",
        legal_hold_ref="legal-hold:case-1",
    )
    with IngestionUnitOfWork(engine) as repo:
        receipt = repo.record_delete_lifecycle(
            tenant_id="tenant-a",
            **held.model_dump(),
        )
        restored = repo.get_delete_lifecycle(receipt.ref)

    assert restored["state"] == "legal_hold"
    assert restored["legal_hold_ref"] == "legal-hold:case-1"
    assert restored["physical_delete_ref"] is None
    assert restored["restored_authorization"] is False


def test_ingestion_human_review_resume_round_trips_review_task_and_receipt_after_restart(engine) -> None:
    runtime = HumanReviewRuntime(review_ttl_seconds=60)
    task = ReviewTask(
        review_task_id="review-task:resume:1",
        parse_snapshot_id="parse-snapshot:resume:1",
        document_version_id="document-version:resume:1",
        workspace_id="workspace_review",
        reviewer_scope="workspace_reviewer",
        security_epoch_ref="security_epoch:workspace_review",
        expires_at=datetime(2026, 7, 24, 0, 0, tzinfo=timezone.utc).timestamp(),
        reason="quality_review_required",
        decision_hash=HEX_64,
    )

    with IngestionUnitOfWork(engine) as repo:
        source = repo.record_source_object(
            source_object_id="source:resume:1",
            tenant_id="tenant-a",
            workspace_id="workspace_review",
            filename="review.md",
            mime_type="text/markdown",
            storage_uri="s3://bucket/workspace_review/review.md",
            object_manifest_ref="manifest:resume:1",
            source_sha256=HEX_64,
            size_bytes=1,
            classification_ref="classification:internal",
            security_epoch_ref=task.security_epoch_ref,
        )
        document = repo.record_document_version(
            document_version_id=task.document_version_id,
            tenant_id="tenant-a",
            workspace_id=task.workspace_id,
            source_object_id=source.ref,
            version_no=1,
            content_hash=HEX_64,
            metadata={"filename": "review.md"},
            immutability_ref="immutability:resume:1",
        )
        repo.record_parse_plan(
            parse_plan_id="parse-plan:resume:1",
            tenant_id="tenant-a",
            document_version_id=document.ref,
            parser_route={"primary": "native_markdown"},
            parser_policy_ref="parser-policy:resume:1",
            parser_bundle={"parser": "native_markdown", "version": "v1"},
            quality_policy_ref="quality-policy:resume:1",
            security_decision_ref="security-decision:resume:1",
        )
        repo.record_parse_job(
            parse_job_id="parse-job:resume:1",
            tenant_id="tenant-a",
            parse_plan_id="parse-plan:resume:1",
            document_version_id=document.ref,
            idempotency_key="parse:resume:1",
        )
        repo.record_parse_attempt(
            parse_attempt_id="parse-attempt:resume:1",
            tenant_id="tenant-a",
            parse_job_id="parse-job:resume:1",
            attempt_no=1,
            worker_id="worker:resume:1",
            lease_ref="lease:resume:1",
            fencing_token=1,
        )
        repo.record_parse_snapshot(
            parse_snapshot_id=task.parse_snapshot_id,
            tenant_id="tenant-a",
            parse_job_id="parse-job:resume:1",
            parse_attempt_id="parse-attempt:resume:1",
            document_version_id=document.ref,
            canonical_ir={"blocks": [{"block_id": "block:1", "text": "review"}]},
            canonical_ir_ref="canonical-ir:resume:1",
            canonical_ir_schema_ref="CanonicalDocumentIR:v1",
            parser_id="native_markdown",
            parser_version="v1",
        )
        repo.record_quality_decision(
            quality_decision_id="quality:resume:1",
            tenant_id="tenant-a",
            parse_snapshot_id=task.parse_snapshot_id,
            coverage_score=0.98,
            confidence_score=0.88,
            decision="human_review",
        )
        repo.record_review_task(
            review_task_id=task.review_task_id,
            tenant_id="tenant-a",
            parse_snapshot_id=task.parse_snapshot_id,
            quality_decision_id="quality:resume:1",
            document_version_id=task.document_version_id,
            workspace_id=task.workspace_id,
            reviewer_scope=task.reviewer_scope,
            security_epoch_ref=task.security_epoch_ref,
            status=task.status,
            reason=task.reason,
            decision_hash=task.decision_hash,
            expires_at=task.expires_at,
        )
        receipt = runtime.decide(
            task=task,
            reviewer_id="reviewer:phase11",
            reviewer_scope=task.reviewer_scope,
            status="approved",
            security_epoch_ref=task.security_epoch_ref,
        )
        repo.record_review_decision_receipt(
            decision_id=receipt.decision_id,
            tenant_id="tenant-a",
            review_task_id=receipt.review_task_id,
            status=receipt.status,
            reviewer_id=receipt.reviewer_id,
            reviewer_scope=receipt.reviewer_scope,
            security_epoch_ref=receipt.security_epoch_ref,
            reason=receipt.reason,
            decision_hash=receipt.decision_hash,
            decided_at=receipt.decided_at,
        )
        loaded_task_row = repo.get_review_task(task.review_task_id)
        loaded_receipt_row = repo.get_review_decision_receipt(receipt.decision_id)
        loaded_task = ReviewTask(
            review_task_id=str(loaded_task_row["review_task_id"]),
            parse_snapshot_id=str(loaded_task_row["parse_snapshot_id"]),
            document_version_id=str(loaded_task_row["document_version_id"]),
            workspace_id=str(loaded_task_row["workspace_id"]),
            reviewer_scope=str(loaded_task_row["reviewer_scope"]),
            security_epoch_ref=str(loaded_task_row["security_epoch_ref"]),
            status=str(loaded_task_row["status"]),
            expires_at=loaded_task_row["expires_at"].timestamp(),
            reason=str(loaded_task_row["reason"]),
            decision_hash=str(loaded_task_row["decision_hash"]),
        )
        loaded_receipt = ReviewDecisionReceipt(
            review_task_id=str(loaded_receipt_row["review_task_id"]),
            decision_id=str(loaded_receipt_row["decision_id"]),
            status=str(loaded_receipt_row["status"]),
            reviewer_id=str(loaded_receipt_row["reviewer_id"]),
            reviewer_scope=str(loaded_receipt_row["reviewer_scope"]),
            security_epoch_ref=str(loaded_receipt_row["security_epoch_ref"]),
            decision_hash=str(loaded_receipt_row["decision_hash"]),
            reason=str(loaded_receipt_row["reason"]),
            decided_at=loaded_receipt_row["decided_at"].timestamp(),
        )
        resumed = runtime.decide(
            task=loaded_task,
            reviewer_id=loaded_receipt.reviewer_id,
            reviewer_scope=loaded_receipt.reviewer_scope,
            status="approved",
            security_epoch_ref=loaded_receipt.security_epoch_ref,
            existing_receipt=loaded_receipt,
        )

    assert resumed.duplicate is True
    assert resumed.decision_hash == receipt.decision_hash


def test_ingestion_approved_review_resume_persists_snapshot_and_outbox_once(engine) -> None:
    runtime = PackageAProductionIngestionRuntime(
        engine=engine,
        object_store=None,
        worker_id="phase11-package-a-worker",
    )
    document_version_id = "document-version:approved-resume:1"
    source_object_id = "source:approved-resume:1"
    workspace_id = "workspace_review"
    security_epoch_ref = "security_epoch:workspace_review"
    document_payload = {
        "metadata": {
            "document_id": source_object_id,
            "source_id": source_object_id,
            "source_object_ref": "s3://bucket/tenant-a/workspace_review/review.md",
            "object_manifest_ref": "manifest:approved-resume:1",
            "workspace_id": workspace_id,
            "source_uri": "s3://bucket/tenant-a/workspace_review/review.md",
            "mime_type": "text/markdown",
            "hash": HEX_64,
            "source_sha256": HEX_64,
            "parser_id": "native_markdown",
            "parser_version": "phase11-package-a-v1",
            "document_version_id": document_version_id,
            "security_epoch_ref": security_epoch_ref,
        },
        "blocks": [
            {
                "block_id": "block-low-confidence",
                "type": "paragraph",
                "text": "Low confidence parse result.",
                "source_span": {"page": 1, "line_range": [1, 1]},
                "confidence": 0.5,
            }
        ],
        "tables": [],
        "figures": [],
        "transform_ledger": [],
        "provenance": {
            "parser_id": "native_markdown",
            "parser_version": "phase11-package-a-v1",
            "source_uri": "s3://bucket/tenant-a/workspace_review/review.md",
            "confidence": 0.5,
        },
    }
    task = ReviewTask(
        review_task_id="review-task:approved-resume:1",
        parse_snapshot_id="parse-snapshot:approved-resume:1",
        document_version_id=document_version_id,
        workspace_id=workspace_id,
        reviewer_scope="workspace_reviewer",
        security_epoch_ref=security_epoch_ref,
        expires_at=datetime(2026, 7, 24, 0, 0, tzinfo=timezone.utc).timestamp(),
        reason="quality_review_required",
        decision_hash=HEX_64,
    )

    with IngestionUnitOfWork(engine) as repo:
        source = repo.record_source_object(
            source_object_id=source_object_id,
            tenant_id="tenant-a",
            workspace_id=workspace_id,
            filename="review.md",
            mime_type="text/markdown",
            storage_uri="s3://bucket/tenant-a/workspace_review/review.md",
            object_manifest_ref="manifest:approved-resume:1",
            source_sha256=HEX_64,
            size_bytes=1,
            classification_ref="classification:internal",
            security_epoch_ref=security_epoch_ref,
        )
        repo.record_document_version(
            document_version_id=document_version_id,
            tenant_id="tenant-a",
            workspace_id=workspace_id,
            source_object_id=source.ref,
            version_no=1,
            content_hash=HEX_64,
            metadata={"filename": "review.md"},
            immutability_ref="immutability:approved-resume:1",
        )
        repo.record_parse_plan(
            parse_plan_id="parse-plan:approved-resume:1",
            tenant_id="tenant-a",
            document_version_id=document_version_id,
            parser_route={"primary": "native_markdown"},
            parser_policy_ref="parser-policy:approved-resume:1",
            parser_bundle={"parser": "native_markdown", "version": "v1"},
            quality_policy_ref="quality-policy:approved-resume:1",
            security_decision_ref="security-decision:approved-resume:1",
        )
        repo.record_parse_job(
            parse_job_id="parse-job:approved-resume:1",
            tenant_id="tenant-a",
            parse_plan_id="parse-plan:approved-resume:1",
            document_version_id=document_version_id,
            idempotency_key="parse:approved-resume:1",
        )
        repo.record_parse_attempt(
            parse_attempt_id="parse-attempt:approved-resume:1",
            tenant_id="tenant-a",
            parse_job_id="parse-job:approved-resume:1",
            attempt_no=1,
            worker_id="worker:approved-resume:1",
            lease_ref="lease:approved-resume:1",
            fencing_token=1,
        )
        snapshot = repo.record_parse_snapshot(
            parse_snapshot_id=task.parse_snapshot_id,
            tenant_id="tenant-a",
            parse_job_id="parse-job:approved-resume:1",
            parse_attempt_id="parse-attempt:approved-resume:1",
            document_version_id=document_version_id,
            canonical_ir=document_payload,
            canonical_ir_ref="canonical-ir:approved-resume:1",
            canonical_ir_schema_ref="canonical-document-ir-v1",
            parser_id="native_markdown",
            parser_version="phase11-package-a-v1",
        )
        quality = repo.record_quality_decision(
            quality_decision_id="quality:approved-resume:1",
            tenant_id="tenant-a",
            parse_snapshot_id=snapshot.ref,
            coverage_score=0.98,
            confidence_score=0.88,
            decision="human_review",
            review_task_ref=task.review_task_id,
        )
        repo.record_review_task(
            review_task_id=task.review_task_id,
            tenant_id="tenant-a",
            parse_snapshot_id=snapshot.ref,
            quality_decision_id=quality.ref,
            document_version_id=document_version_id,
            workspace_id=workspace_id,
            reviewer_scope=task.reviewer_scope,
            security_epoch_ref=security_epoch_ref,
            status=task.status,
            reason=task.reason,
            decision_hash=task.decision_hash,
            expires_at=task.expires_at,
        )
        receipt = HumanReviewRuntime(review_ttl_seconds=60).decide(
            task=task,
            reviewer_id="reviewer:approved-resume",
            reviewer_scope=task.reviewer_scope,
            status="approved",
            security_epoch_ref=security_epoch_ref,
            now=task.expires_at - 1,
        )
        repo.record_review_decision_receipt(
            decision_id=receipt.decision_id,
            tenant_id="tenant-a",
            review_task_id=receipt.review_task_id,
            status=receipt.status,
            reviewer_id=receipt.reviewer_id,
            reviewer_scope=receipt.reviewer_scope,
            security_epoch_ref=receipt.security_epoch_ref,
            reason=receipt.reason,
            decision_hash=receipt.decision_hash,
            decided_at=receipt.decided_at,
        )

    first = runtime.resume_approved_review(
        tenant_id="tenant-a",
        review_task_id=task.review_task_id,
        decision_id=receipt.decision_id,
    )
    second = runtime.resume_approved_review(
        tenant_id="tenant-a",
        review_task_id=task.review_task_id,
        decision_id=receipt.decision_id,
    )

    assert first.status == "succeeded"
    assert first.acked_after_domain_commit is True
    assert first.indexable_snapshot_id is not None
    assert first.outbox_event_id is not None
    assert second.indexable_snapshot_id == first.indexable_snapshot_id
    assert second.outbox_event_id == first.outbox_event_id
    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM ingestion_indexable_document_snapshots")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM ingestion_outbox_events")).scalar_one() == 1
        persisted = conn.execute(
            text(
                """
                SELECT canonical_ir_json
                FROM ingestion_parse_snapshots
                WHERE parse_snapshot_id = :parse_snapshot_id
                """
            ),
            {"parse_snapshot_id": task.parse_snapshot_id},
        ).mappings().one()
        assert persisted["canonical_ir_json"]["metadata"]["document_version_id"] == document_version_id


def test_ingestion_delete_restore_reconciles_restored_lifecycle_after_restart(engine) -> None:
    runtime = DeleteRestoreRuntime()
    requested = runtime.request_delete(
        snapshot_ref="snapshot:phase11:restore",
        visibility_ref="visibility:workspace-a:restore",
    )
    cleanup = runtime.request_cleanup(requested)
    confirmed = runtime.confirm_knowledge_cleanup(cleanup)
    physical = runtime.mark_physical_delete(confirmed)
    verified = runtime.verify_delete(physical)

    with IngestionUnitOfWork(engine) as repo:
        repo.record_delete_lifecycle(tenant_id="tenant-a", **verified.model_dump())
        loaded = DeleteLifecycleReceipt.model_validate(repo.get_delete_lifecycle(verified.delete_ref))
        restored = runtime.restore(loaded, restore_authorization_ref="restore-auth:phase11:restore")
        repo.reconcile_delete_lifecycle(restored)
        replayed = repo.get_delete_lifecycle(restored.delete_ref)

    assert replayed["state"] == "restored"
    assert replayed["restored_authorization"] is True
    assert replayed["restore_authorization_ref"] == "restore-auth:phase11:restore"
    assert replayed["history"][-1] == "restored"


def test_ingestion_delete_restore_coordinator_deletes_verifies_and_restores_real_object(engine) -> None:
    content = b"phase11 durable delete restore"
    bucket = f"phase11-delete-{uuid4().hex}"
    raw_store = MinioObjectStore(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
    )
    durable_store = DurableMinioObjectStore(
        store=raw_store,
        engine=engine,
        owner="phase11-delete-restore-test",
    )
    try:
        ticket = durable_store.stage(
            bucket=bucket,
            committed_object_name="workspace-a/delete-target.md",
            content=content,
        )
        committed = durable_store.commit(ticket)
        object_ref = f"s3://{bucket}/{committed.object_name}"
        with IngestionUnitOfWork(engine) as repo:
            source = repo.record_source_object(
                source_object_id="source:phase11:delete-real-object",
                tenant_id="tenant-a",
                workspace_id="workspace-a",
                filename="delete-target.md",
                mime_type="text/markdown",
                storage_uri=object_ref,
                object_manifest_ref=f"manifest:{object_ref}",
                source_sha256=committed.content_hash,
                size_bytes=committed.size_bytes,
                classification_ref="classification:internal",
                security_epoch_ref="security-epoch:phase11-delete",
            )
            document = repo.record_document_version(
                document_version_id="document-version:phase11:delete-real-object",
                tenant_id="tenant-a",
                workspace_id="workspace-a",
                source_object_id=source.ref,
                version_no=1,
                content_hash=committed.content_hash,
                metadata={"filename": "delete-target.md"},
                immutability_ref="immutability:phase11:delete-real-object",
            )
            plan = repo.record_parse_plan(
                parse_plan_id="parse-plan:phase11:delete-real-object",
                tenant_id="tenant-a",
                document_version_id=document.ref,
                parser_route={"primary": "native_markdown"},
                parser_policy_ref="parser-policy:phase11-delete",
                parser_bundle={"parser": "native_markdown", "version": "v1"},
                quality_policy_ref="quality-policy:phase11-delete",
                security_decision_ref="security-decision:phase11-delete",
            )
            job = repo.record_parse_job(
                parse_job_id="parse-job:phase11:delete-real-object",
                tenant_id="tenant-a",
                parse_plan_id=plan.ref,
                document_version_id=document.ref,
                idempotency_key="parse:phase11:delete-real-object",
            )
            attempt = repo.record_parse_attempt(
                parse_attempt_id="parse-attempt:phase11:delete-real-object",
                tenant_id="tenant-a",
                parse_job_id=job.ref,
                attempt_no=1,
                worker_id="worker:phase11-delete",
                lease_ref="lease:phase11-delete",
                fencing_token=1,
            )
            snapshot = repo.record_parse_snapshot(
                parse_snapshot_id="parse-snapshot:phase11:delete-real-object",
                tenant_id="tenant-a",
                parse_job_id=job.ref,
                parse_attempt_id=attempt.ref,
                document_version_id=document.ref,
                canonical_ir={"metadata": {"document_id": source.ref}, "blocks": []},
                canonical_ir_ref="canonical-ir:phase11-delete",
                canonical_ir_schema_ref="canonical-document-ir-v1",
                parser_id="native_markdown",
                parser_version="v1",
            )
            quality = repo.record_quality_decision(
                quality_decision_id="quality:phase11:delete-real-object",
                tenant_id="tenant-a",
                parse_snapshot_id=snapshot.ref,
                coverage_score=1.0,
                confidence_score=1.0,
                decision="publish",
            )
            repo.record_indexable_snapshot(
                indexable_snapshot_id="snapshot:phase11:delete-real-object",
                tenant_id="tenant-a",
                parse_snapshot_id=snapshot.ref,
                document_version_id=document.ref,
                quality_decision_id=quality.ref,
                visibility_ref="visibility:workspace-a:delete-real-object",
                payload={"object_ref": object_ref},
                handoff_idempotency_key="handoff:phase11:delete-real-object",
            )
        coordinator = PersistentDeleteRestoreCoordinator(
            engine=engine,
            object_store=durable_store,
        )

        requested = coordinator.request_delete_after_snapshot(
            DeleteLifecycleCommand(
                tenant_id="tenant-a",
                snapshot_ref="snapshot:phase11:delete-real-object",
                indexable_snapshot_id="snapshot:phase11:delete-real-object",
                handoff_outbox_event_id="outbox:snapshot:phase11:delete-real-object",
                visibility_ref="visibility:workspace-a:delete-real-object",
                object_ref=object_ref,
                restore_point_name="_restore/workspace-a/delete-target.md",
                projection_cleanup_ref="projection-cleanup:snapshot:phase11:delete-real-object",
            )
        )
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    UPDATE infra_outbox_events
                    SET status = 'published'
                    WHERE event_id = :event_id
                    """
                ),
                {"event_id": f"outbox:{requested.delete_ref}:cleanup"},
            )
        with pytest.raises(ValueError, match="knowledge cleanup confirmation"):
            coordinator.execute_cleanup(
                tenant_id="tenant-a",
                delete_ref=requested.delete_ref,
            )

        confirmed = coordinator.confirm_knowledge_cleanup(
            tenant_id="tenant-a",
            delete_ref=requested.delete_ref,
            cleanup_ref=requested.cleanup_ref,
        )
        verified = coordinator.execute_cleanup(
            tenant_id="tenant-a",
            delete_ref=confirmed.delete_ref,
        )

        assert verified.state == "verified"
        assert verified.cleanup_verified is True
        assert verified.physical_delete_verified is True
        assert "knowledge_cleanup_confirmed" in verified.history
        with pytest.raises(S3Error):
            raw_store.read_object(bucket=bucket, object_name=committed.object_name)

        with pytest.raises(ValueError, match="fresh authorization"):
            coordinator.restore_deleted(
                tenant_id="tenant-a",
                delete_ref=requested.delete_ref,
            )
        coordinator.authorization_port = StaticRestoreAuthorizationPort(
            revoked_refs=frozenset({"restore-auth:phase11:revoked"}),
        )
        with pytest.raises(ValueError, match="restore_authorization_revoked"):
            coordinator.restore_deleted(
                tenant_id="tenant-a",
                delete_ref=requested.delete_ref,
                restore_authorization_ref="restore-auth:phase11:revoked",
            )
        with pytest.raises(S3Error):
            raw_store.read_object(bucket=bucket, object_name=committed.object_name)
        coordinator.authorization_port = StaticRestoreAuthorizationPort()

        restored = coordinator.restore_deleted(
            tenant_id="tenant-a",
            delete_ref=requested.delete_ref,
            restore_authorization_ref="restore-auth:phase11:delete-real-object",
        )
        duplicate_restore = coordinator.restore_deleted(
            tenant_id="tenant-a",
            delete_ref=requested.delete_ref,
            restore_authorization_ref="restore-auth:phase11:delete-real-object",
        )

        assert restored.state == "restored"
        assert restored.restored_authorization is True
        assert restored.restore_authorization_ref == "restore-auth:phase11:delete-real-object"
        assert duplicate_restore.duplicate is True
        assert raw_store.read_object(bucket=bucket, object_name=committed.object_name) == content
        with engine.connect() as conn:
            lifecycle = conn.execute(
                text(
                    """
                    SELECT state, object_ref, restore_point_name, cleanup_verified,
                           physical_delete_verified, restored_authorization,
                           restore_authorization_ref, duplicate
                    FROM ingestion_delete_lifecycles
                    WHERE delete_ref = :delete_ref
                    """
                ),
                {"delete_ref": requested.delete_ref},
            ).mappings().one()
            outbox = conn.execute(
                text(
                    """
                    SELECT topic, status, payload ->> 'object_ref' AS object_ref
                    FROM infra_outbox_events
                    WHERE event_id = :event_id
                    """
                ),
                {"event_id": f"outbox:{requested.delete_ref}:cleanup"},
            ).mappings().one()
            manifest = conn.execute(
                text(
                    """
                    SELECT visibility
                    FROM infra_object_manifests
                    WHERE object_ref = :object_ref
                    """
                ),
                {"object_ref": object_ref},
            ).mappings().one()
        assert lifecycle["state"] == "restored"
        assert lifecycle["object_ref"] == object_ref
        assert lifecycle["restore_point_name"] == "_restore/workspace-a/delete-target.md"
        assert lifecycle["cleanup_verified"] is True
        assert lifecycle["physical_delete_verified"] is True
        assert lifecycle["restored_authorization"] is True
        assert lifecycle["restore_authorization_ref"] == "restore-auth:phase11:delete-real-object"
        assert lifecycle["duplicate"] is True
        assert outbox["topic"] == PersistentDeleteRestoreCoordinator.cleanup_topic
        assert outbox["status"] == "published"
        assert outbox["object_ref"] == object_ref
        assert manifest["visibility"] == "restored"
    finally:
        raw_store.remove_bucket_tree(bucket)


def test_ingestion_review_decision_requires_review_task(engine) -> None:
    with pytest.raises(exc.IntegrityError):
        with IngestionUnitOfWork(engine) as repo:
            repo.record_review_decision_receipt(
                decision_id="review-decision:missing-task",
                tenant_id="tenant-a",
                review_task_id="review-task:missing",
                status="approved",
                reviewer_id="reviewer:phase11",
                reviewer_scope="workspace_reviewer",
                security_epoch_ref="security-epoch:phase11",
                reason="review_decision_recorded",
                decision_hash=HEX_64,
                decided_at=1893456001.0,
            )

    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM ingestion_review_decision_receipts")).scalar_one() == 0


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


def test_ingestion_uow_rolls_back_source_when_later_domain_write_fails(engine) -> None:
    with pytest.raises(IngestionPersistenceError):
        with IngestionUnitOfWork(engine) as repo:
            source = repo.record_source_object(
                source_object_id="source:rollback",
                tenant_id="tenant-a",
                workspace_id="workspace-a",
                filename="rollback.md",
                mime_type="text/markdown",
                storage_uri="s3://bucket/rollback.md",
                object_manifest_ref="manifest:rollback",
                source_sha256=HEX_64,
                size_bytes=9,
                classification_ref="classification:internal",
                security_epoch_ref="security-epoch:phase11",
            )
            repo.record_document_version(
                document_version_id="document-version:rollback",
                tenant_id="tenant-a",
                workspace_id="workspace-a",
                source_object_id=source.ref,
                version_no=1,
                content_hash="bad-content-hash",
                metadata={"filename": "rollback.md"},
                immutability_ref="immutability:rollback",
            )

    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM ingestion_source_objects")).scalar_one() == 0
        assert conn.execute(text("SELECT count(*) FROM ingestion_document_versions")).scalar_one() == 0


def test_ingestion_parse_job_idempotency_conflict_is_tenant_scoped(engine) -> None:
    with IngestionUnitOfWork(engine) as repo:
        source = repo.record_source_object(
            source_object_id="source:idempotency",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            filename="idem.md",
            mime_type="text/markdown",
            storage_uri="s3://bucket/idem.md",
            object_manifest_ref="manifest:idempotency",
            source_sha256=HEX_64,
            size_bytes=12,
            classification_ref="classification:internal",
            security_epoch_ref="security-epoch:phase11",
        )
        document = repo.record_document_version(
            document_version_id="document-version:idempotency",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            source_object_id=source.ref,
            version_no=1,
            content_hash=HEX_64,
            metadata={"filename": "idem.md"},
            immutability_ref="immutability:idempotency",
        )
        plan = repo.record_parse_plan(
            parse_plan_id="parse-plan:idempotency",
            tenant_id="tenant-a",
            document_version_id=document.ref,
            parser_route={"primary": "native_markdown"},
            parser_policy_ref="parser-policy:idempotency",
            parser_bundle={"parser": "native_markdown", "version": "v1"},
            quality_policy_ref="quality-policy:idempotency",
            security_decision_ref="security-decision:idempotency",
        )
        repo.record_parse_job(
            parse_job_id="parse-job:idempotency:1",
            tenant_id="tenant-a",
            parse_plan_id=plan.ref,
            document_version_id=document.ref,
            idempotency_key="parse:tenant-a:idem:v1",
        )

    with pytest.raises(exc.IntegrityError):
        with IngestionUnitOfWork(engine) as repo:
            repo.record_parse_job(
                parse_job_id="parse-job:idempotency:duplicate",
                tenant_id="tenant-a",
                parse_plan_id="parse-plan:idempotency",
                document_version_id="document-version:idempotency",
                idempotency_key="parse:tenant-a:idem:v1",
            )

    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM ingestion_parse_jobs")).scalar_one() == 1
