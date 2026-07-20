from __future__ import annotations

import hashlib
import json
from typing import Any, Literal

from pydantic import BaseModel, Field


LeaseState = Literal[
    "claimed",
    "renewed",
    "expired",
    "released",
    "lost",
    "reconciled",
    "committed",
    "late_result_rejected",
]


class ParseAttemptLeaseReceipt(BaseModel):
    parse_attempt_id: str
    parse_job_id: str
    worker_id: str
    attempt_no: int
    fencing_token: int
    state: LeaseState
    heartbeat_at: float
    lease_expires_at: float
    lease_lost_reason: str | None = None
    domain_commit_ref: str | None = None
    idempotency_key: str | None = None
    duplicate_commit: bool = False
    late_result_rejected: bool = False
    orphan_reconciled: bool = False
    receipt_hash: str
    history: list[str] = Field(default_factory=list)


class ParseAttemptLeaseRuntime:
    def claim(
        self,
        *,
        parse_job_id: str,
        worker_id: str,
        attempt_no: int = 1,
        now: float = 0.0,
        ttl_seconds: float = 60.0,
        previous: ParseAttemptLeaseReceipt | None = None,
    ) -> ParseAttemptLeaseReceipt:
        if attempt_no <= 0:
            raise ValueError("attempt_no must be positive")
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        fencing_token = (previous.fencing_token + 1) if previous else attempt_no
        parse_attempt_id = f"attempt_{_hash({'parse_job_id': parse_job_id, 'attempt_no': attempt_no, 'fencing_token': fencing_token})[:24]}"
        receipt = ParseAttemptLeaseReceipt(
            parse_attempt_id=parse_attempt_id,
            parse_job_id=parse_job_id,
            worker_id=worker_id,
            attempt_no=attempt_no,
            fencing_token=fencing_token,
            state="claimed",
            heartbeat_at=now,
            lease_expires_at=now + ttl_seconds,
            receipt_hash="",
            history=["claimed"],
        )
        return _with_hash(receipt)

    def renew(
        self,
        receipt: ParseAttemptLeaseReceipt,
        *,
        worker_id: str,
        fencing_token: int,
        now: float,
        ttl_seconds: float,
    ) -> ParseAttemptLeaseReceipt:
        self._require_current_owner(receipt, worker_id=worker_id, fencing_token=fencing_token)
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        return _with_hash(
            receipt.model_copy(
                update={
                    "state": "renewed",
                    "heartbeat_at": now,
                    "lease_expires_at": now + ttl_seconds,
                    "history": [*receipt.history, "heartbeat_renewed"],
                }
            )
        )

    def expire(self, receipt: ParseAttemptLeaseReceipt, *, now: float) -> ParseAttemptLeaseReceipt:
        if now < receipt.lease_expires_at or receipt.state in {"committed", "released"}:
            return receipt
        return _with_hash(
            receipt.model_copy(
                update={
                    "state": "expired",
                    "lease_lost_reason": "heartbeat_expired",
                    "history": [*receipt.history, "expired"],
                }
            )
        )

    def release(
        self,
        receipt: ParseAttemptLeaseReceipt,
        *,
        worker_id: str,
        fencing_token: int,
    ) -> ParseAttemptLeaseReceipt:
        self._require_current_owner(receipt, worker_id=worker_id, fencing_token=fencing_token)
        return _with_hash(
            receipt.model_copy(
                update={
                    "state": "released",
                    "history": [*receipt.history, "released"],
                }
            )
        )

    def lose(
        self,
        receipt: ParseAttemptLeaseReceipt,
        *,
        reason: str,
    ) -> ParseAttemptLeaseReceipt:
        return _with_hash(
            receipt.model_copy(
                update={
                    "state": "lost",
                    "lease_lost_reason": reason,
                    "history": [*receipt.history, f"lost:{reason}"],
                }
            )
        )

    def reconcile_orphan(
        self,
        receipt: ParseAttemptLeaseReceipt,
        *,
        now: float,
    ) -> ParseAttemptLeaseReceipt:
        expired = self.expire(receipt, now=now)
        if expired.state not in {"expired", "lost"}:
            return expired
        return _with_hash(
            expired.model_copy(
                update={
                    "state": "reconciled",
                    "orphan_reconciled": True,
                    "history": [*expired.history, "orphan_reconciled"],
                }
            )
        )

    def reject_late_result(
        self,
        current: ParseAttemptLeaseReceipt,
        *,
        worker_id: str,
        fencing_token: int,
        parse_attempt_id: str,
    ) -> ParseAttemptLeaseReceipt:
        is_stale_owner = worker_id != current.worker_id
        is_stale_token = fencing_token != current.fencing_token
        is_stale_attempt = parse_attempt_id != current.parse_attempt_id
        is_closed = current.state in {"expired", "lost", "reconciled", "released", "late_result_rejected"}
        if not (is_stale_owner or is_stale_token or is_stale_attempt or is_closed):
            return current
        return _with_hash(
            current.model_copy(
                update={
                    "state": "late_result_rejected",
                    "late_result_rejected": True,
                    "history": [*current.history, "late_result_rejected"],
                }
            )
        )

    def commit_if_current(
        self,
        receipt: ParseAttemptLeaseReceipt,
        *,
        worker_id: str,
        fencing_token: int,
        idempotency_key: str,
    ) -> ParseAttemptLeaseReceipt:
        if receipt.idempotency_key == idempotency_key and receipt.domain_commit_ref:
            return receipt.model_copy(update={"duplicate_commit": True})
        self._require_current_owner(receipt, worker_id=worker_id, fencing_token=fencing_token)
        if receipt.state in {"expired", "lost", "reconciled", "released", "late_result_rejected"}:
            raise ValueError(f"cannot commit closed lease state: {receipt.state}")
        domain_commit_ref = f"domain_commit_{_hash({'parse_attempt_id': receipt.parse_attempt_id, 'idempotency_key': idempotency_key})[:24]}"
        return _with_hash(
            receipt.model_copy(
                update={
                    "state": "committed",
                    "domain_commit_ref": domain_commit_ref,
                    "idempotency_key": idempotency_key,
                    "history": [*receipt.history, "domain_commit"],
                }
            )
        )

    def _require_current_owner(
        self,
        receipt: ParseAttemptLeaseReceipt,
        *,
        worker_id: str,
        fencing_token: int,
    ) -> None:
        if worker_id != receipt.worker_id or fencing_token != receipt.fencing_token:
            raise ValueError("stale parse attempt lease owner or fencing token")


def _with_hash(receipt: ParseAttemptLeaseReceipt) -> ParseAttemptLeaseReceipt:
    payload = receipt.model_dump(exclude={"receipt_hash"})
    return receipt.model_copy(update={"receipt_hash": _hash(payload)})


def _hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


__all__ = ["LeaseState", "ParseAttemptLeaseReceipt", "ParseAttemptLeaseRuntime"]
