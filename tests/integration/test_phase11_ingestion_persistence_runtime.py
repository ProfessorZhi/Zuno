from __future__ import annotations

import asyncio
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
    KnowledgeCleanupReceipt,
    PackageAProductionIngestionRuntime,
    PersistentDeleteRestoreCoordinator,
    ReviewDecisionReceipt,
    ReviewTask,
    StaticRestoreAuthorizationPort,
    StaticReviewDecisionAuthorizationPort,
    VisibilityRevocationReceipt,
)
from zuno.knowledge.ingestion.delete_restore import DeleteLifecycleReceipt
from zuno.platform.database.foundation import InfrastructureUnitOfWork, create_foundation_engine
from zuno.platform.database.ingestion import IngestionPersistenceError, IngestionUnitOfWork
from zuno.platform.queue import PostgresOutboxRabbitMQPublisher, RabbitMQTopology, RabbitMQTransport
from zuno.platform.storage.object_store import ObjectAuthorizationError
from zuno.platform.storage import DurableMinioObjectStore, MinioObjectStore


REPO_ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno?connect_timeout=5",
)
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"
HEX_64 = "b" * 64


class _DenyVisibilityRevocationPort:
    def revoke_visibility(self, *, tenant_id, receipt):
        return VisibilityRevocationReceipt(
            tenant_id=tenant_id,
            delete_ref=receipt.delete_ref,
            visibility_ref=receipt.visibility_ref,
            revoked=False,
            reason="visibility_revocation_denied",
        )


class _DenyKnowledgeCleanupPort:
    def require_cleanup_confirmed(self, receipt):
        return KnowledgeCleanupReceipt(
            delete_ref=receipt.delete_ref,
            cleanup_ref=receipt.cleanup_ref,
            confirmed=False,
            reason="knowledge_cleanup_port_denied",
        )


class _FailAfterPhysicalDeleteAuditPort:
    def record_delete_event(self, *, tenant_id, delete_ref, event_type, payload):
        if event_type == "delete_physical_absence_verified":
            raise RuntimeError("simulated_domain_commit_failure_after_minio_delete")
        return {
            "tenant_id": tenant_id,
            "delete_ref": delete_ref,
            "event_type": event_type,
            "recorded": True,
        }


def _cleanup_topology() -> RabbitMQTopology:
    suffix = uuid4().hex
    return RabbitMQTopology(
        exchange=f"phase11.delete.cleanup.exchange.{suffix}",
        queue=f"phase11.delete.cleanup.queue.{suffix}",
        routing_key=f"phase11.delete.cleanup.route.{suffix}",
        dead_letter_exchange=f"phase11.delete.cleanup.dlx.{suffix}",
        dead_letter_queue=f"phase11.delete.cleanup.dlq.{suffix}",
        dead_letter_routing_key=f"phase11.delete.cleanup.dead.{suffix}",
    )


async def _publish_and_ack_cleanup_contract(*, engine, event_id: str) -> dict:
    topology = _cleanup_topology()
    async with RabbitMQTransport(RABBITMQ_URL) as transport:
        await transport.declare_topology(topology)
        try:
            publisher = PostgresOutboxRabbitMQPublisher(
                engine=engine,
                transport=transport,
                topology=topology,
                worker_id="phase11-delete-cleanup-publisher",
                tenant_id="tenant-a",
                trace_id="trace-phase11-delete-cleanup",
                topics=(PersistentDeleteRestoreCoordinator.cleanup_topic,),
            )
            published = await publisher.publish_pending(limit=1)
            assert [item.event_id for item in published] == [event_id]
            delivery = await transport.get(topology.queue, timeout=5.0)
            assert delivery is not None
            await delivery.ack()
            payload = delivery.payload
            assert payload["event_id"] == event_id
            assert payload["topic"] == PersistentDeleteRestoreCoordinator.cleanup_topic
            return dict(payload["payload"])
        finally:
            await transport.delete_topology(topology)


async def _publish_cleanup_then_replay_after_crash(*, engine, event_id: str) -> tuple[dict, dict]:
    topology = _cleanup_topology()
    async with RabbitMQTransport(RABBITMQ_URL) as transport:
        await transport.declare_topology(topology)
        try:
            with InfrastructureUnitOfWork(engine) as repo:
                assert repo.claim_outbox_event(event_id=event_id, worker_id="phase11-delete-crashed-publisher")
                record = repo.load_claimed_outbox_event(
                    event_id=event_id,
                    worker_id="phase11-delete-crashed-publisher",
                )
            await transport.publish(
                topology,
                message_id=record.event_id,
                payload={
                    "aggregate_id": record.aggregate_id,
                    "event_id": record.event_id,
                    "idempotency_key": record.idempotency_key,
                    "payload": record.payload,
                    "payload_hash": record.payload_hash,
                    "topic": record.topic,
                },
                tenant_id="tenant-a",
                trace_id="trace-phase11-delete-cleanup-crash",
                ordering_key=record.ordering_key,
                ordering_sequence=record.ordering_sequence,
                outbox_publish_attempt=record.publish_attempts + 1,
                outbox_retry_count=record.retry_count,
                outbox_replay_count=record.replay_count,
            )
            first_delivery = await transport.get(topology.queue, timeout=5.0)
            assert first_delivery is not None
            first_payload = dict(first_delivery.payload)
            with InfrastructureUnitOfWork(engine) as repo:
                first_hash = repo.record_inbox(
                    consumer="phase11-delete-cleanup-consumer",
                    message_id=first_delivery.message_id,
                    payload=first_delivery.payload,
                )
            await first_delivery.ack()

            with engine.begin() as conn:
                conn.execute(
                    text(
                        """
                        UPDATE infra_outbox_events
                        SET claimed_at = now() - interval '5 minutes'
                        WHERE event_id = :event_id
                        """
                    ),
                    {"event_id": event_id},
                )
            with InfrastructureUnitOfWork(engine) as repo:
                assert repo.reclaim_stale_outbox_claims(older_than_seconds=1) == [event_id]

            publisher = PostgresOutboxRabbitMQPublisher(
                engine=engine,
                transport=transport,
                topology=topology,
                worker_id="phase11-delete-cleanup-replay-publisher",
                tenant_id="tenant-a",
                trace_id="trace-phase11-delete-cleanup-replay",
                topics=(PersistentDeleteRestoreCoordinator.cleanup_topic,),
            )
            assert [item.event_id for item in await publisher.publish_pending(limit=1)] == [event_id]
            replay_delivery = await transport.get(topology.queue, timeout=5.0)
            assert replay_delivery is not None
            replay_payload = dict(replay_delivery.payload)
            with InfrastructureUnitOfWork(engine) as repo:
                assert (
                    repo.record_inbox(
                        consumer="phase11-delete-cleanup-consumer",
                        message_id=replay_delivery.message_id,
                        payload=replay_delivery.payload,
                    )
                    == first_hash
                )
            await replay_delivery.ack()
            return first_payload, replay_payload
        finally:
            await transport.delete_topology(topology)


async def _publish_cleanup_to_dlq_then_replay(*, engine, event_id: str) -> tuple[dict, dict]:
    topology = _cleanup_topology()
    async with RabbitMQTransport(RABBITMQ_URL) as transport:
        await transport.declare_topology(topology)
        try:
            publisher = PostgresOutboxRabbitMQPublisher(
                engine=engine,
                transport=transport,
                topology=topology,
                worker_id="phase11-delete-cleanup-dlq-publisher",
                tenant_id="tenant-a",
                trace_id="trace-phase11-delete-cleanup-dlq",
                topics=(PersistentDeleteRestoreCoordinator.cleanup_topic,),
            )
            assert [item.event_id for item in await publisher.publish_pending(limit=1)] == [event_id]
            delivery = await transport.get(topology.queue, timeout=5.0)
            assert delivery is not None
            await transport.retry_or_dead_letter(
                topology,
                delivery,
                max_attempts=1,
                retry_trace_id="trace-phase11-delete-cleanup-dlq-dead-letter",
            )
            dlq_delivery = await transport.get(topology.dead_letter_queue, timeout=5.0)
            assert dlq_delivery is not None
            dead_letter_payload = dict(dlq_delivery.payload)
            await transport.replay_dead_letter(
                topology,
                dlq_delivery,
                replay_trace_id="trace-phase11-delete-cleanup-dlq-replay",
            )
            await dlq_delivery.ack()
            replay_delivery = await transport.get(topology.queue, timeout=5.0)
            assert replay_delivery is not None
            replay_payload = dict(replay_delivery.payload)
            await replay_delivery.ack()
            assert replay_delivery.headers["replayed_from_dlq"] is True
            assert int(replay_delivery.headers["outbox_replay_count"]) >= 1
            return dead_letter_payload, replay_payload
        finally:
            await transport.delete_topology(topology)


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


def test_ingestion_parse_attempt_can_wait_for_human_review_without_failure(engine) -> None:
    with IngestionUnitOfWork(engine) as repo:
        source = repo.record_source_object(
            source_object_id="source:review-pending:1",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            filename="review-pending.md",
            mime_type="text/markdown",
            storage_uri="s3://bucket/workspace-a/review-pending.md",
            object_manifest_ref="manifest:review-pending:1",
            source_sha256=HEX_64,
            size_bytes=42,
            classification_ref="classification:internal",
            security_epoch_ref="security-epoch:review-pending",
        )
        document = repo.record_document_version(
            document_version_id="document-version:review-pending:1",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            source_object_id=source.ref,
            version_no=1,
            content_hash=HEX_64,
            metadata={"filename": "review-pending.md"},
            immutability_ref="immutability:review-pending:1",
        )
        plan = repo.record_parse_plan(
            parse_plan_id="parse-plan:review-pending:1",
            tenant_id="tenant-a",
            document_version_id=document.ref,
            parser_route={"primary": "native_markdown"},
            parser_policy_ref="parser-policy:review-pending",
            parser_bundle={"parser": "native_markdown", "version": "v1"},
            quality_policy_ref="quality-policy:review-pending",
            security_decision_ref="security-decision:review-pending",
        )
        job = repo.record_parse_job(
            parse_job_id="parse-job:review-pending:1",
            tenant_id="tenant-a",
            parse_plan_id=plan.ref,
            document_version_id=document.ref,
            idempotency_key="parse:tenant-a:review-pending:v1",
        )
        attempt = repo.claim_parse_attempt_lease(
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            source_object_id=source.ref,
            document_version_id=document.ref,
            parse_plan_id=plan.ref,
            parse_job_id=job.ref,
            worker_id="worker:review-pending",
            idempotency_key="parse:tenant-a:review-pending:v1:attempt:1",
            security_epoch_ref="security-epoch:review-pending",
            lease_ttl_seconds=60,
        )
        fencing_token = int(attempt.payload_hash or "0")
        repo.mark_parse_attempt_running(
            parse_attempt_id=attempt.ref,
            parse_job_id=job.ref,
            tenant_id="tenant-a",
            worker_id="worker:review-pending",
            fencing_token=fencing_token,
        )
        repo.mark_parse_attempt_review_pending(
            parse_attempt_id=attempt.ref,
            parse_job_id=job.ref,
            tenant_id="tenant-a",
            worker_id="worker:review-pending",
            fencing_token=fencing_token,
        )

    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT attempt.status AS attempt_status,
                       attempt.failure_code AS failure_code,
                       lease.state AS lease_state,
                       job.status AS job_status
                FROM ingestion_parse_attempts AS attempt
                JOIN ingestion_parse_leases AS lease
                  ON lease.parse_attempt_id = attempt.parse_attempt_id
                JOIN ingestion_parse_jobs AS job
                  ON job.parse_job_id = attempt.parse_job_id
                WHERE attempt.parse_attempt_id = :parse_attempt_id
                """
            ),
            {"parse_attempt_id": attempt.ref},
        ).mappings().one()

    assert row["attempt_status"] == "review_pending"
    assert row["failure_code"] is None
    assert row["lease_state"] == "released"
    assert row["job_status"] == "review_pending"


def test_ingestion_review_decision_revoked_reviewer_rejects_without_handoff(engine) -> None:
    runtime = HumanReviewRuntime(
        review_ttl_seconds=60,
        authorization_port=StaticReviewDecisionAuthorizationPort(
            revoked_reviewer_ids=frozenset({"reviewer:revoked"})
        ),
    )
    task = ReviewTask(
        review_task_id="review-task:revoked-reviewer:1",
        parse_snapshot_id="parse-snapshot:revoked-reviewer:1",
        document_version_id="document-version:revoked-reviewer:1",
        workspace_id="workspace_review",
        reviewer_principal_id="reviewer:revoked",
        reviewer_scope="workspace_reviewer",
        security_decision_ref="security-decision:revoked-reviewer:1",
        security_epoch_ref="security_epoch:workspace_review",
        idempotency_key="review:revoked-reviewer:1",
        trace_id="trace:revoked-reviewer:1",
        audit_ref="audit:revoked-reviewer:1",
        expires_at=1893456000.0,
        reason="quality_review_required",
        decision_hash=HEX_64,
    )

    with IngestionUnitOfWork(engine) as repo:
        source = repo.record_source_object(
            source_object_id="source:revoked-reviewer:1",
            tenant_id="tenant-a",
            workspace_id=task.workspace_id,
            filename="revoked-reviewer.md",
            mime_type="text/markdown",
            storage_uri="s3://bucket/workspace_review/revoked-reviewer.md",
            object_manifest_ref="manifest:revoked-reviewer:1",
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
            metadata={"filename": "revoked-reviewer.md"},
            immutability_ref="immutability:revoked-reviewer:1",
        )
        repo.record_parse_plan(
            parse_plan_id="parse-plan:revoked-reviewer:1",
            tenant_id="tenant-a",
            document_version_id=document.ref,
            parser_route={"primary": "native_markdown"},
            parser_policy_ref="parser-policy:revoked-reviewer:1",
            parser_bundle={"parser": "native_markdown", "version": "v1"},
            quality_policy_ref="quality-policy:revoked-reviewer:1",
            security_decision_ref=task.security_decision_ref or "security-decision:revoked-reviewer:1",
        )
        repo.record_parse_job(
            parse_job_id="parse-job:revoked-reviewer:1",
            tenant_id="tenant-a",
            parse_plan_id="parse-plan:revoked-reviewer:1",
            document_version_id=document.ref,
            idempotency_key="parse:revoked-reviewer:1",
        )
        repo.record_parse_attempt(
            parse_attempt_id="parse-attempt:revoked-reviewer:1",
            tenant_id="tenant-a",
            parse_job_id="parse-job:revoked-reviewer:1",
            attempt_no=1,
            worker_id="worker:revoked-reviewer:1",
            lease_ref="lease:revoked-reviewer:1",
            fencing_token=1,
        )
        repo.record_parse_snapshot(
            parse_snapshot_id=task.parse_snapshot_id,
            tenant_id="tenant-a",
            parse_job_id="parse-job:revoked-reviewer:1",
            parse_attempt_id="parse-attempt:revoked-reviewer:1",
            document_version_id=document.ref,
            canonical_ir={"blocks": [{"block_id": "block:1", "text": "review"}]},
            canonical_ir_ref="canonical-ir:revoked-reviewer:1",
            canonical_ir_schema_ref="CanonicalDocumentIR:v1",
            parser_id="native_markdown",
            parser_version="v1",
        )
        quality = repo.record_quality_decision(
            quality_decision_id="quality:revoked-reviewer:1",
            tenant_id="tenant-a",
            parse_snapshot_id=task.parse_snapshot_id,
            coverage_score=0.98,
            confidence_score=0.88,
            decision="human_review",
            review_task_ref=task.review_task_id,
        )
        repo.record_review_task(
            review_task_id=task.review_task_id,
            tenant_id="tenant-a",
            parse_snapshot_id=task.parse_snapshot_id,
            quality_decision_id=quality.ref,
            document_version_id=task.document_version_id,
            workspace_id=task.workspace_id,
            reviewer_principal_id=task.reviewer_principal_id,
            reviewer_scope=task.reviewer_scope,
            security_decision_ref=task.security_decision_ref,
            security_epoch_ref=task.security_epoch_ref,
            idempotency_key=task.idempotency_key,
            trace_id=task.trace_id,
            audit_ref=task.audit_ref,
            status=task.status,
            reason=task.reason,
            decision_hash=task.decision_hash,
            expires_at=task.expires_at,
        )
        receipt = runtime.decide(
            task=task,
            reviewer_id="reviewer:revoked",
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

    assert receipt.status == "rejected"
    assert receipt.reason == "reviewer_authorization_revoked"
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT review_task.status AS task_status,
                       receipt.status AS receipt_status,
                       receipt.reason AS receipt_reason
                FROM ingestion_review_tasks AS review_task
                JOIN ingestion_review_decision_receipts AS receipt
                  ON receipt.review_task_id = review_task.review_task_id
                WHERE review_task.review_task_id = :review_task_id
                """
            ),
            {"review_task_id": task.review_task_id},
        ).mappings().one()
        assert row["task_status"] == "rejected"
        assert row["receipt_status"] == "rejected"
        assert row["receipt_reason"] == "reviewer_authorization_revoked"
        assert conn.execute(text("SELECT count(*) FROM ingestion_indexable_document_snapshots")).scalar_one() == 0
        assert conn.execute(text("SELECT count(*) FROM ingestion_outbox_events")).scalar_one() == 0


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
        with pytest.raises(ValueError, match="conflicting review decision"):
            runtime.decide(
                task=loaded_task,
                reviewer_id=loaded_receipt.reviewer_id,
                reviewer_scope=loaded_receipt.reviewer_scope,
                status="rejected",
                security_epoch_ref=loaded_receipt.security_epoch_ref,
                existing_receipt=loaded_receipt,
                now=loaded_task.expires_at - 1,
            )
        conflicting_receipt = runtime.decide(
            task=loaded_task,
            reviewer_id="reviewer:phase11:conflict",
            reviewer_scope=loaded_receipt.reviewer_scope,
            status="rejected",
            security_epoch_ref=loaded_receipt.security_epoch_ref,
        )
        with pytest.raises(IngestionPersistenceError, match="conflicting review decision receipt"):
            repo.record_review_decision_receipt(
                decision_id=f"{conflicting_receipt.decision_id}:conflict",
                tenant_id="tenant-a",
                review_task_id=conflicting_receipt.review_task_id,
                status=conflicting_receipt.status,
                reviewer_id=conflicting_receipt.reviewer_id,
                reviewer_scope=conflicting_receipt.reviewer_scope,
                security_epoch_ref=conflicting_receipt.security_epoch_ref,
                reason=conflicting_receipt.reason,
                decision_hash=conflicting_receipt.decision_hash,
                decided_at=conflicting_receipt.decided_at,
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


def test_ingestion_delete_visibility_port_denial_prevents_lifecycle_and_outbox(engine) -> None:
    coordinator = PersistentDeleteRestoreCoordinator(
        engine=engine,
        object_store=None,
        visibility_port=_DenyVisibilityRevocationPort(),
    )

    with pytest.raises(ValueError, match="visibility_revocation_denied"):
        coordinator.request_delete_after_snapshot(
            DeleteLifecycleCommand(
                tenant_id="tenant-a",
                snapshot_ref="snapshot:phase11:visibility-denied",
                indexable_snapshot_id="snapshot:phase11:visibility-denied",
                handoff_outbox_event_id="outbox:snapshot:phase11:visibility-denied",
                visibility_ref="visibility:workspace-a:visibility-denied",
                object_ref="s3://phase11-visibility-denied/workspace-a/source.md",
                restore_point_name="_restore/workspace-a/source.md",
                projection_cleanup_ref="projection-cleanup:snapshot:phase11:visibility-denied",
            )
        )

    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM ingestion_delete_lifecycles")).scalar_one() == 0
        assert conn.execute(text("SELECT count(*) FROM infra_outbox_events")).scalar_one() == 0


def test_ingestion_delete_knowledge_cleanup_port_denial_prevents_object_delete(engine) -> None:
    content = b"phase11 knowledge cleanup port denied"
    bucket = f"phase11-cleanup-port-denied-{uuid4().hex}"
    raw_store = MinioObjectStore(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
    )
    durable_store = DurableMinioObjectStore(
        store=raw_store,
        engine=engine,
        owner="phase11-cleanup-port-denied-test",
    )
    try:
        ticket = durable_store.stage(
            bucket=bucket,
            committed_object_name="workspace-a/cleanup-port-denied.md",
            content=content,
        )
        committed = durable_store.commit(ticket)
        object_ref = f"s3://{bucket}/{committed.object_name}"
        runtime = DeleteRestoreRuntime()
        requested = runtime.request_delete(
            snapshot_ref="snapshot:phase11:cleanup-port-denied",
            visibility_ref="visibility:workspace-a:cleanup-port-denied",
            object_ref=object_ref,
            restore_point_name="_restore/workspace-a/cleanup-port-denied.md",
        )
        confirmed = runtime.confirm_knowledge_cleanup(runtime.request_cleanup(requested))
        with IngestionUnitOfWork(engine) as repo:
            repo.record_delete_lifecycle(tenant_id="tenant-a", **confirmed.model_dump())

        coordinator = PersistentDeleteRestoreCoordinator(
            engine=engine,
            object_store=durable_store,
            knowledge_cleanup_port=_DenyKnowledgeCleanupPort(),
        )

        with pytest.raises(ValueError, match="knowledge cleanup confirmation"):
            coordinator.execute_cleanup(
                tenant_id="tenant-a",
                delete_ref=confirmed.delete_ref,
            )

        assert raw_store.read_object(bucket=bucket, object_name=committed.object_name) == content
        with engine.connect() as conn:
            lifecycle = conn.execute(
                text(
                    """
                    SELECT state, cleanup_verified, physical_delete_verified,
                           physical_delete_ref, verification_ref
                    FROM ingestion_delete_lifecycles
                    WHERE delete_ref = :delete_ref
                    """
                ),
                {"delete_ref": confirmed.delete_ref},
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
        assert lifecycle["state"] == "cleanup_requested"
        assert lifecycle["cleanup_verified"] is True
        assert lifecycle["physical_delete_verified"] is False
        assert lifecycle["physical_delete_ref"] is None
        assert lifecycle["verification_ref"] is None
        assert manifest["visibility"] == "visible"
    finally:
        raw_store.remove_bucket_tree(bucket)


def test_ingestion_delete_minio_success_requires_absence_verification(engine) -> None:
    content = b"phase11 minio delete needs verification"
    bucket = f"phase11-delete-verify-denied-{uuid4().hex}"
    raw_store = MinioObjectStore(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
    )
    durable_store = DurableMinioObjectStore(
        store=raw_store,
        engine=engine,
        owner="phase11-delete-verify-denied-test",
    )
    try:
        ticket = durable_store.stage(
            bucket=bucket,
            committed_object_name="workspace-a/delete-verify-denied.md",
            content=content,
        )
        committed = durable_store.commit(ticket)
        object_ref = f"s3://{bucket}/{committed.object_name}"
        runtime = DeleteRestoreRuntime()
        requested = runtime.request_delete(
            snapshot_ref="snapshot:phase11:delete-verify-denied",
            visibility_ref="visibility:workspace-a:delete-verify-denied",
            object_ref=object_ref,
            restore_point_name="_restore/workspace-a/delete-verify-denied.md",
        )
        confirmed = runtime.confirm_knowledge_cleanup(runtime.request_cleanup(requested))
        with IngestionUnitOfWork(engine) as repo:
            repo.record_delete_lifecycle(tenant_id="tenant-a", **confirmed.model_dump())

        read_count = {"value": 0}

        def deny_absence_verification_read(action, _bucket, _object_name):
            if action != "object:read":
                return True
            read_count["value"] += 1
            return read_count["value"] <= 2

        verify_denied_store = DurableMinioObjectStore(
            store=MinioObjectStore(
                endpoint=MINIO_ENDPOINT,
                access_key=MINIO_ACCESS_KEY,
                secret_key=MINIO_SECRET_KEY,
                authorization_hook=deny_absence_verification_read,
            ),
            engine=engine,
            owner="phase11-delete-verify-denied-test",
        )
        coordinator = PersistentDeleteRestoreCoordinator(
            engine=engine,
            object_store=verify_denied_store,
        )

        with pytest.raises(ObjectAuthorizationError, match="object:read"):
            coordinator.execute_cleanup(
                tenant_id="tenant-a",
                delete_ref=confirmed.delete_ref,
            )

        with pytest.raises(S3Error):
            raw_store.read_object(bucket=bucket, object_name=committed.object_name)
        with engine.connect() as conn:
            lifecycle = conn.execute(
                text(
                    """
                    SELECT state, cleanup_verified, physical_delete_verified,
                           physical_delete_ref, verification_ref
                    FROM ingestion_delete_lifecycles
                    WHERE delete_ref = :delete_ref
                    """
                ),
                {"delete_ref": confirmed.delete_ref},
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
        assert lifecycle["state"] == "cleanup_requested"
        assert lifecycle["cleanup_verified"] is True
        assert lifecycle["physical_delete_verified"] is False
        assert lifecycle["physical_delete_ref"] is None
        assert lifecycle["verification_ref"] is None
        assert manifest["visibility"] == "deleted"
    finally:
        raw_store.remove_bucket_tree(bucket)


def test_ingestion_delete_reconciles_after_minio_success_before_domain_commit(engine) -> None:
    content = b"phase11 minio success before db commit"
    bucket = f"phase11-delete-db-fail-{uuid4().hex}"
    raw_store = MinioObjectStore(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
    )
    durable_store = DurableMinioObjectStore(
        store=raw_store,
        engine=engine,
        owner="phase11-delete-db-fail-test",
    )
    try:
        ticket = durable_store.stage(
            bucket=bucket,
            committed_object_name="workspace-a/delete-db-fail.md",
            content=content,
        )
        committed = durable_store.commit(ticket)
        object_ref = f"s3://{bucket}/{committed.object_name}"
        runtime = DeleteRestoreRuntime()
        requested = runtime.request_delete(
            snapshot_ref="snapshot:phase11:delete-db-fail",
            visibility_ref="visibility:workspace-a:delete-db-fail",
            object_ref=object_ref,
            restore_point_name="_restore/workspace-a/delete-db-fail.md",
        )
        confirmed = runtime.confirm_knowledge_cleanup(runtime.request_cleanup(requested))
        with IngestionUnitOfWork(engine) as repo:
            repo.record_delete_lifecycle(tenant_id="tenant-a", **confirmed.model_dump())

        crashing_coordinator = PersistentDeleteRestoreCoordinator(
            engine=engine,
            object_store=durable_store,
            audit_port=_FailAfterPhysicalDeleteAuditPort(),
        )
        with pytest.raises(RuntimeError, match="simulated_domain_commit_failure_after_minio_delete"):
            crashing_coordinator.execute_cleanup(
                tenant_id="tenant-a",
                delete_ref=confirmed.delete_ref,
            )

        with pytest.raises(S3Error):
            raw_store.read_object(bucket=bucket, object_name=committed.object_name)
        with engine.connect() as conn:
            after_crash = conn.execute(
                text(
                    """
                    SELECT state, cleanup_verified, physical_delete_verified,
                           physical_delete_ref, verification_ref
                    FROM ingestion_delete_lifecycles
                    WHERE delete_ref = :delete_ref
                    """
                ),
                {"delete_ref": confirmed.delete_ref},
            ).mappings().one()
            manifest_after_crash = conn.execute(
                text(
                    """
                    SELECT visibility
                    FROM infra_object_manifests
                    WHERE object_ref = :object_ref
                    """
                ),
                {"object_ref": object_ref},
            ).mappings().one()
        assert after_crash["state"] == "cleanup_requested"
        assert after_crash["cleanup_verified"] is True
        assert after_crash["physical_delete_verified"] is False
        assert after_crash["physical_delete_ref"] is None
        assert after_crash["verification_ref"] is None
        assert manifest_after_crash["visibility"] == "deleted"

        recovered = PersistentDeleteRestoreCoordinator(
            engine=engine,
            object_store=durable_store,
        ).execute_cleanup(
            tenant_id="tenant-a",
            delete_ref=confirmed.delete_ref,
        )

        assert recovered.state == "verified"
        assert recovered.physical_delete_ref == object_ref
        assert recovered.cleanup_verified is True
        assert recovered.physical_delete_verified is True
        with engine.connect() as conn:
            lifecycle = conn.execute(
                text(
                    """
                    SELECT state, cleanup_verified, physical_delete_verified,
                           physical_delete_ref, verification_ref
                    FROM ingestion_delete_lifecycles
                    WHERE delete_ref = :delete_ref
                    """
                ),
                {"delete_ref": confirmed.delete_ref},
            ).mappings().one()
        assert lifecycle["state"] == "verified"
        assert lifecycle["cleanup_verified"] is True
        assert lifecycle["physical_delete_verified"] is True
        assert lifecycle["physical_delete_ref"] == object_ref
        assert lifecycle["verification_ref"] == f"verify_{confirmed.delete_ref}"
    finally:
        raw_store.remove_bucket_tree(bucket)


def test_ingestion_delete_during_parse_persists_late_worker_rejection_after_restart(engine) -> None:
    runtime = DeleteRestoreRuntime()
    requested = runtime.request_delete_during_parse(
        parse_job_id="parse-job:phase11:late-worker",
        parse_attempt_id="parse-attempt:phase11:late-worker:1",
        fencing_token=7,
        visibility_ref="visibility:workspace-a:late-worker",
        object_ref="s3://phase11-late-worker/workspace-a/source.md",
        restore_point_name="_restore/workspace-a/source.md",
    )
    verified = runtime.verify_delete(
        runtime.mark_physical_delete(
            runtime.confirm_knowledge_cleanup(runtime.request_cleanup(requested))
        )
    )

    with IngestionUnitOfWork(engine) as repo:
        source = repo.record_source_object(
            source_object_id="source:phase11:late-worker",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            filename="source.md",
            mime_type="text/markdown",
            storage_uri=verified.object_ref or "s3://phase11-late-worker/workspace-a/source.md",
            object_manifest_ref="manifest:phase11:late-worker",
            source_sha256=HEX_64,
            size_bytes=42,
            classification_ref="classification:internal",
            security_epoch_ref="security-epoch:phase11-late-worker",
        )
        document = repo.record_document_version(
            document_version_id="document-version:phase11:late-worker",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            source_object_id=source.ref,
            version_no=1,
            content_hash=HEX_64,
            metadata={"filename": "source.md"},
            immutability_ref="immutability:phase11:late-worker",
        )
        plan = repo.record_parse_plan(
            parse_plan_id="parse-plan:phase11:late-worker",
            tenant_id="tenant-a",
            document_version_id=document.ref,
            parser_route={"primary": "native_markdown"},
            parser_policy_ref="parser-policy:phase11-late-worker",
            parser_bundle={"parser": "native_markdown", "version": "v1"},
            quality_policy_ref="quality-policy:phase11-late-worker",
            security_decision_ref="security-decision:phase11-late-worker",
        )
        repo.record_parse_job(
            parse_job_id=verified.parse_job_id or "parse-job:phase11:late-worker",
            tenant_id="tenant-a",
            parse_plan_id=plan.ref,
            document_version_id=document.ref,
            idempotency_key="parse:phase11:late-worker",
        )
        repo.record_parse_attempt(
            parse_attempt_id=verified.parse_attempt_id or "parse-attempt:phase11:late-worker:1",
            tenant_id="tenant-a",
            parse_job_id=verified.parse_job_id or "parse-job:phase11:late-worker",
            attempt_no=1,
            worker_id="worker:phase11-late-worker",
            lease_ref="lease:phase11-late-worker",
            fencing_token=verified.fencing_token or 7,
        )
        repo.record_delete_lifecycle(tenant_id="tenant-a", **verified.model_dump())

    coordinator = PersistentDeleteRestoreCoordinator(
        engine=engine,
        object_store=None,
    )
    rejected = coordinator.reject_late_worker_result(
        tenant_id="tenant-a",
        delete_ref=verified.delete_ref,
        parse_attempt_id=verified.parse_attempt_id,
        fencing_token=verified.fencing_token + 1,
    )

    assert rejected.late_worker_result_rejected is True
    assert rejected.state == "verified"
    assert rejected.history[-1] == "late_worker_result_rejected"
    with engine.connect() as conn:
        persisted = conn.execute(
            text(
                """
                SELECT state, parse_job_id, parse_attempt_id, fencing_token,
                       late_worker_result_rejected, history
                FROM ingestion_delete_lifecycles
                WHERE delete_ref = :delete_ref
                """
            ),
            {"delete_ref": verified.delete_ref},
        ).mappings().one()
    assert persisted["state"] == "verified"
    assert persisted["parse_job_id"] == verified.parse_job_id
    assert persisted["parse_attempt_id"] == verified.parse_attempt_id
    assert persisted["fencing_token"] == verified.fencing_token
    assert persisted["late_worker_result_rejected"] is True
    assert persisted["history"][-1] == "late_worker_result_rejected"


def test_ingestion_delete_cleanup_publish_crash_replays_without_physical_delete(engine) -> None:
    object_ref = "s3://phase11-cleanup-crash/workspace-a/delete-target.md"
    with IngestionUnitOfWork(engine) as repo:
        source = repo.record_source_object(
            source_object_id="source:phase11:cleanup-crash",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            filename="delete-target.md",
            mime_type="text/markdown",
            storage_uri=object_ref,
            object_manifest_ref=f"manifest:{object_ref}",
            source_sha256=HEX_64,
            size_bytes=42,
            classification_ref="classification:internal",
            security_epoch_ref="security-epoch:phase11-cleanup-crash",
        )
        document = repo.record_document_version(
            document_version_id="document-version:phase11:cleanup-crash",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            source_object_id=source.ref,
            version_no=1,
            content_hash=HEX_64,
            metadata={"filename": "delete-target.md"},
            immutability_ref="immutability:phase11:cleanup-crash",
        )
        plan = repo.record_parse_plan(
            parse_plan_id="parse-plan:phase11:cleanup-crash",
            tenant_id="tenant-a",
            document_version_id=document.ref,
            parser_route={"primary": "native_markdown"},
            parser_policy_ref="parser-policy:phase11-cleanup-crash",
            parser_bundle={"parser": "native_markdown", "version": "v1"},
            quality_policy_ref="quality-policy:phase11-cleanup-crash",
            security_decision_ref="security-decision:phase11-cleanup-crash",
        )
        job = repo.record_parse_job(
            parse_job_id="parse-job:phase11:cleanup-crash",
            tenant_id="tenant-a",
            parse_plan_id=plan.ref,
            document_version_id=document.ref,
            idempotency_key="parse:phase11:cleanup-crash",
        )
        attempt = repo.record_parse_attempt(
            parse_attempt_id="parse-attempt:phase11:cleanup-crash",
            tenant_id="tenant-a",
            parse_job_id=job.ref,
            attempt_no=1,
            worker_id="worker:phase11-cleanup-crash",
            lease_ref="lease:phase11-cleanup-crash",
            fencing_token=1,
        )
        snapshot = repo.record_parse_snapshot(
            parse_snapshot_id="parse-snapshot:phase11:cleanup-crash",
            tenant_id="tenant-a",
            parse_job_id=job.ref,
            parse_attempt_id=attempt.ref,
            document_version_id=document.ref,
            canonical_ir={"metadata": {"document_id": source.ref}, "blocks": []},
            canonical_ir_ref="canonical-ir:phase11-cleanup-crash",
            canonical_ir_schema_ref="canonical-document-ir-v1",
            parser_id="native_markdown",
            parser_version="v1",
        )
        quality = repo.record_quality_decision(
            quality_decision_id="quality:phase11:cleanup-crash",
            tenant_id="tenant-a",
            parse_snapshot_id=snapshot.ref,
            coverage_score=1.0,
            confidence_score=1.0,
            decision="publish",
        )
        repo.record_indexable_snapshot(
            indexable_snapshot_id="snapshot:phase11:cleanup-crash",
            tenant_id="tenant-a",
            parse_snapshot_id=snapshot.ref,
            document_version_id=document.ref,
            quality_decision_id=quality.ref,
            visibility_ref="visibility:workspace-a:cleanup-crash",
            payload={"object_ref": object_ref},
            handoff_idempotency_key="handoff:phase11:cleanup-crash",
        )
    coordinator = PersistentDeleteRestoreCoordinator(
        engine=engine,
        object_store=None,
    )
    requested = coordinator.request_delete_after_snapshot(
        DeleteLifecycleCommand(
            tenant_id="tenant-a",
            snapshot_ref="snapshot:phase11:cleanup-crash",
            indexable_snapshot_id="snapshot:phase11:cleanup-crash",
            handoff_outbox_event_id="outbox:snapshot:phase11:cleanup-crash",
            visibility_ref="visibility:workspace-a:cleanup-crash",
            object_ref=object_ref,
            restore_point_name="_restore/workspace-a/delete-target.md",
            projection_cleanup_ref="projection-cleanup:snapshot:phase11:cleanup-crash",
        )
    )

    first, replay = asyncio.run(
        _publish_cleanup_then_replay_after_crash(
            engine=engine,
            event_id=f"outbox:{requested.delete_ref}:cleanup",
        )
    )

    assert first["event_id"] == replay["event_id"] == f"outbox:{requested.delete_ref}:cleanup"
    assert first["payload"] == replay["payload"]
    assert first["payload"]["delete_ref"] == requested.delete_ref
    with pytest.raises(ValueError, match="knowledge cleanup confirmation"):
        coordinator.execute_cleanup(
            tenant_id="tenant-a",
            delete_ref=requested.delete_ref,
        )
    with engine.connect() as conn:
        lifecycle = conn.execute(
            text(
                """
                SELECT state, cleanup_verified, physical_delete_verified,
                       physical_delete_ref
                FROM ingestion_delete_lifecycles
                WHERE delete_ref = :delete_ref
                """
            ),
            {"delete_ref": requested.delete_ref},
        ).mappings().one()
        outbox = conn.execute(
            text(
                """
                SELECT status, claim_owner
                FROM infra_outbox_events
                WHERE event_id = :event_id
                """
            ),
            {"event_id": f"outbox:{requested.delete_ref}:cleanup"},
        ).mappings().one()
    assert lifecycle["state"] == "visibility_revoked"
    assert lifecycle["cleanup_verified"] is False
    assert lifecycle["physical_delete_verified"] is False
    assert lifecycle["physical_delete_ref"] is None
    assert outbox["status"] == "published"
    assert outbox["claim_owner"] is None


def test_ingestion_delete_cleanup_dlq_replay_does_not_restore_revoked_data(engine) -> None:
    object_ref = "s3://phase11-cleanup-dlq/workspace-a/delete-target.md"
    with IngestionUnitOfWork(engine) as repo:
        source = repo.record_source_object(
            source_object_id="source:phase11:cleanup-dlq",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            filename="delete-target.md",
            mime_type="text/markdown",
            storage_uri=object_ref,
            object_manifest_ref=f"manifest:{object_ref}",
            source_sha256=HEX_64,
            size_bytes=42,
            classification_ref="classification:internal",
            security_epoch_ref="security-epoch:phase11-cleanup-dlq",
        )
        document = repo.record_document_version(
            document_version_id="document-version:phase11:cleanup-dlq",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            source_object_id=source.ref,
            version_no=1,
            content_hash=HEX_64,
            metadata={"filename": "delete-target.md"},
            immutability_ref="immutability:phase11:cleanup-dlq",
        )
        plan = repo.record_parse_plan(
            parse_plan_id="parse-plan:phase11:cleanup-dlq",
            tenant_id="tenant-a",
            document_version_id=document.ref,
            parser_route={"primary": "native_markdown"},
            parser_policy_ref="parser-policy:phase11-cleanup-dlq",
            parser_bundle={"parser": "native_markdown", "version": "v1"},
            quality_policy_ref="quality-policy:phase11-cleanup-dlq",
            security_decision_ref="security-decision:phase11-cleanup-dlq",
        )
        job = repo.record_parse_job(
            parse_job_id="parse-job:phase11:cleanup-dlq",
            tenant_id="tenant-a",
            parse_plan_id=plan.ref,
            document_version_id=document.ref,
            idempotency_key="parse:phase11:cleanup-dlq",
        )
        attempt = repo.record_parse_attempt(
            parse_attempt_id="parse-attempt:phase11:cleanup-dlq",
            tenant_id="tenant-a",
            parse_job_id=job.ref,
            attempt_no=1,
            worker_id="worker:phase11-cleanup-dlq",
            lease_ref="lease:phase11-cleanup-dlq",
            fencing_token=1,
        )
        snapshot = repo.record_parse_snapshot(
            parse_snapshot_id="parse-snapshot:phase11:cleanup-dlq",
            tenant_id="tenant-a",
            parse_job_id=job.ref,
            parse_attempt_id=attempt.ref,
            document_version_id=document.ref,
            canonical_ir={"metadata": {"document_id": source.ref}, "blocks": []},
            canonical_ir_ref="canonical-ir:phase11-cleanup-dlq",
            canonical_ir_schema_ref="canonical-document-ir-v1",
            parser_id="native_markdown",
            parser_version="v1",
        )
        quality = repo.record_quality_decision(
            quality_decision_id="quality:phase11:cleanup-dlq",
            tenant_id="tenant-a",
            parse_snapshot_id=snapshot.ref,
            coverage_score=1.0,
            confidence_score=1.0,
            decision="publish",
        )
        repo.record_indexable_snapshot(
            indexable_snapshot_id="snapshot:phase11:cleanup-dlq",
            tenant_id="tenant-a",
            parse_snapshot_id=snapshot.ref,
            document_version_id=document.ref,
            quality_decision_id=quality.ref,
            visibility_ref="visibility:workspace-a:cleanup-dlq",
            payload={"object_ref": object_ref},
            handoff_idempotency_key="handoff:phase11:cleanup-dlq",
        )
    coordinator = PersistentDeleteRestoreCoordinator(
        engine=engine,
        object_store=None,
    )
    requested = coordinator.request_delete_after_snapshot(
        DeleteLifecycleCommand(
            tenant_id="tenant-a",
            snapshot_ref="snapshot:phase11:cleanup-dlq",
            indexable_snapshot_id="snapshot:phase11:cleanup-dlq",
            handoff_outbox_event_id="outbox:snapshot:phase11:cleanup-dlq",
            visibility_ref="visibility:workspace-a:cleanup-dlq",
            object_ref=object_ref,
            restore_point_name="_restore/workspace-a/delete-target.md",
            projection_cleanup_ref="projection-cleanup:snapshot:phase11:cleanup-dlq",
        )
    )

    dead_lettered, replayed = asyncio.run(
        _publish_cleanup_to_dlq_then_replay(
            engine=engine,
            event_id=f"outbox:{requested.delete_ref}:cleanup",
        )
    )

    assert dead_lettered == replayed
    assert replayed["event_id"] == f"outbox:{requested.delete_ref}:cleanup"
    assert replayed["payload"]["delete_ref"] == requested.delete_ref
    with pytest.raises(ValueError, match="knowledge cleanup confirmation"):
        coordinator.execute_cleanup(
            tenant_id="tenant-a",
            delete_ref=requested.delete_ref,
        )
    with engine.connect() as conn:
        lifecycle = conn.execute(
            text(
                """
                SELECT state, cleanup_verified, physical_delete_verified,
                       restored_authorization, physical_delete_ref
                FROM ingestion_delete_lifecycles
                WHERE delete_ref = :delete_ref
                """
            ),
            {"delete_ref": requested.delete_ref},
        ).mappings().one()
        outbox = conn.execute(
            text(
                """
                SELECT status, claim_owner
                FROM infra_outbox_events
                WHERE event_id = :event_id
                """
            ),
            {"event_id": f"outbox:{requested.delete_ref}:cleanup"},
        ).mappings().one()
    assert lifecycle["state"] == "visibility_revoked"
    assert lifecycle["cleanup_verified"] is False
    assert lifecycle["physical_delete_verified"] is False
    assert lifecycle["restored_authorization"] is False
    assert lifecycle["physical_delete_ref"] is None
    assert outbox["status"] == "published"
    assert outbox["claim_owner"] is None


def test_ingestion_delete_cleanup_minio_delete_failure_keeps_lifecycle_unverified(engine) -> None:
    content = b"phase11 minio delete denied"
    bucket = f"phase11-delete-denied-{uuid4().hex}"
    raw_store = MinioObjectStore(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
    )
    durable_store = DurableMinioObjectStore(
        store=raw_store,
        engine=engine,
        owner="phase11-delete-denied-test",
    )
    try:
        ticket = durable_store.stage(
            bucket=bucket,
            committed_object_name="workspace-a/delete-denied.md",
            content=content,
        )
        committed = durable_store.commit(ticket)
        object_ref = f"s3://{bucket}/{committed.object_name}"
        with IngestionUnitOfWork(engine) as repo:
            source = repo.record_source_object(
                source_object_id="source:phase11:delete-denied",
                tenant_id="tenant-a",
                workspace_id="workspace-a",
                filename="delete-denied.md",
                mime_type="text/markdown",
                storage_uri=object_ref,
                object_manifest_ref=f"manifest:{object_ref}",
                source_sha256=committed.content_hash,
                size_bytes=committed.size_bytes,
                classification_ref="classification:internal",
                security_epoch_ref="security-epoch:phase11-delete-denied",
            )
            document = repo.record_document_version(
                document_version_id="document-version:phase11:delete-denied",
                tenant_id="tenant-a",
                workspace_id="workspace-a",
                source_object_id=source.ref,
                version_no=1,
                content_hash=committed.content_hash,
                metadata={"filename": "delete-denied.md"},
                immutability_ref="immutability:phase11:delete-denied",
            )
            plan = repo.record_parse_plan(
                parse_plan_id="parse-plan:phase11:delete-denied",
                tenant_id="tenant-a",
                document_version_id=document.ref,
                parser_route={"primary": "native_markdown"},
                parser_policy_ref="parser-policy:phase11-delete-denied",
                parser_bundle={"parser": "native_markdown", "version": "v1"},
                quality_policy_ref="quality-policy:phase11-delete-denied",
                security_decision_ref="security-decision:phase11-delete-denied",
            )
            job = repo.record_parse_job(
                parse_job_id="parse-job:phase11:delete-denied",
                tenant_id="tenant-a",
                parse_plan_id=plan.ref,
                document_version_id=document.ref,
                idempotency_key="parse:phase11:delete-denied",
            )
            attempt = repo.record_parse_attempt(
                parse_attempt_id="parse-attempt:phase11:delete-denied",
                tenant_id="tenant-a",
                parse_job_id=job.ref,
                attempt_no=1,
                worker_id="worker:phase11-delete-denied",
                lease_ref="lease:phase11-delete-denied",
                fencing_token=1,
            )
            snapshot = repo.record_parse_snapshot(
                parse_snapshot_id="parse-snapshot:phase11:delete-denied",
                tenant_id="tenant-a",
                parse_job_id=job.ref,
                parse_attempt_id=attempt.ref,
                document_version_id=document.ref,
                canonical_ir={"metadata": {"document_id": source.ref}, "blocks": []},
                canonical_ir_ref="canonical-ir:phase11-delete-denied",
                canonical_ir_schema_ref="canonical-document-ir-v1",
                parser_id="native_markdown",
                parser_version="v1",
            )
            quality = repo.record_quality_decision(
                quality_decision_id="quality:phase11:delete-denied",
                tenant_id="tenant-a",
                parse_snapshot_id=snapshot.ref,
                coverage_score=1.0,
                confidence_score=1.0,
                decision="publish",
            )
            repo.record_indexable_snapshot(
                indexable_snapshot_id="snapshot:phase11:delete-denied",
                tenant_id="tenant-a",
                parse_snapshot_id=snapshot.ref,
                document_version_id=document.ref,
                quality_decision_id=quality.ref,
                visibility_ref="visibility:workspace-a:delete-denied",
                payload={"object_ref": object_ref},
                handoff_idempotency_key="handoff:phase11:delete-denied",
            )
        denied_store = DurableMinioObjectStore(
            store=MinioObjectStore(
                endpoint=MINIO_ENDPOINT,
                access_key=MINIO_ACCESS_KEY,
                secret_key=MINIO_SECRET_KEY,
                authorization_hook=lambda action, _bucket, _object_name: action != "object:delete",
            ),
            engine=engine,
            owner="phase11-delete-denied-test",
        )
        coordinator = PersistentDeleteRestoreCoordinator(
            engine=engine,
            object_store=denied_store,
        )
        requested = coordinator.request_delete_after_snapshot(
            DeleteLifecycleCommand(
                tenant_id="tenant-a",
                snapshot_ref="snapshot:phase11:delete-denied",
                indexable_snapshot_id="snapshot:phase11:delete-denied",
                handoff_outbox_event_id="outbox:snapshot:phase11:delete-denied",
                visibility_ref="visibility:workspace-a:delete-denied",
                object_ref=object_ref,
                restore_point_name="_restore/workspace-a/delete-denied.md",
                projection_cleanup_ref="projection-cleanup:snapshot:phase11:delete-denied",
            )
        )
        confirmed = coordinator.confirm_knowledge_cleanup(
            tenant_id="tenant-a",
            delete_ref=requested.delete_ref,
            cleanup_ref=requested.cleanup_ref,
        )

        with pytest.raises(ObjectAuthorizationError, match="object:delete"):
            coordinator.execute_cleanup(
                tenant_id="tenant-a",
                delete_ref=confirmed.delete_ref,
            )

        assert raw_store.read_object(bucket=bucket, object_name=committed.object_name) == content
        with engine.connect() as conn:
            lifecycle = conn.execute(
                text(
                    """
                    SELECT state, cleanup_verified, physical_delete_verified,
                           physical_delete_ref, verification_ref
                    FROM ingestion_delete_lifecycles
                    WHERE delete_ref = :delete_ref
                    """
                ),
                {"delete_ref": requested.delete_ref},
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
        assert lifecycle["state"] == "cleanup_requested"
        assert lifecycle["cleanup_verified"] is True
        assert lifecycle["physical_delete_verified"] is False
        assert lifecycle["physical_delete_ref"] is None
        assert lifecycle["verification_ref"] is None
        assert manifest["visibility"] == "visible"
    finally:
        raw_store.remove_bucket_tree(bucket)


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
        cleanup_delivery = asyncio.run(
            _publish_and_ack_cleanup_contract(
                engine=engine,
                event_id=f"outbox:{requested.delete_ref}:cleanup",
            )
        )
        assert cleanup_delivery["delete_ref"] == requested.delete_ref
        assert cleanup_delivery["projection_cleanup_ref"] == requested.projection_cleanup_ref
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


def test_ingestion_delete_cleanup_reconciles_object_already_missing(engine) -> None:
    content = b"phase11 object already missing"
    bucket = f"phase11-missing-{uuid4().hex}"
    raw_store = MinioObjectStore(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
    )
    durable_store = DurableMinioObjectStore(
        store=raw_store,
        engine=engine,
        owner="phase11-delete-missing-test",
    )
    try:
        ticket = durable_store.stage(
            bucket=bucket,
            committed_object_name="workspace-a/already-missing.md",
            content=content,
        )
        committed = durable_store.commit(ticket)
        object_ref = f"s3://{bucket}/{committed.object_name}"
        with IngestionUnitOfWork(engine) as repo:
            source = repo.record_source_object(
                source_object_id="source:phase11:already-missing",
                tenant_id="tenant-a",
                workspace_id="workspace-a",
                filename="already-missing.md",
                mime_type="text/markdown",
                storage_uri=object_ref,
                object_manifest_ref=f"manifest:{object_ref}",
                source_sha256=committed.content_hash,
                size_bytes=committed.size_bytes,
                classification_ref="classification:internal",
                security_epoch_ref="security-epoch:phase11-missing",
            )
            document = repo.record_document_version(
                document_version_id="document-version:phase11:already-missing",
                tenant_id="tenant-a",
                workspace_id="workspace-a",
                source_object_id=source.ref,
                version_no=1,
                content_hash=committed.content_hash,
                metadata={"filename": "already-missing.md"},
                immutability_ref="immutability:phase11:already-missing",
            )
            plan = repo.record_parse_plan(
                parse_plan_id="parse-plan:phase11:already-missing",
                tenant_id="tenant-a",
                document_version_id=document.ref,
                parser_route={"primary": "native_markdown"},
                parser_policy_ref="parser-policy:phase11-missing",
                parser_bundle={"parser": "native_markdown", "version": "v1"},
                quality_policy_ref="quality-policy:phase11-missing",
                security_decision_ref="security-decision:phase11-missing",
            )
            job = repo.record_parse_job(
                parse_job_id="parse-job:phase11:already-missing",
                tenant_id="tenant-a",
                parse_plan_id=plan.ref,
                document_version_id=document.ref,
                idempotency_key="parse:phase11:already-missing",
            )
            attempt = repo.record_parse_attempt(
                parse_attempt_id="parse-attempt:phase11:already-missing",
                tenant_id="tenant-a",
                parse_job_id=job.ref,
                attempt_no=1,
                worker_id="worker:phase11-missing",
                lease_ref="lease:phase11-missing",
                fencing_token=1,
            )
            snapshot = repo.record_parse_snapshot(
                parse_snapshot_id="parse-snapshot:phase11:already-missing",
                tenant_id="tenant-a",
                parse_job_id=job.ref,
                parse_attempt_id=attempt.ref,
                document_version_id=document.ref,
                canonical_ir={"metadata": {"document_id": source.ref}, "blocks": []},
                canonical_ir_ref="canonical-ir:phase11-missing",
                canonical_ir_schema_ref="canonical-document-ir-v1",
                parser_id="native_markdown",
                parser_version="v1",
            )
            quality = repo.record_quality_decision(
                quality_decision_id="quality:phase11:already-missing",
                tenant_id="tenant-a",
                parse_snapshot_id=snapshot.ref,
                coverage_score=1.0,
                confidence_score=1.0,
                decision="publish",
            )
            repo.record_indexable_snapshot(
                indexable_snapshot_id="snapshot:phase11:already-missing",
                tenant_id="tenant-a",
                parse_snapshot_id=snapshot.ref,
                document_version_id=document.ref,
                quality_decision_id=quality.ref,
                visibility_ref="visibility:workspace-a:already-missing",
                payload={"object_ref": object_ref},
                handoff_idempotency_key="handoff:phase11:already-missing",
            )
        coordinator = PersistentDeleteRestoreCoordinator(
            engine=engine,
            object_store=durable_store,
        )
        requested = coordinator.request_delete_after_snapshot(
            DeleteLifecycleCommand(
                tenant_id="tenant-a",
                snapshot_ref="snapshot:phase11:already-missing",
                indexable_snapshot_id="snapshot:phase11:already-missing",
                handoff_outbox_event_id="outbox:snapshot:phase11:already-missing",
                visibility_ref="visibility:workspace-a:already-missing",
                object_ref=object_ref,
                restore_point_name="_restore/workspace-a/already-missing.md",
                projection_cleanup_ref="projection-cleanup:snapshot:phase11:already-missing",
            )
        )
        coordinator.confirm_knowledge_cleanup(
            tenant_id="tenant-a",
            delete_ref=requested.delete_ref,
            cleanup_ref=requested.cleanup_ref,
        )
        raw_store.client.remove_object(bucket, committed.object_name)

        verified = coordinator.execute_cleanup(
            tenant_id="tenant-a",
            delete_ref=requested.delete_ref,
        )

        assert verified.state == "verified"
        assert verified.cleanup_verified is True
        assert verified.physical_delete_verified is True
        assert verified.physical_delete_ref == object_ref
        with engine.connect() as conn:
            lifecycle = conn.execute(
                text(
                    """
                    SELECT state, physical_delete_ref, cleanup_verified,
                           physical_delete_verified
                    FROM ingestion_delete_lifecycles
                    WHERE delete_ref = :delete_ref
                    """
                ),
                {"delete_ref": requested.delete_ref},
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
        assert lifecycle["state"] == "verified"
        assert lifecycle["physical_delete_ref"] == object_ref
        assert lifecycle["cleanup_verified"] is True
        assert lifecycle["physical_delete_verified"] is True
        assert manifest["visibility"] == "deleted"
        with pytest.raises(S3Error):
            raw_store.read_object(bucket=bucket, object_name=committed.object_name)
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
