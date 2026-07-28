from __future__ import annotations

import pytest

from zuno.agent.runtime.planning.dynamic_dag import (
    DynamicPlanInputBinding,
    DynamicPlanOutputContract,
    DynamicPlanProposal,
    DynamicPlanRepairer,
    DynamicPlanResourceClaim,
    DynamicPlanResourceMode,
    DynamicPlanSideEffectClass,
    DynamicPlanStep,
    DynamicPlanValidationError,
    DynamicPlanValidator,
)


def _output(name: str = "result") -> DynamicPlanOutputContract:
    return DynamicPlanOutputContract(output_name=name, schema_ref=f"schema://{name}")


def _step(step_id: str, *, dependencies: list[str] | None = None) -> DynamicPlanStep:
    return DynamicPlanStep(
        step_id=step_id,
        objective_ref=f"objective:{step_id}",
        goal=f"complete {step_id}",
        executor="model",
        dependencies=dependencies or [],
        outputs=[_output()],
        acceptance_criteria=["output contract satisfied"],
    )


def test_phase17_dynamic_plan_validator_accepts_dependency_bound_dag() -> None:
    proposal = DynamicPlanProposal(
        plan_id="plan:phase17:valid",
        goal_version_id="goal-version:1",
        planner_ref="planner:deterministic",
        steps=[
            _step("retrieve"),
            DynamicPlanStep(
                step_id="synthesize",
                objective_ref="objective:synthesize",
                goal="synthesize answer",
                executor="model",
                dependencies=["retrieve"],
                inputs=[
                    DynamicPlanInputBinding(
                        input_name="evidence",
                        source_step_id="retrieve",
                        source_output_name="result",
                    )
                ],
                outputs=[_output("draft")],
                acceptance_criteria=["draft cites evidence"],
            ),
        ],
    )

    assert DynamicPlanValidator().validate(proposal) is proposal


@pytest.mark.parametrize(
    ("proposal", "message"),
    [
        (
            DynamicPlanProposal(
                plan_id="plan:phase17:cycle",
                goal_version_id="goal-version:1",
                planner_ref="planner:model",
                steps=[
                    _step("a", dependencies=["b"]),
                    _step("b", dependencies=["a"]),
                ],
            ),
            "cycle",
        ),
        (
            DynamicPlanProposal(
                plan_id="plan:phase17:missing",
                goal_version_id="goal-version:1",
                planner_ref="planner:model",
                steps=[_step("a", dependencies=["missing"])],
            ),
            "missing dependencies",
        ),
        (
            DynamicPlanProposal(
                plan_id="plan:phase17:unbound-input",
                goal_version_id="goal-version:1",
                planner_ref="planner:model",
                steps=[
                    _step("source"),
                    DynamicPlanStep(
                        step_id="consumer",
                        objective_ref="objective:consumer",
                        goal="consume source",
                        executor="model",
                        inputs=[
                            DynamicPlanInputBinding(
                                input_name="source",
                                source_step_id="source",
                                source_output_name="result",
                            )
                        ],
                        outputs=[_output()],
                        acceptance_criteria=["consumer output accepted"],
                    ),
                ],
            ),
            "input is not dependency-bound",
        ),
    ],
)
def test_phase17_dynamic_plan_validator_rejects_invalid_dag_shapes(
    proposal: DynamicPlanProposal,
    message: str,
) -> None:
    with pytest.raises(DynamicPlanValidationError, match=message):
        DynamicPlanValidator().validate(proposal)


def test_phase17_dynamic_plan_validator_rejects_unsafe_parallel_writes() -> None:
    proposal = DynamicPlanProposal(
        plan_id="plan:phase17:write-conflict",
        goal_version_id="goal-version:1",
        planner_ref="planner:model",
        steps=[
            _step("write-a").model_copy(
                update={
                    "resource_claims": [
                        DynamicPlanResourceClaim(
                            resource_ref="workspace://case-1/report.md",
                            mode=DynamicPlanResourceMode.WRITE,
                        )
                    ],
                    "side_effect_class": DynamicPlanSideEffectClass.REVERSIBLE_WRITE,
                }
            ),
            _step("write-b").model_copy(
                update={
                    "resource_claims": [
                        DynamicPlanResourceClaim(
                            resource_ref="workspace://case-1/report.md",
                            mode=DynamicPlanResourceMode.WRITE,
                        )
                    ],
                    "side_effect_class": DynamicPlanSideEffectClass.REVERSIBLE_WRITE,
                }
            ),
        ],
    )

    with pytest.raises(DynamicPlanValidationError, match="resource conflict"):
        DynamicPlanValidator().validate(proposal)


def test_phase17_dynamic_plan_repairer_adds_deterministic_acceptance_and_output_contract() -> None:
    proposal = DynamicPlanProposal(
        plan_id="plan:phase17:repair",
        goal_version_id="goal-version:1",
        planner_ref="planner:model",
        steps=[
            DynamicPlanStep(
                step_id="draft",
                objective_ref="objective:draft",
                goal="draft answer",
                executor="model",
            )
        ],
    )

    repaired = DynamicPlanRepairer().repair(proposal)

    assert repaired.steps[0].acceptance_criteria == ["draft output contract satisfied"]
    assert repaired.steps[0].outputs[0].output_name == "result"
    DynamicPlanValidator().validate(repaired)
