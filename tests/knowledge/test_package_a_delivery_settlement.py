import asyncio
from datetime import datetime, timezone

import pytest

from zuno.knowledge.ingestion import (
    PACKAGE_A_PARSE_CONSUMER_MODULE,
    PACKAGE_A_PARSE_CONTRACT_NAME,
    PACKAGE_A_PARSE_REQUESTED_TOPIC,
    PackageAProductionIngestionRuntime,
    PackageAParserIdentityError,
    PackageARejectDeliveryError,
    PackageAWorkerReceipt,
)
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


def test_package_a_rejects_wrong_topic_without_requeue() -> None:
    delivery = _delivery_for_envelope(_envelope(payload={"parse_job_id": "job-1"}))
    delivery.payload["topic"] = "knowledge.snapshot.ready"

    _assert_rejected_parse_delivery(delivery, "delivery is not a Package A parse request")


def test_package_a_rejects_wrong_contract_without_requeue() -> None:
    delivery = _delivery_for_envelope(
        _envelope(
            payload={"parse_job_id": "job-1"},
            contract_name="zuno.knowledge.snapshot.ready",
        )
    )

    _assert_rejected_parse_delivery(delivery, "delivery is not a Package A parse request")


def test_package_a_rejects_wrong_consumer_without_requeue() -> None:
    delivery = _delivery_for_envelope(
        _envelope(
            payload={"parse_job_id": "job-1"},
            consumer_module="knowledge.indexer",
        )
    )

    _assert_rejected_parse_delivery(delivery, "delivery is not a Package A parse request")


def test_package_a_lineage_validator_requires_payload_to_match_postgres_context() -> None:
    payload = _lineage_payload()
    context = _lineage_context()

    PackageAProductionIngestionRuntime._validate_delivery_lineage(payload=payload, context=context)

    forged_payload = {**payload, "object_ref": "s3://bucket/tenant-b/workspace-a/source/source-a/file.md"}
    with pytest.raises(PackageARejectDeliveryError, match="delivery lineage mismatch: object_ref"):
        PackageAProductionIngestionRuntime._validate_delivery_lineage(
            payload=forged_payload,
            context=context,
        )


def test_package_a_lineage_validator_rejects_size_mismatch() -> None:
    payload = {**_lineage_payload(), "size_bytes": 999}

    with pytest.raises(PackageARejectDeliveryError, match="delivery lineage mismatch: size_bytes"):
        PackageAProductionIngestionRuntime._validate_delivery_lineage(
            payload=payload,
            context=_lineage_context(),
        )


def test_package_a_quality_failure_code_uses_verdict() -> None:
    class _Gate:
        verdict = "REVIEW"

    assert PackageAProductionIngestionRuntime._quality_failure_code(_Gate()) == "quality_gate_review"


def test_package_a_parser_identity_validator_requires_current_job_and_attempt() -> None:
    class _Result:
        job_id = "parse-job-a"
        status = "succeeded"

    class _Snapshot:
        parse_attempt_id = "parse-job-a:attempt:1"

    PackageAProductionIngestionRuntime._validate_parser_identity(
        result=_Result(),
        snapshot=_Snapshot(),
        parse_job_id="parse-job-a",
        parse_attempt_id="parse-job-a:attempt:1",
    )

    class _WrongJobResult:
        job_id = "parse-job-b"
        status = "succeeded"

    with pytest.raises(PackageAParserIdentityError, match="result job_id"):
        PackageAProductionIngestionRuntime._validate_parser_identity(
            result=_WrongJobResult(),
            snapshot=_Snapshot(),
            parse_job_id="parse-job-a",
            parse_attempt_id="parse-job-a:attempt:1",
        )

    class _WrongAttemptSnapshot:
        parse_attempt_id = "parse-job-a:attempt:2"

    with pytest.raises(PackageAParserIdentityError, match="snapshot parse_attempt_id"):
        PackageAProductionIngestionRuntime._validate_parser_identity(
            result=_Result(),
            snapshot=_WrongAttemptSnapshot(),
            parse_job_id="parse-job-a",
            parse_attempt_id="parse-job-a:attempt:1",
        )


def test_package_a_worker_inbox_uses_runtime_worker_identity(monkeypatch) -> None:
    import zuno.knowledge.ingestion.production_runtime as production_runtime

    calls: list[dict] = []

    class _Inbox:
        processable = False

    class _Repo:
        def record_worker_inbox(self, **kwargs):
            calls.append(kwargs)
            return _Inbox()

        def load_parse_job_replay_receipt(self, *, parse_job_id: str, tenant_id: str):
            return {
                "job_status": "succeeded",
                "parse_attempt_id": "attempt-1",
                "indexable_snapshot_id": "indexable-1",
                "outbox_event_id": "outbox-1",
                "dead_letter_id": None,
            }

    class _UnitOfWork:
        def __init__(self, engine):
            self.repo = _Repo()

        def __enter__(self):
            return self.repo

        def __exit__(self, exc_type, exc, tb):
            return None

    monkeypatch.setattr(production_runtime, "IngestionUnitOfWork", _UnitOfWork)
    runtime = _runtime_without_init()
    runtime.engine = object()
    runtime.worker_id = "worker-from-config"
    delivery = _delivery_for_envelope(_envelope(payload={"parse_job_id": "job-1"}))

    receipt = asyncio.run(runtime.process_rabbitmq_delivery(delivery))

    assert receipt.duplicate_delivery is True
    assert delivery.acked is True
    assert calls[0]["consumer"] == "worker-from-config"


def _runtime_without_init() -> PackageAProductionIngestionRuntime:
    return object.__new__(PackageAProductionIngestionRuntime)


def _envelope(
    *,
    payload: dict,
    contract_name: str = PACKAGE_A_PARSE_CONTRACT_NAME,
    consumer_module: str = PACKAGE_A_PARSE_CONSUMER_MODULE,
) -> CrossModuleEnvelopeV1:
    now = datetime(2026, 7, 20, tzinfo=timezone.utc)
    return CrossModuleEnvelopeV1(
        contract_name=contract_name,
        contract_version="v1",
        contract_bundle_version="phase11-package-a",
        message_id="event-1",
        producer_module="workspace.file_upload",
        consumer_module=consumer_module,
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


def _delivery_for_envelope(envelope: CrossModuleEnvelopeV1) -> _RecordingDelivery:
    delivery = _RecordingDelivery()
    delivery.headers = {"tenant_id": envelope.tenant_id}
    delivery.payload = {
        "aggregate_id": envelope.aggregate_id,
        "event_id": envelope.message_id,
        "idempotency_key": envelope.idempotency_key,
        "payload": envelope.model_dump(mode="json"),
        "payload_hash": canonical_sha256(envelope.model_dump(mode="json")),
        "topic": PACKAGE_A_PARSE_REQUESTED_TOPIC,
    }
    return delivery


def _assert_rejected_parse_delivery(delivery: _RecordingDelivery, match: str) -> None:
    with pytest.raises(IngestionPersistenceError, match=match):
        asyncio.run(
            PackageAProductionIngestionRuntime.process_rabbitmq_delivery(
                _runtime_without_init(),
                delivery,
            )
        )

    assert delivery.acked is False
    assert delivery.rejected is True
    assert delivery.requeue is False


def _lineage_payload() -> dict:
    return {
        "tenant_id": "tenant-a",
        "workspace_id": "workspace-a",
        "source_object_id": "source-a",
        "document_version_id": "document-version-a",
        "parse_plan_id": "parse-plan-a",
        "parse_job_id": "parse-job-a",
        "object_ref": "s3://bucket/tenant-a/workspace-a/source/source-a/file.md",
        "object_manifest_ref": "manifest-a",
        "content_hash": "a" * 64,
        "size_bytes": 12,
        "mime_type": "text/markdown",
        "security_epoch_ref": "security-epoch-a",
    }


def _lineage_context() -> dict:
    return {
        "tenant_id": "tenant-a",
        "workspace_id": "workspace-a",
        "source_object_id": "source-a",
        "document_version_id": "document-version-a",
        "parse_plan_id": "parse-plan-a",
        "parse_job_id": "parse-job-a",
        "storage_uri": "s3://bucket/tenant-a/workspace-a/source/source-a/file.md",
        "object_manifest_ref": "manifest-a",
        "source_sha256": "a" * 64,
        "size_bytes": 12,
        "mime_type": "text/markdown",
        "security_epoch_ref": "security-epoch-a",
    }
