from datetime import datetime, timezone

import pytest

from zuno.knowledge.ingestion import PackageAProductionIngestionRuntime, PackageARejectDeliveryError
from zuno.platform.contracts import CrossModuleEnvelopeV1, canonical_sha256


def _runtime(*, max_attempts: int) -> PackageAProductionIngestionRuntime:
    runtime = object.__new__(PackageAProductionIngestionRuntime)
    runtime.max_attempts = max_attempts
    return runtime


def test_retryable_failure_retries_until_max_attempts_including_first_attempt() -> None:
    runtime = _runtime(max_attempts=2)

    assert runtime._failure_terminal_status(
        retryable=True,
        prior_attempt_count=0,
    ) == "failed"
    assert runtime._failure_terminal_status(
        retryable=True,
        prior_attempt_count=1,
    ) == "dead_letter"


def test_non_retryable_failure_dead_letters_on_first_attempt() -> None:
    runtime = _runtime(max_attempts=3)

    assert runtime._failure_terminal_status(
        retryable=False,
        prior_attempt_count=0,
    ) == "dead_letter"


def test_retry_boundary_rejects_negative_prior_attempt_count() -> None:
    runtime = _runtime(max_attempts=2)

    with pytest.raises(ValueError, match="prior_attempt_count"):
        runtime._failure_terminal_status(
            retryable=True,
            prior_attempt_count=-1,
        )


def test_retry_envelope_records_parent_attempt_and_rehashes_payload() -> None:
    runtime = _runtime(max_attempts=3)
    envelope = _parse_requested_envelope()

    retry = runtime._retry_parse_requested_envelope(
        envelope=envelope,
        context={"parse_job_id": "parse-job-a"},
        retry_parent_attempt_id="parse-job-a:attempt:1",
        next_attempt_no=2,
    )

    assert retry.message_id == "outbox:parse-job-a:retry:2"
    assert retry.causation_id == "outbox:parse-job-a"
    assert retry.idempotency_key == "parse:tenant-a:workspace-a:hash:1:retry:2"
    assert retry.payload["retry_attempt_no"] == 2
    assert retry.payload["retry_parent_attempt_id"] == "parse-job-a:attempt:1"
    assert retry.payload["retry_parent_message_id"] == "outbox:parse-job-a"
    assert retry.payload["retry_parent_idempotency_key"] == "parse:tenant-a:workspace-a:hash:1"
    assert retry.payload_hash == canonical_sha256(retry.payload)


def test_retry_delivery_envelope_must_match_retry_payload_identity() -> None:
    runtime = _runtime(max_attempts=3)
    retry = runtime._retry_parse_requested_envelope(
        envelope=_parse_requested_envelope(),
        context={"parse_job_id": "parse-job-a"},
        retry_parent_attempt_id="parse-job-a:attempt:1",
        next_attempt_no=2,
    )

    PackageAProductionIngestionRuntime._validate_delivery_retry_envelope(
        payload=retry.payload,
        envelope=retry,
    )

    forged = retry.model_copy(update={"causation_id": "outbox:parse-job-other"})
    with pytest.raises(PackageARejectDeliveryError, match="causation_id"):
        PackageAProductionIngestionRuntime._validate_delivery_retry_envelope(
            payload=retry.payload,
            envelope=forged,
        )


def test_retry_delivery_envelope_rejects_first_attempt_number() -> None:
    retry = _parse_requested_envelope().model_copy(
        update={
            "message_id": "outbox:parse-job-a:retry:1",
            "causation_id": "outbox:parse-job-a",
            "idempotency_key": "parse:tenant-a:workspace-a:hash:1:retry:1",
        }
    )
    payload = {
        **retry.payload,
        "retry_attempt_no": 1,
        "retry_parent_attempt_id": "parse-job-a:attempt:0",
        "retry_parent_message_id": "outbox:parse-job-a",
        "retry_parent_idempotency_key": "parse:tenant-a:workspace-a:hash:1",
    }

    with pytest.raises(PackageARejectDeliveryError, match="retry_attempt_no"):
        PackageAProductionIngestionRuntime._validate_delivery_retry_envelope(
            payload=payload,
            envelope=retry,
        )


def test_retry_policy_rejects_retry_attempt_beyond_max_attempts() -> None:
    payload = {
        "max_attempts": 2,
        "retry_attempt_no": 3,
    }

    with pytest.raises(PackageARejectDeliveryError, match="retry_attempt_no"):
        PackageAProductionIngestionRuntime._validate_delivery_retry_policy(
            payload=payload,
            max_attempts=2,
        )


def _parse_requested_envelope() -> CrossModuleEnvelopeV1:
    now = datetime(2026, 7, 20, tzinfo=timezone.utc)
    payload = {
        "parse_job_id": "parse-job-a",
        "source_object_id": "source-a",
        "security_epoch_ref": "security-epoch-a",
    }
    return CrossModuleEnvelopeV1(
        contract_name="zuno.ingestion.parse.requested",
        contract_version="v1",
        contract_bundle_version="phase11-package-a",
        message_id="outbox:parse-job-a",
        producer_module="workspace.file_upload",
        consumer_module="ingestion.parser_worker",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        correlation_id="trace-a",
        idempotency_key="parse:tenant-a:workspace-a:hash:1",
        aggregate_type="ParseJob",
        aggregate_id="parse-job-a",
        trace_id="trace-a",
        data_classification="internal",
        occurred_at=now,
        created_at=now,
        payload=payload,
        payload_hash=canonical_sha256(payload),
        payload_schema_hash=canonical_sha256({"schema": "zuno.ingestion.parse.requested.v1"}),
    )
