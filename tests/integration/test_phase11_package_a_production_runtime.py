from __future__ import annotations

import asyncio
import hashlib
import os
import subprocess
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from sqlalchemy import text

from zuno.knowledge.ingestion import (
    PackageAObjectVerificationError,
    PackageAProductionIngestionRuntime,
    PackageARejectDeliveryError,
    PackageAUploadCommand,
)
from zuno.knowledge.ingestion.contracts import (
    CanonicalDocumentIR,
    DocumentBlock,
    DocumentMetadata,
    DocumentProvenance,
    ParseDocumentResult,
    ParseJobSnapshot,
    ParserFailure,
    SourceSpan,
)
from zuno.knowledge.ingestion.gateway import ParseGateway
from zuno.platform.contracts import CrossModuleEnvelopeV1, canonical_sha256
from zuno.platform.database.foundation import InfrastructureUnitOfWork, create_foundation_engine
from zuno.platform.database.ingestion import IngestionPersistenceError, IngestionUnitOfWork
from zuno.platform.queue.domain import CanonicalOutboxDeliveryV1
from zuno.platform.queue import (
    OutboxPublishPolicy,
    PostgresOutboxRabbitMQPublisher,
    RabbitMQTopology,
    RabbitMQTransport,
)
from zuno.platform.storage import DurableMinioObjectStore, MinioObjectStore


REPO_ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno?connect_timeout=5",
)
RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"
MINIO_ENDPOINT = "localhost:9000"


class _FakeObjectReader:
    def __init__(self, *, bucket: str, object_name: str, content: bytes) -> None:
        self.bucket = bucket
        self.object_name = object_name
        self.content = content
        self.read_count = 0

    def read_object(self, *, bucket: str, object_name: str) -> bytes:
        assert bucket == self.bucket
        assert object_name == self.object_name
        self.read_count += 1
        return self.content


class _FakeObjectStore:
    def __init__(self, *, bucket: str, object_name: str, content: bytes) -> None:
        self.store = _FakeObjectReader(bucket=bucket, object_name=object_name, content=content)


class _RecordingDelivery:
    def __init__(self, *, payload: dict[str, Any], tenant_id: str) -> None:
        self.message_id = str(payload["event_id"])
        self.payload = payload
        envelope_payload = payload.get("payload") or {}
        self.headers = {
            "tenant_id": tenant_id,
            "workspace_id": envelope_payload.get("workspace_id"),
            "trace_id": envelope_payload.get("trace_id"),
            "data_classification": envelope_payload.get("data_classification"),
            "message_version": envelope_payload.get("contract_version"),
            "security_epoch_ref": envelope_payload.get("effective_security_epoch_ref"),
            "ordering_key": envelope_payload.get("aggregate_id"),
            "ordering_sequence": 1,
            "outbox_publish_attempt": 1,
            "outbox_retry_count": 0,
            "outbox_replay_count": 0,
        }
        self.redelivered = False
        self.acked = False
        self.nacked = False
        self.rejected = False

    async def ack(self) -> None:
        self.acked = True

    async def nack(self, *, requeue: bool) -> None:
        self.nacked = True

    async def reject(self, *, requeue: bool = False) -> None:
        self.rejected = True


class _FailingRabbitMQTransport:
    async def publish(self, *_args, **_kwargs) -> None:
        raise ConnectionError("publisher confirm failed")


def _migrate() -> None:
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


def _engine():
    _migrate()
    engine = create_foundation_engine(DATABASE_URL)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                TRUNCATE
                    ingestion_parse_leases,
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
                    ingestion_source_objects,
                    infra_delivery_watermarks,
                    infra_outbox_sequences,
                    infra_outbox_events,
                    infra_inbox_messages,
                    infra_object_manifests
                RESTART IDENTITY
                """
            )
        )
    return engine


def _seed_job(engine) -> None:
    with IngestionUnitOfWork(engine) as repo:
        source = repo.record_source_object(
            source_object_id="source:pkg-a:b",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            filename="pkg-a.md",
            mime_type="text/markdown",
            declared_format="markdown",
            storage_uri="s3://bucket/tenant-a/workspace-a/pkg-a.md",
            object_manifest_ref="manifest:pkg-a",
            source_sha256="c" * 64,
            size_bytes=21,
            classification_ref="internal",
            security_epoch_ref="security-epoch:pkg-a",
        )
        document = repo.record_document_version(
            document_version_id="document-version:pkg-a:b",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            source_object_id=source.ref,
            version_no=1,
            content_hash="c" * 64,
            metadata={"filename": "pkg-a.md"},
            immutability_ref="immutability:pkg-a",
        )
        plan = repo.record_parse_plan(
            parse_plan_id="parse-plan:pkg-a:b",
            tenant_id="tenant-a",
            document_version_id=document.ref,
            parser_route={"primary": "native_markdown"},
            parser_policy_ref="parser-policy:pkg-a",
            parser_bundle={"parser": "native_markdown"},
            quality_policy_ref="quality-policy:pkg-a",
            security_decision_ref="security-decision:pkg-a",
        )
        repo.record_parse_job(
            parse_job_id="parse-job:pkg-a:b",
            tenant_id="tenant-a",
            parse_plan_id=plan.ref,
            document_version_id=document.ref,
            idempotency_key="parse:tenant-a:pkg-a:b",
        )


def _seed_retryable_job(engine, *, content: bytes) -> CrossModuleEnvelopeV1:
    content_hash = hashlib.sha256(content).hexdigest()
    payload = {
        "tenant_id": "tenant-a",
        "workspace_id": "workspace-a",
        "source_object_id": "source:pkg-a:retry",
        "document_version_id": "document-version:pkg-a:retry",
        "parse_plan_id": "parse-plan:pkg-a:retry",
        "parse_job_id": "parse-job:pkg-a:retry",
        "object_ref": "s3://bucket/tenant-a/workspace-a/retry.md",
        "object_manifest_ref": "manifest:pkg-a:retry",
        "content_hash": content_hash,
        "size_bytes": len(content),
        "mime_type": "text/markdown",
        "parser_policy_ref": "parser-policy:pkg-a",
        "quality_policy_ref": "quality-policy:pkg-a",
        "security_decision_ref": "security-decision:pkg-a",
        "security_epoch_ref": "security-epoch:pkg-a:retry",
        "max_attempts": 2,
    }
    envelope = CrossModuleEnvelopeV1(
        contract_name="zuno.ingestion.parse.requested",
        contract_version="v1",
        contract_bundle_version="wave1",
        message_id="outbox:parse-job:pkg-a:retry",
        producer_module="workspace.file_upload",
        consumer_module="ingestion.parser_worker",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        correlation_id="trace-pkg-a-retry",
        idempotency_key=f"parse:tenant-a:workspace-a:{content_hash}:1",
        aggregate_type="ParseJob",
        aggregate_id="parse-job:pkg-a:retry",
        effective_security_epoch_ref="security-epoch:pkg-a:retry",
        trace_id="trace-pkg-a-retry",
        data_classification="internal",
        occurred_at="2026-07-20T00:00:00Z",
        created_at="2026-07-20T00:00:00Z",
        payload=payload,
        payload_hash=canonical_sha256(payload),
        payload_schema_hash=canonical_sha256({"schema": "zuno.ingestion.parse.requested.v1"}),
    )
    with IngestionUnitOfWork(engine) as repo:
        source = repo.record_source_object(
            source_object_id="source:pkg-a:retry",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            filename="retry.md",
            mime_type="text/markdown",
            declared_format="markdown",
            storage_uri="s3://bucket/tenant-a/workspace-a/retry.md",
            object_manifest_ref="manifest:pkg-a:retry",
            source_sha256=content_hash,
            size_bytes=len(content),
            classification_ref="internal",
            security_epoch_ref="security-epoch:pkg-a:retry",
        )
        document = repo.record_document_version(
            document_version_id="document-version:pkg-a:retry",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            source_object_id=source.ref,
            version_no=1,
            content_hash=content_hash,
            metadata={"filename": "retry.md"},
            immutability_ref="immutability:pkg-a:retry",
        )
        plan = repo.record_parse_plan(
            parse_plan_id="parse-plan:pkg-a:retry",
            tenant_id="tenant-a",
            document_version_id=document.ref,
            parser_route={"primary": "native_markdown"},
            parser_policy_ref="parser-policy:pkg-a",
            parser_bundle={"parser": "native_markdown"},
            quality_policy_ref="quality-policy:pkg-a",
            security_decision_ref="security-decision:pkg-a",
        )
        repo.record_parse_job(
            parse_job_id="parse-job:pkg-a:retry",
            tenant_id="tenant-a",
            parse_plan_id=plan.ref,
            document_version_id=document.ref,
            idempotency_key=f"parse:tenant-a:workspace-a:{content_hash}:1",
        )
        repo.enqueue_parse_requested(envelope=envelope)
    return envelope


def test_worker_object_ref_verifier_rejects_scope_hash_and_revoked_visibility() -> None:
    content = b"# Object verifier\nPackage A."
    content_hash = hashlib.sha256(content).hexdigest()
    runtime = PackageAProductionIngestionRuntime(
        engine=None,
        object_store=_FakeObjectStore(
            bucket="bucket",
            object_name="tenant-a/workspace-a/source/source-a/file.md",
            content=content,
        ),
        worker_id="phase11-package-a-worker",
    )
    context = {
        "tenant_id": "tenant-a",
        "workspace_id": "workspace-a",
        "storage_uri": "s3://bucket/tenant-a/workspace-a/source/source-a/file.md",
        "source_sha256": content_hash,
        "size_bytes": len(content),
        "source_status": "committed",
    }

    assert runtime._read_and_verify_object(context) == content

    scoped_out_context = {
        **context,
        "storage_uri": "s3://bucket/tenant-b/workspace-a/source/source-a/file.md",
    }
    with pytest.raises(PackageAObjectVerificationError, match="tenant/workspace scope") as scoped_out:
        runtime._read_and_verify_object(scoped_out_context)
    assert scoped_out.value.failure_code == "object_ref_scope_mismatch"

    hash_mismatch_context = {**context, "source_sha256": "0" * 64}
    with pytest.raises(PackageAObjectVerificationError, match="lineage facts") as hash_mismatch:
        runtime._read_and_verify_object(hash_mismatch_context)
    assert hash_mismatch.value.failure_code == "object_bytes_mismatch"

    revoked_context = {**context, "source_status": "revoked"}
    with pytest.raises(PackageAObjectVerificationError, match="not visible") as revoked:
        runtime._read_and_verify_object(revoked_context)
    assert revoked.value.failure_code == "object_visibility_revoked"

    deleted_context = {**context, "source_status": "physically_deleted"}
    with pytest.raises(PackageAObjectVerificationError, match="not visible") as deleted:
        runtime._read_and_verify_object(deleted_context)
    assert deleted.value.failure_code == "object_deleted"
    assert runtime.object_store.store.read_count == 2


def test_gate_b_postgres_attempt_lease_and_fencing_rejects_stale_worker() -> None:
    engine = _engine()
    try:
        _seed_job(engine)
        with IngestionUnitOfWork(engine) as repo:
            attempt1 = repo.claim_parse_attempt_lease(
                tenant_id="tenant-a",
                workspace_id="workspace-a",
                source_object_id="source:pkg-a:b",
                document_version_id="document-version:pkg-a:b",
                parse_plan_id="parse-plan:pkg-a:b",
                parse_job_id="parse-job:pkg-a:b",
                worker_id="worker-a",
                idempotency_key="parse:tenant-a:pkg-a:b:attempt:1",
                security_epoch_ref="security-epoch:pkg-a",
                lease_ttl_seconds=60,
            )
            repo.mark_parse_attempt_running(
                parse_attempt_id=attempt1.ref,
                parse_job_id="parse-job:pkg-a:b",
                tenant_id="tenant-a",
                worker_id="worker-a",
                fencing_token=int(attempt1.payload_hash or "0"),
            )
        with IngestionUnitOfWork(engine) as repo:
            attempt2 = repo.claim_parse_attempt_lease(
                tenant_id="tenant-a",
                workspace_id="workspace-a",
                source_object_id="source:pkg-a:b",
                document_version_id="document-version:pkg-a:b",
                parse_plan_id="parse-plan:pkg-a:b",
                parse_job_id="parse-job:pkg-a:b",
                worker_id="worker-b",
                idempotency_key="parse:tenant-a:pkg-a:b:attempt:2",
                security_epoch_ref="security-epoch:pkg-a",
                lease_ttl_seconds=60,
            )
            repo.commit_parse_attempt_if_current(
                parse_attempt_id=attempt2.ref,
                parse_job_id="parse-job:pkg-a:b",
                tenant_id="tenant-a",
                worker_id="worker-b",
                fencing_token=int(attempt2.payload_hash or "0"),
                domain_commit_ref="domain-commit:worker-b",
            )
        try:
            with IngestionUnitOfWork(engine) as repo:
                repo.commit_parse_attempt_if_current(
                    parse_attempt_id=attempt1.ref,
                    parse_job_id="parse-job:pkg-a:b",
                    tenant_id="tenant-a",
                    worker_id="worker-a",
                    fencing_token=int(attempt1.payload_hash or "0"),
                    domain_commit_ref="domain-commit:stale-worker-a",
                )
        except IngestionPersistenceError:
            pass
        else:
            raise AssertionError("stale worker commit must be rejected by PostgreSQL fencing")
    finally:
        engine.dispose()


def test_gate_b_heartbeat_renews_lease_and_expiry_reconciles_attempt() -> None:
    engine = _engine()
    try:
        _seed_job(engine)
        with IngestionUnitOfWork(engine) as repo:
            attempt = repo.claim_parse_attempt_lease(
                tenant_id="tenant-a",
                workspace_id="workspace-a",
                source_object_id="source:pkg-a:b",
                document_version_id="document-version:pkg-a:b",
                parse_plan_id="parse-plan:pkg-a:b",
                parse_job_id="parse-job:pkg-a:b",
                worker_id="worker-heartbeat",
                idempotency_key="parse:tenant-a:pkg-a:b:attempt:1",
                security_epoch_ref="security-epoch:pkg-a",
                lease_ttl_seconds=60,
            )
            fencing_token = int(attempt.payload_hash or "0")
            repo.mark_parse_attempt_running(
                parse_attempt_id=attempt.ref,
                parse_job_id="parse-job:pkg-a:b",
                tenant_id="tenant-a",
                worker_id="worker-heartbeat",
                fencing_token=fencing_token,
            )
            renewed = repo.renew_parse_attempt_lease(
                parse_attempt_id=attempt.ref,
                parse_job_id="parse-job:pkg-a:b",
                tenant_id="tenant-a",
                worker_id="worker-heartbeat",
                fencing_token=fencing_token,
                lease_ttl_seconds=120,
            )
            assert renewed.status == "lease_renewed"
        with engine.connect() as conn:
            renewed_row = conn.execute(
                text(
                    """
                    SELECT lease.state AS lease_state,
                           lease.lease_expires_at = attempt.lease_expires_at AS expiry_matches_attempt,
                           attempt.status AS attempt_status
                    FROM ingestion_parse_leases AS lease
                    JOIN ingestion_parse_attempts AS attempt
                      ON attempt.parse_attempt_id = lease.parse_attempt_id
                    WHERE lease.parse_attempt_id = :parse_attempt_id
                    """
                ),
                {"parse_attempt_id": attempt.ref},
            ).mappings().one()
            assert renewed_row["lease_state"] == "renewed"
            assert renewed_row["expiry_matches_attempt"] is True
            assert renewed_row["attempt_status"] == "running"
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    UPDATE ingestion_parse_leases
                    SET lease_expires_at = now() - interval '1 second'
                    WHERE parse_attempt_id = :parse_attempt_id
                    """
                ),
                {"parse_attempt_id": attempt.ref},
            )
            conn.execute(
                text(
                    """
                    UPDATE ingestion_parse_attempts
                    SET lease_expires_at = now() - interval '1 second'
                    WHERE parse_attempt_id = :parse_attempt_id
                    """
                ),
                {"parse_attempt_id": attempt.ref},
            )
        with IngestionUnitOfWork(engine) as repo:
            reconciled = repo.reconcile_expired_parse_attempt_lease(
                parse_attempt_id=attempt.ref,
                parse_job_id="parse-job:pkg-a:b",
                tenant_id="tenant-a",
            )
            assert reconciled.status == "lease_reconciled"
        with engine.connect() as conn:
            reconciled_row = conn.execute(
                text(
                    """
                    SELECT attempt.status AS attempt_status,
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
            assert reconciled_row["attempt_status"] == "lease_lost"
            assert reconciled_row["lease_state"] == "expired"
            assert reconciled_row["job_status"] == "queued"
    finally:
        engine.dispose()


def test_gate_b_retryable_failure_closes_lease_enqueues_retry_and_acks_after_commit(monkeypatch) -> None:
    engine = _engine()
    content = b"# Retry\nTemporary parser failure."
    envelope = _seed_retryable_job(engine, content=content)
    delivery_payload = CanonicalOutboxDeliveryV1(
        aggregate_id=envelope.aggregate_id or "",
        event_id=envelope.message_id,
        idempotency_key=envelope.idempotency_key or "",
        payload=envelope.model_dump(mode="json"),
        payload_hash=canonical_sha256(envelope.model_dump(mode="json")),
        topic="ingestion.parse.requested",
    ).model_dump(mode="json")
    delivery = _RecordingDelivery(payload=delivery_payload, tenant_id="tenant-a")
    runtime = PackageAProductionIngestionRuntime(
        engine=engine,
        object_store=_FakeObjectStore(bucket="bucket", object_name="tenant-a/workspace-a/retry.md", content=content),
        worker_id="phase11-package-a-worker",
        max_attempts=2,
    )

    def _failed_parse(_request):
        return ParseDocumentResult(
            job_id="parse-job:pkg-a:retry",
            status="failed",
            failure=ParserFailure(
                parser_id="native_markdown",
                format="markdown",
                reason="temporary parser outage",
                retryable=True,
                failure_classification="temporary_parser_failure",
            ),
        )

    def _failed_snapshot(_job_id):
        return ParseJobSnapshot(
            job_id="parse-job:pkg-a:retry",
            status="failed",
            document_id="source:pkg-a:retry",
            workspace_id="workspace-a",
            source_uri="s3://bucket/tenant-a/workspace-a/retry.md",
            mime_type="text/markdown",
            parser_id="native_markdown",
            parser_format="markdown",
            parse_plan_id="parse-plan:pkg-a:retry",
            parse_attempt_id="parse-attempt:pkg-a:retry:1",
            retryable=True,
        )

    monkeypatch.setattr(ParseGateway, "submit_parse_job", staticmethod(_failed_parse))
    monkeypatch.setattr(ParseGateway, "get_job_snapshot", staticmethod(_failed_snapshot))

    try:
        receipt = asyncio.run(runtime.process_rabbitmq_delivery(delivery))

        assert receipt.status == "failed"
        assert receipt.acked_after_domain_commit is True
        assert receipt.retry_enqueued_after_domain_commit is True
        assert receipt.outbox_event_id == "outbox:parse-job:pkg-a:retry:retry:2"
        assert delivery.acked is True
        assert delivery.nacked is False
        assert delivery.rejected is False

        with engine.connect() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT attempt.state AS attempt_state,
                           lease.state AS lease_state,
                           job.status AS job_status,
                           job.attempt_count AS attempt_count
                    FROM ingestion_parse_attempts AS attempt
                    JOIN ingestion_parse_leases AS lease
                      ON lease.parse_attempt_id = attempt.parse_attempt_id
                    JOIN ingestion_parse_jobs AS job
                      ON job.parse_job_id = attempt.parse_job_id
                    WHERE attempt.parse_attempt_id = :parse_attempt_id
                    """
                ),
                {"parse_attempt_id": receipt.parse_attempt_id},
            ).mappings().one()
            assert row["attempt_state"] == "failed"
            assert row["lease_state"] == "released"
            assert row["job_status"] == "queued"
            assert row["attempt_count"] == 1

            outbox = conn.execute(
                text(
                    """
                    SELECT outbox_event_id, payload ->> 'message_id' AS message_id,
                           payload ->> 'causation_id' AS causation_id,
                           publish_status
                    FROM ingestion_outbox_events
                    ORDER BY created_at, outbox_event_id
                    """
                )
            ).mappings().all()
            assert [item["outbox_event_id"] for item in outbox] == [
                "outbox:parse-job:pkg-a:retry",
                "outbox:parse-job:pkg-a:retry:retry:2",
            ]
            assert outbox[1]["message_id"] != outbox[0]["message_id"]
            assert outbox[1]["causation_id"] == outbox[0]["message_id"]
            assert outbox[1]["publish_status"] == "pending"
    finally:
        engine.dispose()


def test_gate_b_duplicate_delivery_acks_without_reparse_or_attempt(monkeypatch) -> None:
    engine = _engine()
    content = b"# Duplicate\nAlready consumed."
    envelope = _seed_retryable_job(engine, content=content)
    delivery_payload = CanonicalOutboxDeliveryV1(
        aggregate_id=envelope.aggregate_id or "",
        event_id=envelope.message_id,
        idempotency_key=envelope.idempotency_key or "",
        payload=envelope.model_dump(mode="json"),
        payload_hash=canonical_sha256(envelope.model_dump(mode="json")),
        topic="ingestion.parse.requested",
    ).model_dump(mode="json")
    delivery = _RecordingDelivery(payload=delivery_payload, tenant_id="tenant-a")
    delivery.redelivered = True
    runtime = PackageAProductionIngestionRuntime(
        engine=engine,
        object_store=_FakeObjectStore(
            bucket="bucket",
            object_name="tenant-a/workspace-a/retry.md",
            content=content,
        ),
        worker_id="phase11-package-a-worker",
        max_attempts=2,
    )

    def _unexpected_parse(_request):
        raise AssertionError("duplicate delivery must not call Parser Gateway")

    monkeypatch.setattr(ParseGateway, "submit_parse_job", staticmethod(_unexpected_parse))
    with IngestionUnitOfWork(engine) as repo:
        inbox = repo.record_worker_inbox(
            consumer="phase11-package-a-parser-worker",
            message_id=envelope.message_id,
            payload=delivery.payload,
            tenant_id="tenant-a",
        )
        assert inbox.processable is True

    try:
        receipt = asyncio.run(runtime.process_rabbitmq_delivery(delivery))

        assert receipt.status == "duplicate"
        assert receipt.duplicate_delivery is True
        assert receipt.acked_after_domain_commit is True
        assert delivery.acked is True
        assert delivery.nacked is False
        assert delivery.rejected is False

        with engine.connect() as conn:
            assert conn.execute(text("SELECT count(*) FROM ingestion_parse_attempts")).scalar_one() == 0
            assert conn.execute(text("SELECT count(*) FROM ingestion_parse_leases")).scalar_one() == 0
            assert conn.execute(text("SELECT count(*) FROM ingestion_parse_snapshots")).scalar_one() == 0
            assert conn.execute(text("SELECT count(*) FROM ingestion_outbox_events")).scalar_one() == 1
    finally:
        engine.dispose()


def test_gate_b_rejects_transport_message_id_mismatch_before_inbox(monkeypatch) -> None:
    engine = _engine()
    content = b"# Forged message id\nDo not lease."
    envelope = _seed_retryable_job(engine, content=content)
    delivery_payload = CanonicalOutboxDeliveryV1(
        aggregate_id=envelope.aggregate_id or "",
        event_id=envelope.message_id,
        idempotency_key=envelope.idempotency_key or "",
        payload=envelope.model_dump(mode="json"),
        payload_hash=canonical_sha256(envelope.model_dump(mode="json")),
        topic="ingestion.parse.requested",
    ).model_dump(mode="json")
    delivery = _RecordingDelivery(payload=delivery_payload, tenant_id="tenant-a")
    delivery.message_id = "rabbitmq-message-other"
    runtime = PackageAProductionIngestionRuntime(
        engine=engine,
        object_store=_FakeObjectStore(
            bucket="bucket",
            object_name="tenant-a/workspace-a/retry.md",
            content=content,
        ),
        worker_id="phase11-package-a-worker",
        max_attempts=2,
    )

    def _unexpected_parse(_request):
        raise AssertionError("message id mismatch must be rejected before Parser Gateway")

    monkeypatch.setattr(ParseGateway, "submit_parse_job", staticmethod(_unexpected_parse))

    try:
        with pytest.raises(PackageARejectDeliveryError, match="delivery message_id does not match envelope"):
            asyncio.run(runtime.process_rabbitmq_delivery(delivery))

        assert delivery.acked is False
        assert delivery.nacked is False
        assert delivery.rejected is True

        with engine.connect() as conn:
            assert conn.execute(text("SELECT count(*) FROM infra_inbox_messages")).scalar_one() == 0
            assert conn.execute(text("SELECT count(*) FROM ingestion_parse_attempts")).scalar_one() == 0
            assert conn.execute(text("SELECT count(*) FROM ingestion_parse_leases")).scalar_one() == 0
            assert conn.execute(text("SELECT status FROM ingestion_parse_jobs")).scalar_one() == "queued"
    finally:
        engine.dispose()


def test_gate_b_rejects_retry_policy_mismatch_before_inbox(monkeypatch) -> None:
    engine = _engine()
    content = b"# Forged retry policy\nDo not lease."
    envelope = _seed_retryable_job(engine, content=content)
    forged_payload = dict(envelope.payload or {})
    forged_payload["max_attempts"] = 3
    forged_envelope = envelope.model_copy(
        update={
            "payload": forged_payload,
            "payload_hash": canonical_sha256(forged_payload),
        }
    )
    delivery_payload = CanonicalOutboxDeliveryV1(
        aggregate_id=forged_envelope.aggregate_id or "",
        event_id=forged_envelope.message_id,
        idempotency_key=forged_envelope.idempotency_key or "",
        payload=forged_envelope.model_dump(mode="json"),
        payload_hash=canonical_sha256(forged_envelope.model_dump(mode="json")),
        topic="ingestion.parse.requested",
    ).model_dump(mode="json")
    delivery = _RecordingDelivery(payload=delivery_payload, tenant_id="tenant-a")
    runtime = PackageAProductionIngestionRuntime(
        engine=engine,
        object_store=_FakeObjectStore(
            bucket="bucket",
            object_name="tenant-a/workspace-a/retry.md",
            content=content,
        ),
        worker_id="phase11-package-a-worker",
        max_attempts=2,
    )

    def _unexpected_parse(_request):
        raise AssertionError("retry policy mismatch must be rejected before Parser Gateway")

    monkeypatch.setattr(ParseGateway, "submit_parse_job", staticmethod(_unexpected_parse))

    try:
        with pytest.raises(PackageARejectDeliveryError, match="delivery retry policy mismatch: max_attempts"):
            asyncio.run(runtime.process_rabbitmq_delivery(delivery))

        assert delivery.acked is False
        assert delivery.nacked is False
        assert delivery.rejected is True

        with engine.connect() as conn:
            assert conn.execute(text("SELECT count(*) FROM infra_inbox_messages")).scalar_one() == 0
            assert conn.execute(text("SELECT count(*) FROM ingestion_parse_attempts")).scalar_one() == 0
            assert conn.execute(text("SELECT count(*) FROM ingestion_parse_leases")).scalar_one() == 0
            assert conn.execute(text("SELECT status FROM ingestion_parse_jobs")).scalar_one() == "queued"
    finally:
        engine.dispose()


def test_package_a_rejects_retry_envelope_causation_mismatch_before_inbox() -> None:
    payload = {
        "tenant_id": "tenant-a",
        "workspace_id": "workspace-a",
        "source_object_id": "source:pkg-a:retry",
        "document_version_id": "document-version:pkg-a:retry",
        "parse_plan_id": "parse-plan:pkg-a:retry",
        "parse_job_id": "parse-job:pkg-a:retry",
        "object_ref": "s3://bucket/tenant-a/workspace-a/retry.md",
        "object_manifest_ref": "manifest:pkg-a:retry",
        "content_hash": "a" * 64,
        "size_bytes": 12,
        "mime_type": "text/markdown",
        "parser_policy_ref": "parser-policy:pkg-a",
        "quality_policy_ref": "quality-policy:pkg-a",
        "security_decision_ref": "security-decision:pkg-a",
        "security_epoch_ref": "security-epoch:pkg-a:retry",
        "max_attempts": 2,
        "retry_attempt_no": 2,
        "retry_parent_attempt_id": "parse-job:pkg-a:retry:attempt:1",
        "retry_parent_message_id": "outbox:parse-job:pkg-a:retry",
        "retry_parent_idempotency_key": "parse:tenant-a:workspace-a:hash:1",
    }
    envelope = CrossModuleEnvelopeV1(
        contract_name="zuno.ingestion.parse.requested",
        contract_version="v1",
        contract_bundle_version="wave1",
        message_id="outbox:parse-job:pkg-a:retry:retry:2",
        producer_module="ingestion.parser_worker",
        consumer_module="ingestion.parser_worker",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        causation_id="outbox:parse-job:pkg-a:other",
        correlation_id="trace-pkg-a-retry",
        idempotency_key="parse:tenant-a:workspace-a:hash:1:retry:2",
        aggregate_type="ParseJob",
        aggregate_id="parse-job:pkg-a:retry",
        effective_security_epoch_ref="security-epoch:pkg-a:retry",
        trace_id="trace-pkg-a-retry",
        data_classification="internal",
        occurred_at="2026-07-20T00:00:00Z",
        created_at="2026-07-20T00:00:00Z",
        payload=payload,
        payload_hash=canonical_sha256(payload),
        payload_schema_hash=canonical_sha256({"schema": "zuno.ingestion.parse.requested.v1"}),
    )
    delivery_payload = CanonicalOutboxDeliveryV1(
        aggregate_id=envelope.aggregate_id or "",
        event_id=envelope.message_id,
        idempotency_key=envelope.idempotency_key or "",
        payload=envelope.model_dump(mode="json"),
        payload_hash=canonical_sha256(envelope.model_dump(mode="json")),
        topic="ingestion.parse.requested",
    ).model_dump(mode="json")
    delivery = _RecordingDelivery(payload=delivery_payload, tenant_id="tenant-a")
    runtime = object.__new__(PackageAProductionIngestionRuntime)
    runtime.max_attempts = 2

    with pytest.raises(PackageARejectDeliveryError, match="delivery retry envelope mismatch: causation_id"):
        asyncio.run(runtime.process_rabbitmq_delivery(delivery))

    assert delivery.acked is False
    assert delivery.nacked is False
    assert delivery.rejected is True


def test_package_a_rejects_retry_attempt_beyond_budget_before_inbox() -> None:
    payload = {
        "tenant_id": "tenant-a",
        "workspace_id": "workspace-a",
        "source_object_id": "source:pkg-a:retry",
        "document_version_id": "document-version:pkg-a:retry",
        "parse_plan_id": "parse-plan:pkg-a:retry",
        "parse_job_id": "parse-job:pkg-a:retry",
        "object_ref": "s3://bucket/tenant-a/workspace-a/retry.md",
        "object_manifest_ref": "manifest:pkg-a:retry",
        "content_hash": "a" * 64,
        "size_bytes": 12,
        "mime_type": "text/markdown",
        "parser_policy_ref": "parser-policy:pkg-a",
        "quality_policy_ref": "quality-policy:pkg-a",
        "security_decision_ref": "security-decision:pkg-a",
        "security_epoch_ref": "security-epoch:pkg-a:retry",
        "max_attempts": 2,
        "retry_attempt_no": 3,
        "retry_parent_attempt_id": "parse-job:pkg-a:retry:attempt:2",
        "retry_parent_message_id": "outbox:parse-job:pkg-a:retry:retry:2",
        "retry_parent_idempotency_key": "parse:tenant-a:workspace-a:hash:1:retry:2",
    }
    envelope = CrossModuleEnvelopeV1(
        contract_name="zuno.ingestion.parse.requested",
        contract_version="v1",
        contract_bundle_version="wave1",
        message_id="outbox:parse-job:pkg-a:retry:retry:3",
        producer_module="ingestion.parser_worker",
        consumer_module="ingestion.parser_worker",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        causation_id="outbox:parse-job:pkg-a:retry:retry:2",
        correlation_id="trace-pkg-a-retry",
        idempotency_key="parse:tenant-a:workspace-a:hash:1:retry:2:retry:3",
        aggregate_type="ParseJob",
        aggregate_id="parse-job:pkg-a:retry",
        effective_security_epoch_ref="security-epoch:pkg-a:retry",
        trace_id="trace-pkg-a-retry",
        data_classification="internal",
        occurred_at="2026-07-20T00:00:00Z",
        created_at="2026-07-20T00:00:00Z",
        payload=payload,
        payload_hash=canonical_sha256(payload),
        payload_schema_hash=canonical_sha256({"schema": "zuno.ingestion.parse.requested.v1"}),
    )
    delivery_payload = CanonicalOutboxDeliveryV1(
        aggregate_id=envelope.aggregate_id or "",
        event_id=envelope.message_id,
        idempotency_key=envelope.idempotency_key or "",
        payload=envelope.model_dump(mode="json"),
        payload_hash=canonical_sha256(envelope.model_dump(mode="json")),
        topic="ingestion.parse.requested",
    ).model_dump(mode="json")
    delivery = _RecordingDelivery(payload=delivery_payload, tenant_id="tenant-a")
    runtime = object.__new__(PackageAProductionIngestionRuntime)
    runtime.max_attempts = 2

    with pytest.raises(PackageARejectDeliveryError, match="delivery retry policy mismatch: retry_attempt_no"):
        asyncio.run(runtime.process_rabbitmq_delivery(delivery))

    assert delivery.acked is False
    assert delivery.nacked is False
    assert delivery.rejected is True


def test_package_a_rejects_retry_header_count_mismatch_before_inbox() -> None:
    payload = {
        "tenant_id": "tenant-a",
        "workspace_id": "workspace-a",
        "source_object_id": "source:pkg-a:retry",
        "document_version_id": "document-version:pkg-a:retry",
        "parse_plan_id": "parse-plan:pkg-a:retry",
        "parse_job_id": "parse-job:pkg-a:retry",
        "object_ref": "s3://bucket/tenant-a/workspace-a/retry.md",
        "object_manifest_ref": "manifest:pkg-a:retry",
        "content_hash": "a" * 64,
        "size_bytes": 12,
        "mime_type": "text/markdown",
        "parser_policy_ref": "parser-policy:pkg-a",
        "quality_policy_ref": "quality-policy:pkg-a",
        "security_decision_ref": "security-decision:pkg-a",
        "security_epoch_ref": "security-epoch:pkg-a:retry",
        "max_attempts": 2,
        "retry_attempt_no": 2,
        "retry_parent_attempt_id": "parse-job:pkg-a:retry:attempt:1",
        "retry_parent_message_id": "outbox:parse-job:pkg-a:retry",
        "retry_parent_idempotency_key": "parse:tenant-a:workspace-a:hash:1",
    }
    envelope = CrossModuleEnvelopeV1(
        contract_name="zuno.ingestion.parse.requested",
        contract_version="v1",
        contract_bundle_version="wave1",
        message_id="outbox:parse-job:pkg-a:retry:retry:2",
        producer_module="ingestion.parser_worker",
        consumer_module="ingestion.parser_worker",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        causation_id="outbox:parse-job:pkg-a:retry",
        correlation_id="trace-pkg-a-retry",
        idempotency_key="parse:tenant-a:workspace-a:hash:1:retry:2",
        aggregate_type="ParseJob",
        aggregate_id="parse-job:pkg-a:retry",
        effective_security_epoch_ref="security-epoch:pkg-a:retry",
        trace_id="trace-pkg-a-retry",
        data_classification="internal",
        occurred_at="2026-07-20T00:00:00Z",
        created_at="2026-07-20T00:00:00Z",
        payload=payload,
        payload_hash=canonical_sha256(payload),
        payload_schema_hash=canonical_sha256({"schema": "zuno.ingestion.parse.requested.v1"}),
    )
    delivery_payload = CanonicalOutboxDeliveryV1(
        aggregate_id=envelope.aggregate_id or "",
        event_id=envelope.message_id,
        idempotency_key=envelope.idempotency_key or "",
        payload=envelope.model_dump(mode="json"),
        payload_hash=canonical_sha256(envelope.model_dump(mode="json")),
        topic="ingestion.parse.requested",
    ).model_dump(mode="json")
    delivery = _RecordingDelivery(payload=delivery_payload, tenant_id="tenant-a")
    runtime = object.__new__(PackageAProductionIngestionRuntime)
    runtime.max_attempts = 2

    with pytest.raises(PackageARejectDeliveryError, match="delivery outbox header mismatch: retry_count"):
        asyncio.run(runtime.process_rabbitmq_delivery(delivery))

    assert delivery.acked is False
    assert delivery.nacked is False
    assert delivery.rejected is True


def test_package_a_rejects_retry_upload_producer_before_inbox() -> None:
    payload = {
        "tenant_id": "tenant-a",
        "workspace_id": "workspace-a",
        "source_object_id": "source:pkg-a:retry",
        "document_version_id": "document-version:pkg-a:retry",
        "parse_plan_id": "parse-plan:pkg-a:retry",
        "parse_job_id": "parse-job:pkg-a:retry",
        "object_ref": "s3://bucket/tenant-a/workspace-a/retry.md",
        "object_manifest_ref": "manifest:pkg-a:retry",
        "content_hash": "a" * 64,
        "size_bytes": 12,
        "mime_type": "text/markdown",
        "parser_policy_ref": "parser-policy:pkg-a",
        "quality_policy_ref": "quality-policy:pkg-a",
        "security_decision_ref": "security-decision:pkg-a",
        "security_epoch_ref": "security-epoch:pkg-a:retry",
        "max_attempts": 2,
        "retry_attempt_no": 2,
        "retry_parent_attempt_id": "parse-job:pkg-a:retry:attempt:1",
        "retry_parent_message_id": "outbox:parse-job:pkg-a:retry",
        "retry_parent_idempotency_key": "parse:tenant-a:workspace-a:hash:1",
    }
    envelope = CrossModuleEnvelopeV1(
        contract_name="zuno.ingestion.parse.requested",
        contract_version="v1",
        contract_bundle_version="wave1",
        message_id="outbox:parse-job:pkg-a:retry:retry:2",
        producer_module="workspace.file_upload",
        consumer_module="ingestion.parser_worker",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        causation_id="outbox:parse-job:pkg-a:retry",
        correlation_id="trace-pkg-a-retry",
        idempotency_key="parse:tenant-a:workspace-a:hash:1:retry:2",
        aggregate_type="ParseJob",
        aggregate_id="parse-job:pkg-a:retry",
        effective_security_epoch_ref="security-epoch:pkg-a:retry",
        trace_id="trace-pkg-a-retry",
        data_classification="internal",
        occurred_at="2026-07-20T00:00:00Z",
        created_at="2026-07-20T00:00:00Z",
        payload=payload,
        payload_hash=canonical_sha256(payload),
        payload_schema_hash=canonical_sha256({"schema": "zuno.ingestion.parse.requested.v1"}),
    )
    delivery_payload = CanonicalOutboxDeliveryV1(
        aggregate_id=envelope.aggregate_id or "",
        event_id=envelope.message_id,
        idempotency_key=envelope.idempotency_key or "",
        payload=envelope.model_dump(mode="json"),
        payload_hash=canonical_sha256(envelope.model_dump(mode="json")),
        topic="ingestion.parse.requested",
    ).model_dump(mode="json")
    delivery = _RecordingDelivery(payload=delivery_payload, tenant_id="tenant-a")
    delivery.headers["outbox_retry_count"] = 1
    runtime = object.__new__(PackageAProductionIngestionRuntime)
    runtime.max_attempts = 2

    with pytest.raises(PackageARejectDeliveryError, match="delivery producer lineage mismatch"):
        asyncio.run(runtime.process_rabbitmq_delivery(delivery))

    assert delivery.acked is False
    assert delivery.nacked is False
    assert delivery.rejected is True


def test_package_a_rejects_workspace_header_mismatch_before_inbox() -> None:
    payload = {
        "tenant_id": "tenant-a",
        "workspace_id": "workspace-a",
        "source_object_id": "source:pkg-a:workspace",
        "document_version_id": "document-version:pkg-a:workspace",
        "parse_plan_id": "parse-plan:pkg-a:workspace",
        "parse_job_id": "parse-job:pkg-a:workspace",
        "object_ref": "s3://bucket/tenant-a/workspace-a/workspace.md",
        "object_manifest_ref": "manifest:pkg-a:workspace",
        "content_hash": "a" * 64,
        "size_bytes": 12,
        "mime_type": "text/markdown",
        "parser_policy_ref": "parser-policy:pkg-a",
        "quality_policy_ref": "quality-policy:pkg-a",
        "security_decision_ref": "security-decision:pkg-a",
        "security_epoch_ref": "security-epoch:pkg-a:workspace",
        "max_attempts": 2,
    }
    envelope = CrossModuleEnvelopeV1(
        contract_name="zuno.ingestion.parse.requested",
        contract_version="v1",
        contract_bundle_version="wave1",
        message_id="outbox:parse-job:pkg-a:workspace",
        producer_module="workspace.file_upload",
        consumer_module="ingestion.parser_worker",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        correlation_id="trace-pkg-a-workspace",
        idempotency_key="parse:tenant-a:workspace-a:hash:workspace",
        aggregate_type="ParseJob",
        aggregate_id="parse-job:pkg-a:workspace",
        effective_security_epoch_ref="security-epoch:pkg-a:workspace",
        trace_id="trace-pkg-a-workspace",
        data_classification="internal",
        occurred_at="2026-07-20T00:00:00Z",
        created_at="2026-07-20T00:00:00Z",
        payload=payload,
        payload_hash=canonical_sha256(payload),
        payload_schema_hash=canonical_sha256({"schema": "zuno.ingestion.parse.requested.v1"}),
    )
    delivery_payload = CanonicalOutboxDeliveryV1(
        aggregate_id=envelope.aggregate_id or "",
        event_id=envelope.message_id,
        idempotency_key=envelope.idempotency_key or "",
        payload=envelope.model_dump(mode="json"),
        payload_hash=canonical_sha256(envelope.model_dump(mode="json")),
        topic="ingestion.parse.requested",
    ).model_dump(mode="json")
    delivery = _RecordingDelivery(payload=delivery_payload, tenant_id="tenant-a")
    delivery.headers["workspace_id"] = "workspace-b"
    runtime = object.__new__(PackageAProductionIngestionRuntime)
    runtime.max_attempts = 2

    with pytest.raises(PackageARejectDeliveryError, match="delivery workspace header does not match envelope"):
        asyncio.run(runtime.process_rabbitmq_delivery(delivery))

    assert delivery.acked is False
    assert delivery.nacked is False
    assert delivery.rejected is True


def test_package_a_rejects_payload_tenant_mismatch_before_inbox() -> None:
    payload = {
        "tenant_id": "tenant-b",
        "workspace_id": "workspace-a",
        "source_object_id": "source:pkg-a:tenant",
        "document_version_id": "document-version:pkg-a:tenant",
        "parse_plan_id": "parse-plan:pkg-a:tenant",
        "parse_job_id": "parse-job:pkg-a:tenant",
        "object_ref": "s3://bucket/tenant-a/workspace-a/tenant.md",
        "object_manifest_ref": "manifest:pkg-a:tenant",
        "content_hash": "a" * 64,
        "size_bytes": 12,
        "mime_type": "text/markdown",
        "parser_policy_ref": "parser-policy:pkg-a",
        "quality_policy_ref": "quality-policy:pkg-a",
        "security_decision_ref": "security-decision:pkg-a",
        "security_epoch_ref": "security-epoch:pkg-a:tenant",
        "max_attempts": 2,
    }
    envelope = CrossModuleEnvelopeV1(
        contract_name="zuno.ingestion.parse.requested",
        contract_version="v1",
        contract_bundle_version="wave1",
        message_id="outbox:parse-job:pkg-a:tenant",
        producer_module="workspace.file_upload",
        consumer_module="ingestion.parser_worker",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        correlation_id="trace-pkg-a-tenant",
        idempotency_key="parse:tenant-a:workspace-a:hash:tenant",
        aggregate_type="ParseJob",
        aggregate_id="parse-job:pkg-a:tenant",
        effective_security_epoch_ref="security-epoch:pkg-a:tenant",
        trace_id="trace-pkg-a-tenant",
        data_classification="internal",
        occurred_at="2026-07-20T00:00:00Z",
        created_at="2026-07-20T00:00:00Z",
        payload=payload,
        payload_hash=canonical_sha256(payload),
        payload_schema_hash=canonical_sha256({"schema": "zuno.ingestion.parse.requested.v1"}),
    )
    delivery_payload = CanonicalOutboxDeliveryV1(
        aggregate_id=envelope.aggregate_id or "",
        event_id=envelope.message_id,
        idempotency_key=envelope.idempotency_key or "",
        payload=envelope.model_dump(mode="json"),
        payload_hash=canonical_sha256(envelope.model_dump(mode="json")),
        topic="ingestion.parse.requested",
    ).model_dump(mode="json")
    delivery = _RecordingDelivery(payload=delivery_payload, tenant_id="tenant-a")
    runtime = object.__new__(PackageAProductionIngestionRuntime)
    runtime.max_attempts = 2

    with pytest.raises(PackageARejectDeliveryError, match="delivery tenant header does not match envelope"):
        asyncio.run(runtime.process_rabbitmq_delivery(delivery))

    assert delivery.acked is False
    assert delivery.nacked is False
    assert delivery.rejected is True


def test_package_a_rejects_trace_header_mismatch_before_inbox() -> None:
    payload = {
        "tenant_id": "tenant-a",
        "workspace_id": "workspace-a",
        "source_object_id": "source:pkg-a:trace",
        "document_version_id": "document-version:pkg-a:trace",
        "parse_plan_id": "parse-plan:pkg-a:trace",
        "parse_job_id": "parse-job:pkg-a:trace",
        "object_ref": "s3://bucket/tenant-a/workspace-a/trace.md",
        "object_manifest_ref": "manifest:pkg-a:trace",
        "content_hash": "a" * 64,
        "size_bytes": 12,
        "mime_type": "text/markdown",
        "parser_policy_ref": "parser-policy:pkg-a",
        "quality_policy_ref": "quality-policy:pkg-a",
        "security_decision_ref": "security-decision:pkg-a",
        "security_epoch_ref": "security-epoch:pkg-a:trace",
        "max_attempts": 2,
    }
    envelope = CrossModuleEnvelopeV1(
        contract_name="zuno.ingestion.parse.requested",
        contract_version="v1",
        contract_bundle_version="wave1",
        message_id="outbox:parse-job:pkg-a:trace",
        producer_module="workspace.file_upload",
        consumer_module="ingestion.parser_worker",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        correlation_id="trace-pkg-a-trace",
        idempotency_key="parse:tenant-a:workspace-a:hash:trace",
        aggregate_type="ParseJob",
        aggregate_id="parse-job:pkg-a:trace",
        effective_security_epoch_ref="security-epoch:pkg-a:trace",
        trace_id="trace-pkg-a-trace",
        data_classification="internal",
        occurred_at="2026-07-20T00:00:00Z",
        created_at="2026-07-20T00:00:00Z",
        payload=payload,
        payload_hash=canonical_sha256(payload),
        payload_schema_hash=canonical_sha256({"schema": "zuno.ingestion.parse.requested.v1"}),
    )
    delivery_payload = CanonicalOutboxDeliveryV1(
        aggregate_id=envelope.aggregate_id or "",
        event_id=envelope.message_id,
        idempotency_key=envelope.idempotency_key or "",
        payload=envelope.model_dump(mode="json"),
        payload_hash=canonical_sha256(envelope.model_dump(mode="json")),
        topic="ingestion.parse.requested",
    ).model_dump(mode="json")
    delivery = _RecordingDelivery(payload=delivery_payload, tenant_id="tenant-a")
    delivery.headers["trace_id"] = "trace-other"
    runtime = object.__new__(PackageAProductionIngestionRuntime)
    runtime.max_attempts = 2

    with pytest.raises(PackageARejectDeliveryError, match="delivery trace header does not match envelope"):
        asyncio.run(runtime.process_rabbitmq_delivery(delivery))

    assert delivery.acked is False
    assert delivery.nacked is False
    assert delivery.rejected is True


def test_package_a_rejects_data_classification_header_mismatch_before_inbox() -> None:
    payload = {
        "tenant_id": "tenant-a",
        "workspace_id": "workspace-a",
        "source_object_id": "source:pkg-a:classification",
        "document_version_id": "document-version:pkg-a:classification",
        "parse_plan_id": "parse-plan:pkg-a:classification",
        "parse_job_id": "parse-job:pkg-a:classification",
        "object_ref": "s3://bucket/tenant-a/workspace-a/classification.md",
        "object_manifest_ref": "manifest:pkg-a:classification",
        "content_hash": "a" * 64,
        "size_bytes": 12,
        "mime_type": "text/markdown",
        "parser_policy_ref": "parser-policy:pkg-a",
        "quality_policy_ref": "quality-policy:pkg-a",
        "security_decision_ref": "security-decision:pkg-a",
        "security_epoch_ref": "security-epoch:pkg-a:classification",
        "max_attempts": 2,
    }
    envelope = CrossModuleEnvelopeV1(
        contract_name="zuno.ingestion.parse.requested",
        contract_version="v1",
        contract_bundle_version="wave1",
        message_id="outbox:parse-job:pkg-a:classification",
        producer_module="workspace.file_upload",
        consumer_module="ingestion.parser_worker",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        correlation_id="trace-pkg-a-classification",
        idempotency_key="parse:tenant-a:workspace-a:hash:classification",
        aggregate_type="ParseJob",
        aggregate_id="parse-job:pkg-a:classification",
        effective_security_epoch_ref="security-epoch:pkg-a:classification",
        trace_id="trace-pkg-a-classification",
        data_classification="internal",
        occurred_at="2026-07-20T00:00:00Z",
        created_at="2026-07-20T00:00:00Z",
        payload=payload,
        payload_hash=canonical_sha256(payload),
        payload_schema_hash=canonical_sha256({"schema": "zuno.ingestion.parse.requested.v1"}),
    )
    delivery_payload = CanonicalOutboxDeliveryV1(
        aggregate_id=envelope.aggregate_id or "",
        event_id=envelope.message_id,
        idempotency_key=envelope.idempotency_key or "",
        payload=envelope.model_dump(mode="json"),
        payload_hash=canonical_sha256(envelope.model_dump(mode="json")),
        topic="ingestion.parse.requested",
    ).model_dump(mode="json")
    delivery = _RecordingDelivery(payload=delivery_payload, tenant_id="tenant-a")
    delivery.headers["data_classification"] = "restricted"
    runtime = object.__new__(PackageAProductionIngestionRuntime)
    runtime.max_attempts = 2

    with pytest.raises(
        PackageARejectDeliveryError,
        match="delivery data classification header does not match envelope",
    ):
        asyncio.run(runtime.process_rabbitmq_delivery(delivery))

    assert delivery.acked is False
    assert delivery.nacked is False
    assert delivery.rejected is True


def test_package_a_rejects_message_version_header_mismatch_before_inbox() -> None:
    payload = {
        "tenant_id": "tenant-a",
        "workspace_id": "workspace-a",
        "source_object_id": "source:pkg-a:version",
        "document_version_id": "document-version:pkg-a:version",
        "parse_plan_id": "parse-plan:pkg-a:version",
        "parse_job_id": "parse-job:pkg-a:version",
        "object_ref": "s3://bucket/tenant-a/workspace-a/version.md",
        "object_manifest_ref": "manifest:pkg-a:version",
        "content_hash": "a" * 64,
        "size_bytes": 12,
        "mime_type": "text/markdown",
        "parser_policy_ref": "parser-policy:pkg-a",
        "quality_policy_ref": "quality-policy:pkg-a",
        "security_decision_ref": "security-decision:pkg-a",
        "security_epoch_ref": "security-epoch:pkg-a:version",
        "max_attempts": 2,
    }
    envelope = CrossModuleEnvelopeV1(
        contract_name="zuno.ingestion.parse.requested",
        contract_version="v1",
        contract_bundle_version="wave1",
        message_id="outbox:parse-job:pkg-a:version",
        producer_module="workspace.file_upload",
        consumer_module="ingestion.parser_worker",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        correlation_id="trace-pkg-a-version",
        idempotency_key="parse:tenant-a:workspace-a:hash:version",
        aggregate_type="ParseJob",
        aggregate_id="parse-job:pkg-a:version",
        effective_security_epoch_ref="security-epoch:pkg-a:version",
        trace_id="trace-pkg-a-version",
        data_classification="internal",
        occurred_at="2026-07-20T00:00:00Z",
        created_at="2026-07-20T00:00:00Z",
        payload=payload,
        payload_hash=canonical_sha256(payload),
        payload_schema_hash=canonical_sha256({"schema": "zuno.ingestion.parse.requested.v1"}),
    )
    delivery_payload = CanonicalOutboxDeliveryV1(
        aggregate_id=envelope.aggregate_id or "",
        event_id=envelope.message_id,
        idempotency_key=envelope.idempotency_key or "",
        payload=envelope.model_dump(mode="json"),
        payload_hash=canonical_sha256(envelope.model_dump(mode="json")),
        topic="ingestion.parse.requested",
    ).model_dump(mode="json")
    delivery = _RecordingDelivery(payload=delivery_payload, tenant_id="tenant-a")
    delivery.headers["message_version"] = "v2"
    runtime = object.__new__(PackageAProductionIngestionRuntime)
    runtime.max_attempts = 2

    with pytest.raises(
        PackageARejectDeliveryError,
        match="delivery message version header does not match envelope",
    ):
        asyncio.run(runtime.process_rabbitmq_delivery(delivery))

    assert delivery.acked is False
    assert delivery.nacked is False
    assert delivery.rejected is True


def test_package_a_rejects_outbox_ordering_header_mismatch_before_inbox() -> None:
    payload = {
        "tenant_id": "tenant-a",
        "workspace_id": "workspace-a",
        "source_object_id": "source:pkg-a:retry",
        "document_version_id": "document-version:pkg-a:retry",
        "parse_plan_id": "parse-plan:pkg-a:retry",
        "parse_job_id": "parse-job:pkg-a:retry",
        "object_ref": "s3://bucket/tenant-a/workspace-a/retry.md",
        "object_manifest_ref": "manifest:pkg-a:retry",
        "content_hash": "a" * 64,
        "size_bytes": 12,
        "mime_type": "text/markdown",
        "parser_policy_ref": "parser-policy:pkg-a",
        "quality_policy_ref": "quality-policy:pkg-a",
        "security_decision_ref": "security-decision:pkg-a",
        "security_epoch_ref": "security-epoch:pkg-a:retry",
        "max_attempts": 2,
    }
    envelope = CrossModuleEnvelopeV1(
        contract_name="zuno.ingestion.parse.requested",
        contract_version="v1",
        contract_bundle_version="wave1",
        message_id="outbox:parse-job:pkg-a:retry",
        producer_module="workspace.file_upload",
        consumer_module="ingestion.parser_worker",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        correlation_id="trace-pkg-a-retry",
        idempotency_key="parse:tenant-a:workspace-a:hash:1",
        aggregate_type="ParseJob",
        aggregate_id="parse-job:pkg-a:retry",
        effective_security_epoch_ref="security-epoch:pkg-a:retry",
        trace_id="trace-pkg-a-retry",
        data_classification="internal",
        occurred_at="2026-07-20T00:00:00Z",
        created_at="2026-07-20T00:00:00Z",
        payload=payload,
        payload_hash=canonical_sha256(payload),
        payload_schema_hash=canonical_sha256({"schema": "zuno.ingestion.parse.requested.v1"}),
    )
    delivery_payload = CanonicalOutboxDeliveryV1(
        aggregate_id=envelope.aggregate_id or "",
        event_id=envelope.message_id,
        idempotency_key=envelope.idempotency_key or "",
        payload=envelope.model_dump(mode="json"),
        payload_hash=canonical_sha256(envelope.model_dump(mode="json")),
        topic="ingestion.parse.requested",
    ).model_dump(mode="json")
    delivery = _RecordingDelivery(payload=delivery_payload, tenant_id="tenant-a")
    delivery.headers["ordering_key"] = "parse-job:pkg-a:other"
    runtime = object.__new__(PackageAProductionIngestionRuntime)
    runtime.max_attempts = 2

    with pytest.raises(PackageARejectDeliveryError, match="delivery outbox header mismatch: ordering_key"):
        asyncio.run(runtime.process_rabbitmq_delivery(delivery))

    assert delivery.acked is False
    assert delivery.nacked is False
    assert delivery.rejected is True


def test_gate_b_rejects_retry_parent_attempt_mismatch_before_new_attempt(monkeypatch) -> None:
    engine = _engine()
    content = b"# Forged retry parent\nDo not lease."
    envelope = _seed_retryable_job(engine, content=content)
    with IngestionUnitOfWork(engine) as repo:
        attempt = repo.claim_parse_attempt_lease(
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            source_object_id="source:pkg-a:retry",
            document_version_id="document-version:pkg-a:retry",
            parse_plan_id="parse-plan:pkg-a:retry",
            parse_job_id="parse-job:pkg-a:retry",
            worker_id="phase11-package-a-worker",
            idempotency_key=f"{envelope.idempotency_key}:attempt:1",
            security_epoch_ref="security-epoch:pkg-a:retry",
            lease_ttl_seconds=60,
        )
        fencing_token = int(attempt.payload_hash or "0")
        repo.mark_parse_attempt_running(
            parse_attempt_id=attempt.ref,
            parse_job_id="parse-job:pkg-a:retry",
            tenant_id="tenant-a",
            worker_id="phase11-package-a-worker",
            fencing_token=fencing_token,
        )
        repo.fail_parse_attempt(
            parse_attempt_id=attempt.ref,
            parse_job_id="parse-job:pkg-a:retry",
            tenant_id="tenant-a",
            worker_id="phase11-package-a-worker",
            fencing_token=fencing_token,
            status="failed",
            failure_code="retryable_parser_failure",
        )
        repo.update_parse_job_status(parse_job_id="parse-job:pkg-a:retry", tenant_id="tenant-a", status="queued")

    forged_payload = dict(envelope.payload or {})
    forged_payload.update(
        {
            "retry_attempt_no": 2,
            "retry_parent_attempt_id": "parse-job:pkg-a:retry:attempt:stale",
            "retry_parent_message_id": envelope.message_id,
            "retry_parent_idempotency_key": envelope.idempotency_key,
        }
    )
    forged_envelope = envelope.model_copy(
        update={
            "message_id": "outbox:parse-job:pkg-a:retry:2",
            "producer_module": "ingestion.parser_worker",
            "idempotency_key": f"{envelope.idempotency_key}:retry:2",
            "payload": forged_payload,
            "payload_hash": canonical_sha256(forged_payload),
        }
    )
    delivery_payload = CanonicalOutboxDeliveryV1(
        aggregate_id=forged_envelope.aggregate_id or "",
        event_id=forged_envelope.message_id,
        idempotency_key=forged_envelope.idempotency_key or "",
        payload=forged_envelope.model_dump(mode="json"),
        payload_hash=canonical_sha256(forged_envelope.model_dump(mode="json")),
        topic="ingestion.parse.requested",
    ).model_dump(mode="json")
    delivery = _RecordingDelivery(payload=delivery_payload, tenant_id="tenant-a")
    delivery.headers["outbox_retry_count"] = 1
    runtime = PackageAProductionIngestionRuntime(
        engine=engine,
        object_store=_FakeObjectStore(
            bucket="bucket",
            object_name="tenant-a/workspace-a/retry.md",
            content=content,
        ),
        worker_id="phase11-package-a-worker",
        max_attempts=2,
    )

    def _unexpected_parse(_request):
        raise AssertionError("retry parent mismatch must be rejected before Parser Gateway")

    monkeypatch.setattr(ParseGateway, "submit_parse_job", staticmethod(_unexpected_parse))

    try:
        with pytest.raises(PackageARejectDeliveryError, match="retry_parent_attempt_id"):
            asyncio.run(runtime.process_rabbitmq_delivery(delivery))

        assert delivery.acked is False
        assert delivery.nacked is False
        assert delivery.rejected is True

        with engine.connect() as conn:
            assert conn.execute(text("SELECT count(*) FROM infra_inbox_messages")).scalar_one() == 0
            assert conn.execute(text("SELECT count(*) FROM ingestion_parse_attempts")).scalar_one() == 1
            assert conn.execute(text("SELECT count(*) FROM ingestion_parse_leases")).scalar_one() == 1
            assert conn.execute(text("SELECT status FROM ingestion_parse_jobs")).scalar_one() == "queued"
    finally:
        engine.dispose()


def test_gate_b_rejects_delivery_lineage_mismatch_before_attempt(monkeypatch) -> None:
    engine = _engine()
    content = b"# Forged lineage\nDo not lease."
    envelope = _seed_retryable_job(engine, content=content)
    forged_payload = dict(envelope.payload or {})
    forged_payload["source_object_id"] = "source:pkg-a:forged"
    forged_envelope = envelope.model_copy(
        update={
            "payload": forged_payload,
            "payload_hash": canonical_sha256(forged_payload),
        }
    )
    delivery_payload = CanonicalOutboxDeliveryV1(
        aggregate_id=forged_envelope.aggregate_id or "",
        event_id=forged_envelope.message_id,
        idempotency_key=forged_envelope.idempotency_key or "",
        payload=forged_envelope.model_dump(mode="json"),
        payload_hash=canonical_sha256(forged_envelope.model_dump(mode="json")),
        topic="ingestion.parse.requested",
    ).model_dump(mode="json")
    delivery = _RecordingDelivery(payload=delivery_payload, tenant_id="tenant-a")
    runtime = PackageAProductionIngestionRuntime(
        engine=engine,
        object_store=_FakeObjectStore(
            bucket="bucket",
            object_name="tenant-a/workspace-a/retry.md",
            content=content,
        ),
        worker_id="phase11-package-a-worker",
        max_attempts=2,
    )

    def _unexpected_parse(_request):
        raise AssertionError("lineage mismatch must be rejected before Parser Gateway")

    monkeypatch.setattr(ParseGateway, "submit_parse_job", staticmethod(_unexpected_parse))

    try:
        with pytest.raises(PackageARejectDeliveryError, match="delivery lineage mismatch: source_object_id"):
            asyncio.run(runtime.process_rabbitmq_delivery(delivery))

        assert delivery.acked is False
        assert delivery.nacked is False
        assert delivery.rejected is True

        with engine.connect() as conn:
            assert conn.execute(text("SELECT count(*) FROM infra_inbox_messages")).scalar_one() == 0
            assert conn.execute(text("SELECT count(*) FROM ingestion_parse_attempts")).scalar_one() == 0
            assert conn.execute(text("SELECT count(*) FROM ingestion_parse_leases")).scalar_one() == 0
            assert conn.execute(text("SELECT count(*) FROM ingestion_parse_snapshots")).scalar_one() == 0
            assert conn.execute(text("SELECT status FROM ingestion_parse_jobs")).scalar_one() == "queued"
    finally:
        engine.dispose()


def test_gate_b_redelivery_after_commit_returns_existing_success_without_reparse(monkeypatch) -> None:
    engine = _engine()
    content = b"# Redelivery\nCommitted before ACK."
    envelope = _seed_retryable_job(engine, content=content)
    delivery_payload = CanonicalOutboxDeliveryV1(
        aggregate_id=envelope.aggregate_id or "",
        event_id=envelope.message_id,
        idempotency_key=envelope.idempotency_key or "",
        payload=envelope.model_dump(mode="json"),
        payload_hash=canonical_sha256(envelope.model_dump(mode="json")),
        topic="ingestion.parse.requested",
    ).model_dump(mode="json")
    delivery = _RecordingDelivery(payload=delivery_payload, tenant_id="tenant-a")
    delivery.redelivered = True
    runtime = PackageAProductionIngestionRuntime(
        engine=engine,
        object_store=_FakeObjectStore(
            bucket="bucket",
            object_name="tenant-a/workspace-a/retry.md",
            content=content,
        ),
        worker_id="phase11-package-a-worker",
        max_attempts=2,
    )

    def _unexpected_parse(_request):
        raise AssertionError("redelivery after committed domain result must not reparse")

    monkeypatch.setattr(ParseGateway, "submit_parse_job", staticmethod(_unexpected_parse))
    with IngestionUnitOfWork(engine) as repo:
        inbox = repo.record_worker_inbox(
            consumer="phase11-package-a-parser-worker",
            message_id=envelope.message_id,
            payload=delivery.payload,
            tenant_id="tenant-a",
        )
        assert inbox.processable is True
        attempt = repo.claim_parse_attempt_lease(
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            source_object_id="source:pkg-a:retry",
            document_version_id="document-version:pkg-a:retry",
            parse_plan_id="parse-plan:pkg-a:retry",
            parse_job_id="parse-job:pkg-a:retry",
            worker_id="phase11-package-a-worker",
            idempotency_key=f"{envelope.idempotency_key}:attempt:1",
            security_epoch_ref="security-epoch:pkg-a:retry",
            lease_ttl_seconds=60,
        )
        fencing_token = int(attempt.payload_hash or "0")
        repo.mark_parse_attempt_running(
            parse_attempt_id=attempt.ref,
            parse_job_id="parse-job:pkg-a:retry",
            tenant_id="tenant-a",
            worker_id="phase11-package-a-worker",
            fencing_token=fencing_token,
        )
        snapshot = repo.record_parse_snapshot(
            parse_snapshot_id=f"parse-snapshot:{attempt.ref}",
            tenant_id="tenant-a",
            parse_job_id="parse-job:pkg-a:retry",
            parse_attempt_id=attempt.ref,
            document_version_id="document-version:pkg-a:retry",
            canonical_ir={"metadata": {"document_id": "source:pkg-a:retry"}, "blocks": []},
            canonical_ir_ref=f"canonical-ir:{attempt.ref}",
            canonical_ir_schema_ref="canonical-document-ir-v1",
            parser_id="native_markdown",
            parser_version="phase11-package-a-v1",
        )
        quality = repo.record_quality_decision(
            quality_decision_id=f"quality:{attempt.ref}",
            tenant_id="tenant-a",
            parse_snapshot_id=snapshot.ref,
            coverage_score=1.0,
            confidence_score=1.0,
            decision="publish",
        )
        indexable = repo.record_indexable_snapshot(
            indexable_snapshot_id=f"indexable:{attempt.ref}",
            tenant_id="tenant-a",
            parse_snapshot_id=snapshot.ref,
            document_version_id="document-version:pkg-a:retry",
            quality_decision_id=quality.ref,
            visibility_ref="visibility:workspace-a:source:pkg-a:retry",
            payload={"indexable_snapshot_id": f"indexable:{attempt.ref}"},
        )
        outbox = repo.enqueue_outbox_event(
            outbox_event_id=f"outbox:indexable:{attempt.ref}",
            tenant_id="tenant-a",
            aggregate_ref=indexable.ref,
            event_type="ingestion.indexable_snapshot.ready",
            payload={"indexable_snapshot_id": indexable.ref},
        )
        repo.commit_parse_attempt_if_current(
            parse_attempt_id=attempt.ref,
            parse_job_id="parse-job:pkg-a:retry",
            tenant_id="tenant-a",
            worker_id="phase11-package-a-worker",
            fencing_token=fencing_token,
            domain_commit_ref=f"domain-commit:{attempt.ref}:{snapshot.ref}:{outbox.ref}",
        )

    try:
        receipt = asyncio.run(runtime.process_rabbitmq_delivery(delivery))

        assert receipt.status == "succeeded"
        assert receipt.duplicate_delivery is True
        assert receipt.acked_after_domain_commit is True
        assert receipt.parse_attempt_id == "parse-job:pkg-a:retry:attempt:1"
        assert receipt.indexable_snapshot_id == "indexable:parse-job:pkg-a:retry:attempt:1"
        assert receipt.outbox_event_id == "outbox:indexable:parse-job:pkg-a:retry:attempt:1"
        assert delivery.acked is True
        assert delivery.nacked is False
        assert delivery.rejected is False

        with engine.connect() as conn:
            assert conn.execute(text("SELECT count(*) FROM ingestion_parse_attempts")).scalar_one() == 1
            assert conn.execute(text("SELECT count(*) FROM ingestion_parse_snapshots")).scalar_one() == 1
            assert conn.execute(text("SELECT count(*) FROM ingestion_indexable_document_snapshots")).scalar_one() == 1
    finally:
        engine.dispose()


def test_gate_b_non_retryable_failure_records_dlq_without_retry_outbox(monkeypatch) -> None:
    engine = _engine()
    content = b"# DLQ\nPermanent parser failure."
    envelope = _seed_retryable_job(engine, content=content)
    delivery_payload = CanonicalOutboxDeliveryV1(
        aggregate_id=envelope.aggregate_id or "",
        event_id=envelope.message_id,
        idempotency_key=envelope.idempotency_key or "",
        payload=envelope.model_dump(mode="json"),
        payload_hash=canonical_sha256(envelope.model_dump(mode="json")),
        topic="ingestion.parse.requested",
    ).model_dump(mode="json")
    delivery = _RecordingDelivery(payload=delivery_payload, tenant_id="tenant-a")
    runtime = PackageAProductionIngestionRuntime(
        engine=engine,
        object_store=_FakeObjectStore(
            bucket="bucket",
            object_name="tenant-a/workspace-a/retry.md",
            content=content,
        ),
        worker_id="phase11-package-a-worker",
        max_attempts=2,
    )

    def _failed_parse(_request):
        return ParseDocumentResult(
            job_id="parse-job:pkg-a:retry",
            status="failed",
            failure=ParserFailure(
                parser_id="native_markdown",
                format="markdown",
                reason="corrupt source object",
                retryable=False,
                failure_classification="corrupt_source",
            ),
        )

    def _failed_snapshot(_job_id):
        return ParseJobSnapshot(
            job_id="parse-job:pkg-a:retry",
            status="failed",
            document_id="source:pkg-a:retry",
            workspace_id="workspace-a",
            source_uri="s3://bucket/tenant-a/workspace-a/retry.md",
            mime_type="text/markdown",
            parser_id="native_markdown",
            parser_format="markdown",
            parse_plan_id="parse-plan:pkg-a:retry",
            parse_attempt_id="parse-attempt:pkg-a:retry:1",
            retryable=False,
        )

    monkeypatch.setattr(ParseGateway, "submit_parse_job", staticmethod(_failed_parse))
    monkeypatch.setattr(ParseGateway, "get_job_snapshot", staticmethod(_failed_snapshot))

    try:
        receipt = asyncio.run(runtime.process_rabbitmq_delivery(delivery))

        assert receipt.status == "dead_letter"
        assert receipt.acked_after_domain_commit is False
        assert receipt.retry_enqueued_after_domain_commit is False
        assert receipt.outbox_event_id is None
        assert receipt.dead_letter_id == f"dead-letter:{receipt.parse_attempt_id}"
        assert delivery.acked is False
        assert delivery.nacked is False
        assert delivery.rejected is True

        with engine.connect() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT attempt.state AS attempt_state,
                           lease.state AS lease_state,
                           job.status AS job_status,
                           job.attempt_count AS attempt_count
                    FROM ingestion_parse_attempts AS attempt
                    JOIN ingestion_parse_leases AS lease
                      ON lease.parse_attempt_id = attempt.parse_attempt_id
                    JOIN ingestion_parse_jobs AS job
                      ON job.parse_job_id = attempt.parse_job_id
                    WHERE attempt.parse_attempt_id = :parse_attempt_id
                    """
                ),
                {"parse_attempt_id": receipt.parse_attempt_id},
            ).mappings().one()
            assert row["attempt_state"] == "dead_letter"
            assert row["lease_state"] == "released"
            assert row["job_status"] == "dead_letter"
            assert row["attempt_count"] == 1

            dead_letter = conn.execute(
                text(
                    """
                    SELECT failure_code, retryable, retry_count, rabbitmq_dead_letter_ref
                    FROM ingestion_dead_letters
                    WHERE dead_letter_id = :dead_letter_id
                    """
                ),
                {"dead_letter_id": receipt.dead_letter_id},
            ).mappings().one()
            assert dead_letter["failure_code"] == "corrupt_source"
            assert dead_letter["retryable"] is False
            assert dead_letter["retry_count"] == 1
            assert dead_letter["rabbitmq_dead_letter_ref"] == f"rabbitmq-dlq:{envelope.message_id}"

            outbox_ids = conn.execute(
                text("SELECT outbox_event_id FROM ingestion_outbox_events ORDER BY outbox_event_id")
            ).scalars().all()
            assert outbox_ids == ["outbox:parse-job:pkg-a:retry"]
    finally:
        engine.dispose()


def test_gate_b_object_hash_mismatch_records_dlq_without_requeue(monkeypatch) -> None:
    engine = _engine()
    content = b"# Object mismatch\nExpected content."
    envelope = _seed_retryable_job(engine, content=content)
    delivery_payload = CanonicalOutboxDeliveryV1(
        aggregate_id=envelope.aggregate_id or "",
        event_id=envelope.message_id,
        idempotency_key=envelope.idempotency_key or "",
        payload=envelope.model_dump(mode="json"),
        payload_hash=canonical_sha256(envelope.model_dump(mode="json")),
        topic="ingestion.parse.requested",
    ).model_dump(mode="json")
    delivery = _RecordingDelivery(payload=delivery_payload, tenant_id="tenant-a")
    runtime = PackageAProductionIngestionRuntime(
        engine=engine,
        object_store=_FakeObjectStore(
            bucket="bucket",
            object_name="tenant-a/workspace-a/retry.md",
            content=b"# Object mismatch\nTampered content.",
        ),
        worker_id="phase11-package-a-worker",
        max_attempts=2,
    )

    def _unexpected_parse(_request):
        raise AssertionError("object verification failure must not call Parser Gateway")

    monkeypatch.setattr(ParseGateway, "submit_parse_job", staticmethod(_unexpected_parse))

    try:
        receipt = asyncio.run(runtime.process_rabbitmq_delivery(delivery))

        assert receipt.status == "dead_letter"
        assert receipt.acked_after_domain_commit is False
        assert receipt.dead_letter_id == f"dead-letter:{receipt.parse_attempt_id}"
        assert delivery.acked is False
        assert delivery.nacked is False
        assert delivery.rejected is True

        with engine.connect() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT attempt.status AS attempt_status,
                           attempt.failure_code AS failure_code,
                           lease.state AS lease_state,
                           job.status AS job_status,
                           job.attempt_count AS attempt_count
                    FROM ingestion_parse_attempts AS attempt
                    JOIN ingestion_parse_leases AS lease
                      ON lease.parse_attempt_id = attempt.parse_attempt_id
                    JOIN ingestion_parse_jobs AS job
                      ON job.parse_job_id = attempt.parse_job_id
                    WHERE attempt.parse_attempt_id = :parse_attempt_id
                    """
                ),
                {"parse_attempt_id": receipt.parse_attempt_id},
            ).mappings().one()
            assert row["attempt_status"] == "dead_letter"
            assert row["failure_code"] == "object_bytes_mismatch"
            assert row["lease_state"] == "released"
            assert row["job_status"] == "dead_letter"
            assert row["attempt_count"] == 1

            dead_letter = conn.execute(
                text(
                    """
                    SELECT failure_code, retryable, retry_count, rabbitmq_dead_letter_ref
                    FROM ingestion_dead_letters
                    WHERE dead_letter_id = :dead_letter_id
                    """
                ),
                {"dead_letter_id": receipt.dead_letter_id},
            ).mappings().one()
            assert dead_letter["failure_code"] == "object_bytes_mismatch"
            assert dead_letter["retryable"] is False
            assert dead_letter["retry_count"] == 1
            assert dead_letter["rabbitmq_dead_letter_ref"] == f"rabbitmq-dlq:{envelope.message_id}"
    finally:
        engine.dispose()


def test_gate_b_quality_review_records_snapshot_without_indexable_handoff(monkeypatch) -> None:
    engine = _engine()
    content = b"# Quality review\nLow confidence parse."
    envelope = _seed_retryable_job(engine, content=content)
    delivery_payload = CanonicalOutboxDeliveryV1(
        aggregate_id=envelope.aggregate_id or "",
        event_id=envelope.message_id,
        idempotency_key=envelope.idempotency_key or "",
        payload=envelope.model_dump(mode="json"),
        payload_hash=canonical_sha256(envelope.model_dump(mode="json")),
        topic="ingestion.parse.requested",
    ).model_dump(mode="json")
    delivery = _RecordingDelivery(payload=delivery_payload, tenant_id="tenant-a")
    runtime = PackageAProductionIngestionRuntime(
        engine=engine,
        object_store=_FakeObjectStore(
            bucket="bucket",
            object_name="tenant-a/workspace-a/retry.md",
            content=content,
        ),
        worker_id="phase11-package-a-worker",
        max_attempts=2,
    )

    def _low_confidence_parse(_request):
        return ParseDocumentResult(
            job_id="parse-job:pkg-a:retry",
            status="succeeded",
            document=_low_confidence_document(content_hash=hashlib.sha256(content).hexdigest()),
        )

    def _succeeded_snapshot(_job_id):
        return ParseJobSnapshot(
            job_id="parse-job:pkg-a:retry",
            status="succeeded",
            document_id="source:pkg-a:retry",
            workspace_id="workspace-a",
            source_uri="s3://bucket/tenant-a/workspace-a/retry.md",
            mime_type="text/markdown",
            parser_id="native_markdown",
            parser_format="markdown",
            parse_plan_id="parse-plan:pkg-a:retry",
            parse_attempt_id="parse-job:pkg-a:retry:attempt:1",
            retryable=False,
        )

    monkeypatch.setattr(ParseGateway, "submit_parse_job", staticmethod(_low_confidence_parse))
    monkeypatch.setattr(ParseGateway, "get_job_snapshot", staticmethod(_succeeded_snapshot))

    try:
        receipt = asyncio.run(runtime.process_rabbitmq_delivery(delivery))

        assert receipt.status == "failed"
        assert receipt.acked_after_domain_commit is True
        assert receipt.indexable_snapshot_id is None
        assert receipt.outbox_event_id is None
        assert delivery.acked is True
        assert delivery.nacked is False
        assert delivery.rejected is False

        with engine.connect() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT attempt.status AS attempt_status,
                           attempt.failure_code AS failure_code,
                           lease.state AS lease_state,
                           job.status AS job_status,
                           quality.decision AS quality_decision
                    FROM ingestion_parse_attempts AS attempt
                    JOIN ingestion_parse_leases AS lease
                      ON lease.parse_attempt_id = attempt.parse_attempt_id
                    JOIN ingestion_parse_jobs AS job
                      ON job.parse_job_id = attempt.parse_job_id
                    JOIN ingestion_parse_snapshots AS snapshot
                      ON snapshot.parse_attempt_id = attempt.parse_attempt_id
                    JOIN ingestion_quality_gate_decisions AS quality
                      ON quality.parse_snapshot_id = snapshot.parse_snapshot_id
                    WHERE attempt.parse_attempt_id = :parse_attempt_id
                    """
                ),
                {"parse_attempt_id": receipt.parse_attempt_id},
            ).mappings().one()
            assert row["attempt_status"] == "failed"
            assert row["failure_code"] == "quality_gate_review"
            assert row["lease_state"] == "released"
            assert row["job_status"] == "failed"
            assert row["quality_decision"] == "review_required"
            assert conn.execute(text("SELECT count(*) FROM ingestion_source_spans")).scalar_one() == 1
            assert conn.execute(text("SELECT count(*) FROM ingestion_indexable_document_snapshots")).scalar_one() == 0
            assert conn.execute(text("SELECT count(*) FROM ingestion_outbox_events")).scalar_one() == 1
    finally:
        engine.dispose()


def test_gate_b_parser_attempt_identity_mismatch_dead_letters_without_snapshot(monkeypatch) -> None:
    engine = _engine()
    content = b"# Parser identity\nWrong attempt."
    envelope = _seed_retryable_job(engine, content=content)
    delivery_payload = CanonicalOutboxDeliveryV1(
        aggregate_id=envelope.aggregate_id or "",
        event_id=envelope.message_id,
        idempotency_key=envelope.idempotency_key or "",
        payload=envelope.model_dump(mode="json"),
        payload_hash=canonical_sha256(envelope.model_dump(mode="json")),
        topic="ingestion.parse.requested",
    ).model_dump(mode="json")
    delivery = _RecordingDelivery(payload=delivery_payload, tenant_id="tenant-a")
    runtime = PackageAProductionIngestionRuntime(
        engine=engine,
        object_store=_FakeObjectStore(
            bucket="bucket",
            object_name="tenant-a/workspace-a/retry.md",
            content=content,
        ),
        worker_id="phase11-package-a-worker",
        max_attempts=2,
    )

    def _succeeded_parse(_request):
        return ParseDocumentResult(
            job_id="parse-job:pkg-a:retry",
            status="succeeded",
            document=_low_confidence_document(content_hash=hashlib.sha256(content).hexdigest()),
        )

    def _wrong_attempt_snapshot(_job_id):
        return ParseJobSnapshot(
            job_id="parse-job:pkg-a:retry",
            status="succeeded",
            document_id="source:pkg-a:retry",
            workspace_id="workspace-a",
            source_uri="s3://bucket/tenant-a/workspace-a/retry.md",
            mime_type="text/markdown",
            parser_id="native_markdown",
            parser_format="markdown",
            parse_plan_id="parse-plan:pkg-a:retry",
            parse_attempt_id="parse-job:pkg-a:retry:attempt:999",
            retryable=False,
        )

    monkeypatch.setattr(ParseGateway, "submit_parse_job", staticmethod(_succeeded_parse))
    monkeypatch.setattr(ParseGateway, "get_job_snapshot", staticmethod(_wrong_attempt_snapshot))

    try:
        receipt = asyncio.run(runtime.process_rabbitmq_delivery(delivery))

        assert receipt.status == "dead_letter"
        assert receipt.acked_after_domain_commit is False
        assert receipt.dead_letter_id == f"dead-letter:{receipt.parse_attempt_id}"
        assert delivery.acked is False
        assert delivery.nacked is False
        assert delivery.rejected is True

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
                {"parse_attempt_id": receipt.parse_attempt_id},
            ).mappings().one()
            assert row["attempt_status"] == "dead_letter"
            assert row["failure_code"] == "parser_attempt_identity_mismatch"
            assert row["lease_state"] == "released"
            assert row["job_status"] == "dead_letter"
            assert conn.execute(text("SELECT count(*) FROM ingestion_parse_snapshots")).scalar_one() == 0
            assert conn.execute(text("SELECT count(*) FROM ingestion_indexable_document_snapshots")).scalar_one() == 0
    finally:
        engine.dispose()


def test_gate_b_cancel_requested_closes_attempt_and_lease_without_snapshot(monkeypatch) -> None:
    engine = _engine()
    content = b"# Cancel\nDo not parse."
    envelope = _seed_retryable_job(engine, content=content)
    payload = dict(envelope.payload or {})
    payload["cancel_requested"] = True
    envelope = envelope.model_copy(
        update={
            "payload": payload,
            "payload_hash": canonical_sha256(payload),
        }
    )
    delivery_payload = CanonicalOutboxDeliveryV1(
        aggregate_id=envelope.aggregate_id or "",
        event_id=envelope.message_id,
        idempotency_key=envelope.idempotency_key or "",
        payload=envelope.model_dump(mode="json"),
        payload_hash=canonical_sha256(envelope.model_dump(mode="json")),
        topic="ingestion.parse.requested",
    ).model_dump(mode="json")
    delivery = _RecordingDelivery(payload=delivery_payload, tenant_id="tenant-a")
    runtime = PackageAProductionIngestionRuntime(
        engine=engine,
        object_store=_FakeObjectStore(
            bucket="bucket",
            object_name="tenant-a/workspace-a/retry.md",
            content=content,
        ),
        worker_id="phase11-package-a-worker",
        max_attempts=2,
    )

    def _unexpected_parse(_request):
        raise AssertionError("cancelled delivery must not call Parser Gateway")

    monkeypatch.setattr(ParseGateway, "submit_parse_job", staticmethod(_unexpected_parse))

    try:
        receipt = asyncio.run(runtime.process_rabbitmq_delivery(delivery))

        assert receipt.status == "cancelled"
        assert receipt.acked_after_domain_commit is True
        assert receipt.indexable_snapshot_id is None
        assert receipt.outbox_event_id is None
        assert receipt.dead_letter_id is None
        assert delivery.acked is True
        assert delivery.nacked is False
        assert delivery.rejected is False

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
                {"parse_attempt_id": receipt.parse_attempt_id},
            ).mappings().one()
            assert row["attempt_status"] == "cancelled"
            assert row["failure_code"] == "cancel_requested"
            assert row["lease_state"] == "released"
            assert row["job_status"] == "cancelled"
            assert conn.execute(text("SELECT count(*) FROM ingestion_parse_snapshots")).scalar_one() == 0
            assert conn.execute(text("SELECT count(*) FROM ingestion_indexable_document_snapshots")).scalar_one() == 0
            assert conn.execute(text("SELECT count(*) FROM ingestion_outbox_events")).scalar_one() == 1
    finally:
        engine.dispose()


def test_gate_c_outbox_publish_failure_keeps_parse_request_replayable() -> None:
    engine = _engine()
    content = b"# Publish failure\nKeep the outbox replayable."
    envelope = _seed_retryable_job(engine, content=content)
    publisher = PostgresOutboxRabbitMQPublisher(
        engine=engine,
        transport=_FailingRabbitMQTransport(),
        topology=_topology(),
        worker_id="phase11-package-a-publisher",
        tenant_id="tenant-a",
        trace_id="trace-pkg-a-publish-failure",
        policy=OutboxPublishPolicy(
            max_attempts=3,
            base_backoff_seconds=0,
            max_backoff_seconds=0,
            publish_timeout_seconds=1,
        ),
    )

    try:
        batch = asyncio.run(publisher.publish_batch(limit=10))

        assert batch.published == ()
        assert len(batch.failed) == 1
        failed = batch.failed[0]
        assert failed.event_id == envelope.message_id
        assert failed.status == "pending"
        assert failed.publish_attempts == 1
        assert failed.retry_count == 1
        assert failed.error_code == "ConnectionError"

        with engine.connect() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT status, publish_attempts, retry_count, claim_owner,
                           last_error_code, next_attempt_at <= now() AS retry_ready
                    FROM infra_outbox_events
                    WHERE event_id = :event_id
                    """
                ),
                {"event_id": envelope.message_id},
            ).mappings().one()
            assert row["status"] == "pending"
            assert row["publish_attempts"] == 1
            assert row["retry_count"] == 1
            assert row["claim_owner"] is None
            assert row["last_error_code"] == "ConnectionError"
            assert row["retry_ready"] is True
        with InfrastructureUnitOfWork(engine) as repo:
            assert repo.claim_outbox(worker_id="phase11-package-a-replay-publisher", limit=10) == [
                envelope.message_id
            ]
    finally:
        engine.dispose()


def test_gate_c_real_minio_rabbitmq_upload_to_snapshot_outbox() -> None:
    asyncio.run(_gate_c_real_minio_rabbitmq_upload_to_snapshot_outbox())


async def _gate_c_real_minio_rabbitmq_upload_to_snapshot_outbox() -> None:
    engine = _engine()
    topology = _topology()
    object_store = DurableMinioObjectStore(
        store=MinioObjectStore(
            endpoint=MINIO_ENDPOINT,
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False,
        ),
        engine=engine,
        owner="phase11-package-a",
    )
    runtime = PackageAProductionIngestionRuntime(
        engine=engine,
        object_store=object_store,
        worker_id="phase11-package-a-worker",
    )
    try:
        upload = runtime.accept_workspace_upload(
            PackageAUploadCommand(
                tenant_id="tenant-a",
                workspace_id="workspace-a",
                principal_id="user-a",
                filename="package-a.md",
                mime_type="text/markdown",
                content=b"# Package A\nProduction path.",
                bucket="zuno-phase11-package-a",
                source_object_id="source-pkg-a-c",
                classification_ref="internal",
                security_epoch_ref="security-epoch:pkg-a:c",
                trace_id="trace-pkg-a-c",
            )
        )
        assert upload.status == "accepted"

        async with RabbitMQTransport(RABBITMQ_URL) as transport:
            await transport.declare_topology(topology)
            publisher = PostgresOutboxRabbitMQPublisher(
                engine=engine,
                transport=transport,
                topology=topology,
                worker_id="phase11-package-a-publisher",
                tenant_id="tenant-a",
                trace_id="trace-pkg-a-c",
            )
            published = await publisher.publish_pending(limit=10)
            assert [item.event_id for item in published] == [upload.outbox_event_id]

            delivery = await transport.get(topology.queue)
            assert delivery is not None
            worker_receipt = await runtime.process_rabbitmq_delivery(delivery)
            assert worker_receipt.status == "succeeded"
            assert worker_receipt.acked_after_domain_commit is True
            assert worker_receipt.indexable_snapshot_id
            assert worker_receipt.outbox_event_id

        with engine.connect() as conn:
            assert conn.execute(text("SELECT count(*) FROM ingestion_parse_snapshots")).scalar_one() == 1
            assert conn.execute(text("SELECT count(*) FROM ingestion_indexable_document_snapshots")).scalar_one() == 1
            assert conn.execute(text("SELECT count(*) FROM ingestion_outbox_events")).scalar_one() == 1
    finally:
        engine.dispose()


def _low_confidence_document(*, content_hash: str) -> CanonicalDocumentIR:
    return CanonicalDocumentIR(
        metadata=DocumentMetadata(
            document_id="source:pkg-a:retry",
            source_id="source:pkg-a:retry",
            source_object_ref="s3://bucket/tenant-a/workspace-a/retry.md",
            object_manifest_ref="manifest:pkg-a:retry",
            workspace_id="workspace-a",
            source_uri="s3://bucket/tenant-a/workspace-a/retry.md",
            mime_type="text/markdown",
            hash=content_hash,
            source_sha256=content_hash,
            parser_id="native_markdown",
            parser_version="phase11-package-a-v1",
            document_version_id="document-version:pkg-a:retry",
            security_epoch_ref="security-epoch:pkg-a:retry",
        ),
        blocks=[
            DocumentBlock(
                block_id="block-low-confidence",
                type="paragraph",
                text="Low confidence parse result.",
                source_span=SourceSpan(page=1, line_range=[1, 1]),
                confidence=0.5,
            )
        ],
        provenance=DocumentProvenance(
            parser_id="native_markdown",
            parser_version="phase11-package-a-v1",
            source_uri="s3://bucket/tenant-a/workspace-a/retry.md",
            confidence=0.5,
        ),
    )


def _topology() -> RabbitMQTopology:
    suffix = uuid4().hex
    return RabbitMQTopology(
        exchange=f"phase11.package_a.exchange.{suffix}",
        queue=f"phase11.package_a.queue.{suffix}",
        routing_key=f"phase11.package_a.route.{suffix}",
        dead_letter_exchange=f"phase11.package_a.dlx.{suffix}",
        dead_letter_queue=f"phase11.package_a.dlq.{suffix}",
        dead_letter_routing_key=f"phase11.package_a.dead.{suffix}",
    )
