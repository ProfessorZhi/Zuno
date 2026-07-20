import asyncio
from datetime import datetime, timezone

import pytest

from zuno.knowledge.ingestion import PackageAProductionIngestionRuntime, PackageAWorkerReceipt
from zuno.platform.contracts import CrossModuleEnvelopeV1, canonical_sha256
from zuno.platform.database.ingestion import IngestionPersistenceError


class _RecordingDelivery:
    message_id = "event-1"
    payload = {}
    headers = {}
    redelivered = False

    def __init__(self) -> None:
        self.acked = False
        self.rejected = False
        self.requeue: bool | None = None

    async def ack(self) -> None:
        self.acked = True

    async def nack(self, *, requeue: bool) -> None:
        raise AssertionError("Package A settlement should not nack terminal receipts")

    async def reject(self, *, requeue: bool = False) -> None:
        self.rejected = True
        self.requeue = requeue


def test_package_a_settlement_acks_success_after_domain_commit() -> None:
    delivery = _RecordingDelivery()
    receipt = PackageAWorkerReceipt(
        parse_job_id="job-1",
        parse_attempt_id="attempt-1",
        status="succeeded",
        acked_after_domain_commit=True,
    )

    asyncio.run(
        PackageAProductionIngestionRuntime._settle_delivery_after_domain_commit(
            delivery=delivery,
            worker_receipt=receipt,
        )
    )

    assert delivery.acked is True
    assert delivery.rejected is False


def test_package_a_settlement_rejects_dead_letter_after_domain_commit() -> None:
    delivery = _RecordingDelivery()
    receipt = PackageAWorkerReceipt(
        parse_job_id="job-1",
        parse_attempt_id="attempt-1",
        status="dead_letter",
        acked_after_domain_commit=False,
        dead_letter_id="dead-letter:attempt-1",
    )

    asyncio.run(
        PackageAProductionIngestionRuntime._settle_delivery_after_domain_commit(
            delivery=delivery,
            worker_receipt=receipt,
        )
    )

    assert delivery.acked is False
    assert delivery.rejected is True
    assert delivery.requeue is False


def test_package_a_rejects_invalid_delivery_schema_without_requeue() -> None:
    delivery = _RecordingDelivery()
    delivery.payload = {"event_id": "event-1"}

    with pytest.raises(IngestionPersistenceError, match="invalid Package A parse delivery envelope"):
        asyncio.run(
            PackageAProductionIngestionRuntime.process_rabbitmq_delivery(
                _runtime_without_init(),
                delivery,
            )
        )

    assert delivery.acked is False
    assert delivery.rejected is True
    assert delivery.requeue is False


def test_package_a_rejects_payload_hash_mismatch_without_requeue() -> None:
    envelope = _envelope(payload={"parse_job_id": "job-1"})
    delivery = _RecordingDelivery()
    delivery.payload = {
        "aggregate_id": envelope.aggregate_id,
        "event_id": envelope.message_id,
        "idempotency_key": envelope.idempotency_key,
        "payload": envelope.model_dump(mode="json"),
        "payload_hash": "not-the-canonical-hash",
        "topic": "ingestion.parse.requested",
    }

    with pytest.raises(IngestionPersistenceError, match="invalid Package A parse delivery envelope"):
        asyncio.run(
            PackageAProductionIngestionRuntime.process_rabbitmq_delivery(
                _runtime_without_init(),
                delivery,
            )
        )

    assert delivery.acked is False
    assert delivery.rejected is True
    assert delivery.requeue is False


def _runtime_without_init() -> PackageAProductionIngestionRuntime:
    return object.__new__(PackageAProductionIngestionRuntime)


def _envelope(*, payload: dict) -> CrossModuleEnvelopeV1:
    now = datetime(2026, 7, 20, tzinfo=timezone.utc)
    return CrossModuleEnvelopeV1(
        contract_name="zuno.ingestion.parse.requested",
        contract_version="v1",
        contract_bundle_version="phase11-package-a",
        message_id="event-1",
        producer_module="workspace.file_upload",
        consumer_module="ingestion.parser_worker",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        correlation_id="trace-1",
        idempotency_key="idem-1",
        aggregate_type="ParseJob",
        aggregate_id="job-1",
        trace_id="trace-1",
        data_classification="internal",
        occurred_at=now,
        created_at=now,
        payload=payload,
        payload_hash=canonical_sha256(payload),
        payload_schema_hash=canonical_sha256({"schema": "zuno.ingestion.parse.requested.v1"}),
    )
