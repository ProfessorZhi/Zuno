from __future__ import annotations

from enum import StrEnum
import hashlib
import json

from pydantic import BaseModel

from zuno.agent.runtime.planning.dispatch import StepRun, StepRunStatus


class BranchResultValidationError(ValueError):
    pass


class BranchResultStatus(StrEnum):
    ACCEPTED = "ACCEPTED"
    REJECTED_STALE_PLAN = "REJECTED_STALE_PLAN"
    REJECTED_STALE_EPOCH = "REJECTED_STALE_EPOCH"
    REJECTED_STALE_STEP_HASH = "REJECTED_STALE_STEP_HASH"
    REJECTED_OBSOLETE_STEP_RUN = "REJECTED_OBSOLETE_STEP_RUN"
    REJECTED_INLINE_PAYLOAD = "REJECTED_INLINE_PAYLOAD"


class BranchResultSubmission(BaseModel):
    branch_result_id: str
    step_run_id: str
    run_id: str
    plan_version_id: str
    dynamic_step_id: str
    execution_epoch: int
    attempt_no: int
    step_hash: str
    result_ref: str
    result_hash: str
    producer_ref: str


class BranchResultRef(BaseModel):
    branch_result_id: str
    step_run_id: str
    run_id: str
    plan_version_id: str
    dynamic_step_id: str
    execution_epoch: int
    attempt_no: int
    result_ref: str
    result_hash: str
    producer_ref: str
    ref_hash: str = ""

    def model_post_init(self, __context: object) -> None:
        if not self.result_ref.startswith("object://"):
            raise BranchResultValidationError("BranchResultRef must point to object storage")
        expected_hash = _canonical_hash(
            {
                "branch_result_id": self.branch_result_id,
                "step_run_id": self.step_run_id,
                "run_id": self.run_id,
                "plan_version_id": self.plan_version_id,
                "dynamic_step_id": self.dynamic_step_id,
                "execution_epoch": self.execution_epoch,
                "attempt_no": self.attempt_no,
                "result_ref": self.result_ref,
                "result_hash": self.result_hash,
                "producer_ref": self.producer_ref,
            }
        )
        if not self.ref_hash:
            self.ref_hash = expected_hash
        elif self.ref_hash != expected_hash:
            raise BranchResultValidationError("BranchResultRef hash mismatch")


class BranchResultDecision(BaseModel):
    status: BranchResultStatus
    branch_result: BranchResultRef | None = None
    reason: str = ""


class BranchResultFencer:
    ACCEPTABLE_STEP_STATUSES = {
        StepRunStatus.CLAIMED,
        StepRunStatus.RUNNING,
        StepRunStatus.QUEUED,
    }

    def accept(
        self,
        submission: BranchResultSubmission,
        *,
        step_run: StepRun,
        active_plan_version_id: str,
        active_execution_epoch: int,
    ) -> BranchResultDecision:
        if submission.plan_version_id != active_plan_version_id:
            return BranchResultDecision(
                status=BranchResultStatus.REJECTED_STALE_PLAN,
                reason="branch result plan_version_id is no longer active",
            )
        if submission.execution_epoch != active_execution_epoch or submission.execution_epoch != step_run.execution_epoch:
            return BranchResultDecision(
                status=BranchResultStatus.REJECTED_STALE_EPOCH,
                reason="branch result execution epoch is stale",
            )
        if submission.step_hash != step_run.step_hash:
            return BranchResultDecision(
                status=BranchResultStatus.REJECTED_STALE_STEP_HASH,
                reason="branch result step hash does not match committed StepRun",
            )
        if step_run.status not in self.ACCEPTABLE_STEP_STATUSES:
            return BranchResultDecision(
                status=BranchResultStatus.REJECTED_OBSOLETE_STEP_RUN,
                reason="branch result arrived after StepRun terminal or obsolete state",
            )
        if not submission.result_ref.startswith("object://"):
            return BranchResultDecision(
                status=BranchResultStatus.REJECTED_INLINE_PAYLOAD,
                reason="branch result must reference immutable object storage",
            )
        return BranchResultDecision(
            status=BranchResultStatus.ACCEPTED,
            branch_result=BranchResultRef(
                branch_result_id=submission.branch_result_id,
                step_run_id=submission.step_run_id,
                run_id=submission.run_id,
                plan_version_id=submission.plan_version_id,
                dynamic_step_id=submission.dynamic_step_id,
                execution_epoch=submission.execution_epoch,
                attempt_no=submission.attempt_no,
                result_ref=submission.result_ref,
                result_hash=submission.result_hash,
                producer_ref=submission.producer_ref,
            ),
        )


def _canonical_hash(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


__all__ = [
    "BranchResultDecision",
    "BranchResultFencer",
    "BranchResultRef",
    "BranchResultStatus",
    "BranchResultSubmission",
    "BranchResultValidationError",
]
