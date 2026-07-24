from __future__ import annotations

from pathlib import Path
import tempfile


def _parsed_text_document():
    from zuno.knowledge.ingestion import HumanReviewRuntime, ParseDocumentRequest, ParseGateway

    parsed = ParseGateway.submit_parse_job(
        ParseDocumentRequest(
            document_id="doc_delete_handoff",
            workspace_id="workspace_handoff",
            source_uri="file://docs/delete-handoff.md",
            mime_type="text/markdown",
            source_text="# Delete Handoff\nDelete refs must survive snapshot creation.",
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


def test_delete_lifecycle_orders_visibility_cleanup_physical_delete_and_verification() -> None:
    from zuno.knowledge.ingestion import DeleteRestoreRuntime

    runtime = DeleteRestoreRuntime()
    requested = runtime.request_delete(
        snapshot_ref="snapshot_doc_1",
        visibility_ref="visibility:workspace:file_1",
    )
    cleanup = runtime.request_cleanup(requested)
    confirmed = runtime.confirm_knowledge_cleanup(cleanup)
    physical = runtime.mark_physical_delete(confirmed)
    verified = runtime.verify_delete(physical)
    late_rejected = runtime.reject_late_worker_result(verified)

    assert requested.state == "visibility_revoked"
    assert cleanup.state == "cleanup_requested"
    assert physical.state == "physically_deleted"
    assert verified.state == "verified"
    assert verified.history == [
        "visibility_revoked",
        "cleanup_requested",
        "knowledge_cleanup_confirmed",
        "physically_deleted",
        "verified",
    ]
    assert late_rejected.late_worker_result_rejected is True
    duplicate = runtime.request_delete(
        snapshot_ref="snapshot_doc_1",
        visibility_ref="visibility:workspace:file_1",
        existing=verified,
    )
    assert duplicate.duplicate is True


def test_legal_hold_blocks_physical_delete_but_restore_does_not_restore_authorization() -> None:
    from zuno.knowledge.ingestion import DeleteRestoreRuntime

    runtime = DeleteRestoreRuntime()
    held = runtime.request_delete(
        snapshot_ref="snapshot_doc_legal",
        visibility_ref="visibility:workspace:file_legal",
        legal_hold_ref="legal_hold:case_1",
    )
    cleanup = runtime.request_cleanup(held)
    physical = runtime.mark_physical_delete(cleanup)
    try:
        runtime.restore(physical)
    except ValueError as exc:
        assert "fresh authorization" in str(exc)
    else:
        raise AssertionError("restore without fresh authorization must fail")
    restored = runtime.restore(physical, restore_authorization_ref="restore-auth:case_1")
    try:
        runtime.restore(restored)
    except ValueError as exc:
        assert "fresh authorization" in str(exc)
    else:
        raise AssertionError("duplicate restore without fresh authorization must fail")
    duplicate_restored = runtime.restore(restored, restore_authorization_ref="restore-auth:case_1")

    assert held.state == "legal_hold"
    assert cleanup.state == "legal_hold"
    assert physical.physical_delete_ref is None
    assert restored.state == "restored"
    assert restored.restored_authorization is True
    assert restored.restore_authorization_ref == "restore-auth:case_1"
    assert duplicate_restored.duplicate is True


def test_delete_ref_is_carried_by_later_indexable_snapshot() -> None:
    from zuno.knowledge.ingestion import DeleteRestoreRuntime, SnapshotHandoffRuntime

    document, parse_snapshot, gate = _parsed_text_document()
    delete_receipt = DeleteRestoreRuntime().verify_delete(
        DeleteRestoreRuntime().mark_physical_delete(
            DeleteRestoreRuntime().confirm_knowledge_cleanup(
                DeleteRestoreRuntime().request_cleanup(
                    DeleteRestoreRuntime().request_delete(
                        snapshot_ref="snapshot_old",
                        visibility_ref="visibility:workspace_handoff:doc_snapshot_handoff",
                    )
                )
            )
        )
    )
    snapshot, _outbox = SnapshotHandoffRuntime().create_snapshot(
        document=document,
        parse_snapshot=parse_snapshot,
        quality_gate=gate,
        visibility_ref="visibility:workspace_handoff:doc_snapshot_handoff",
        delete_refs=[delete_receipt.delete_ref],
    )

    assert snapshot.delete_refs == [delete_receipt.delete_ref]
    assert snapshot.payload["delete_refs"] == [delete_receipt.delete_ref]


def test_delete_after_snapshot_binds_outbox_projection_cleanup_and_verification_evidence() -> None:
    import pytest

    from zuno.knowledge.ingestion import DeleteRestoreRuntime, SnapshotHandoffRuntime

    document, parse_snapshot, gate = _parsed_text_document()
    snapshot, outbox = SnapshotHandoffRuntime().create_snapshot(
        document=document,
        parse_snapshot=parse_snapshot,
        quality_gate=gate,
        visibility_ref="visibility:workspace_handoff:doc_delete_handoff",
    )
    runtime = DeleteRestoreRuntime()
    requested = runtime.request_delete_after_snapshot(
        indexable_snapshot_id=snapshot.indexable_snapshot_id,
        handoff_outbox_event_id=outbox.outbox_event_id,
        visibility_ref=snapshot.security_refs["visibility_ref"],
        projection_cleanup_ref=f"projection_cleanup:{snapshot.indexable_snapshot_id}",
    )
    cleanup = runtime.request_cleanup(requested)
    with pytest.raises(ValueError, match="knowledge cleanup"):
        runtime.mark_physical_delete(cleanup)
    confirmed = runtime.confirm_knowledge_cleanup(cleanup)
    physical = runtime.mark_physical_delete(confirmed)

    with pytest.raises(ValueError, match="knowledge cleanup"):
        runtime.verify_delete(physical, cleanup_verified=False)
    with pytest.raises(ValueError, match="physical delete"):
        runtime.verify_delete(physical, physical_delete_verified=False)

    verified = runtime.verify_delete(
        physical,
        cleanup_verified=True,
        physical_delete_verified=True,
    )

    assert requested.snapshot_ref == snapshot.indexable_snapshot_id
    assert requested.indexable_snapshot_id == snapshot.indexable_snapshot_id
    assert requested.handoff_outbox_event_id == outbox.outbox_event_id
    assert requested.projection_cleanup_ref == f"projection_cleanup:{snapshot.indexable_snapshot_id}"
    assert "snapshot_delete_requested" in requested.history
    assert verified.state == "verified"
    assert verified.cleanup_verified is True
    assert verified.physical_delete_verified is True


def test_delete_during_parse_rejects_late_worker_result_by_attempt_and_fencing() -> None:
    from zuno.knowledge.ingestion import DeleteRestoreRuntime, ParseAttemptLeaseRuntime

    lease = ParseAttemptLeaseRuntime().claim(
        parse_job_id="parse_job_delete_during_parse",
        worker_id="worker_1",
        attempt_no=1,
        now=10.0,
        ttl_seconds=30.0,
    )
    runtime = DeleteRestoreRuntime()
    requested = runtime.request_delete_during_parse(
        parse_job_id=lease.parse_job_id,
        parse_attempt_id=lease.parse_attempt_id,
        fencing_token=lease.fencing_token,
        visibility_ref="visibility:workspace:file_parse_delete",
    )
    cleanup = runtime.request_cleanup(requested)
    physical = runtime.mark_physical_delete(runtime.confirm_knowledge_cleanup(cleanup))
    verified = runtime.verify_delete(physical)
    rejected_current = runtime.reject_late_worker_result(
        verified,
        parse_attempt_id=lease.parse_attempt_id,
        fencing_token=lease.fencing_token,
    )
    rejected_stale = runtime.reject_late_worker_result(
        verified,
        parse_attempt_id="attempt_stale",
        fencing_token=lease.fencing_token + 1,
    )

    assert requested.snapshot_ref == f"parse_inflight:{lease.parse_job_id}"
    assert requested.parse_job_id == lease.parse_job_id
    assert requested.parse_attempt_id == lease.parse_attempt_id
    assert requested.fencing_token == lease.fencing_token
    assert "parse_inflight_delete_requested" in requested.history
    assert verified.state == "verified"
    assert rejected_current.late_worker_result_rejected is True
    assert rejected_current.history[-1] == "late_worker_result_rejected"
    assert rejected_stale.late_worker_result_rejected is True


def test_delete_during_parse_legal_hold_blocks_cleanup_without_rejecting_active_result() -> None:
    from zuno.knowledge.ingestion import DeleteRestoreRuntime

    runtime = DeleteRestoreRuntime()
    held = runtime.request_delete_during_parse(
        parse_job_id="parse_job_held",
        parse_attempt_id="attempt_held",
        fencing_token=7,
        visibility_ref="visibility:workspace:file_held",
        legal_hold_ref="legal_hold:case_held",
    )
    cleanup = runtime.request_cleanup(held)
    physical = runtime.mark_physical_delete(cleanup)
    not_rejected = runtime.reject_late_worker_result(
        physical,
        parse_attempt_id="attempt_held",
        fencing_token=7,
    )

    assert held.state == "legal_hold"
    assert cleanup.state == "legal_hold"
    assert physical.physical_delete_ref is None
    assert not_rejected.late_worker_result_rejected is False


def test_sqlite_store_round_trips_delete_lifecycle_receipt() -> None:
    from zuno.knowledge.ingestion import DeleteRestoreRuntime
    from zuno.knowledge.storage import DeleteLifecycleRecord, SQLiteDurableIngestionStore

    receipt = DeleteRestoreRuntime().verify_delete(
        DeleteRestoreRuntime().mark_physical_delete(
            DeleteRestoreRuntime().confirm_knowledge_cleanup(
                DeleteRestoreRuntime().request_delete(
                    snapshot_ref="snapshot_doc_1",
                    visibility_ref="visibility:workspace:file_1",
                )
            )
        )
    )
    store = SQLiteDurableIngestionStore(Path(tempfile.mkdtemp()) / "zuno.db")
    store.save_delete_lifecycle(DeleteLifecycleRecord(**receipt.model_dump()))

    restored = store.get_delete_lifecycle(receipt.delete_ref)

    assert restored.state == "verified"
    assert restored.verification_ref == receipt.verification_ref
    assert restored.history[-1] == "verified"
