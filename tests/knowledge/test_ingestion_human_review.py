from __future__ import annotations

from pathlib import Path


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
