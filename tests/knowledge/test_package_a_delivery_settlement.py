import asyncio
from datetime import datetime, timezone
import hashlib
from types import SimpleNamespace

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
from zuno.knowledge.ingestion.review import HumanReviewRuntime
from zuno.knowledge.ingestion.handoff import SnapshotHandoffRuntime
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


def test_package_a_settlement_refuses_ack_without_domain_commit_receipt() -> None:
    delivery = _RecordingDelivery()
    receipt = PackageAWorkerReceipt(
        parse_job_id="job-1",
        parse_attempt_id="attempt-1",
        status="failed",
        acked_after_domain_commit=False,
        failure_code="retryable_parser_failure",
    )

    with pytest.raises(IngestionPersistenceError, match="cannot ACK before domain commit"):
        asyncio.run(
            PackageAProductionIngestionRuntime._settle_delivery_after_domain_commit(
                delivery=delivery,
                worker_receipt=receipt,
            )
        )

    assert delivery.acked is False
    assert delivery.rejected is False
    assert delivery.requeue is None


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


def test_package_a_rejects_transport_message_id_mismatch_without_requeue() -> None:
    delivery = _delivery_for_envelope(_envelope(payload={"parse_job_id": "job-1"}))
    delivery.message_id = "transport-event-other"

    _assert_rejected_parse_delivery(delivery, "delivery message_id does not match envelope")


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


def test_package_a_rejects_security_epoch_header_mismatch_without_requeue() -> None:
    delivery = _delivery_for_envelope(
        _envelope(
            payload={
                "parse_job_id": "job-1",
                "security_epoch_ref": "security-epoch-a",
            }
        )
    )
    delivery.headers["security_epoch_ref"] = "security-epoch-b"

    _assert_rejected_parse_delivery(delivery, "delivery security epoch header does not match envelope")


def test_package_a_rejects_retry_policy_mismatch_without_requeue() -> None:
    delivery = _delivery_for_envelope(_envelope(payload={"parse_job_id": "job-1", "max_attempts": 3}))

    _assert_rejected_parse_delivery(delivery, "delivery retry policy mismatch: max_attempts")


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


def test_package_a_lineage_validator_requires_retry_parent_attempt_to_match_postgres() -> None:
    payload = {
        **_lineage_payload(),
        "retry_attempt_no": 2,
        "retry_parent_attempt_id": "parse-job-a:attempt:1",
        "retry_parent_message_id": "outbox:parse-job-a",
        "retry_parent_idempotency_key": "parse:tenant-a:workspace-a:hash:1",
    }
    context = {
        **_lineage_context(),
        "attempt_count": 1,
        "latest_attempt_id": "parse-job-a:attempt:1",
        "latest_attempt_status": "failed",
    }

    PackageAProductionIngestionRuntime._validate_delivery_lineage(payload=payload, context=context)

    forged_payload = {**payload, "retry_parent_attempt_id": "parse-job-a:attempt:stale"}
    with pytest.raises(PackageARejectDeliveryError, match="retry_parent_attempt_id"):
        PackageAProductionIngestionRuntime._validate_delivery_lineage(
            payload=forged_payload,
            context=context,
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
                "handoff_idempotency_key": "handoff-idem-1",
                "outbox_idempotency_key": "handoff-idem-1",
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
    assert receipt.handoff_idempotency_key == "handoff-idem-1"
    assert receipt.outbox_idempotency_key == "handoff-idem-1"
    assert calls[0]["consumer"] == "worker-from-config"


def test_package_a_first_seen_worker_records_heartbeats_before_and_after_parser_gateway(monkeypatch) -> None:
    events: list[str] = []
    repo = _FirstSeenRepo(events)
    runtime = _runtime_without_init()
    runtime.worker_id = "worker-a"
    runtime.lease_ttl_seconds = 30
    runtime.review_runtime = HumanReviewRuntime(min_confidence=0.1)
    runtime.handoff_runtime = SnapshotHandoffRuntime()
    source_bytes = b"# Title\n\nPackage A heartbeat evidence.\n"
    source_hash = hashlib.sha256(source_bytes).hexdigest()

    def read_object(context):
        events.append("read_object")
        return source_bytes

    monkeypatch.setattr(
        runtime,
        "_read_and_verify_object",
        read_object,
    )
    payload = {
        **_lineage_payload(),
        "content_hash": source_hash,
        "size_bytes": len(source_bytes),
        "parser_policy_ref": "parser-policy-a",
        "security_decision_ref": "security-decision-a",
    }
    repo.source_hash = source_hash
    repo.source_size = len(source_bytes)
    envelope = _envelope(payload=payload)

    receipt = runtime._process_first_seen_delivery(
        repo=repo,
        payload=payload,
        envelope=envelope,
        parse_job_id="parse-job-a",
        tenant_id="tenant-a",
    )

    assert receipt.status == "succeeded"
    assert events[:7] == [
        "load_context",
        "claim",
        "running",
        "renew",
        "read_object",
        "heartbeat",
        "heartbeat",
    ]
    assert events[7] == "snapshot"
    assert events.count("span") >= 1
    assert events[-4:] == [
        "quality",
        "indexable",
        "outbox",
        "commit",
    ]


def test_package_a_cancel_requested_receipt_carries_failure_code_without_parser_or_snapshot(monkeypatch) -> None:
    events: list[str] = []
    repo = _FirstSeenRepo(events)
    runtime = _runtime_without_init()
    runtime.worker_id = "worker-a"
    runtime.lease_ttl_seconds = 30
    runtime.review_runtime = HumanReviewRuntime(min_confidence=0.1)
    runtime.handoff_runtime = SnapshotHandoffRuntime()

    def read_object(context):
        raise AssertionError("cancelled delivery must not read object bytes")

    monkeypatch.setattr(runtime, "_read_and_verify_object", read_object)
    payload = {
        **_lineage_payload(),
        "cancel_requested": True,
    }
    envelope = _envelope(payload=payload)

    receipt = runtime._process_first_seen_delivery(
        repo=repo,
        payload=payload,
        envelope=envelope,
        parse_job_id="parse-job-a",
        tenant_id="tenant-a",
    )

    assert receipt.status == "cancelled"
    assert receipt.acked_after_domain_commit is True
    assert receipt.failure_code == "cancel_requested"
    assert events == [
        "load_context",
        "claim",
        "running",
        "fail:cancelled:cancel_requested",
    ]


def _runtime_without_init() -> PackageAProductionIngestionRuntime:
    runtime = object.__new__(PackageAProductionIngestionRuntime)
    runtime.max_attempts = 2
    return runtime


def _envelope(
    *,
    payload: dict,
    contract_name: str = PACKAGE_A_PARSE_CONTRACT_NAME,
    consumer_module: str = PACKAGE_A_PARSE_CONSUMER_MODULE,
) -> CrossModuleEnvelopeV1:
    now = datetime(2026, 7, 20, tzinfo=timezone.utc)
    payload = {
        "security_epoch_ref": "security-epoch-a",
        "max_attempts": 2,
        **payload,
    }
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
        effective_security_epoch_ref=str(payload.get("security_epoch_ref", "security-epoch-a")),
        occurred_at=now,
        created_at=now,
        payload=payload,
        payload_hash=canonical_sha256(payload),
        payload_schema_hash=canonical_sha256({"schema": "zuno.ingestion.parse.requested.v1"}),
    )


def _delivery_for_envelope(envelope: CrossModuleEnvelopeV1) -> _RecordingDelivery:
    delivery = _RecordingDelivery()
    delivery.headers = {
        "tenant_id": envelope.tenant_id,
        "security_epoch_ref": envelope.effective_security_epoch_ref,
    }
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
        "attempt_count": 0,
        "latest_attempt_id": None,
        "latest_attempt_status": None,
    }


class _FirstSeenRepo:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.source_hash = "a" * 64
        self.source_size = 12

    def load_parse_job_context(self, *, parse_job_id: str, tenant_id: str) -> dict:
        self.events.append("load_context")
        return {
            **_lineage_context(),
            "source_sha256": self.source_hash,
            "size_bytes": self.source_size,
            "filename": "file.md",
            "classification_ref": "internal",
            "source_status": "committed",
            "idempotency_key": "parse:tenant-a:workspace-a:source-a",
            "attempt_count": 0,
            "quality_policy_ref": "quality-policy-a",
            "security_decision_ref": "security-decision-a",
        }

    def claim_parse_attempt_lease(self, **kwargs):
        self.events.append("claim")
        return SimpleNamespace(ref="parse-job-a:attempt:1", payload_hash="1")

    def mark_parse_attempt_running(self, **kwargs):
        self.events.append("running")

    def renew_parse_attempt_lease(self, **kwargs):
        self.events.append("renew")

    def heartbeat_parse_attempt_lease(self, **kwargs):
        self.events.append("heartbeat")

    def record_parse_snapshot(self, **kwargs):
        self.events.append("snapshot")
        return SimpleNamespace(ref="parse-snapshot:parse-job-a:attempt:1")

    def record_source_span(self, **kwargs):
        self.events.append("span")
        return SimpleNamespace(ref=kwargs["source_span_id"])

    def record_quality_decision(self, **kwargs):
        self.events.append("quality")
        return SimpleNamespace(ref="quality:parse-job-a:attempt:1")

    def record_indexable_snapshot(self, **kwargs):
        self.events.append("indexable")
        return SimpleNamespace(ref=kwargs["indexable_snapshot_id"])

    def enqueue_outbox_event(self, **kwargs):
        self.events.append("outbox")
        return SimpleNamespace(ref=kwargs["outbox_event_id"])

    def commit_parse_attempt_if_current(self, **kwargs):
        self.events.append("commit")

    def fail_parse_attempt(self, **kwargs):
        self.events.append(f"fail:{kwargs['status']}:{kwargs['failure_code']}")
