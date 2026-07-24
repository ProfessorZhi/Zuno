from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import time
from typing import Any, Literal, Protocol

from pydantic import BaseModel, Field

from .contracts import CanonicalDocumentIR, ParseJobSnapshot


QualityVerdict = Literal["PASS", "BLOCK", "REVIEW", "FALLBACK"]
ReviewDecisionStatus = Literal["pending", "approved", "rejected", "expired", "cancelled"]


class QualityMetric(BaseModel):
    name: str
    value: float
    threshold: float
    passed: bool
    reason: str = ""


class QualityGateResult(BaseModel):
    quality_decision_id: str
    parse_snapshot_id: str
    verdict: QualityVerdict
    metrics: list[QualityMetric] = Field(default_factory=list)
    review_task_id: str | None = None
    decision_hash: str


class ReviewTask(BaseModel):
    review_task_id: str
    parse_snapshot_id: str
    document_version_id: str
    workspace_id: str
    reviewer_principal_id: str | None = None
    reviewer_scope: str
    security_decision_ref: str | None = None
    security_epoch_ref: str
    idempotency_key: str | None = None
    trace_id: str | None = None
    audit_ref: str | None = None
    status: ReviewDecisionStatus = "pending"
    expires_at: float
    reason: str
    decision_hash: str


class ReviewDecisionReceipt(BaseModel):
    review_task_id: str
    decision_id: str
    status: ReviewDecisionStatus
    reviewer_id: str
    reviewer_scope: str
    security_epoch_ref: str
    decision_hash: str
    duplicate: bool = False
    reason: str = ""
    decided_at: float = Field(default_factory=time.time)


class ReviewDecisionAuthorizationReceipt(BaseModel):
    review_task_id: str
    reviewer_id: str
    reviewer_scope: str
    security_epoch_ref: str
    authorized: bool
    reason: str
    authorization_ref: str


class ReviewExpirationSweepReceipt(BaseModel):
    sweep_id: str
    now: float
    expired_task_ids: list[str] = Field(default_factory=list)
    skipped_task_ids: list[str] = Field(default_factory=list)
    decision_receipts: list[ReviewDecisionReceipt] = Field(default_factory=list)
    sweep_hash: str


class ReviewDecisionAuthorizationPort(Protocol):
    def authorize_review_decision(
        self,
        *,
        task: ReviewTask,
        reviewer_id: str,
        reviewer_scope: str,
        security_epoch_ref: str,
    ) -> ReviewDecisionAuthorizationReceipt: ...


@dataclass(frozen=True, slots=True)
class StaticReviewDecisionAuthorizationPort:
    revoked_reviewer_ids: frozenset[str] = frozenset()
    revoked_security_decision_refs: frozenset[str] = frozenset()

    def authorize_review_decision(
        self,
        *,
        task: ReviewTask,
        reviewer_id: str,
        reviewer_scope: str,
        security_epoch_ref: str,
    ) -> ReviewDecisionAuthorizationReceipt:
        authorized = True
        reason = "review_authorization_accepted"
        if task.reviewer_principal_id is not None and reviewer_id != task.reviewer_principal_id:
            authorized = False
            reason = "reviewer_principal_mismatch"
        elif reviewer_id in self.revoked_reviewer_ids:
            authorized = False
            reason = "reviewer_authorization_revoked"
        elif reviewer_scope != task.reviewer_scope:
            authorized = False
            reason = "review_scope_mismatch"
        elif security_epoch_ref != task.security_epoch_ref:
            authorized = False
            reason = "review_security_epoch_mismatch"
        elif task.security_decision_ref in self.revoked_security_decision_refs:
            authorized = False
            reason = "review_security_decision_revoked"
        return ReviewDecisionAuthorizationReceipt(
            review_task_id=task.review_task_id,
            reviewer_id=reviewer_id,
            reviewer_scope=reviewer_scope,
            security_epoch_ref=security_epoch_ref,
            authorized=authorized,
            reason=reason,
            authorization_ref=f"review-auth:{task.review_task_id}:{reviewer_id}:{security_epoch_ref}",
        )


@dataclass
class HumanReviewRuntime:
    review_ttl_seconds: int = 3600
    min_confidence: float = 0.9
    authorization_port: ReviewDecisionAuthorizationPort = field(
        default_factory=StaticReviewDecisionAuthorizationPort
    )

    def evaluate(
        self,
        *,
        document: CanonicalDocumentIR,
        parse_snapshot: ParseJobSnapshot,
        security_epoch_ref: str,
        reviewer_scope: str = "workspace_reviewer",
        reviewer_principal_id: str | None = None,
        security_decision_ref: str | None = None,
        idempotency_key: str | None = None,
        trace_id: str | None = None,
        audit_ref: str | None = None,
    ) -> tuple[QualityGateResult, ReviewTask | None]:
        metrics = self._metrics(document)
        requires_review = any(
            bool(block.metadata.get("requires_human_review"))
            for block in document.blocks
        )
        low_confidence = any(not metric.passed for metric in metrics)
        verdict: QualityVerdict = "REVIEW" if requires_review or low_confidence else "PASS"
        review_task = None
        review_task_id = None
        if verdict == "REVIEW":
            review_task_id = f"review_{parse_snapshot.job_id}"
            review_task = ReviewTask(
                review_task_id=review_task_id,
                parse_snapshot_id=parse_snapshot.job_id,
                document_version_id=document.metadata.document_version_id,
                workspace_id=document.metadata.workspace_id,
                reviewer_principal_id=reviewer_principal_id,
                reviewer_scope=reviewer_scope,
                security_decision_ref=security_decision_ref,
                security_epoch_ref=security_epoch_ref,
                idempotency_key=idempotency_key,
                trace_id=trace_id,
                audit_ref=audit_ref,
                expires_at=time.time() + self.review_ttl_seconds,
                reason="quality_review_required",
                decision_hash=_hash(
                    {
                        "review_task_id": review_task_id,
                        "parse_snapshot_id": parse_snapshot.job_id,
                        "document_version_id": document.metadata.document_version_id,
                        "reviewer_principal_id": reviewer_principal_id,
                        "reviewer_scope": reviewer_scope,
                        "security_decision_ref": security_decision_ref,
                        "security_epoch_ref": security_epoch_ref,
                        "idempotency_key": idempotency_key,
                        "trace_id": trace_id,
                        "audit_ref": audit_ref,
                        "status": "pending",
                    }
                ),
            )
        decision_id = f"quality_{parse_snapshot.job_id}"
        decision_hash = _hash(
            {
                "quality_decision_id": decision_id,
                "parse_snapshot_id": parse_snapshot.job_id,
                "verdict": verdict,
                "metrics": [metric.model_dump() for metric in metrics],
                "review_task_id": review_task_id,
                "security_epoch_ref": security_epoch_ref,
            }
        )
        return (
            QualityGateResult(
                quality_decision_id=decision_id,
                parse_snapshot_id=parse_snapshot.job_id,
                verdict=verdict,
                metrics=metrics,
                review_task_id=review_task_id,
                decision_hash=decision_hash,
            ),
            review_task,
        )

    def decide(
        self,
        *,
        task: ReviewTask,
        reviewer_id: str,
        reviewer_scope: str,
        status: Literal["approved", "rejected", "cancelled"],
        security_epoch_ref: str,
        existing_receipt: ReviewDecisionReceipt | None = None,
        now: float | None = None,
    ) -> ReviewDecisionReceipt:
        requested_status: ReviewDecisionStatus = status
        authorization = self.authorization_port.authorize_review_decision(
            task=task,
            reviewer_id=reviewer_id,
            reviewer_scope=reviewer_scope,
            security_epoch_ref=security_epoch_ref,
        )
        if status == "approved" and not authorization.authorized:
            requested_status = "rejected"
        current_time = time.time() if now is None else now
        final_status: ReviewDecisionStatus = (
            "expired" if current_time > task.expires_at else requested_status
        )
        decision_id = f"review_decision_{task.review_task_id}"
        requested_decision_hashes = {
            _hash(
                {
                    "review_task_id": task.review_task_id,
                    "decision_id": decision_id,
                    "status": requested_status,
                    "reviewer_id": reviewer_id,
                    "reviewer_scope": reviewer_scope,
                    "security_epoch_ref": security_epoch_ref,
                }
            ),
            _hash(
                {
                    "review_task_id": task.review_task_id,
                    "decision_id": decision_id,
                    "status": final_status,
                    "reviewer_id": reviewer_id,
                    "reviewer_scope": reviewer_scope,
                    "security_epoch_ref": security_epoch_ref,
                }
            ),
        }
        if existing_receipt is not None:
            if (
                existing_receipt.review_task_id != task.review_task_id
                or existing_receipt.decision_hash not in requested_decision_hashes
            ):
                raise ValueError(f"conflicting review decision: {task.review_task_id}")
            return existing_receipt.model_copy(update={"duplicate": True})
        decision_hash = _hash(
            {
                "review_task_id": task.review_task_id,
                "decision_id": decision_id,
                "status": final_status,
                "reviewer_id": reviewer_id,
                "reviewer_scope": reviewer_scope,
                "security_epoch_ref": security_epoch_ref,
            }
        )
        return ReviewDecisionReceipt(
            review_task_id=task.review_task_id,
            decision_id=decision_id,
            status=final_status,
            reviewer_id=reviewer_id,
            reviewer_scope=reviewer_scope,
            security_epoch_ref=security_epoch_ref,
            decision_hash=decision_hash,
            reason=authorization.reason if not authorization.authorized else "review_decision_recorded",
            decided_at=current_time,
        )

    def expire_pending_reviews(
        self,
        *,
        tasks: list[ReviewTask],
        existing_receipts: dict[str, ReviewDecisionReceipt] | None = None,
        now: float | None = None,
    ) -> ReviewExpirationSweepReceipt:
        current_time = time.time() if now is None else now
        existing = existing_receipts or {}
        expired_task_ids: list[str] = []
        skipped_task_ids: list[str] = []
        receipts: list[ReviewDecisionReceipt] = []
        for task in tasks:
            if task.status != "pending" or task.review_task_id in existing:
                skipped_task_ids.append(task.review_task_id)
                continue
            if current_time <= task.expires_at:
                skipped_task_ids.append(task.review_task_id)
                continue
            receipt = self.decide(
                task=task,
                reviewer_id="system:review-expiration",
                reviewer_scope=task.reviewer_scope,
                status="cancelled",
                security_epoch_ref=task.security_epoch_ref,
                now=current_time,
            )
            expired_task_ids.append(task.review_task_id)
            receipts.append(receipt)
        sweep_id = f"review_expiration_sweep_{int(current_time)}_{len(expired_task_ids)}"
        sweep_hash = _hash(
            {
                "sweep_id": sweep_id,
                "now": current_time,
                "expired_task_ids": expired_task_ids,
                "skipped_task_ids": skipped_task_ids,
                "decision_hashes": [receipt.decision_hash for receipt in receipts],
            }
        )
        return ReviewExpirationSweepReceipt(
            sweep_id=sweep_id,
            now=current_time,
            expired_task_ids=expired_task_ids,
            skipped_task_ids=skipped_task_ids,
            decision_receipts=receipts,
            sweep_hash=sweep_hash,
        )

    @classmethod
    def can_publish_snapshot(
        cls,
        *,
        gate: QualityGateResult,
        receipt: ReviewDecisionReceipt | None = None,
    ) -> bool:
        if gate.verdict == "PASS":
            return True
        if gate.verdict == "REVIEW":
            return receipt is not None and receipt.status == "approved"
        return False

    def _metrics(self, document: CanonicalDocumentIR) -> list[QualityMetric]:
        confidences = [block.confidence for block in document.blocks] or [0.0]
        min_confidence = min(confidences)
        return [
            QualityMetric(
                name="min_block_confidence",
                value=min_confidence,
                threshold=self.min_confidence,
                passed=min_confidence >= self.min_confidence,
                reason="minimum parser block confidence",
            )
        ]


def _hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


__all__ = [
    "HumanReviewRuntime",
    "QualityGateResult",
    "QualityMetric",
    "ReviewDecisionReceipt",
    "ReviewDecisionAuthorizationPort",
    "ReviewDecisionAuthorizationReceipt",
    "StaticReviewDecisionAuthorizationPort",
    "ReviewExpirationSweepReceipt",
    "ReviewTask",
]
