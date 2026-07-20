from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import time
from typing import Any, Literal

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
    reviewer_scope: str
    security_epoch_ref: str
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


@dataclass
class HumanReviewRuntime:
    review_ttl_seconds: int = 3600
    min_confidence: float = 0.9

    def evaluate(
        self,
        *,
        document: CanonicalDocumentIR,
        parse_snapshot: ParseJobSnapshot,
        security_epoch_ref: str,
        reviewer_scope: str = "workspace_reviewer",
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
                reviewer_scope=reviewer_scope,
                security_epoch_ref=security_epoch_ref,
                expires_at=time.time() + self.review_ttl_seconds,
                reason="quality_review_required",
                decision_hash=_hash(
                    {
                        "review_task_id": review_task_id,
                        "parse_snapshot_id": parse_snapshot.job_id,
                        "document_version_id": document.metadata.document_version_id,
                        "security_epoch_ref": security_epoch_ref,
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
        if existing_receipt is not None:
            return existing_receipt.model_copy(update={"duplicate": True})
        current_time = time.time() if now is None else now
        final_status: ReviewDecisionStatus = "expired" if current_time > task.expires_at else status
        if reviewer_scope != task.reviewer_scope:
            final_status = "rejected"
        if security_epoch_ref != task.security_epoch_ref:
            final_status = "rejected"
        decision_id = f"review_decision_{task.review_task_id}"
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
            reason="review_decision_recorded",
            decided_at=current_time,
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
    "ReviewTask",
]
