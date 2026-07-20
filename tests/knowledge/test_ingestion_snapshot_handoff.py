from __future__ import annotations


def _parsed_text_document():
    from zuno.knowledge.ingestion import HumanReviewRuntime, ParseDocumentRequest, ParseGateway

    parsed = ParseGateway.submit_parse_job(
        ParseDocumentRequest(
            document_id="doc_snapshot_handoff",
            workspace_id="workspace_handoff",
            source_uri="file://docs/handoff.md",
            mime_type="text/markdown",
            source_text="# Handoff\nApproved text can be published as a snapshot.",
        )
    )
    snapshot = ParseGateway.get_job_snapshot(parsed.job_id)
    assert parsed.document is not None
    gate, task = HumanReviewRuntime().evaluate(
        document=parsed.document,
        parse_snapshot=snapshot,
        security_epoch_ref="security_epoch:workspace_handoff",
    )
    assert gate.verdict == "PASS"
    assert task is None
    return parsed.document, snapshot, gate


def test_snapshot_handoff_builds_immutable_snapshot_and_pending_outbox() -> None:
    from zuno.knowledge.ingestion import SnapshotHandoffRuntime

    document, parse_snapshot, gate = _parsed_text_document()
    runtime = SnapshotHandoffRuntime()

    first, first_outbox = runtime.create_snapshot(
        document=document,
        parse_snapshot=parse_snapshot,
        quality_gate=gate,
        visibility_ref="visibility:workspace_handoff:doc_snapshot_handoff",
    )
    second, second_outbox = runtime.create_snapshot(
        document=document,
        parse_snapshot=parse_snapshot,
        quality_gate=gate,
        visibility_ref="visibility:workspace_handoff:doc_snapshot_handoff",
    )

    assert first.indexable_snapshot_id.startswith("snapshot_")
    assert len(first.canonical_hash) == 64
    assert len(first.idempotency_key) == 64
    assert first.document_version_id == document.metadata.document_version_id
    assert first.quality_decision_id == gate.quality_decision_id
    assert first.security_refs["visibility_ref"] == "visibility:workspace_handoff:doc_snapshot_handoff"
    assert first.source_span_refs
    assert first_outbox.publish_status == "pending"
    assert first_outbox.event_type == "indexable_document_snapshot.ready"
    assert first_outbox.aggregate_ref == first.indexable_snapshot_id
    assert first_outbox.idempotency_key == first.idempotency_key
    assert SnapshotHandoffRuntime.duplicate_handoff(first, second) is True
    assert first_outbox.payload_hash == second_outbox.payload_hash


def test_snapshot_handoff_requires_approved_review_receipt_for_review_gate() -> None:
    import pytest

    from zuno.knowledge.ingestion import (
        HumanReviewRuntime,
        ParseDocumentRequest,
        ParseGateway,
        SnapshotHandoffBlockedError,
        SnapshotHandoffRuntime,
    )

    parsed = ParseGateway.submit_parse_job(
        ParseDocumentRequest(
            document_id="doc_review_snapshot",
            workspace_id="workspace_handoff",
            source_uri="file://scans/review.png",
            mime_type="image/png",
            source_text="OCR text requires approval before snapshot handoff.",
        )
    )
    parse_snapshot = ParseGateway.get_job_snapshot(parsed.job_id)
    assert parsed.document is not None
    review_runtime = HumanReviewRuntime(review_ttl_seconds=60)
    gate, task = review_runtime.evaluate(
        document=parsed.document,
        parse_snapshot=parse_snapshot,
        security_epoch_ref="security_epoch:workspace_handoff",
    )
    assert gate.verdict == "REVIEW"
    assert task is not None
    handoff = SnapshotHandoffRuntime()

    with pytest.raises(SnapshotHandoffBlockedError):
        handoff.create_snapshot(
            document=parsed.document,
            parse_snapshot=parse_snapshot,
            quality_gate=gate,
            visibility_ref="visibility:workspace_handoff:doc_review_snapshot",
        )

    rejected = review_runtime.decide(
        task=task,
        reviewer_id="reviewer_wrong_scope",
        reviewer_scope="tenant_admin",
        status="approved",
        security_epoch_ref="security_epoch:workspace_handoff",
    )
    with pytest.raises(SnapshotHandoffBlockedError):
        handoff.create_snapshot(
            document=parsed.document,
            parse_snapshot=parse_snapshot,
            quality_gate=gate,
            review_receipt=rejected,
            visibility_ref="visibility:workspace_handoff:doc_review_snapshot",
        )

    approved = review_runtime.decide(
        task=task,
        reviewer_id="reviewer_1",
        reviewer_scope=task.reviewer_scope,
        status="approved",
        security_epoch_ref=task.security_epoch_ref,
    )
    snapshot, outbox = handoff.create_snapshot(
        document=parsed.document,
        parse_snapshot=parse_snapshot,
        quality_gate=gate,
        review_receipt=approved,
        visibility_ref="visibility:workspace_handoff:doc_review_snapshot",
    )

    assert snapshot.quality_decision_id == gate.quality_decision_id
    assert snapshot.security_refs["review_task_id"] == task.review_task_id
    assert snapshot.security_refs["review_decision_id"] == approved.decision_id
    assert snapshot.security_refs["review_status"] == "approved"
    assert snapshot.payload["review_decision_hash"] == approved.decision_hash
    assert outbox.publish_status == "pending"


def test_sqlite_store_round_trips_snapshot_and_outbox() -> None:
    from pathlib import Path
    import tempfile

    from zuno.knowledge.ingestion import SnapshotHandoffRuntime
    from zuno.knowledge.storage import (
        IndexableSnapshotRecord,
        IngestionOutboxRecord,
        SQLiteDurableIngestionStore,
    )

    document, parse_snapshot, gate = _parsed_text_document()
    snapshot, outbox = SnapshotHandoffRuntime().create_snapshot(
        document=document,
        parse_snapshot=parse_snapshot,
        quality_gate=gate,
        visibility_ref="visibility:workspace_handoff:doc_snapshot_handoff",
        delete_refs=["delete_ref:none"],
    )
    store = SQLiteDurableIngestionStore(Path(tempfile.mkdtemp()) / "zuno.db")
    store.save_indexable_snapshot(
        IndexableSnapshotRecord(
            indexable_snapshot_id=snapshot.indexable_snapshot_id,
            document_version_id=snapshot.document_version_id,
            parse_snapshot_id=snapshot.parse_snapshot_id,
            quality_decision_id=snapshot.quality_decision_id,
            workspace_id=snapshot.workspace_id,
            document_id=snapshot.document_id,
            canonical_hash=snapshot.canonical_hash,
            idempotency_key=snapshot.idempotency_key,
            security_refs=snapshot.security_refs,
            delete_refs=snapshot.delete_refs,
            payload=snapshot.payload,
        )
    )
    store.save_ingestion_outbox(
        IngestionOutboxRecord(
            outbox_event_id=outbox.outbox_event_id,
            aggregate_ref=outbox.aggregate_ref,
            event_type=outbox.event_type,
            payload_hash=outbox.payload_hash,
            idempotency_key=outbox.idempotency_key,
            publish_status=outbox.publish_status,
            replay_count=outbox.replay_count,
        )
    )

    restored_snapshot = store.get_indexable_snapshot(snapshot.indexable_snapshot_id)
    restored_outbox = store.get_ingestion_outbox(outbox.outbox_event_id)

    assert restored_snapshot.canonical_hash == snapshot.canonical_hash
    assert restored_snapshot.security_refs["acl_scope"] == "workspace"
    assert restored_snapshot.delete_refs == ["delete_ref:none"]
    assert restored_outbox.publish_status == "pending"
    assert restored_outbox.idempotency_key == snapshot.idempotency_key


def test_snapshot_handoff_dispatch_replays_when_knowledge_is_unavailable() -> None:
    from zuno.knowledge.ingestion import SnapshotHandoffRuntime

    class FailingPublisher:
        def publish_snapshot(self, snapshot):
            raise RuntimeError(f"knowledge offline for {snapshot.indexable_snapshot_id}")

    class RecordingPublisher:
        def __init__(self) -> None:
            self.published = []

        def publish_snapshot(self, snapshot):
            self.published.append(snapshot.indexable_snapshot_id)
            return f"knowledge_receipt:{snapshot.indexable_snapshot_id}"

    document, parse_snapshot, gate = _parsed_text_document()
    snapshot, outbox = SnapshotHandoffRuntime().create_snapshot(
        document=document,
        parse_snapshot=parse_snapshot,
        quality_gate=gate,
        visibility_ref="visibility:workspace_handoff:doc_snapshot_handoff",
    )

    replayed, failed_receipt = SnapshotHandoffRuntime.dispatch_outbox(
        snapshot=snapshot,
        outbox=outbox,
        publisher=FailingPublisher(),
    )
    publisher = RecordingPublisher()
    handed_off, success_receipt = SnapshotHandoffRuntime.dispatch_outbox(
        snapshot=snapshot,
        outbox=replayed,
        publisher=publisher,
    )

    assert replayed.publish_status == "pending"
    assert replayed.replay_count == 1
    assert failed_receipt.acknowledged is False
    assert failed_receipt.failure_reason == "knowledge_unavailable:RuntimeError"
    assert handed_off.publish_status == "handed_off"
    assert handed_off.replay_count == 1
    assert success_receipt.acknowledged is True
    assert success_receipt.knowledge_receipt_ref == (
        f"knowledge_receipt:{snapshot.indexable_snapshot_id}"
    )
    assert publisher.published == [snapshot.indexable_snapshot_id]
