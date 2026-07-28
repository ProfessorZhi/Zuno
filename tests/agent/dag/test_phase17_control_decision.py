from __future__ import annotations

import pytest

from zuno.agent.runtime.planning import (
    BranchReductionInput,
    BranchResultReducer,
    BranchResultRef,
    BranchTerminalStatus,
    ConditionalReflectionPolicy,
    ControlDecisionReason,
    DynamicControlAction,
    DynamicPlanJoinPolicy,
    JoinControlDecisionEngine,
    JoinDecision,
)


def _result(step_id: str, *, result_hash: str = "d") -> BranchResultRef:
    return BranchResultRef(
        branch_result_id=f"branch-result:p17:control:{step_id}",
        step_run_id=f"step-run:p17:control:{step_id}",
        run_id="run:p17:control",
        plan_version_id="plan-version:p17:control",
        dynamic_step_id=step_id,
        execution_epoch=1,
        attempt_no=1,
        result_ref=f"object://agent-results/p17/control/{step_id}.json",
        result_hash=result_hash * 64,
        producer_ref=f"langgraph-send:{step_id}",
    )


def _input(step_id: str, status: BranchTerminalStatus = BranchTerminalStatus.SUCCEEDED) -> BranchReductionInput:
    return BranchReductionInput(branch_result=_result(step_id), terminal_status=status)


def _outcome(
    policy: DynamicPlanJoinPolicy,
    items: tuple[BranchReductionInput, ...],
    *,
    expected: int = 3,
):
    return BranchResultReducer().reduce(
        plan_id="plan:p17:control",
        plan_version_id="plan-version:p17:control",
        join_policy=policy,
        expected_branch_count=expected,
        branch_results=items,
    )


def test_phase17_control_decision_continues_completed_join_without_reflection() -> None:
    outcome = _outcome(
        DynamicPlanJoinPolicy.ALL_REQUIRED,
        (_input("a"), _input("b"), _input("c")),
    )

    decision = JoinControlDecisionEngine().decide(outcome=outcome)

    assert outcome.decision is JoinDecision.CONTINUE
    assert decision.action is DynamicControlAction.CONTINUE
    assert decision.reason is ControlDecisionReason.JOIN_COMPLETE
    assert decision.reflection_required is False
    assert decision.replan_barrier_required is False
    assert decision.retry_permitted is False


def test_phase17_control_decision_waits_for_pending_branches_without_replan() -> None:
    outcome = _outcome(DynamicPlanJoinPolicy.ALL_REQUIRED, (_input("a"),))

    decision = JoinControlDecisionEngine().decide(outcome=outcome)

    assert outcome.decision is JoinDecision.WAIT
    assert decision.action is DynamicControlAction.WAIT_FOR_BRANCHES
    assert decision.reason is ControlDecisionReason.BRANCHES_PENDING
    assert decision.pending_branch_count == 2
    assert decision.reflection_required is False
    assert decision.replan_barrier_required is False


def test_phase17_control_decision_requests_reflection_for_best_effort_partial_join() -> None:
    outcome = _outcome(DynamicPlanJoinPolicy.BEST_EFFORT, (_input("a"),))

    decision = JoinControlDecisionEngine().decide(outcome=outcome)

    assert outcome.decision is JoinDecision.PARTIAL_CONTINUE
    assert decision.action is DynamicControlAction.REQUEST_REFLECTION
    assert decision.reason is ControlDecisionReason.PARTIAL_BRANCH_RESULT
    assert decision.reflection_required is True
    assert decision.replan_barrier_required is False
    assert decision.pending_branch_count == 2


def test_phase17_control_decision_requests_replan_barrier_for_failed_join() -> None:
    outcome = _outcome(
        DynamicPlanJoinPolicy.FAIL_FAST,
        (_input("a"), _input("b", BranchTerminalStatus.FAILED)),
    )

    decision = JoinControlDecisionEngine().decide(outcome=outcome)

    assert outcome.decision is JoinDecision.FAIL
    assert decision.action is DynamicControlAction.REQUEST_REPLAN_BARRIER
    assert decision.reason is ControlDecisionReason.JOIN_FAILURE
    assert decision.reflection_required is True
    assert decision.replan_barrier_required is True
    assert decision.retry_permitted is False
    assert decision.failed_branch_result_ids == ("branch-result:p17:control:b",)


def test_phase17_control_decision_can_fail_closed_when_reflection_and_replan_are_disabled() -> None:
    outcome = _outcome(
        DynamicPlanJoinPolicy.ALL_REQUIRED,
        (
            _input("a", BranchTerminalStatus.FAILED),
            _input("b", BranchTerminalStatus.CANCELLED),
            _input("c", BranchTerminalStatus.FAILED),
        ),
    )
    policy = ConditionalReflectionPolicy(
        policy_id="phase17-no-reflection-no-replan",
        allow_reflection=False,
        allow_replan_barrier=False,
    )

    decision = JoinControlDecisionEngine().decide(outcome=outcome, policy=policy)

    assert decision.action is DynamicControlAction.FAIL_RUN
    assert decision.reason is ControlDecisionReason.REFLECTION_DISABLED
    assert decision.reflection_required is False
    assert decision.replan_barrier_required is False
    assert decision.retry_permitted is False
    assert decision.failed_branch_result_ids == (
        "branch-result:p17:control:a",
        "branch-result:p17:control:b",
        "branch-result:p17:control:c",
    )


def test_phase17_control_decision_hash_fences_mutation() -> None:
    outcome = _outcome(DynamicPlanJoinPolicy.BEST_EFFORT, (_input("a"),))
    decision = JoinControlDecisionEngine().decide(outcome=outcome)

    with pytest.raises(ValueError, match="hash mismatch"):
        type(decision)(
            **{
                **decision.model_dump(),
                "reflection_required": False,
                "decision_hash": decision.decision_hash,
            }
        )
