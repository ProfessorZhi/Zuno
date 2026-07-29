from __future__ import annotations

from zuno.agent.runtime.planning.recovery import (
    CrashInjectionPoint,
    CrashScenarioSnapshot,
    ParallelRecoveryPlanner,
    PersistedStepRunSnapshot,
    Phase21CrashRecoveryMatrix,
    RecoveryAction,
)
from zuno.agent.runtime.planning.dispatch import DispatchItemStatus, StepRunStatus


def _snapshot(
    step_id: str,
    status: StepRunStatus,
    *,
    outbox_status: str | None = None,
    branch_result_id: str | None = None,
) -> PersistedStepRunSnapshot:
    return PersistedStepRunSnapshot(
        step_run_id=f"step-run:run:p21:{step_id}:epoch:2:attempt:1",
        dynamic_step_id=step_id,
        execution_epoch=2,
        status=status,
        dispatch_item_status=DispatchItemStatus.PENDING_SEND,
        outbox_event_id=f"outbox:step-run:run:p21:{step_id}:epoch:2:attempt:1",
        outbox_status=outbox_status,
        branch_result_id=branch_result_id,
    )


def test_phase21_crash_matrix_reconciles_domain_checkpoint_and_resends_committed_outbox() -> None:
    verdict = Phase21CrashRecoveryMatrix().evaluate(
        run_id="run:p21",
        plan_version_id="plan-version:p21",
        scenarios=(
            CrashScenarioSnapshot(
                scenario_id="domain_commit_before_checkpoint",
                injection_point=CrashInjectionPoint.DOMAIN_COMMIT_BEFORE_CHECKPOINT,
                domain_generation=8,
                checkpoint_generation=7,
                active_execution_epoch=2,
                persisted_step_runs=(
                    _snapshot("collect", StepRunStatus.QUEUED, outbox_status="pending"),
                ),
                external_effect_keys=("effect:email:123",),
            ),
        ),
    )[0]

    assert verdict.verdict == "passed"
    assert verdict.checkpoint_reconciled is True
    assert verdict.duplicate_effect_suppressed is True
    assert [decision.action for decision in verdict.decisions] == [
        RecoveryAction.RESEND_OUTBOX,
        RecoveryAction.RECONCILE_CHECKPOINT,
    ]
    assert verdict.decisions[0].outbox_event_id == "outbox:step-run:run:p21:collect:epoch:2:attempt:1"
    assert verdict.evidence_ref == "phase21-crash-matrix:run:p21:domain_commit_before_checkpoint"


def test_phase21_crash_matrix_reduces_persisted_result_and_rejects_late_epoch() -> None:
    verdict = Phase21CrashRecoveryMatrix().evaluate(
        run_id="run:p21",
        plan_version_id="plan-version:p21",
        scenarios=(
            CrashScenarioSnapshot(
                scenario_id="result_before_reducer",
                injection_point=CrashInjectionPoint.RESULT_BEFORE_REDUCER,
                domain_generation=9,
                checkpoint_generation=9,
                active_execution_epoch=3,
                incoming_execution_epoch=2,
                persisted_step_runs=(
                    _snapshot(
                        "summarize",
                        StepRunStatus.RUNNING,
                        outbox_status="claimed",
                        branch_result_id="branch-result:run:p21:summarize:epoch:3",
                    ),
                ),
            ),
        ),
    )[0]

    assert verdict.verdict == "passed"
    assert verdict.late_result_rejected is True
    assert [decision.action for decision in verdict.decisions] == [
        RecoveryAction.REDUCE_RESULT,
        RecoveryAction.REJECT_LATE_RESULT,
    ]
    assert verdict.terminal_state_preserved is True


def test_phase17_recovery_planner_still_honors_replan_barrier_without_phase21_bypass() -> None:
    plan = ParallelRecoveryPlanner().plan(
        run_id="run:p21",
        plan_version_id="plan-version:p21",
        execution_epoch=2,
        step_runs=(
            _snapshot("collect", StepRunStatus.QUEUED, outbox_status="pending"),
        ),
    )

    assert plan.resend_outbox_event_ids == ("outbox:step-run:run:p21:collect:epoch:2:attempt:1",)
