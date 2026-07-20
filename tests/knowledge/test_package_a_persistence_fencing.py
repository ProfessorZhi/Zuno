import pytest

from zuno.platform.database.ingestion.persistence import (
    IngestionPersistenceError,
    IngestionRepository,
)


class _Result:
    rowcount = 1

    def mappings(self):
        return self

    def first(self):
        return {
            "indexable_snapshot_id": "snapshot-a",
            "handoff_idempotency_key": "handoff-idem-a",
            "outbox_event_id": "outbox-a",
        }


class _Connection:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def execute(self, statement, params):
        self.calls.append({"statement": str(statement), "params": params})
        return _Result()


def test_parse_attempt_running_requires_lease_claimed_state() -> None:
    connection = _Connection()
    repo = IngestionRepository(connection)

    repo.mark_parse_attempt_running(
        parse_attempt_id="parse-job-a:attempt:1",
        parse_job_id="parse-job-a",
        tenant_id="tenant-a",
        worker_id="worker-a",
        fencing_token=1,
    )

    assert connection.calls[0]["params"]["expected_statuses"] == ("lease_claimed",)


def test_parse_attempt_commit_requires_running_state() -> None:
    connection = _Connection()
    repo = IngestionRepository(connection)

    repo.commit_parse_attempt_if_current(
        parse_attempt_id="parse-job-a:attempt:1",
        parse_job_id="parse-job-a",
        tenant_id="tenant-a",
        worker_id="worker-a",
        fencing_token=1,
        domain_commit_ref="domain-commit-a",
    )

    assert connection.calls[0]["params"]["expected_statuses"] == ("running",)


def test_parse_attempt_failure_requires_running_state() -> None:
    connection = _Connection()
    repo = IngestionRepository(connection)

    repo.fail_parse_attempt(
        parse_attempt_id="parse-job-a:attempt:1",
        parse_job_id="parse-job-a",
        tenant_id="tenant-a",
        worker_id="worker-a",
        fencing_token=1,
        status="dead_letter",
        failure_code="object_hash_mismatch",
    )

    assert connection.calls[0]["params"]["expected_statuses"] == ("running",)


def test_parse_attempt_heartbeat_requires_running_state_without_extending_lease() -> None:
    connection = _Connection()
    repo = IngestionRepository(connection)

    receipt = repo.heartbeat_parse_attempt_lease(
        parse_attempt_id="parse-job-a:attempt:1",
        parse_job_id="parse-job-a",
        tenant_id="tenant-a",
        worker_id="worker-a",
        fencing_token=1,
    )

    lease_update = connection.calls[0]
    attempt_update = connection.calls[1]
    assert receipt.status == "lease_heartbeat"
    assert "SET heartbeat_at = now()" in lease_update["statement"]
    assert "lease_expires_at =" not in lease_update["statement"]
    assert lease_update["params"] == {
        "parse_attempt_id": "parse-job-a:attempt:1",
        "parse_job_id": "parse-job-a",
        "tenant_id": "tenant-a",
        "worker_id": "worker-a",
        "fencing_token": 1,
    }
    assert attempt_update["params"]["expected_statuses"] == ("running",)
    assert attempt_update["params"]["lease_expires_at"] is None


def test_parse_attempt_update_rejects_empty_expected_state_set() -> None:
    repo = IngestionRepository(_Connection())

    with pytest.raises(IngestionPersistenceError, match="expected parse attempt status"):
        repo._update_attempt_if_current(
            parse_attempt_id="parse-job-a:attempt:1",
            parse_job_id="parse-job-a",
            tenant_id="tenant-a",
            worker_id="worker-a",
            fencing_token=1,
            status="running",
            expected_statuses=(),
        )


def test_indexable_snapshot_persists_handoff_idempotency_key() -> None:
    connection = _Connection()
    repo = IngestionRepository(connection)

    repo.record_indexable_snapshot(
        indexable_snapshot_id="snapshot-a",
        tenant_id="tenant-a",
        parse_snapshot_id="parse-snapshot-a",
        document_version_id="document-version-a",
        quality_decision_id="quality-a",
        visibility_ref="visibility-a",
        payload={"indexable_snapshot_id": "snapshot-a"},
        handoff_idempotency_key="handoff-idem-a",
    )

    assert connection.calls[0]["params"]["handoff_idempotency_key"] == "handoff-idem-a"


def test_snapshot_outbox_persists_idempotency_key() -> None:
    connection = _Connection()
    repo = IngestionRepository(connection)

    repo.enqueue_outbox_event(
        outbox_event_id="outbox-a",
        tenant_id="tenant-a",
        aggregate_ref="snapshot-a",
        event_type="ingestion.indexable_snapshot.ready",
        payload={"indexable_snapshot_id": "snapshot-a"},
        idempotency_key="handoff-idem-a",
    )

    assert connection.calls[0]["params"]["idempotency_key"] == "handoff-idem-a"


def test_parse_job_replay_receipt_selects_handoff_idempotency_fields() -> None:
    connection = _Connection()
    repo = IngestionRepository(connection)

    repo.load_parse_job_replay_receipt(parse_job_id="parse-job-a", tenant_id="tenant-a")

    statement = connection.calls[0]["statement"]
    assert "latest_attempt.failure_code" in statement
    assert "snapshot.parse_snapshot_id" in statement
    assert "snapshot.document_version_id" in statement
    assert "indexable.quality_decision_id" in statement
    assert "indexable.handoff_idempotency_key" in statement
    assert "outbox.idempotency_key AS outbox_idempotency_key" in statement


def test_snapshot_handoff_replay_receipt_loads_by_tenant_scoped_idempotency() -> None:
    connection = _Connection()
    repo = IngestionRepository(connection)

    receipt = repo.load_snapshot_handoff_replay_receipt(
        tenant_id="tenant-a",
        handoff_idempotency_key="handoff-idem-a",
    )

    assert receipt["indexable_snapshot_id"] == "snapshot-a"
    assert connection.calls[0]["params"] == {
        "tenant_id": "tenant-a",
        "handoff_idempotency_key": "handoff-idem-a",
    }
    statement = connection.calls[0]["statement"]
    assert "outbox.idempotency_key = indexable.handoff_idempotency_key" in statement


def test_workspace_upload_replay_receipt_joins_parse_job_to_source_and_outbox() -> None:
    connection = _Connection()
    repo = IngestionRepository(connection)

    repo.load_workspace_upload_replay_receipt(
        tenant_id="tenant-a",
        idempotency_key="parse:tenant-a:workspace-a:hash:1",
    )

    assert connection.calls[0]["params"] == {
        "tenant_id": "tenant-a",
        "idempotency_key": "parse:tenant-a:workspace-a:hash:1",
    }
    statement = connection.calls[0]["statement"]
    assert "FROM ingestion_parse_jobs AS job" in statement
    assert "JOIN ingestion_parse_plans AS plan" in statement
    assert "JOIN ingestion_document_versions AS document" in statement
    assert "JOIN ingestion_source_objects AS source" in statement
    assert "LEFT JOIN infra_outbox_events AS outbox" in statement
    assert "outbox.topic = 'ingestion.parse.requested'" in statement
