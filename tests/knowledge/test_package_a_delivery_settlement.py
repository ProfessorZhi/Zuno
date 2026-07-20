import asyncio
from datetime import datetime, timezone
import hashlib
from types import SimpleNamespace

import pytest

from zuno.knowledge.ingestion import (
    PACKAGE_A_PARSE_CONSUMER_MODULE,
    PACKAGE_A_PARSE_CONTRACT_NAME,
    PACKAGE_A_PARSE_INITIAL_PRODUCER_MODULE,
    PACKAGE_A_PARSE_REQUESTED_TOPIC,
    PACKAGE_A_PARSE_RETRY_PRODUCER_MODULE,
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


def test_package_a_rejects_initial_delivery_from_worker_producer_without_requeue() -> None:
    delivery = _delivery_for_envelope(
        _envelope(
            payload={"parse_job_id": "job-1"},
            producer_module=PACKAGE_A_PARSE_RETRY_PRODUCER_MODULE,
        )
    )

    _assert_rejected_parse_delivery(delivery, "delivery producer lineage mismatch")


def test_package_a_rejects_retry_delivery_from_upload_producer_without_requeue() -> None:
    delivery = _delivery_for_envelope(
        _envelope(
            payload={
                "parse_job_id": "job-1",
                "retry_attempt_no": 2,
                "retry_parent_attempt_id": "job-1:attempt:1",
                "retry_parent_message_id": "event-1",
                "retry_parent_idempotency_key": "idem-1",
            },
            message_id="outbox:job-1:retry:2",
            causation_id="event-1",
            idempotency_key="idem-1:retry:2",
            producer_module=PACKAGE_A_PARSE_INITIAL_PRODUCER_MODULE,
        )
    )
    delivery.headers["outbox_retry_count"] = 1

    _assert_rejected_parse_delivery(delivery, "delivery producer lineage mismatch")


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


def test_package_a_rejects_parse_job_identity_mismatch_without_requeue() -> None:
    delivery = _delivery_for_envelope(_envelope(payload={"parse_job_id": "job-other"}))

    _assert_rejected_parse_delivery(delivery, "delivery parse job identity mismatch")


def test_package_a_rejects_payload_tenant_mismatch_without_requeue() -> None:
    delivery = _delivery_for_envelope(
        _envelope(
            payload={
                "tenant_id": "tenant-b",
                "parse_job_id": "job-1",
            }
        )
    )

    _assert_rejected_parse_delivery(delivery, "delivery tenant header does not match envelope")


def test_package_a_rejects_workspace_header_mismatch_without_requeue() -> None:
    delivery = _delivery_for_envelope(_envelope(payload={"parse_job_id": "job-1"}))
    delivery.headers["workspace_id"] = "workspace-b"

    _assert_rejected_parse_delivery(delivery, "delivery workspace header does not match envelope")


def test_package_a_rejects_trace_header_mismatch_without_requeue() -> None:
    delivery = _delivery_for_envelope(_envelope(payload={"parse_job_id": "job-1"}))
    delivery.headers["trace_id"] = "trace-other"

    _assert_rejected_parse_delivery(delivery, "delivery trace header does not match envelope")


def test_package_a_rejects_data_classification_header_mismatch_without_requeue() -> None:
    delivery = _delivery_for_envelope(_envelope(payload={"parse_job_id": "job-1"}))
    delivery.headers["data_classification"] = "restricted"

    _assert_rejected_parse_delivery(
        delivery,
        "delivery data classification header does not match envelope",
    )


def test_package_a_rejects_message_version_header_mismatch_without_requeue() -> None:
    delivery = _delivery_for_envelope(_envelope(payload={"parse_job_id": "job-1"}))
    delivery.headers["message_version"] = "v2"

    _assert_rejected_parse_delivery(
        delivery,
        "delivery message version header does not match envelope",
    )


def test_package_a_rejects_outbox_ordering_header_mismatch_without_requeue() -> None:
    delivery = _delivery_for_envelope(_envelope(payload={"parse_job_id": "job-1"}))
    delivery.headers["ordering_key"] = "parse-job-other"

    _assert_rejected_parse_delivery(delivery, "delivery outbox header mismatch: ordering_key")


def test_package_a_rejects_dlq_replay_without_replay_counter_without_requeue() -> None:
    delivery = _delivery_for_envelope(_envelope(payload={"parse_job_id": "job-1"}))
    delivery.headers["replayed_from_dlq"] = True

    _assert_rejected_parse_delivery(delivery, "delivery outbox header mismatch: replay_count")


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


def test_package_a_lineage_validator_rejects_filename_mismatch_before_lease() -> None:
    payload = {**_lineage_payload(), "filename": "forged.md"}

    with pytest.raises(PackageARejectDeliveryError, match="delivery lineage mismatch: filename"):
        PackageAProductionIngestionRuntime._validate_delivery_lineage(
            payload=payload,
            context=_lineage_context(),
        )


def test_package_a_lineage_validator_rejects_declared_format_mismatch_before_lease() -> None:
    payload = {**_lineage_payload(), "declared_format": "pdf"}

    with pytest.raises(PackageARejectDeliveryError, match="delivery lineage mismatch: declared_format"):
        PackageAProductionIngestionRuntime._validate_delivery_lineage(
            payload=payload,
            context=_lineage_context(),
        )


def test_package_a_lineage_validator_rejects_parser_policy_mismatch_before_lease() -> None:
    payload = {**_lineage_payload(), "parser_policy_ref": "parser-policy-forged"}

    with pytest.raises(PackageARejectDeliveryError, match="delivery lineage mismatch: parser_policy_ref"):
        PackageAProductionIngestionRuntime._validate_delivery_lineage(
            payload=payload,
            context=_lineage_context(),
        )


def test_package_a_lineage_validator_rejects_classification_mismatch_before_lease() -> None:
    payload = {**_lineage_payload(), "classification_ref": "restricted"}

    with pytest.raises(PackageARejectDeliveryError, match="delivery lineage mismatch: classification_ref"):
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
        status = "received"
        processable = False

    class _Repo:
        def record_worker_inbox(self, **kwargs):
            calls.append(kwargs)
            return _Inbox()

        def load_parse_job_replay_receipt(self, *, parse_job_id: str, tenant_id: str):
            return {
                "parse_job_id": parse_job_id,
                "tenant_id": tenant_id,
                "job_status": "succeeded",
                "attempt_status": "succeeded",
                "parse_attempt_id": "attempt-1",
                "indexable_snapshot_id": "indexable-1",
                "outbox_event_id": "outbox-1",
                "handoff_idempotency_key": "handoff-idem-1",
                "outbox_idempotency_key": "handoff-idem-1",
                "dead_letter_id": None,
            }

        def load_snapshot_handoff_replay_receipt(
            self,
            *,
            tenant_id: str,
            handoff_idempotency_key: str,
        ):
            return {
                "indexable_snapshot_id": "indexable-1",
                "outbox_event_id": "outbox-1",
                "handoff_idempotency_key": handoff_idempotency_key,
                "snapshot_hash": "snapshot-hash-1",
                "handoff_envelope_hash": "handoff-hash-1",
                "visibility_ref": "visibility-1",
                "quality_decision_id": "quality-1",
                "knowledge_handoff_status": "pending",
                "outbox_publish_status": "pending",
                "outbox_payload_hash": "outbox-payload-hash-1",
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
    assert calls[0]["ordering_key"] == "job-1"
    assert calls[0]["ordering_sequence"] == 1


def test_package_a_duplicate_success_replay_refuses_handoff_receipt_mismatch_without_ack(
    monkeypatch,
) -> None:
    import zuno.knowledge.ingestion.production_runtime as production_runtime

    class _Inbox:
        status = "received"
        processable = False

    class _Repo:
        def record_worker_inbox(self, **_kwargs):
            return _Inbox()

        def load_parse_job_replay_receipt(self, *, parse_job_id: str, tenant_id: str):
            return {
                "parse_job_id": parse_job_id,
                "tenant_id": tenant_id,
                "job_status": "succeeded",
                "attempt_status": "succeeded",
                "parse_attempt_id": "attempt-1",
                "indexable_snapshot_id": "indexable-1",
                "outbox_event_id": "outbox-1",
                "handoff_idempotency_key": "handoff-idem-1",
                "outbox_idempotency_key": "handoff-idem-1",
                "dead_letter_id": None,
            }

        def load_snapshot_handoff_replay_receipt(
            self,
            *,
            tenant_id: str,
            handoff_idempotency_key: str,
        ):
            return {
                "indexable_snapshot_id": "indexable-1",
                "outbox_event_id": "outbox-forged",
                "handoff_idempotency_key": handoff_idempotency_key,
                "snapshot_hash": "snapshot-hash-1",
                "handoff_envelope_hash": "handoff-hash-1",
                "visibility_ref": "visibility-1",
                "quality_decision_id": "quality-1",
                "knowledge_handoff_status": "pending",
                "outbox_publish_status": "pending",
                "outbox_payload_hash": "outbox-payload-hash-1",
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

    with pytest.raises(IngestionPersistenceError, match="snapshot handoff replay mismatch"):
        asyncio.run(runtime.process_rabbitmq_delivery(delivery))

    assert delivery.acked is False
    assert delivery.rejected is False


def test_package_a_duplicate_success_replay_refuses_incomplete_handoff_outbox_without_ack(
    monkeypatch,
) -> None:
    import zuno.knowledge.ingestion.production_runtime as production_runtime

    class _Inbox:
        status = "received"
        processable = False

    class _Repo:
        def record_worker_inbox(self, **_kwargs):
            return _Inbox()

        def load_parse_job_replay_receipt(self, *, parse_job_id: str, tenant_id: str):
            return {
                "parse_job_id": parse_job_id,
                "tenant_id": tenant_id,
                "job_status": "succeeded",
                "attempt_status": "succeeded",
                "parse_attempt_id": "attempt-1",
                "indexable_snapshot_id": "indexable-1",
                "outbox_event_id": "outbox-1",
                "handoff_idempotency_key": "handoff-idem-1",
                "outbox_idempotency_key": "handoff-idem-1",
                "dead_letter_id": None,
            }

        def load_snapshot_handoff_replay_receipt(
            self,
            *,
            tenant_id: str,
            handoff_idempotency_key: str,
        ):
            return {
                "indexable_snapshot_id": "indexable-1",
                "outbox_event_id": "outbox-1",
                "handoff_idempotency_key": handoff_idempotency_key,
                "snapshot_hash": "snapshot-hash-1",
                "handoff_envelope_hash": "handoff-hash-1",
                "visibility_ref": "visibility-1",
                "quality_decision_id": "quality-1",
                "knowledge_handoff_status": "pending",
                "outbox_publish_status": "pending",
                "outbox_payload_hash": None,
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

    with pytest.raises(IngestionPersistenceError, match="outbox_payload_hash"):
        asyncio.run(runtime.process_rabbitmq_delivery(delivery))

    assert delivery.acked is False
    assert delivery.rejected is False


def test_package_a_duplicate_delivery_rejects_mismatched_replay_receipt_without_ack(monkeypatch) -> None:
    import zuno.knowledge.ingestion.production_runtime as production_runtime

    class _Inbox:
        status = "received"
        processable = False

    class _Repo:
        def record_worker_inbox(self, **_kwargs):
            return _Inbox()

        def load_parse_job_replay_receipt(self, *, parse_job_id: str, tenant_id: str):
            return {
                "parse_job_id": f"{parse_job_id}:forged",
                "tenant_id": tenant_id,
                "job_status": "succeeded",
                "attempt_status": "succeeded",
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

    with pytest.raises(IngestionPersistenceError, match="replay receipt mismatch: parse_job_id"):
        asyncio.run(runtime.process_rabbitmq_delivery(delivery))

    assert delivery.acked is False
    assert delivery.rejected is False


def test_package_a_duplicate_delivery_refuses_incomplete_success_replay_without_ack(monkeypatch) -> None:
    import zuno.knowledge.ingestion.production_runtime as production_runtime

    class _Inbox:
        status = "received"
        processable = False

    class _Repo:
        def record_worker_inbox(self, **_kwargs):
            return _Inbox()

        def load_parse_job_replay_receipt(self, *, parse_job_id: str, tenant_id: str):
            return {
                "parse_job_id": parse_job_id,
                "tenant_id": tenant_id,
                "job_status": "succeeded",
                "attempt_status": "succeeded",
                "parse_attempt_id": "attempt-1",
                "indexable_snapshot_id": None,
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

    with pytest.raises(IngestionPersistenceError, match="replay receipt incomplete for succeeded"):
        asyncio.run(runtime.process_rabbitmq_delivery(delivery))

    assert delivery.acked is False
    assert delivery.rejected is False


def test_package_a_duplicate_delivery_refuses_attempt_status_mismatch_without_ack(monkeypatch) -> None:
    import zuno.knowledge.ingestion.production_runtime as production_runtime

    class _Inbox:
        status = "received"
        processable = False

    class _Repo:
        def record_worker_inbox(self, **_kwargs):
            return _Inbox()

        def load_parse_job_replay_receipt(self, *, parse_job_id: str, tenant_id: str):
            return {
                "parse_job_id": parse_job_id,
                "tenant_id": tenant_id,
                "job_status": "succeeded",
                "attempt_status": "running",
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

    with pytest.raises(IngestionPersistenceError, match="attempt_status"):
        asyncio.run(runtime.process_rabbitmq_delivery(delivery))

    assert delivery.acked is False
    assert delivery.rejected is False


def test_package_a_duplicate_delivery_refuses_failed_replay_without_retry_outbox(monkeypatch) -> None:
    import zuno.knowledge.ingestion.production_runtime as production_runtime

    class _Inbox:
        status = "received"
        processable = False

    class _Repo:
        def record_worker_inbox(self, **_kwargs):
            return _Inbox()

        def load_parse_job_replay_receipt(self, *, parse_job_id: str, tenant_id: str):
            return {
                "parse_job_id": parse_job_id,
                "tenant_id": tenant_id,
                "job_status": "failed",
                "attempt_status": "failed",
                "parse_attempt_id": "attempt-1",
                "failure_code": "temporary_parser_failure",
                "retry_outbox_event_id": None,
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

    with pytest.raises(IngestionPersistenceError, match="retry_outbox_event_id"):
        asyncio.run(runtime.process_rabbitmq_delivery(delivery))

    assert delivery.acked is False
    assert delivery.rejected is False


def test_package_a_duplicate_delivery_refuses_cancelled_replay_with_publish_artifact_without_ack(
    monkeypatch,
) -> None:
    import zuno.knowledge.ingestion.production_runtime as production_runtime

    class _Inbox:
        status = "received"
        processable = False

    class _Repo:
        def record_worker_inbox(self, **_kwargs):
            return _Inbox()

        def load_parse_job_replay_receipt(self, *, parse_job_id: str, tenant_id: str):
            return {
                "parse_job_id": parse_job_id,
                "tenant_id": tenant_id,
                "job_status": "cancelled",
                "attempt_status": "cancelled",
                "parse_attempt_id": "attempt-1",
                "failure_code": "deadline_expired",
                "indexable_snapshot_id": "indexable-forged",
                "outbox_event_id": None,
                "handoff_idempotency_key": None,
                "outbox_idempotency_key": None,
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

    with pytest.raises(IngestionPersistenceError, match="replay receipt conflict for cancelled"):
        asyncio.run(runtime.process_rabbitmq_delivery(delivery))

    assert delivery.acked is False
    assert delivery.rejected is False


def test_package_a_buffered_inbox_delivery_is_not_acked_or_replayed(monkeypatch) -> None:
    import zuno.knowledge.ingestion.production_runtime as production_runtime

    events: list[str] = []

    class _Inbox:
        status = "buffered"
        processable = False

    class _Repo:
        def record_worker_inbox(self, **_kwargs):
            events.append("record_inbox")
            return _Inbox()

        def load_parse_job_replay_receipt(self, *, parse_job_id: str, tenant_id: str):
            raise AssertionError("buffered Inbox deliveries must not load replay receipts")

    class _UnitOfWork:
        def __init__(self, engine):
            self.repo = _Repo()

        def __enter__(self):
            return self.repo

        def __exit__(self, exc_type, exc, tb):
            events.append(f"exit:{exc_type.__name__ if exc_type else 'none'}")
            return None

    monkeypatch.setattr(production_runtime, "IngestionUnitOfWork", _UnitOfWork)
    runtime = _runtime_without_init()
    runtime.engine = object()
    runtime.worker_id = "worker-from-config"
    delivery = _delivery_for_envelope(_envelope(payload={"parse_job_id": "job-1"}))

    with pytest.raises(IngestionPersistenceError, match="inbox delivery is not processable: buffered"):
        asyncio.run(runtime.process_rabbitmq_delivery(delivery))

    assert delivery.acked is False
    assert delivery.rejected is False
    assert events == ["record_inbox", "exit:none"]


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


def test_package_a_expired_deadline_receipt_carries_failure_code_without_parser_or_snapshot(monkeypatch) -> None:
    events: list[str] = []
    repo = _FirstSeenRepo(events)
    runtime = _runtime_without_init()
    runtime.worker_id = "worker-a"
    runtime.lease_ttl_seconds = 30
    runtime.review_runtime = HumanReviewRuntime(min_confidence=0.1)
    runtime.handoff_runtime = SnapshotHandoffRuntime()

    def read_object(context):
        raise AssertionError("expired deadline delivery must not read object bytes")

    monkeypatch.setattr(runtime, "_read_and_verify_object", read_object)
    payload = _lineage_payload()
    envelope = _envelope(payload=payload, deadline_at=datetime(2000, 1, 1, tzinfo=timezone.utc))

    receipt = runtime._process_first_seen_delivery(
        repo=repo,
        payload=payload,
        envelope=envelope,
        parse_job_id="parse-job-a",
        tenant_id="tenant-a",
    )

    assert receipt.status == "cancelled"
    assert receipt.acked_after_domain_commit is True
    assert receipt.failure_code == "deadline_expired"
    assert events == [
        "load_context",
        "claim",
        "running",
        "fail:cancelled:deadline_expired",
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
    producer_module: str = PACKAGE_A_PARSE_INITIAL_PRODUCER_MODULE,
    message_id: str = "event-1",
    causation_id: str | None = None,
    idempotency_key: str = "idem-1",
    deadline_at: datetime | None = None,
) -> CrossModuleEnvelopeV1:
    now = datetime(2026, 7, 20, tzinfo=timezone.utc)
    payload = {
        "tenant_id": "tenant-a",
        "workspace_id": "workspace-a",
        "security_epoch_ref": "security-epoch-a",
        "max_attempts": 2,
        **payload,
    }
    return CrossModuleEnvelopeV1(
        contract_name=contract_name,
        contract_version="v1",
        contract_bundle_version="phase11-package-a",
        message_id=message_id,
        producer_module=producer_module,
        consumer_module=consumer_module,
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        causation_id=causation_id,
        correlation_id="trace-1",
        idempotency_key=idempotency_key,
        aggregate_type="ParseJob",
        aggregate_id="job-1",
        trace_id="trace-1",
        data_classification="internal",
        effective_security_epoch_ref=str(payload.get("security_epoch_ref", "security-epoch-a")),
        occurred_at=now,
        created_at=now,
        deadline_at=deadline_at,
        payload=payload,
        payload_hash=canonical_sha256(payload),
        payload_schema_hash=canonical_sha256({"schema": "zuno.ingestion.parse.requested.v1"}),
    )


def _delivery_for_envelope(envelope: CrossModuleEnvelopeV1) -> _RecordingDelivery:
    delivery = _RecordingDelivery()
    delivery.message_id = envelope.message_id
    delivery.headers = {
        "tenant_id": envelope.tenant_id,
        "workspace_id": envelope.workspace_id,
        "trace_id": envelope.trace_id,
        "data_classification": envelope.data_classification,
        "message_version": envelope.contract_version,
        "security_epoch_ref": envelope.effective_security_epoch_ref,
        "ordering_key": envelope.aggregate_id,
        "ordering_sequence": 1,
        "outbox_publish_attempt": 1,
        "outbox_retry_count": 0,
        "outbox_replay_count": 0,
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
        "filename": "file.md",
        "mime_type": "text/markdown",
        "declared_format": "markdown",
        "classification_ref": "internal",
        "parser_policy_ref": "parser-policy-a",
        "quality_policy_ref": "quality-policy-a",
        "security_decision_ref": "security-decision-a",
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
        "filename": "file.md",
        "mime_type": "text/markdown",
        "declared_format": "markdown",
        "classification_ref": "internal",
        "parser_policy_ref": "parser-policy-a",
        "quality_policy_ref": "quality-policy-a",
        "security_decision_ref": "security-decision-a",
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
            "parser_policy_ref": "parser-policy-a",
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
