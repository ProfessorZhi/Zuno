from __future__ import annotations

import hashlib
import json
from typing import Any, Literal

from pydantic import BaseModel, Field


DeleteState = Literal[
    "visibility_revoked",
    "cleanup_requested",
    "physically_deleted",
    "verified",
    "legal_hold",
    "restored",
]


class DeleteLifecycleReceipt(BaseModel):
    delete_ref: str
    snapshot_ref: str
    state: DeleteState
    visibility_ref: str
    indexable_snapshot_id: str | None = None
    handoff_outbox_event_id: str | None = None
    parse_job_id: str | None = None
    parse_attempt_id: str | None = None
    fencing_token: int | None = None
    cleanup_ref: str | None = None
    projection_cleanup_ref: str | None = None
    physical_delete_ref: str | None = None
    verification_ref: str | None = None
    cleanup_verified: bool = False
    physical_delete_verified: bool = False
    legal_hold_ref: str | None = None
    restored_authorization: bool = False
    duplicate: bool = False
    late_worker_result_rejected: bool = False
    receipt_hash: str
    history: list[str] = Field(default_factory=list)


class DeleteRestoreRuntime:
    def request_delete(
        self,
        *,
        snapshot_ref: str,
        visibility_ref: str,
        legal_hold_ref: str | None = None,
        existing: DeleteLifecycleReceipt | None = None,
    ) -> DeleteLifecycleReceipt:
        if existing is not None:
            return existing.model_copy(update={"duplicate": True})
        delete_ref = f"delete_{_hash({'snapshot_ref': snapshot_ref, 'visibility_ref': visibility_ref})[:24]}"
        state: DeleteState = "legal_hold" if legal_hold_ref else "visibility_revoked"
        history = ["visibility_revoked"]
        if legal_hold_ref:
            history.append("legal_hold")
        return DeleteLifecycleReceipt(
            delete_ref=delete_ref,
            snapshot_ref=snapshot_ref,
            state=state,
            visibility_ref=visibility_ref,
            cleanup_ref=None if legal_hold_ref else f"cleanup_{delete_ref}",
            legal_hold_ref=legal_hold_ref,
            receipt_hash=_hash(
                {
                    "delete_ref": delete_ref,
                    "snapshot_ref": snapshot_ref,
                    "visibility_ref": visibility_ref,
                    "state": state,
                    "legal_hold_ref": legal_hold_ref,
                }
            ),
            history=history,
        )

    def request_delete_during_parse(
        self,
        *,
        parse_job_id: str,
        parse_attempt_id: str,
        fencing_token: int,
        visibility_ref: str,
        snapshot_ref: str | None = None,
        legal_hold_ref: str | None = None,
    ) -> DeleteLifecycleReceipt:
        if fencing_token <= 0:
            raise ValueError("fencing_token must be positive")
        requested = self.request_delete(
            snapshot_ref=snapshot_ref or f"parse_inflight:{parse_job_id}",
            visibility_ref=visibility_ref,
            legal_hold_ref=legal_hold_ref,
        )
        return requested.model_copy(
            update={
                "parse_job_id": parse_job_id,
                "parse_attempt_id": parse_attempt_id,
                "fencing_token": fencing_token,
                "history": [*requested.history, "parse_inflight_delete_requested"],
                "receipt_hash": _hash(
                    {
                        "delete_ref": requested.delete_ref,
                        "parse_job_id": parse_job_id,
                        "parse_attempt_id": parse_attempt_id,
                        "fencing_token": fencing_token,
                        "visibility_ref": visibility_ref,
                        "state": requested.state,
                    }
                ),
            }
        )

    def request_delete_after_snapshot(
        self,
        *,
        indexable_snapshot_id: str,
        handoff_outbox_event_id: str,
        visibility_ref: str,
        projection_cleanup_ref: str,
        legal_hold_ref: str | None = None,
    ) -> DeleteLifecycleReceipt:
        requested = self.request_delete(
            snapshot_ref=indexable_snapshot_id,
            visibility_ref=visibility_ref,
            legal_hold_ref=legal_hold_ref,
        )
        return requested.model_copy(
            update={
                "indexable_snapshot_id": indexable_snapshot_id,
                "handoff_outbox_event_id": handoff_outbox_event_id,
                "projection_cleanup_ref": projection_cleanup_ref,
                "history": [*requested.history, "snapshot_delete_requested"],
                "receipt_hash": _hash(
                    {
                        "delete_ref": requested.delete_ref,
                        "indexable_snapshot_id": indexable_snapshot_id,
                        "handoff_outbox_event_id": handoff_outbox_event_id,
                        "projection_cleanup_ref": projection_cleanup_ref,
                        "visibility_ref": visibility_ref,
                        "state": requested.state,
                    }
                ),
            }
        )

    def request_cleanup(self, receipt: DeleteLifecycleReceipt) -> DeleteLifecycleReceipt:
        if receipt.legal_hold_ref:
            return receipt
        return receipt.model_copy(
            update={
                "state": "cleanup_requested",
                "cleanup_ref": receipt.cleanup_ref or f"cleanup_{receipt.delete_ref}",
                "history": [*receipt.history, "cleanup_requested"],
            }
        )

    def mark_physical_delete(self, receipt: DeleteLifecycleReceipt) -> DeleteLifecycleReceipt:
        if receipt.legal_hold_ref:
            return receipt
        physical_delete_ref = f"physical_{receipt.delete_ref}"
        return receipt.model_copy(
            update={
                "state": "physically_deleted",
                "physical_delete_ref": physical_delete_ref,
                "history": [*receipt.history, "physically_deleted"],
            }
        )

    def verify_delete(
        self,
        receipt: DeleteLifecycleReceipt,
        *,
        cleanup_verified: bool = True,
        physical_delete_verified: bool = True,
    ) -> DeleteLifecycleReceipt:
        if receipt.legal_hold_ref:
            return receipt
        if not cleanup_verified:
            raise ValueError("delete verification requires projection cleanup confirmation")
        if not physical_delete_verified:
            raise ValueError("delete verification requires physical delete confirmation")
        verification_ref = f"verify_{receipt.delete_ref}"
        return receipt.model_copy(
            update={
                "state": "verified",
                "verification_ref": verification_ref,
                "cleanup_verified": True,
                "physical_delete_verified": True,
                "history": [*receipt.history, "verified"],
            }
        )

    def reject_late_worker_result(
        self,
        receipt: DeleteLifecycleReceipt,
        *,
        parse_attempt_id: str | None = None,
        fencing_token: int | None = None,
    ) -> DeleteLifecycleReceipt:
        if parse_attempt_id is not None and parse_attempt_id != receipt.parse_attempt_id:
            return receipt.model_copy(update={"late_worker_result_rejected": True})
        if fencing_token is not None and receipt.fencing_token is not None and fencing_token != receipt.fencing_token:
            return receipt.model_copy(update={"late_worker_result_rejected": True})
        if receipt.state in {"visibility_revoked", "cleanup_requested", "physically_deleted", "verified", "restored"}:
            return receipt.model_copy(
                update={
                    "late_worker_result_rejected": True,
                    "history": [*receipt.history, "late_worker_result_rejected"],
                }
            )
        return receipt

    def restore(self, receipt: DeleteLifecycleReceipt) -> DeleteLifecycleReceipt:
        return receipt.model_copy(
            update={
                "state": "restored",
                "restored_authorization": False,
                "history": [*receipt.history, "restored"],
            }
        )


def _hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


__all__ = ["DeleteLifecycleReceipt", "DeleteRestoreRuntime"]
