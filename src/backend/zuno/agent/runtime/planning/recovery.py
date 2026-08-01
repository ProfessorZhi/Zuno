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
    RECONCILE_CHECKPOINT = "RECONCILE_CHECKPOINT"
    REJECT_LATE_RESULT = "REJECT_LATE_RESULT"


class CrashInjectionPoint(StrEnum):
    DOMAIN_COMMIT_BEFORE_CHECKPOINT = "DOMAIN_COMMIT_BEFORE_CHECKPOINT"
    DISPATCH_COMMIT_BEFORE_SEND = "DISPATCH_COMMIT_BEFORE_SEND"
    RESULT_BEFORE_REDUCER = "RESULT_BEFORE_REDUCER"
    PUBLISHER_RESTART = "PUBLISHER_RESTART"
    CONSUMER_RESTART = "CONSUMER_RESTART"
    LATE_BRANCH_RESULT = "LATE_BRANCH_RESULT"


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


class CrashScenarioSnapshot(BaseModel):
    scenario_id: str
    injection_point: CrashInjectionPoint
    domain_generation: int
    checkpoint_generation: int
    active_execution_epoch: int
    incoming_execution_epoch: int | None = None
    persisted_step_runs: tuple[PersistedStepRunSnapshot, ...] = Field(default_factory=tuple)
    external_effect_keys: tuple[str, ...] = Field(default_factory=tuple)


class CrashRecoveryVerdict(BaseModel):
    scenario_id: str
    injection_point: CrashInjectionPoint
    decisions: tuple[RecoveryDecision, ...]
    checkpoint_reconciled: bool
    duplicate_effect_suppressed: bool
    late_result_rejected: bool
    terminal_state_preserved: bool
    verdict: str
    evidence_ref: str


class Phase21CrashRecoveryMatrix:
    def evaluate(
        self,
        *,
        run_id: str,
        plan_version_id: str,
        scenarios: tuple[CrashScenarioSnapshot, ...],
    ) -> tuple[CrashRecoveryVerdict, ...]:
        return tuple(
            self._evaluate_one(
                run_id=run_id,
                plan_version_id=plan_version_id,
                scenario=scenario,
            )
            for scenario in scenarios
        )

    def _evaluate_one(
        self,
        *,
        run_id: str,
        plan_version_id: str,
        scenario: CrashScenarioSnapshot,
    ) -> CrashRecoveryVerdict:
        decisions = list(
            ParallelRecoveryPlanner()
            .plan(
                run_id=run_id,
                plan_version_id=plan_version_id,
                execution_epoch=scenario.active_execution_epoch,
                step_runs=scenario.persisted_step_runs,
            )
            .decisions
        )
        checkpoint_reconciled = scenario.domain_generation == scenario.checkpoint_generation
        if scenario.domain_generation > scenario.checkpoint_generation:
            checkpoint_reconciled = True
            decisions.append(
                RecoveryDecision(
                    step_run_id=f"run:{run_id}",
                    dynamic_step_id="checkpoint",
                    action=RecoveryAction.RECONCILE_CHECKPOINT,
                    reason="domain generation is ahead of checkpoint generation after crash",
                )
            )

        late_result_rejected = False
        if (
            scenario.incoming_execution_epoch is not None
            and scenario.incoming_execution_epoch < scenario.active_execution_epoch
        ):
            late_result_rejected = True
            decisions.append(
                RecoveryDecision(
                    step_run_id=f"run:{run_id}",
                    dynamic_step_id="branch-result",
                    action=RecoveryAction.REJECT_LATE_RESULT,
                    reason="incoming branch result is fenced by a stale execution epoch",
                )
            )

        duplicate_effect_suppressed = len(set(scenario.external_effect_keys)) == len(scenario.external_effect_keys)
        terminal_state_preserved = all(
            decision.action is not RecoveryAction.RESEND_OUTBOX
            for decision in decisions
            if decision.branch_result_id
        )
        verdict = (
            "passed"
            if checkpoint_reconciled and duplicate_effect_suppressed and terminal_state_preserved
            else "failed"
        )
        return CrashRecoveryVerdict(
            scenario_id=scenario.scenario_id,
            injection_point=scenario.injection_point,
            decisions=tuple(decisions),
            checkpoint_reconciled=checkpoint_reconciled,
            duplicate_effect_suppressed=duplicate_effect_suppressed,
            late_result_rejected=late_result_rejected,
            terminal_state_preserved=terminal_state_preserved,
            verdict=verdict,
            evidence_ref=f"phase21-crash-matrix:{run_id}:{scenario.scenario_id}",
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
    "CrashInjectionPoint",
    "CrashRecoveryVerdict",
    "CrashScenarioSnapshot",
    "ParallelRecoveryPlan",
    "ParallelRecoveryPlanner",
    "Phase21CrashRecoveryMatrix",
    "PersistedStepRunSnapshot",
    "RecoveryAction",
    "RecoveryDecision",
]
