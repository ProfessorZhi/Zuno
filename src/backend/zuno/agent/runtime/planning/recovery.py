from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from zuno.agent.runtime.planning.dispatch import DispatchItemStatus, StepRunStatus
from zuno.agent.runtime.planning.replan_barrier import ReplanBarrierStatus


class RecoveryAction(StrEnum):
    RESEND_OUTBOX = "RESEND_OUTBOX"
    RESUME_IN_FLIGHT = "RESUME_IN_FLIGHT"
    REDUCE_RESULT = "REDUCE_RESULT"
    WAIT_FOR_BRANCH = "WAIT_FOR_BRANCH"
    HONOR_REPLAN_BARRIER = "HONOR_REPLAN_BARRIER"


class PersistedStepRunSnapshot(BaseModel):
    step_run_id: str
    dynamic_step_id: str
    execution_epoch: int
    status: StepRunStatus
    dispatch_item_status: DispatchItemStatus | None = None
    outbox_event_id: str | None = None
    outbox_status: str | None = None
    branch_result_id: str | None = None
    barrier_id: str | None = None
    barrier_status: ReplanBarrierStatus | None = None


class RecoveryDecision(BaseModel):
    step_run_id: str
    dynamic_step_id: str
    action: RecoveryAction
    reason: str
    outbox_event_id: str | None = None
    branch_result_id: str | None = None
    barrier_id: str | None = None


class ParallelRecoveryPlan(BaseModel):
    run_id: str
    plan_version_id: str
    execution_epoch: int
    decisions: tuple[RecoveryDecision, ...] = Field(default_factory=tuple)

    @property
    def resend_outbox_event_ids(self) -> tuple[str, ...]:
        return tuple(
            decision.outbox_event_id
            for decision in self.decisions
            if decision.action is RecoveryAction.RESEND_OUTBOX and decision.outbox_event_id
        )


class ParallelRecoveryPlanner:
    def plan(
        self,
        *,
        run_id: str,
        plan_version_id: str,
        execution_epoch: int,
        step_runs: tuple[PersistedStepRunSnapshot, ...],
    ) -> ParallelRecoveryPlan:
        decisions = tuple(
            _decision(snapshot)
            for snapshot in sorted(step_runs, key=lambda item: (item.dynamic_step_id, item.step_run_id))
        )
        return ParallelRecoveryPlan(
            run_id=run_id,
            plan_version_id=plan_version_id,
            execution_epoch=execution_epoch,
            decisions=decisions,
        )


def _decision(snapshot: PersistedStepRunSnapshot) -> RecoveryDecision:
    if snapshot.barrier_id and snapshot.barrier_status in {
        ReplanBarrierStatus.REQUESTED,
        ReplanBarrierStatus.DRAINING,
        ReplanBarrierStatus.READY_FOR_REPLAN,
    }:
        return RecoveryDecision(
            step_run_id=snapshot.step_run_id,
            dynamic_step_id=snapshot.dynamic_step_id,
            action=RecoveryAction.HONOR_REPLAN_BARRIER,
            reason="active replan barrier freezes dispatch recovery",
            barrier_id=snapshot.barrier_id,
        )
    if snapshot.branch_result_id:
        return RecoveryDecision(
            step_run_id=snapshot.step_run_id,
            dynamic_step_id=snapshot.dynamic_step_id,
            action=RecoveryAction.REDUCE_RESULT,
            reason="branch result already persisted",
            branch_result_id=snapshot.branch_result_id,
        )
    if snapshot.status is StepRunStatus.QUEUED and snapshot.outbox_status in {"pending", "claimed"}:
        return RecoveryDecision(
            step_run_id=snapshot.step_run_id,
            dynamic_step_id=snapshot.dynamic_step_id,
            action=RecoveryAction.RESEND_OUTBOX,
            reason="committed step run has replayable dispatch outbox",
            outbox_event_id=snapshot.outbox_event_id,
        )
    if snapshot.status in {StepRunStatus.CLAIMED, StepRunStatus.RUNNING}:
        return RecoveryDecision(
            step_run_id=snapshot.step_run_id,
            dynamic_step_id=snapshot.dynamic_step_id,
            action=RecoveryAction.RESUME_IN_FLIGHT,
            reason="step run was claimed before restart",
            outbox_event_id=snapshot.outbox_event_id,
        )
    return RecoveryDecision(
        step_run_id=snapshot.step_run_id,
        dynamic_step_id=snapshot.dynamic_step_id,
        action=RecoveryAction.WAIT_FOR_BRANCH,
        reason="terminal or non-replayable state needs reducer or operator handling",
    )


__all__ = [
    "ParallelRecoveryPlan",
    "ParallelRecoveryPlanner",
    "PersistedStepRunSnapshot",
    "RecoveryAction",
    "RecoveryDecision",
]
