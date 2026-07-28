from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import text

from zuno.agent.domain import (
    AgentRun,
    DynamicStepDefinition,
    GoalInputClassification,
    GoalVersion,
    PlanVersion,
    StepExecutorType,
    TaskContract,
)
from zuno.agent.runtime.planning import (
    AdmissionContext,
    AdmissionController,
    BranchResultFencer,
    BranchReductionInput,
    BranchResultReducer,
    BranchResultSubmission,
    BranchTerminalStatus,
    DispatchCommitBuilder,
    DynamicPlanJoinPolicy,
    DynamicPlanOutputContract,
    DynamicPlanProposal,
    DynamicPlanResourceClaim,
    DynamicPlanResourceMode,
    DynamicPlanStep,
    ReadySetBuilder,
)
from zuno.platform.database.agent import AgentDomainUnitOfWork
from zuno.platform.database.foundation import create_foundation_engine


REPO_ROOT = Path(__file__).resolve().parents[3]
DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno?connect_timeout=5",
)
HEX_64 = "a" * 64


@pytest.fixture(scope="session", autouse=True)
def migrated_postgres() -> None:
    env = {
        **os.environ,
        "PGCONNECT_TIMEOUT": os.environ.get("PGCONNECT_TIMEOUT", "5"),
        "ZUNO_ALEMBIC_LOCK_TIMEOUT_SECONDS": os.environ.get("ZUNO_ALEMBIC_LOCK_TIMEOUT_SECONDS", "5"),
    }
    result = subprocess.run(
        ["alembic", "-c", "infra/db/alembic.ini", "upgrade", "head"],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.fixture()
def engine(migrated_postgres):
    engine = create_foundation_engine(DATABASE_URL)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                TRUNCATE
                    agent_branch_result_refs,
                    agent_join_outcomes,
                    agent_dispatch_items,
                    agent_step_runs,
                    agent_dispatch_groups,
                    infra_outbox_events,
                    infra_outbox_sequences,
                    agent_plan_step_definitions,
                    agent_plan_versions,
                    agent_domain_events,
                    agent_domain_runs,
                    agent_task_contracts,
                    agent_goal_versions
                RESTART IDENTITY CASCADE
                """
            )
        )
    try:
        yield engine
    finally:
        engine.dispose()


def _now() -> datetime:
    return datetime(2026, 7, 28, 9, 30, tzinfo=timezone.utc)


def _goal() -> GoalVersion:
    return GoalVersion(
        goal_version_id="goal:p17:dispatch:pg:1",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        principal_id="principal-a",
        goal_sequence=1,
        input_classification=GoalInputClassification.OBJECTIVE_CHANGE,
        objective_hash=HEX_64,
        output_contract_ref="output:dynamic",
        constraints_hash="b" * 64,
    )


def _task(goal: GoalVersion) -> TaskContract:
    return TaskContract(
        task_contract_id="task-contract:p17:dispatch:pg:1",
        tenant_id=goal.tenant_id,
        workspace_id=goal.workspace_id,
        principal_id=goal.principal_id,
        goal_version_id=goal.goal_version_id,
        idempotency_key="idem:p17:dispatch:pg:1",
        security_context_ref="security-context:p17:dispatch",
        security_epoch_ref="security-epoch:p17:dispatch:1",
        deadline_at=_now(),
        budget_ref="budget:p17:dispatch",
    )


def _run(task: TaskContract) -> AgentRun:
    return AgentRun(
        run_id="run:p17:dispatch:pg:1",
        tenant_id=task.tenant_id,
        workspace_id=task.workspace_id,
        principal_id=task.principal_id,
        task_contract_id=task.task_contract_id,
        trace_id="trace:p17:dispatch:pg:1",
    )


def _dynamic_plan(goal: GoalVersion) -> PlanVersion:
    steps = (
        DynamicStepDefinition(
            step_definition_id="step-def:p17:dispatch:collect",
            plan_version_id="plan-version:p17:dispatch:pg:1",
            tenant_id=goal.tenant_id,
            step_no=1,
            dynamic_step_id="collect",
            objective_ref="objective:collect",
            input_contract_ref="input:collect",
            output_contract_ref="output:collect",
            acceptance_refs=("acceptance:collect",),
            executor_type=StepExecutorType.MODEL,
            required_evidence_refs=("evidence:collect",),
            dependency_step_ids=(),
            dependency_rule="ALL_SUCCESS",
            activation_condition_ref="activation:always",
            resource_claim_refs=("resource:doc:1:read",),
            join_policy_ref="join:ALL",
            budget_ref="budget:collect",
            deadline_at=_now(),
        ),
        DynamicStepDefinition(
            step_definition_id="step-def:p17:dispatch:enrich",
            plan_version_id="plan-version:p17:dispatch:pg:1",
            tenant_id=goal.tenant_id,
            step_no=2,
            dynamic_step_id="enrich",
            objective_ref="objective:enrich",
            input_contract_ref="input:enrich",
            output_contract_ref="output:enrich",
            acceptance_refs=("acceptance:enrich",),
            executor_type=StepExecutorType.MODEL,
            required_evidence_refs=("evidence:enrich",),
            dependency_step_ids=(),
            dependency_rule="ALL_SUCCESS",
            activation_condition_ref="activation:always",
            resource_claim_refs=("resource:doc:2:read",),
            join_policy_ref="join:ALL",
            budget_ref="budget:enrich",
            deadline_at=_now(),
        ),
    )
    return PlanVersion.create_dynamic_dag(
        plan_version_id="plan-version:p17:dispatch:pg:1",
        tenant_id=goal.tenant_id,
        workspace_id=goal.workspace_id,
        goal_version_id=goal.goal_version_id,
        steps=steps,
    )


def _proposal() -> DynamicPlanProposal:
    return DynamicPlanProposal(
        plan_id="plan:p17:dispatch:pg",
        goal_version_id="goal:p17:dispatch:pg:1",
        planner_ref="planner:p17",
        steps=[
            _proposal_step("collect", "doc:1"),
            _proposal_step("enrich", "doc:2"),
        ],
    )


def _proposal_step(step_id: str, resource_ref: str) -> DynamicPlanStep:
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


def test_phase17_dispatch_commit_persists_step_runs_and_outbox_in_one_uow(engine) -> None:
    goal = _goal()
    task = _task(goal)
    run = _run(task)
    plan = _dynamic_plan(goal)
    proposal = _proposal()
    admission = AdmissionController().admit(
        proposal,
        ReadySetBuilder().build(proposal),
        AdmissionContext(
            plan_id=proposal.plan_id,
            plan_version_id=plan.plan_version_id,
            security_epoch_ref=task.security_epoch_ref,
            current_security_epoch_ref=task.security_epoch_ref,
            authorized_capabilities={"cap:model"},
            available_budget_units=10,
            quota_slots=2,
            capacity_slots=2,
        ),
    )
    commit = DispatchCommitBuilder().build(
        proposal,
        admission,
        run_id=run.run_id,
        execution_epoch=1,
    )

    with AgentDomainUnitOfWork(engine) as repo:
        repo.record_goal_version(goal)
        repo.record_task_contract(task)
        repo.record_agent_run(run)
        repo.record_plan_version(plan)
        repo.activate_plan_version(plan.activate(expected_version=1, activated_at=_now()), expected_version=1)
        receipt = repo.record_dispatch_commit(tenant_id=goal.tenant_id, commit=commit)

    with engine.begin() as conn:
        row = conn.execute(
            text(
                """
                SELECT
                    (SELECT count(*) FROM agent_dispatch_groups) AS groups,
                    (SELECT count(*) FROM agent_dispatch_items) AS items,
                    (SELECT count(*) FROM agent_step_runs) AS step_runs,
                    (SELECT count(*) FROM infra_outbox_events) AS outbox_events,
                    (SELECT count(*) FROM agent_plan_step_definitions WHERE dynamic_step_id IS NOT NULL) AS dynamic_steps
                """
            )
        ).mappings().one()
        payload_rows = conn.execute(
            text(
                """
                SELECT event.payload, event.ordering_sequence, item.step_run_id
                FROM infra_outbox_events AS event
                JOIN agent_dispatch_items AS item
                  ON item.outbox_event_id = event.event_id
                ORDER BY event.ordering_sequence
                """
            )
        ).mappings().all()

    assert receipt.status == "COMMITTED"
    assert dict(row) == {
        "groups": 1,
        "items": 2,
        "step_runs": 2,
        "outbox_events": 2,
        "dynamic_steps": 2,
    }
    assert [payload["ordering_sequence"] for payload in payload_rows] == [1, 2]
    assert all(payload["payload"]["step_run_id"] == payload["step_run_id"] for payload in payload_rows)
    assert all(payload["payload"]["commit_required_before_send"] is True for payload in payload_rows)


def test_phase17_branch_result_ref_persistence_records_only_fenced_object_refs(engine) -> None:
    goal = _goal()
    task = _task(goal)
    run = _run(task)
    plan = _dynamic_plan(goal)
    proposal = _proposal()
    admission = AdmissionController().admit(
        proposal,
        ReadySetBuilder().build(proposal),
        AdmissionContext(
            plan_id=proposal.plan_id,
            plan_version_id=plan.plan_version_id,
            security_epoch_ref=task.security_epoch_ref,
            current_security_epoch_ref=task.security_epoch_ref,
            authorized_capabilities={"cap:model"},
            available_budget_units=10,
            quota_slots=2,
            capacity_slots=2,
        ),
    )
    commit = DispatchCommitBuilder().build(
        proposal,
        admission,
        run_id=run.run_id,
        execution_epoch=1,
    )
    step_run = commit.step_runs[0]
    accepted = BranchResultFencer().accept(
        BranchResultSubmission(
            branch_result_id="branch-result:p17:dispatch:collect:1",
            step_run_id=step_run.step_run_id,
            run_id=step_run.run_id,
            plan_version_id=step_run.plan_version_id,
            dynamic_step_id=step_run.dynamic_step_id,
            execution_epoch=step_run.execution_epoch,
            attempt_no=step_run.attempt_no,
            step_hash=step_run.step_hash,
            result_ref="object://agent-results/p17/collect.json",
            result_hash="c" * 64,
            producer_ref="langgraph-send:worker:1",
        ),
        step_run=step_run,
        active_plan_version_id=plan.plan_version_id,
        active_execution_epoch=1,
    )
    stale = BranchResultFencer().accept(
        BranchResultSubmission(
            branch_result_id="branch-result:p17:dispatch:collect:late",
            step_run_id=step_run.step_run_id,
            run_id=step_run.run_id,
            plan_version_id="plan-version:p17:superseded",
            dynamic_step_id=step_run.dynamic_step_id,
            execution_epoch=step_run.execution_epoch,
            attempt_no=step_run.attempt_no,
            step_hash=step_run.step_hash,
            result_ref="object://agent-results/p17/late.json",
            result_hash="d" * 64,
            producer_ref="langgraph-send:worker:late",
        ),
        step_run=step_run,
        active_plan_version_id=plan.plan_version_id,
        active_execution_epoch=1,
    )
    assert accepted.branch_result is not None
    assert stale.branch_result is None

    with AgentDomainUnitOfWork(engine) as repo:
        repo.record_goal_version(goal)
        repo.record_task_contract(task)
        repo.record_agent_run(run)
        repo.record_plan_version(plan)
        repo.activate_plan_version(plan.activate(expected_version=1, activated_at=_now()), expected_version=1)
        repo.record_dispatch_commit(tenant_id=goal.tenant_id, commit=commit)
        receipt = repo.record_branch_result_ref(tenant_id=goal.tenant_id, branch_result=accepted.branch_result)
        duplicate = repo.record_branch_result_ref(tenant_id=goal.tenant_id, branch_result=accepted.branch_result)

    with engine.begin() as conn:
        row = conn.execute(
            text(
                """
                SELECT branch_result_id, step_run_id, result_ref, ref_hash
                FROM agent_branch_result_refs
                """
            )
        ).mappings().one()

    assert receipt.status == "ACCEPTED"
    assert duplicate.status == "duplicate:ACCEPTED"
    assert row["branch_result_id"] == "branch-result:p17:dispatch:collect:1"
    assert row["step_run_id"] == step_run.step_run_id
    assert row["result_ref"].startswith("object://")
    assert row["ref_hash"] == accepted.branch_result.ref_hash


def test_phase17_join_outcome_persistence_records_reducer_decision(engine) -> None:
    goal = _goal()
    task = _task(goal)
    run = _run(task)
    plan = _dynamic_plan(goal)
    proposal = _proposal()
    admission = AdmissionController().admit(
        proposal,
        ReadySetBuilder().build(proposal),
        AdmissionContext(
            plan_id=proposal.plan_id,
            plan_version_id=plan.plan_version_id,
            security_epoch_ref=task.security_epoch_ref,
            current_security_epoch_ref=task.security_epoch_ref,
            authorized_capabilities={"cap:model"},
            available_budget_units=10,
            quota_slots=2,
            capacity_slots=2,
        ),
    )
    commit = DispatchCommitBuilder().build(
        proposal,
        admission,
        run_id=run.run_id,
        execution_epoch=1,
    )
    branch_results = []
    for step_run in commit.step_runs:
        accepted = BranchResultFencer().accept(
            BranchResultSubmission(
                branch_result_id=f"branch-result:p17:join:{step_run.dynamic_step_id}",
                step_run_id=step_run.step_run_id,
                run_id=step_run.run_id,
                plan_version_id=step_run.plan_version_id,
                dynamic_step_id=step_run.dynamic_step_id,
                execution_epoch=step_run.execution_epoch,
                attempt_no=step_run.attempt_no,
                step_hash=step_run.step_hash,
                result_ref=f"object://agent-results/p17/{step_run.dynamic_step_id}.json",
                result_hash=("d" if step_run.dynamic_step_id == "collect" else "e") * 64,
                producer_ref=f"langgraph-send:{step_run.dynamic_step_id}",
            ),
            step_run=step_run,
            active_plan_version_id=plan.plan_version_id,
            active_execution_epoch=1,
        )
        assert accepted.branch_result is not None
        branch_results.append(accepted.branch_result)
    outcome = BranchResultReducer().reduce(
        plan_id=proposal.plan_id,
        plan_version_id=plan.plan_version_id,
        join_policy=DynamicPlanJoinPolicy.ALL_REQUIRED,
        expected_branch_count=2,
        branch_results=tuple(
            BranchReductionInput(branch_result=result, terminal_status=BranchTerminalStatus.SUCCEEDED)
            for result in reversed(branch_results)
        ),
    )

    with AgentDomainUnitOfWork(engine) as repo:
        repo.record_goal_version(goal)
        repo.record_task_contract(task)
        repo.record_agent_run(run)
        repo.record_plan_version(plan)
        repo.activate_plan_version(plan.activate(expected_version=1, activated_at=_now()), expected_version=1)
        repo.record_dispatch_commit(tenant_id=goal.tenant_id, commit=commit)
        for result in branch_results:
            repo.record_branch_result_ref(tenant_id=goal.tenant_id, branch_result=result)
        receipt = repo.record_join_outcome(
            tenant_id=goal.tenant_id,
            join_outcome_id="join-outcome:p17:join:1",
            outcome=outcome,
        )
        duplicate = repo.record_join_outcome(
            tenant_id=goal.tenant_id,
            join_outcome_id="join-outcome:p17:join:1",
            outcome=outcome,
        )

    with engine.begin() as conn:
        row = conn.execute(
            text(
                """
                SELECT join_policy, decision, expected_branch_count, reduced_results, duplicate_result_ids, outcome_hash
                FROM agent_join_outcomes
                """
            )
        ).mappings().one()

    assert receipt.status == "CONTINUE"
    assert duplicate.status == "duplicate:CONTINUE"
    assert row["join_policy"] == "ALL_REQUIRED"
    assert row["decision"] == "CONTINUE"
    assert row["expected_branch_count"] == 2
    assert [item["dynamic_step_id"] for item in row["reduced_results"]] == ["collect", "enrich"]
    assert row["duplicate_result_ids"] == []
    assert row["outcome_hash"] == outcome.outcome_hash
