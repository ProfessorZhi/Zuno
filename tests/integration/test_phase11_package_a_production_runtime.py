from __future__ import annotations

import asyncio
import os
import subprocess
from pathlib import Path
from uuid import uuid4

from sqlalchemy import text

from zuno.knowledge.ingestion import PackageAProductionIngestionRuntime, PackageAUploadCommand
from zuno.platform.database.foundation import create_foundation_engine
from zuno.platform.database.ingestion import IngestionPersistenceError, IngestionUnitOfWork
from zuno.platform.queue import PostgresOutboxRabbitMQPublisher, RabbitMQTopology, RabbitMQTransport
from zuno.platform.storage import DurableMinioObjectStore, MinioObjectStore


REPO_ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno?connect_timeout=5",
)
RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"
MINIO_ENDPOINT = "localhost:9000"


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
