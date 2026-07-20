from __future__ import annotations

import pytest


def _request(*, document_id: str, source_text: str, cancel_requested: bool = False):
    from zuno.knowledge.ingestion import ParseDocumentRequest

    return ParseDocumentRequest(
        document_id=document_id,
        workspace_id="workspace_parse_control",
        source_uri=f"file://docs/{document_id}.md",
        mime_type="text/markdown",
        source_text=source_text,
        cancel_requested=cancel_requested,
    )


def test_parse_control_runtime_schedules_leases_and_commits_successful_attempt() -> None:
    from zuno.knowledge.ingestion import ParseControlRuntime

    runtime = ParseControlRuntime(lease_ttl_seconds=30.0)
    request = _request(document_id="doc_control_success", source_text="# Success\nParse me.")
    planned = runtime.plan(request, idempotency_key="idem_control_success")
    queued = runtime.queue(planned)
    leased = runtime.lease(queued, worker_id="worker_control", now=10.0)
    completed, result = runtime.run_once(
        request,
        leased,
        worker_id="worker_control",
        fencing_token=leased.fencing_token or 0,
    )

    assert result.status == "succeeded"
    assert completed.state == "succeeded"
    assert completed.parse_job_id == result.job_id
    assert completed.snapshot is not None
    assert completed.snapshot.status == "succeeded"
    assert completed.lease is not None
    assert completed.lease.state == "committed"
    assert completed.lease.domain_commit_ref is not None
    assert completed.history == ["planned", "queued", "leased", "running", "succeeded"]


def test_parse_control_runtime_rejects_stale_worker_fencing_token() -> None:
    from zuno.knowledge.ingestion import ParseControlRuntime

    runtime = ParseControlRuntime()
    request = _request(document_id="doc_control_stale", source_text="# Stale\nNo run.")
    leased = runtime.lease(
        runtime.queue(runtime.plan(request, idempotency_key="idem_control_stale")),
        worker_id="worker_control",
        now=1.0,
    )

    with pytest.raises(ValueError, match="stale"):
        runtime.run_once(
            request,
            leased,
            worker_id="worker_control",
            fencing_token=(leased.fencing_token or 0) + 1,
        )


def test_parse_control_runtime_records_cancelled_terminal_state() -> None:
    from zuno.knowledge.ingestion import ParseControlRuntime

    runtime = ParseControlRuntime()
    request = _request(
        document_id="doc_control_cancel",
        source_text="# Cancel\nDo not run adapter.",
        cancel_requested=True,
    )
    leased = runtime.lease(
        runtime.queue(runtime.plan(request, idempotency_key="idem_control_cancel")),
        worker_id="worker_control",
        now=1.0,
    )
    completed, result = runtime.run_once(
        request,
        leased,
        worker_id="worker_control",
        fencing_token=leased.fencing_token or 0,
    )

    assert result.status == "cancelled"
    assert completed.state == "cancelled"
    assert completed.cancel_reason == "parse request cancelled before adapter execution"
    assert completed.snapshot is not None
    assert completed.snapshot.status == "cancelled"


def test_parse_control_runtime_retries_failed_job_until_dead_letter() -> None:
    from zuno.knowledge.ingestion import ParseControlRuntime

    runtime = ParseControlRuntime()
    request = _request(document_id="doc_control_dead_letter", source_text="")
    leased = runtime.lease(
        runtime.queue(runtime.plan(request, idempotency_key="idem_control_dead_letter")),
        worker_id="worker_control",
        now=1.0,
    )
    completed, result = runtime.run_to_dead_letter(
        request,
        leased,
        worker_id="worker_control",
        fencing_token=leased.fencing_token or 0,
    )

    assert result.status == "dead_letter"
    assert completed.state == "dead_letter"
    assert completed.retry_exhausted is True
    assert completed.snapshot is not None
    assert completed.snapshot.retryable is False
    assert "retrying" in completed.history
    assert completed.history[-1] == "dead_letter"
