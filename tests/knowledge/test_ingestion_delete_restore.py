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
    physical = runtime.mark_physical_delete(cleanup)
    verified = runtime.verify_delete(physical)
    late_rejected = runtime.reject_late_worker_result(verified)

    assert requested.state == "visibility_revoked"
    assert cleanup.state == "cleanup_requested"
    assert physical.state == "physically_deleted"
    assert verified.state == "verified"
    assert verified.history == [
        "visibility_revoked",
        "cleanup_requested",
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
    restored = runtime.restore(physical)

    assert held.state == "legal_hold"
    assert cleanup.state == "legal_hold"
    assert physical.physical_delete_ref is None
    assert restored.state == "restored"
    assert restored.restored_authorization is False


def test_delete_ref_is_carried_by_later_indexable_snapshot() -> None:
    from zuno.knowledge.ingestion import DeleteRestoreRuntime, SnapshotHandoffRuntime

    document, parse_snapshot, gate = _parsed_text_document()
    delete_receipt = DeleteRestoreRuntime().verify_delete(
        DeleteRestoreRuntime().mark_physical_delete(
            DeleteRestoreRuntime().request_cleanup(
                DeleteRestoreRuntime().request_delete(
                    snapshot_ref="snapshot_old",
                    visibility_ref="visibility:workspace_handoff:doc_snapshot_handoff",
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


def test_sqlite_store_round_trips_delete_lifecycle_receipt() -> None:
    from zuno.knowledge.ingestion import DeleteRestoreRuntime
    from zuno.knowledge.storage import DeleteLifecycleRecord, SQLiteDurableIngestionStore

    receipt = DeleteRestoreRuntime().verify_delete(
        DeleteRestoreRuntime().mark_physical_delete(
            DeleteRestoreRuntime().request_cleanup(
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
