from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import exc, text

from zuno.knowledge.ingestion import DeleteRestoreRuntime, HumanReviewRuntime, ReviewDecisionReceipt, ReviewTask
from zuno.knowledge.ingestion.delete_restore import DeleteLifecycleReceipt
from zuno.platform.database.foundation import create_foundation_engine
from zuno.platform.database.ingestion import IngestionPersistenceError, IngestionUnitOfWork


REPO_ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno?connect_timeout=5",
)
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


def test_ingestion_delete_restore_reconciles_restored_lifecycle_after_restart(engine) -> None:
    runtime = DeleteRestoreRuntime()
    requested = runtime.request_delete(
        snapshot_ref="snapshot:phase11:restore",
        visibility_ref="visibility:workspace-a:restore",
    )
    cleanup = runtime.request_cleanup(requested)
    physical = runtime.mark_physical_delete(cleanup)
    verified = runtime.verify_delete(physical)

    with IngestionUnitOfWork(engine) as repo:
        repo.record_delete_lifecycle(tenant_id="tenant-a", **verified.model_dump())
        loaded = DeleteLifecycleReceipt.model_validate(repo.get_delete_lifecycle(verified.delete_ref))
        restored = runtime.restore(loaded)
        repo.reconcile_delete_lifecycle(restored)
        replayed = repo.get_delete_lifecycle(restored.delete_ref)

    assert replayed["state"] == "restored"
    assert replayed["restored_authorization"] is False
    assert replayed["history"][-1] == "restored"


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
