from __future__ import annotations

import pytest

from zuno.agent.runtime.planning import (
    BranchReductionInput,
    BranchResultReducer,
    BranchResultRef,
    BranchTerminalStatus,
    DynamicPlanJoinPolicy,
    JoinControlDecisionEngine,
    ReplanBarrierBuilder,
    ReplanBarrierExecutor,
    ReplanBarrierRequest,
    ReplanBarrierValidationError,
    StepRun,
    StepRunBarrierAction,
    StepRunStatus,
)


def _result(step_id: str, *, result_hash: str = "e") -> BranchResultRef:
    return BranchResultRef(
        branch_result_id=f"branch-result:p17:barrier:{step_id}",
        step_run_id=f"step-run:p17:barrier:{step_id}",
        run_id="run:p17:barrier",
        plan_version_id="plan-version:p17:barrier",
        dynamic_step_id=step_id,
        execution_epoch=3,
        attempt_no=1,
        result_ref=f"object://agent-results/p17/barrier/{step_id}.json",
        result_hash=result_hash * 64,
        producer_ref=f"langgraph-send:{step_id}",
    )


def _control_decision():
    outcome = BranchResultReducer().reduce(
        plan_id="plan:p17:barrier",
        plan_version_id="plan-version:p17:barrier",
        join_policy=DynamicPlanJoinPolicy.FAIL_FAST,
        expected_branch_count=3,
        branch_results=(
            BranchReductionInput(
                branch_result=_result("a"),
                terminal_status=BranchTerminalStatus.SUCCEEDED,
            ),
            BranchReductionInput(
                branch_result=_result("b"),
                terminal_status=BranchTerminalStatus.FAILED,
            ),
        ),
    )
    return JoinControlDecisionEngine().decide(outcome=outcome)


def _step_run(step_id: str, status: StepRunStatus) -> StepRun:
    return StepRun(
        step_run_id=f"step-run:p17:barrier:{step_id}",
        run_id="run:p17:barrier",
        plan_version_id="plan-version:p17:barrier",
        dynamic_step_id=step_id,
        execution_epoch=3,
        status=status,
        step_hash="f" * 64,
    )


def test_phase17_replan_barrier_freezes_dispatch_and_advances_epoch() -> None:
    barrier = ReplanBarrierBuilder().build(
        run_id="run:p17:barrier",
        control_decision=_control_decision(),
        execution_epoch=3,
        step_runs=(_step_run("a", StepRunStatus.QUEUED),),
    )

    assert barrier.freeze_new_dispatch is True
    assert barrier.new_plan_version_required is True
    assert barrier.retry_permitted is False
    assert barrier.execution_epoch == 3
    assert barrier.next_execution_epoch == 4
    assert barrier.source_control_decision_id.startswith("join-control:")
    assert barrier.barrier_id.startswith("replan-barrier:")


def test_phase17_replan_barrier_assigns_cancel_drain_and_terminal_actions() -> None:
    barrier = ReplanBarrierBuilder().build(
        run_id="run:p17:barrier",
        control_decision=_control_decision(),
        execution_epoch=3,
        step_runs=(
            _step_run("queued", StepRunStatus.QUEUED),
            _step_run("running", StepRunStatus.RUNNING),
            _step_run("claimed", StepRunStatus.CLAIMED),
            _step_run("done", StepRunStatus.SUCCEEDED),
            _step_run("old", StepRunStatus.OBSOLETE),
        ),
        non_interruptible_step_ids=("claimed",),
    )

    actions = {
        decision.dynamic_step_id: decision.action
        for decision in barrier.step_decisions
    }

    assert actions == {
        "claimed": StepRunBarrierAction.DRAIN_NON_INTERRUPTIBLE,
        "done": StepRunBarrierAction.KEEP_TERMINAL,
        "old": StepRunBarrierAction.MARK_OBSOLETE,
        "queued": StepRunBarrierAction.CANCEL_BEFORE_SEND,
        "running": StepRunBarrierAction.REQUEST_CANCEL,
    }


def test_phase17_replan_barrier_accepts_late_results_only_for_in_flight_runs() -> None:
    barrier = ReplanBarrierBuilder().build(
        run_id="run:p17:barrier",
        control_decision=_control_decision(),
        execution_epoch=3,
        step_runs=(
            _step_run("queued", StepRunStatus.QUEUED),
            _step_run("running", StepRunStatus.RUNNING),
            _step_run("claimed", StepRunStatus.CLAIMED),
            _step_run("done", StepRunStatus.SUCCEEDED),
        ),
    )

    late_result_policy = {
        decision.dynamic_step_id: decision.accepts_late_result
        for decision in barrier.step_decisions
    }

    assert late_result_policy == {
        "claimed": True,
        "done": False,
        "queued": False,
        "running": True,
    }


def test_phase17_replan_barrier_requires_replan_control_decision() -> None:
    decision = _control_decision().model_copy(update={"replan_barrier_required": False})

    with pytest.raises(ReplanBarrierValidationError, match="missing replan barrier"):
        ReplanBarrierBuilder().build(
            run_id="run:p17:barrier",
            control_decision=decision,
            execution_epoch=3,
            step_runs=(_step_run("a", StepRunStatus.QUEUED),),
        )


def test_phase17_replan_barrier_hash_fences_mutation() -> None:
    barrier = ReplanBarrierBuilder().build(
        run_id="run:p17:barrier",
        control_decision=_control_decision(),
        execution_epoch=3,
        step_runs=(_step_run("a", StepRunStatus.QUEUED),),
    )

    with pytest.raises(ValueError, match="hash mismatch"):
        ReplanBarrierRequest(
            **{
                **barrier.model_dump(),
                "status": "READY_FOR_REPLAN",
                "barrier_hash": barrier.barrier_hash,
            }
        )


def test_phase17_replan_barrier_executor_marks_ready_when_no_in_flight_drain_remains() -> None:
    barrier = ReplanBarrierBuilder().build(
        run_id="run:p17:barrier",
        control_decision=_control_decision(),
        execution_epoch=3,
        step_runs=(
            _step_run("queued", StepRunStatus.QUEUED),
            _step_run("done", StepRunStatus.SUCCEEDED),
        ),
    )

    result = ReplanBarrierExecutor().execute(barrier)

    assert result.status.value == "READY_FOR_REPLAN"
    assert result.ready_for_replan is True
    assert result.cancelled_before_send_step_run_ids == ("step-run:p17:barrier:queued",)
    assert result.terminal_step_run_ids == ("step-run:p17:barrier:done",)


def test_phase17_replan_barrier_executor_enters_draining_for_cancel_or_non_interruptible_work() -> None:
    barrier = ReplanBarrierBuilder().build(
        run_id="run:p17:barrier",
        control_decision=_control_decision(),
        execution_epoch=3,
        step_runs=(
            _step_run("running", StepRunStatus.RUNNING),
            _step_run("claimed", StepRunStatus.CLAIMED),
        ),
        non_interruptible_step_ids=("claimed",),
    )

    result = ReplanBarrierExecutor().execute(barrier)

    assert result.status.value == "DRAINING"
    assert result.ready_for_replan is False
    assert result.cancel_requested_step_run_ids == ("step-run:p17:barrier:running",)
    assert result.draining_step_run_ids == ("step-run:p17:barrier:claimed",)
