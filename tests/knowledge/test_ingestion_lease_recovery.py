from __future__ import annotations

from pathlib import Path
import tempfile

import pytest


def test_parse_attempt_lease_claim_renew_expire_and_reconcile_orphan() -> None:
    from zuno.knowledge.ingestion import ParseAttemptLeaseRuntime

    runtime = ParseAttemptLeaseRuntime()
    claimed = runtime.claim(
        parse_job_id="parse_job_lease_1",
        worker_id="worker_a",
        attempt_no=1,
        now=10.0,
        ttl_seconds=5.0,
    )
    renewed = runtime.renew(
        claimed,
        worker_id="worker_a",
        fencing_token=claimed.fencing_token,
        now=12.0,
        ttl_seconds=5.0,
    )
    still_live = runtime.expire(renewed, now=16.0)
    expired = runtime.expire(renewed, now=18.0)
    reconciled = runtime.reconcile_orphan(expired, now=18.0)

    assert claimed.state == "claimed"
    assert renewed.state == "renewed"
    assert renewed.lease_expires_at == 17.0
    assert still_live.state == "renewed"
    assert expired.state == "expired"
    assert reconciled.state == "reconciled"
    assert reconciled.orphan_reconciled is True
    assert reconciled.history[-1] == "orphan_reconciled"


def test_stale_worker_late_result_is_rejected_after_restart_claims_new_fencing_token() -> None:
    from zuno.knowledge.ingestion import ParseAttemptLeaseRuntime

    runtime = ParseAttemptLeaseRuntime()
    first = runtime.claim(
        parse_job_id="parse_job_restart",
        worker_id="worker_old",
        attempt_no=1,
        now=0.0,
        ttl_seconds=5.0,
    )
    expired = runtime.reconcile_orphan(first, now=6.0)
    restarted = runtime.claim(
        parse_job_id="parse_job_restart",
        worker_id="worker_new",
        attempt_no=2,
        now=7.0,
        ttl_seconds=5.0,
        previous=expired,
    )
    rejected = runtime.reject_late_result(
        restarted,
        worker_id=first.worker_id,
        fencing_token=first.fencing_token,
        parse_attempt_id=first.parse_attempt_id,
    )

    assert restarted.parse_attempt_id != first.parse_attempt_id
    assert restarted.fencing_token > first.fencing_token
    assert rejected.late_result_rejected is True
    assert rejected.state == "late_result_rejected"


def test_commit_requires_current_fencing_token_and_is_idempotent() -> None:
    from zuno.knowledge.ingestion import ParseAttemptLeaseRuntime

    runtime = ParseAttemptLeaseRuntime()
    lease = runtime.claim(
        parse_job_id="parse_job_commit",
        worker_id="worker_commit",
        attempt_no=1,
        now=1.0,
        ttl_seconds=30.0,
    )
    with pytest.raises(ValueError, match="stale parse attempt lease"):
        runtime.commit_if_current(
            lease,
            worker_id="worker_commit",
            fencing_token=lease.fencing_token - 1,
            idempotency_key="idem_parse_commit_1",
        )

    committed = runtime.commit_if_current(
        lease,
        worker_id="worker_commit",
        fencing_token=lease.fencing_token,
        idempotency_key="idem_parse_commit_1",
    )
    duplicate = runtime.commit_if_current(
        committed,
        worker_id="worker_commit",
        fencing_token=lease.fencing_token,
        idempotency_key="idem_parse_commit_1",
    )

    assert committed.state == "committed"
    assert committed.domain_commit_ref is not None
    assert duplicate.duplicate_commit is True
    assert duplicate.domain_commit_ref == committed.domain_commit_ref


def test_sqlite_store_round_trips_parse_attempt_lease_receipt() -> None:
    from zuno.knowledge.ingestion import ParseAttemptLeaseRuntime
    from zuno.knowledge.storage import ParseAttemptLeaseRecord, SQLiteDurableIngestionStore

    receipt = ParseAttemptLeaseRuntime().commit_if_current(
        ParseAttemptLeaseRuntime().claim(
            parse_job_id="parse_job_store",
            worker_id="worker_store",
            attempt_no=1,
            now=3.0,
            ttl_seconds=30.0,
        ),
        worker_id="worker_store",
        fencing_token=1,
        idempotency_key="idem_store",
    )
    store = SQLiteDurableIngestionStore(Path(tempfile.mkdtemp()) / "zuno.db")
    store.save_parse_attempt_lease(ParseAttemptLeaseRecord(**receipt.model_dump()))

    restored = store.get_parse_attempt_lease(receipt.parse_attempt_id)

    assert restored.state == "committed"
    assert restored.fencing_token == receipt.fencing_token
    assert restored.domain_commit_ref == receipt.domain_commit_ref
    assert restored.history[-1] == "domain_commit"
