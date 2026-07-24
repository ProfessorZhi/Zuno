from __future__ import annotations

from pathlib import Path

import pytest


def _ocr_parse():
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    result = ParseGateway.submit_parse_job(
        ParseDocumentRequest(
            document_id="doc_review_ocr",
            workspace_id="workspace_review",
            source_uri="file://scans/review.png",
            mime_type="image/png",
            source_text="OCR text requires review before publication.",
        )
    )
    return result, ParseGateway.get_job_snapshot(result.job_id)


def test_human_review_runtime_blocks_publish_until_approved() -> None:
    from zuno.knowledge.ingestion import HumanReviewRuntime

    result, snapshot = _ocr_parse()
    assert result.document is not None

    runtime = HumanReviewRuntime(review_ttl_seconds=60)
    gate, task = runtime.evaluate(
        document=result.document,
        parse_snapshot=snapshot,
        security_epoch_ref="security_epoch:workspace_review",
    )

    assert gate.verdict == "REVIEW"
    assert task is not None
    assert task.status == "pending"
    assert task.reviewer_scope == "workspace_reviewer"
    assert task.security_epoch_ref == "security_epoch:workspace_review"
    assert len(gate.decision_hash) == 64
    assert HumanReviewRuntime.can_publish_snapshot(gate=gate) is False

    receipt = runtime.decide(
        task=task,
        reviewer_id="reviewer_1",
        reviewer_scope="workspace_reviewer",
        status="approved",
        security_epoch_ref="security_epoch:workspace_review",
    )

    assert receipt.status == "approved"
    assert receipt.duplicate is False
    assert len(receipt.decision_hash) == 64
    assert HumanReviewRuntime.can_publish_snapshot(gate=gate, receipt=receipt) is True

    duplicate = runtime.decide(
        task=task,
        reviewer_id="reviewer_1",
        reviewer_scope="workspace_reviewer",
        status="approved",
        security_epoch_ref="security_epoch:workspace_review",
        existing_receipt=receipt,
    )
    assert duplicate.duplicate is True
    assert duplicate.decision_hash == receipt.decision_hash


def test_human_review_runtime_rejects_conflicting_duplicate_decision() -> None:
    from zuno.knowledge.ingestion import HumanReviewRuntime

    result, snapshot = _ocr_parse()
    assert result.document is not None

    runtime = HumanReviewRuntime(review_ttl_seconds=60)
    _, task = runtime.evaluate(
        document=result.document,
        parse_snapshot=snapshot,
        security_epoch_ref="security_epoch:workspace_review",
    )
    assert task is not None

    receipt = runtime.decide(
        task=task,
        reviewer_id="reviewer_1",
        reviewer_scope="workspace_reviewer",
        status="approved",
        security_epoch_ref="security_epoch:workspace_review",
    )

    duplicate = runtime.decide(
        task=task,
        reviewer_id="reviewer_1",
        reviewer_scope="workspace_reviewer",
        status="approved",
        security_epoch_ref="security_epoch:workspace_review",
        existing_receipt=receipt,
    )

    assert duplicate.duplicate is True
    assert duplicate.decision_hash == receipt.decision_hash

    with pytest.raises(ValueError, match="conflicting review decision"):
        runtime.decide(
            task=task,
            reviewer_id="reviewer_1",
            reviewer_scope="workspace_reviewer",
            status="rejected",
            security_epoch_ref="security_epoch:workspace_review",
            existing_receipt=receipt,
        )

    with pytest.raises(ValueError, match="conflicting review decision"):
        runtime.decide(
            task=task,
            reviewer_id="reviewer_2",
            reviewer_scope="workspace_reviewer",
            status="approved",
            security_epoch_ref="security_epoch:workspace_review",
            existing_receipt=receipt,
        )


def test_human_review_runtime_records_rejected_expired_and_cancelled_states() -> None:
    from zuno.knowledge.ingestion import HumanReviewRuntime

    result, snapshot = _ocr_parse()
    assert result.document is not None
    runtime = HumanReviewRuntime(review_ttl_seconds=1)
    gate, task = runtime.evaluate(
        document=result.document,
        parse_snapshot=snapshot,
        security_epoch_ref="security_epoch:workspace_review",
    )
    assert task is not None

    rejected = runtime.decide(
        task=task,
        reviewer_id="reviewer_wrong_scope",
        reviewer_scope="tenant_admin",
        status="approved",
        security_epoch_ref="security_epoch:workspace_review",
    )
    cancelled = runtime.decide(
        task=task,
        reviewer_id="reviewer_1",
        reviewer_scope="workspace_reviewer",
        status="cancelled",
        security_epoch_ref="security_epoch:workspace_review",
    )
    expired = runtime.decide(
        task=task,
        reviewer_id="reviewer_1",
        reviewer_scope="workspace_reviewer",
        status="approved",
        security_epoch_ref="security_epoch:workspace_review",
        now=task.expires_at + 1,
    )

    assert rejected.status == "rejected"
    assert cancelled.status == "cancelled"
    assert expired.status == "expired"
    assert HumanReviewRuntime.can_publish_snapshot(gate=gate, receipt=rejected) is False
    assert HumanReviewRuntime.can_publish_snapshot(gate=gate, receipt=cancelled) is False
    assert HumanReviewRuntime.can_publish_snapshot(gate=gate, receipt=expired) is False


def test_human_review_runtime_rejects_revoked_reviewer_and_stale_epoch_approval() -> None:
    from zuno.knowledge.ingestion import HumanReviewRuntime, StaticReviewDecisionAuthorizationPort

    result, snapshot = _ocr_parse()
    assert result.document is not None
    runtime = HumanReviewRuntime(
        review_ttl_seconds=60,
        authorization_port=StaticReviewDecisionAuthorizationPort(
            revoked_reviewer_ids=frozenset({"reviewer_revoked"})
        ),
    )
    gate, task = runtime.evaluate(
        document=result.document,
        parse_snapshot=snapshot,
        security_epoch_ref="security_epoch:workspace_review",
        reviewer_principal_id="reviewer_revoked",
        security_decision_ref="security_decision:review",
    )
    assert task is not None

    revoked = runtime.decide(
        task=task,
        reviewer_id="reviewer_revoked",
        reviewer_scope="workspace_reviewer",
        status="approved",
        security_epoch_ref="security_epoch:workspace_review",
    )
    stale_runtime = HumanReviewRuntime(review_ttl_seconds=60)
    stale_gate, stale_task = stale_runtime.evaluate(
        document=result.document,
        parse_snapshot=snapshot,
        security_epoch_ref="security_epoch:workspace_review",
        reviewer_principal_id="reviewer_1",
        security_decision_ref="security_decision:review",
    )
    assert stale_task is not None
    stale_epoch = stale_runtime.decide(
        task=stale_task,
        reviewer_id="reviewer_1",
        reviewer_scope="workspace_reviewer",
        status="approved",
        security_epoch_ref="security_epoch:workspace_review:stale",
    )

    assert revoked.status == "rejected"
    assert revoked.reason == "reviewer_authorization_revoked"
    assert stale_epoch.status == "rejected"
    assert stale_epoch.reason == "review_security_epoch_mismatch"
    assert HumanReviewRuntime.can_publish_snapshot(gate=gate, receipt=revoked) is False
    assert HumanReviewRuntime.can_publish_snapshot(gate=stale_gate, receipt=stale_epoch) is False


def test_human_review_runtime_expiration_sweep_expires_only_pending_overdue_tasks() -> None:
    from zuno.knowledge.ingestion import HumanReviewRuntime

    result, snapshot = _ocr_parse()
    assert result.document is not None
    runtime = HumanReviewRuntime(review_ttl_seconds=10)
    gate, task = runtime.evaluate(
        document=result.document,
        parse_snapshot=snapshot,
        security_epoch_ref="security_epoch:workspace_review",
    )
    assert task is not None
    future_task = task.model_copy(
        update={
            "review_task_id": "review_future_task",
            "expires_at": task.expires_at + 100,
        }
    )
    existing_receipt = runtime.decide(
        task=task,
        reviewer_id="reviewer_1",
        reviewer_scope=task.reviewer_scope,
        status="approved",
        security_epoch_ref=task.security_epoch_ref,
    )

    sweep = runtime.expire_pending_reviews(
        tasks=[task, future_task],
        existing_receipts={task.review_task_id: existing_receipt},
        now=task.expires_at + 1,
    )

    assert sweep.expired_task_ids == []
    assert sweep.skipped_task_ids == [task.review_task_id, future_task.review_task_id]
    assert sweep.decision_receipts == []
    assert len(sweep.sweep_hash) == 64

    expired_sweep = runtime.expire_pending_reviews(
        tasks=[task, future_task],
        now=future_task.expires_at + 1,
    )

    assert expired_sweep.expired_task_ids == [task.review_task_id, future_task.review_task_id]
    assert expired_sweep.skipped_task_ids == []
    assert [receipt.status for receipt in expired_sweep.decision_receipts] == [
        "expired",
        "expired",
    ]
    assert all(
        HumanReviewRuntime.can_publish_snapshot(gate=gate, receipt=receipt) is False
        for receipt in expired_sweep.decision_receipts
    )


def test_sqlite_store_round_trips_quality_gate_review_task_and_receipt(tmp_path: Path) -> None:
    from zuno.knowledge.ingestion import HumanReviewRuntime
    from zuno.knowledge.storage import (
        QualityGateRecord,
        ReviewDecisionRecord,
        ReviewTaskRecord,
        SQLiteDurableIngestionStore,
    )

    result, snapshot = _ocr_parse()
    assert result.document is not None
    gate, task = HumanReviewRuntime().evaluate(
        document=result.document,
        parse_snapshot=snapshot,
        security_epoch_ref="security_epoch:workspace_review",
    )
    assert task is not None
    receipt = HumanReviewRuntime().decide(
        task=task,
        reviewer_id="reviewer_1",
        reviewer_scope=task.reviewer_scope,
        status="approved",
        security_epoch_ref=task.security_epoch_ref,
    )

    store = SQLiteDurableIngestionStore(tmp_path / "zuno.db")
    store.save_quality_gate(
        QualityGateRecord(
            quality_decision_id=gate.quality_decision_id,
            parse_snapshot_id=gate.parse_snapshot_id,
            document_version_id=task.document_version_id,
            workspace_id=task.workspace_id,
            verdict=gate.verdict,
            decision_hash=gate.decision_hash,
            review_task_id=gate.review_task_id,
            metrics=[metric.model_dump() for metric in gate.metrics],
        )
    )
    store.save_review_task(ReviewTaskRecord(**task.model_dump()))
    store.save_review_decision(ReviewDecisionRecord(**receipt.model_dump()))

    restored_gate = store.get_quality_gate(gate.quality_decision_id)
    restored_task = store.get_review_task(task.review_task_id)
    restored_receipt = store.get_review_decision(receipt.decision_id)

    assert restored_gate.verdict == "REVIEW"
    assert restored_gate.review_task_id == task.review_task_id
    assert restored_gate.metrics[0]["name"] == "min_block_confidence"
    assert restored_task.status == "pending"
    assert restored_task.security_epoch_ref == "security_epoch:workspace_review"
    assert restored_receipt.status == "approved"
