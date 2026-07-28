from __future__ import annotations

from zuno.agent.runtime.planning import (
    AdmissionContext,
    DynamicPlanOutputContract,
    DynamicPlanResourceClaim,
    DynamicPlanResourceMode,
    DynamicPlanRuntimeController,
    DynamicPlanStep,
    DynamicPlanProposal,
)


class _Repository:
    def __init__(self) -> None:
        self.commits = []

    def record_dispatch_commit(self, *, tenant_id: str, commit):
        self.commits.append((tenant_id, commit))
        return type("Receipt", (), {"ref": commit.dispatch_group.dispatch_group_id, "status": "COMMITTED"})()


def _proposal() -> DynamicPlanProposal:
    return DynamicPlanProposal(
        plan_id="plan:p17:controller",
        goal_version_id="goal:p17:controller",
        planner_ref="planner:p17",
        steps=[
            DynamicPlanStep(
                step_id="collect",
                objective_ref="objective:collect",
                goal="collect facts",
                executor="model",
                outputs=[DynamicPlanOutputContract(output_name="result", schema_ref="schema:collect")],
                acceptance_criteria=["facts collected"],
                allowed_capabilities=["cap:model"],
                resource_claims=[DynamicPlanResourceClaim(resource_ref="doc:1", mode=DynamicPlanResourceMode.READ)],
                budget={"units": 1},
            ),
            DynamicPlanStep(
                step_id="enrich",
                objective_ref="objective:enrich",
                goal="enrich facts",
                executor="model",
                outputs=[DynamicPlanOutputContract(output_name="result", schema_ref="schema:enrich")],
                acceptance_criteria=["facts enriched"],
                allowed_capabilities=["cap:model"],
                resource_claims=[DynamicPlanResourceClaim(resource_ref="doc:2", mode=DynamicPlanResourceMode.READ)],
                budget={"units": 1},
            ),
        ],
    )


def _context() -> AdmissionContext:
    return AdmissionContext(
        plan_id="plan:p17:controller",
        plan_version_id="plan-version:p17:controller",
        security_epoch_ref="security-epoch:1",
        current_security_epoch_ref="security-epoch:1",
        authorized_capabilities={"cap:model"},
        available_budget_units=10,
        quota_slots=2,
        capacity_slots=2,
    )


def test_phase17_dynamic_runtime_controller_dispatches_ready_steps_through_commit_before_send() -> None:
    repository = _Repository()

    result = DynamicPlanRuntimeController().dispatch_ready_steps(
        tenant_id="tenant-a",
        proposal=_proposal(),
        admission_context=_context(),
        run_id="run:p17:controller",
        execution_epoch=1,
        repository=repository,
    )

    assert result.ready_set.ready_step_ids == ("collect", "enrich")
    assert result.admission.admitted_step_ids == ("collect", "enrich")
    assert result.dispatch_commit is not None
    assert result.persisted_status == "COMMITTED"
    assert len(repository.commits) == 1
    assert all(message.payload["commit_required_before_send"] is True for message in result.dispatch_commit.outbox_messages)


def test_phase17_dynamic_runtime_controller_defers_without_dispatch_commit_when_admission_blocks() -> None:
    repository = _Repository()
    context = _context().model_copy(update={"available_budget_units": 0})

    result = DynamicPlanRuntimeController().dispatch_ready_steps(
        tenant_id="tenant-a",
        proposal=_proposal(),
        admission_context=context,
        run_id="run:p17:controller",
        execution_epoch=1,
        repository=repository,
    )

    assert result.dispatch_commit is None
    assert result.persisted_status is None
    assert repository.commits == []
