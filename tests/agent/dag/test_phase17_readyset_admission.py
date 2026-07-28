from __future__ import annotations

from zuno.agent.runtime.planning import (
    AdmissionContext,
    AdmissionController,
    AdmissionDecisionStatus,
    AdmissionRejectionCode,
    DynamicPlanDependencyRule,
    DynamicPlanJoinPolicy,
    DynamicPlanOutputContract,
    DynamicPlanProposal,
    DynamicPlanResourceClaim,
    DynamicPlanResourceMode,
    DynamicPlanStep,
    DynamicPlanStepStatus,
    DynamicStepRunState,
    ReadySetBuilder,
)


def _step(
    step_id: str,
    *,
    dependencies: list[str] | None = None,
    dependency_rule: DynamicPlanDependencyRule = DynamicPlanDependencyRule.ALL_SUCCESS,
    allowed_capabilities: list[str] | None = None,
    resource_claims: list[DynamicPlanResourceClaim] | None = None,
    budget_units: float = 1,
) -> DynamicPlanStep:
    return DynamicPlanStep(
        step_id=step_id,
        objective_ref=f"objective:{step_id}",
        goal=f"complete {step_id}",
        executor="model",
        dependencies=dependencies or [],
        dependency_rule=dependency_rule,
        outputs=[DynamicPlanOutputContract(output_name="result", schema_ref=f"schema:{step_id}")],
        acceptance_criteria=[f"{step_id} accepted"],
        allowed_capabilities=allowed_capabilities or [],
        resource_claims=resource_claims or [],
        budget={"units": budget_units},
    )


def _proposal() -> DynamicPlanProposal:
    return DynamicPlanProposal(
        plan_id="plan:p17:readyset",
        goal_version_id="goal:p17:readyset",
        planner_ref="planner:p17",
        join_policy=DynamicPlanJoinPolicy.ALL_REQUIRED,
        steps=[
            _step("collect"),
            _step("enrich", dependencies=["collect"]),
            _step("alternative", dependencies=["collect"], dependency_rule=DynamicPlanDependencyRule.ALL_TERMINAL),
            _step("join", dependencies=["enrich", "alternative"], dependency_rule=DynamicPlanDependencyRule.QUORUM),
        ],
    )


def _context(**updates: object) -> AdmissionContext:
    values = {
        "plan_id": "plan:p17:readyset",
        "plan_version_id": "plan-version:p17:readyset:1",
        "security_epoch_ref": "security-epoch:1",
        "current_security_epoch_ref": "security-epoch:1",
        "authorized_capabilities": {"cap:model", "cap:knowledge"},
        "available_budget_units": 10,
        "quota_slots": 4,
        "capacity_slots": 4,
    }
    values.update(updates)
    return AdmissionContext(**values)


def test_phase17_readyset_finds_dependency_satisfied_steps() -> None:
    ready_set = ReadySetBuilder().build(
        _proposal(),
        step_states=(
            DynamicStepRunState(step_id="collect", status=DynamicPlanStepStatus.SUCCEEDED),
            DynamicStepRunState(step_id="alternative", status=DynamicPlanStepStatus.FAILED),
        ),
    )

    assert ready_set.ready_step_ids == ("enrich",)
    assert ready_set.waiting_step_ids == ("join",)
    assert ready_set.terminal_step_ids == ("collect", "alternative")


def test_phase17_admission_admits_ready_steps_with_budget_quota_capacity_and_resources() -> None:
    proposal = DynamicPlanProposal(
        plan_id="plan:p17:readyset",
        goal_version_id="goal:p17:readyset",
        planner_ref="planner:p17",
        steps=[
            _step(
                "read-a",
                allowed_capabilities=["cap:model"],
                resource_claims=[
                    DynamicPlanResourceClaim(resource_ref="doc:1", mode=DynamicPlanResourceMode.READ)
                ],
                budget_units=2,
            ),
            _step(
                "read-b",
                allowed_capabilities=["cap:knowledge"],
                resource_claims=[
                    DynamicPlanResourceClaim(resource_ref="doc:1", mode=DynamicPlanResourceMode.READ)
                ],
                budget_units=3,
            ),
        ],
    )
    ready_set = ReadySetBuilder().build(proposal)
    result = AdmissionController().admit(proposal, ready_set, _context())

    assert result.admitted_step_ids == ("read-a", "read-b")
    assert [decision.reserved_budget_units for decision in result.decisions] == [2, 3]


def test_phase17_admission_rejects_stale_security_epoch_and_unauthorized_capability() -> None:
    proposal = DynamicPlanProposal(
        plan_id="plan:p17:readyset",
        goal_version_id="goal:p17:readyset",
        planner_ref="planner:p17",
        steps=[
            _step("secure", allowed_capabilities=["cap:tool-write"]),
        ],
    )
    ready_set = ReadySetBuilder().build(proposal)
    result = AdmissionController().admit(
        proposal,
        ready_set,
        _context(current_security_epoch_ref="security-epoch:2"),
    )

    assert result.decisions[0].status is AdmissionDecisionStatus.REJECTED
    assert result.decisions[0].reason_codes == (
        AdmissionRejectionCode.STALE_SECURITY_EPOCH,
        AdmissionRejectionCode.CAPABILITY_NOT_AUTHORIZED,
    )


def test_phase17_admission_defers_budget_quota_capacity_and_resource_conflicts() -> None:
    proposal = DynamicPlanProposal(
        plan_id="plan:p17:readyset",
        goal_version_id="goal:p17:readyset",
        planner_ref="planner:p17",
        steps=[
            _step(
                "write-a",
                resource_claims=[
                    DynamicPlanResourceClaim(resource_ref="doc:1", mode=DynamicPlanResourceMode.WRITE)
                ],
                budget_units=4,
            ),
            _step(
                "write-b",
                resource_claims=[
                    DynamicPlanResourceClaim(resource_ref="doc:1", mode=DynamicPlanResourceMode.WRITE)
                ],
                budget_units=4,
            ),
            _step("overflow", budget_units=4),
        ],
    )
    ready_set = ReadySetBuilder().build(proposal)
    result = AdmissionController().admit(
        proposal,
        ready_set,
        _context(available_budget_units=5, quota_slots=2, capacity_slots=2),
    )

    assert result.decisions[0].status is AdmissionDecisionStatus.ADMITTED
    assert result.decisions[1].status is AdmissionDecisionStatus.DEFERRED
    assert result.decisions[1].reason_codes == (
        AdmissionRejectionCode.BUDGET_EXHAUSTED,
        AdmissionRejectionCode.RESOURCE_CONFLICT,
    )
    assert result.decisions[2].status is AdmissionDecisionStatus.DEFERRED
    assert result.decisions[2].reason_codes == (AdmissionRejectionCode.BUDGET_EXHAUSTED,)
