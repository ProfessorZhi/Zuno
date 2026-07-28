from __future__ import annotations

import pytest

from zuno.agent.runtime.planning import (
    AdmissionContext,
    AdmissionController,
    DispatchCommitBuilder,
    DispatchGroupStatus,
    DispatchItemStatus,
    DispatchValidationError,
    DynamicPlanOutputContract,
    DynamicPlanProposal,
    DynamicPlanResourceClaim,
    DynamicPlanResourceMode,
    DynamicPlanStep,
    ReadySetBuilder,
    StepRunStatus,
)


def _step(step_id: str, *, resource_ref: str = "doc:1") -> DynamicPlanStep:
    return DynamicPlanStep(
        step_id=step_id,
        objective_ref=f"objective:{step_id}",
        goal=f"complete {step_id}",
        executor="model",
        outputs=[DynamicPlanOutputContract(output_name="result", schema_ref=f"schema:{step_id}")],
        acceptance_criteria=[f"{step_id} accepted"],
        allowed_capabilities=["cap:model"],
        resource_claims=[DynamicPlanResourceClaim(resource_ref=resource_ref, mode=DynamicPlanResourceMode.READ)],
        budget={"units": 1},
    )


def _proposal(plan_id: str = "plan:p17:dispatch") -> DynamicPlanProposal:
    return DynamicPlanProposal(
        plan_id=plan_id,
        goal_version_id="goal:p17:dispatch",
        planner_ref="planner:p17",
        steps=[
            _step("collect", resource_ref="doc:1"),
            _step("enrich", resource_ref="doc:2"),
        ],
    )


def _admission(proposal: DynamicPlanProposal):
    ready_set = ReadySetBuilder().build(proposal)
    return AdmissionController().admit(
        proposal,
        ready_set,
        AdmissionContext(
            plan_id=proposal.plan_id,
            plan_version_id="plan-version:p17:dispatch:1",
            security_epoch_ref="security-epoch:1",
            current_security_epoch_ref="security-epoch:1",
            authorized_capabilities={"cap:model"},
            available_budget_units=10,
            quota_slots=4,
            capacity_slots=4,
        ),
    )


def test_phase17_dispatch_commit_binds_group_items_step_runs_and_outbox_before_send() -> None:
    proposal = _proposal()
    commit = DispatchCommitBuilder().build(
        proposal,
        _admission(proposal),
        run_id="run:p17:dispatch",
        execution_epoch=3,
    )

    assert commit.dispatch_group.status is DispatchGroupStatus.COMMITTED
    assert commit.dispatch_group.committed_before_send is True
    assert commit.dispatch_group.execution_epoch == 3
    assert [item.status for item in commit.items] == [DispatchItemStatus.PENDING_SEND] * 2
    assert [step_run.status for step_run in commit.step_runs] == [StepRunStatus.QUEUED] * 2
    assert commit.dispatch_group.admitted_step_ids == ("collect", "enrich")
    assert {
        message.payload["step_run_id"]
        for message in commit.outbox_messages
    } == {step_run.step_run_id for step_run in commit.step_runs}
    assert all(
        message.payload["commit_required_before_send"] is True
        and message.payload["execution_epoch"] == 3
        and message.topic == "agent.dynamic_step.dispatch.requested"
        for message in commit.outbox_messages
    )


def test_phase17_dispatch_commit_is_deterministic_for_same_admission() -> None:
    proposal = _proposal()
    admission = _admission(proposal)
    left = DispatchCommitBuilder().build(
        proposal,
        admission,
        run_id="run:p17:dispatch",
        execution_epoch=1,
    )
    right = DispatchCommitBuilder().build(
        proposal,
        admission,
        run_id="run:p17:dispatch",
        execution_epoch=1,
    )

    assert left.model_dump(mode="json") == right.model_dump(mode="json")


def test_phase17_dispatch_commit_rejects_plan_mismatch_or_no_admitted_steps() -> None:
    proposal = _proposal()
    admission = _admission(proposal)

    with pytest.raises(DispatchValidationError, match="plan_id"):
        DispatchCommitBuilder().build(
            _proposal(plan_id="plan:p17:other"),
            admission,
            run_id="run:p17:dispatch",
            execution_epoch=1,
        )

    deferred_admission = AdmissionController().admit(
        proposal,
        ReadySetBuilder().build(proposal),
        AdmissionContext(
            plan_id=proposal.plan_id,
            plan_version_id="plan-version:p17:dispatch:1",
            security_epoch_ref="security-epoch:1",
            current_security_epoch_ref="security-epoch:2",
            authorized_capabilities=set(),
            available_budget_units=0,
            quota_slots=0,
            capacity_slots=0,
        ),
    )
    with pytest.raises(DispatchValidationError, match="at least one admitted"):
        DispatchCommitBuilder().build(
            proposal,
            deferred_admission,
            run_id="run:p17:dispatch",
            execution_epoch=1,
        )
