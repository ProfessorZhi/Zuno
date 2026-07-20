import pytest

from zuno.platform.database.ingestion.persistence import (
    IngestionPersistenceError,
    IngestionRepository,
)


class _Result:
    rowcount = 1


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
