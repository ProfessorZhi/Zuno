from __future__ import annotations

import asyncio
import hashlib
import os
import subprocess
from pathlib import Path
from typing import Any
from uuid import uuid4

from sqlalchemy import text

from zuno.knowledge.ingestion import PackageAProductionIngestionRuntime, PackageAUploadCommand
from zuno.knowledge.ingestion.contracts import ParseDocumentResult, ParseJobSnapshot, ParserFailure
from zuno.knowledge.ingestion.gateway import ParseGateway
from zuno.platform.contracts import CrossModuleEnvelopeV1, canonical_sha256
from zuno.platform.database.foundation import create_foundation_engine
from zuno.platform.database.ingestion import IngestionPersistenceError, IngestionUnitOfWork
from zuno.platform.queue.domain import CanonicalOutboxDeliveryV1
from zuno.platform.queue import PostgresOutboxRabbitMQPublisher, RabbitMQTopology, RabbitMQTransport
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

    def read_object(self, *, bucket: str, object_name: str) -> bytes:
        assert bucket == self.bucket
        assert object_name == self.object_name
        return self.content


class _FakeObjectStore:
    def __init__(self, *, bucket: str, object_name: str, content: bytes) -> None:
        self.store = _FakeObjectReader(bucket=bucket, object_name=object_name, content=content)


class _RecordingDelivery:
    def __init__(self, *, payload: dict[str, Any], tenant_id: str) -> None:
        self.message_id = str(payload["event_id"])
        self.payload = payload
        self.headers = {"tenant_id": tenant_id}
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
        assert receipt.acked_after_domain_commit is True
        assert receipt.retry_enqueued_after_domain_commit is False
        assert receipt.outbox_event_id is None
        assert receipt.dead_letter_id == f"dead-letter:{receipt.parse_attempt_id}"
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
