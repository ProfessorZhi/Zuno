from __future__ import annotations

from enum import StrEnum
import hashlib
import json

from pydantic import BaseModel, Field

from zuno.agent.runtime.planning.control_decision import (
    DynamicControlAction,
    JoinControlDecision,
)
from zuno.agent.runtime.planning.dispatch import StepRun, StepRunStatus


class ReplanBarrierValidationError(ValueError):
    pass


class ReplanBarrierStatus(StrEnum):
    REQUESTED = "REQUESTED"
    DRAINING = "DRAINING"
    READY_FOR_REPLAN = "READY_FOR_REPLAN"
    CANCELLED = "CANCELLED"


class StepRunBarrierAction(StrEnum):
    CANCEL_BEFORE_SEND = "CANCEL_BEFORE_SEND"
    REQUEST_CANCEL = "REQUEST_CANCEL"
    DRAIN_NON_INTERRUPTIBLE = "DRAIN_NON_INTERRUPTIBLE"
    MARK_OBSOLETE = "MARK_OBSOLETE"
    KEEP_TERMINAL = "KEEP_TERMINAL"


class StepRunBarrierDecision(BaseModel):
    step_run_id: str
    dynamic_step_id: str
    previous_status: StepRunStatus
    action: StepRunBarrierAction
    accepts_late_result: bool = False


class ReplanBarrierRequest(BaseModel):
    barrier_id: str
    run_id: str
    plan_id: str
    plan_version_id: str
    execution_epoch: int
    source_control_decision_id: str
    source_control_decision_hash: str
    status: ReplanBarrierStatus = ReplanBarrierStatus.REQUESTED
    freeze_new_dispatch: bool = True
    new_plan_version_required: bool = True
    retry_permitted: bool = False
    next_execution_epoch: int
    step_decisions: tuple[StepRunBarrierDecision, ...] = Field(default_factory=tuple)
    barrier_hash: str = ""

    def model_post_init(self, __context: object) -> None:
        if self.execution_epoch < 1:
            raise ReplanBarrierValidationError("execution_epoch must be positive")
        if self.next_execution_epoch <= self.execution_epoch:
            raise ReplanBarrierValidationError("next_execution_epoch must advance")
        if not self.freeze_new_dispatch:
            raise ReplanBarrierValidationError("replan barrier must freeze new dispatch")
        if not self.new_plan_version_required:
            raise ReplanBarrierValidationError("replan barrier must require new PlanVersion")
        if self.retry_permitted:
            raise ReplanBarrierValidationError("replan barrier must not permit branch retry")
        expected_hash = _canonical_hash(
            {
                "barrier_id": self.barrier_id,
                "run_id": self.run_id,
                "plan_id": self.plan_id,
                "plan_version_id": self.plan_version_id,
                "execution_epoch": self.execution_epoch,
                "source_control_decision_id": self.source_control_decision_id,
                "source_control_decision_hash": self.source_control_decision_hash,
                "status": self.status.value,
                "freeze_new_dispatch": self.freeze_new_dispatch,
                "new_plan_version_required": self.new_plan_version_required,
                "retry_permitted": self.retry_permitted,
                "next_execution_epoch": self.next_execution_epoch,
                "step_decisions": [
                    decision.model_dump(mode="json") for decision in self.step_decisions
                ],
            }
        )
        if not self.barrier_hash:
            self.barrier_hash = expected_hash
        elif self.barrier_hash != expected_hash:
            raise ReplanBarrierValidationError("ReplanBarrierRequest hash mismatch")


class ReplanBarrierBuilder:
    def build(
        self,
        *,
        run_id: str,
        control_decision: JoinControlDecision,
        execution_epoch: int,
        step_runs: tuple[StepRun, ...],
        non_interruptible_step_ids: tuple[str, ...] = (),
    ) -> ReplanBarrierRequest:
        if control_decision.action is not DynamicControlAction.REQUEST_REPLAN_BARRIER:
            raise ReplanBarrierValidationError("control decision does not request replan barrier")
        if not control_decision.replan_barrier_required:
            raise ReplanBarrierValidationError("control decision missing replan barrier requirement")
        if execution_epoch < 1:
            raise ReplanBarrierValidationError("execution_epoch must be positive")
        non_interruptible = set(non_interruptible_step_ids)
        step_decisions = tuple(
            StepRunBarrierDecision(
                step_run_id=step_run.step_run_id,
                dynamic_step_id=step_run.dynamic_step_id,
                previous_status=step_run.status,
                action=_barrier_action(step_run, non_interruptible),
                accepts_late_result=step_run.status
                in {StepRunStatus.CLAIMED, StepRunStatus.RUNNING},
            )
            for step_run in sorted(
                step_runs,
                key=lambda value: (value.dynamic_step_id, value.step_run_id),
            )
        )
        seed = _canonical_hash(
            {
                "run_id": run_id,
                "plan_id": control_decision.plan_id,
                "plan_version_id": control_decision.plan_version_id,
                "execution_epoch": execution_epoch,
                "source_control_decision_id": control_decision.decision_id,
            }
        )
        return ReplanBarrierRequest(
            barrier_id=f"replan-barrier:{seed}",
            run_id=run_id,
            plan_id=control_decision.plan_id,
            plan_version_id=control_decision.plan_version_id,
            execution_epoch=execution_epoch,
            source_control_decision_id=control_decision.decision_id,
            source_control_decision_hash=control_decision.decision_hash,
            next_execution_epoch=execution_epoch + 1,
            step_decisions=step_decisions,
        )


def _barrier_action(
    step_run: StepRun,
    non_interruptible_step_ids: set[str],
) -> StepRunBarrierAction:
    if step_run.status is StepRunStatus.QUEUED:
        return StepRunBarrierAction.CANCEL_BEFORE_SEND
    if step_run.status in {StepRunStatus.CLAIMED, StepRunStatus.RUNNING}:
        if step_run.dynamic_step_id in non_interruptible_step_ids:
            return StepRunBarrierAction.DRAIN_NON_INTERRUPTIBLE
        return StepRunBarrierAction.REQUEST_CANCEL
    if step_run.status in {
        StepRunStatus.SUCCEEDED,
        StepRunStatus.FAILED,
        StepRunStatus.CANCELLED,
    }:
        return StepRunBarrierAction.KEEP_TERMINAL
    return StepRunBarrierAction.MARK_OBSOLETE


def _canonical_hash(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


__all__ = [
    "ReplanBarrierBuilder",
    "ReplanBarrierRequest",
    "ReplanBarrierStatus",
    "ReplanBarrierValidationError",
    "StepRunBarrierAction",
    "StepRunBarrierDecision",
]
