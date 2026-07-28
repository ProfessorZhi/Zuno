from __future__ import annotations

from zuno.agent.runtime.planning import (
    DispatchItemStatus,
    ParallelRecoveryPlanner,
    PersistedStepRunSnapshot,
    RecoveryAction,
    ReplanBarrierStatus,
    StepRunStatus,
)


def _snapshot(
    step_id: str,
    status: StepRunStatus,
    *,
    item_status: DispatchItemStatus | None = DispatchItemStatus.PENDING_SEND,
    outbox_status: str | None = "pending",
    branch_result_id: str | None = None,
    barrier_id: str | None = None,
    barrier_status: ReplanBarrierStatus | None = None,
) -> PersistedStepRunSnapshot:
    return PersistedStepRunSnapshot(
        step_run_id=f"step-run:p17:recovery:{step_id}",
        dynamic_step_id=step_id,
        execution_epoch=2,
        status=status,
        dispatch_item_status=item_status,
        outbox_event_id=f"outbox:p17:recovery:{step_id}",
        outbox_status=outbox_status,
        branch_result_id=branch_result_id,
        barrier_id=barrier_id,
        barrier_status=barrier_status,
    )


def test_phase17_parallel_recovery_resends_committed_queued_outbox() -> None:
    plan = ParallelRecoveryPlanner().plan(
        run_id="run:p17:recovery",
        plan_version_id="plan-version:p17:recovery",
        execution_epoch=2,
        step_runs=(_snapshot("collect", StepRunStatus.QUEUED),),
    )

    assert plan.decisions[0].action is RecoveryAction.RESEND_OUTBOX
    assert plan.resend_outbox_event_ids == ("outbox:p17:recovery:collect",)


def test_phase17_parallel_recovery_resumes_claimed_or_running_without_duplicate_send() -> None:
    plan = ParallelRecoveryPlanner().plan(
        run_id="run:p17:recovery",
        plan_version_id="plan-version:p17:recovery",
        execution_epoch=2,
        step_runs=(
            _snapshot("a", StepRunStatus.CLAIMED, item_status=DispatchItemStatus.SENT, outbox_status="claimed"),
            _snapshot("b", StepRunStatus.RUNNING, item_status=DispatchItemStatus.SENT, outbox_status="claimed"),
        ),
    )

    assert [decision.action for decision in plan.decisions] == [
        RecoveryAction.RESUME_IN_FLIGHT,
        RecoveryAction.RESUME_IN_FLIGHT,
    ]


def test_phase17_parallel_recovery_reduces_already_persisted_branch_result() -> None:
    plan = ParallelRecoveryPlanner().plan(
        run_id="run:p17:recovery",
        plan_version_id="plan-version:p17:recovery",
        execution_epoch=2,
        step_runs=(
            _snapshot(
                "collect",
                StepRunStatus.CLAIMED,
                branch_result_id="branch-result:p17:recovery:collect",
            ),
        ),
    )

    assert plan.decisions[0].action is RecoveryAction.REDUCE_RESULT
    assert plan.decisions[0].branch_result_id == "branch-result:p17:recovery:collect"


def test_phase17_parallel_recovery_honors_replan_barrier_before_resend() -> None:
    plan = ParallelRecoveryPlanner().plan(
        run_id="run:p17:recovery",
        plan_version_id="plan-version:p17:recovery",
        execution_epoch=2,
        step_runs=(
            _snapshot(
                "collect",
                StepRunStatus.QUEUED,
                barrier_id="replan-barrier:p17:recovery",
                barrier_status=ReplanBarrierStatus.REQUESTED,
            ),
        ),
    )

    assert plan.decisions[0].action is RecoveryAction.HONOR_REPLAN_BARRIER
    assert plan.resend_outbox_event_ids == ()
