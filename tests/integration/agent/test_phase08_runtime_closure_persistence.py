from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import text

from zuno.agent.domain import AgentDomainConflict, AgentRun, GoalInputClassification, GoalVersion, TaskContract
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
    result = subprocess.run(
        ["alembic", "-c", "infra/db/alembic.ini", "upgrade", "head"],
        cwd=REPO_ROOT,
        env={**os.environ, "PGCONNECT_TIMEOUT": os.environ.get("PGCONNECT_TIMEOUT", "5")},
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
                    agent_cutover_audit_events,
                    agent_reconciliation_findings,
                    agent_runtime_signals,
                    agent_run_outcomes,
                    agent_final_gate_receipts,
                    agent_effect_claims,
                    agent_step_acceptances,
                    agent_observations,
                    agent_action_runs,
                    agent_request_idempotency_keys,
                    agent_execution_context_snapshots,
                    agent_budget_settlements,
                    agent_budget_reservations,
                    agent_plan_step_definitions,
                    agent_plan_versions,
                    agent_domain_events,
                    agent_domain_runs,
                    agent_task_contracts,
                    agent_goal_versions
                RESTART IDENTITY
                """
            )
        )
    try:
        yield engine
    finally:
        engine.dispose()


def test_phase08_runtime_closure_ledgers_are_persistent_and_idempotent(engine) -> None:
    with AgentDomainUnitOfWork(engine) as repo:
        goal = _goal()
        task = _task(goal)
        run = _run(task)
        repo.record_goal_version(goal)
        repo.record_task_contract(task)
        repo.record_agent_run(run)

        request = repo.claim_request_idempotency(
            tenant_id=task.tenant_id,
            workspace_id=task.workspace_id,
            idempotency_key=task.idempotency_key,
            payload={"goal": "answer with evidence"},
            aggregate_ref=task.task_contract_id,
        )
        duplicate_request = repo.claim_request_idempotency(
            tenant_id=task.tenant_id,
            workspace_id=task.workspace_id,
            idempotency_key=task.idempotency_key,
            payload={"goal": "answer with evidence"},
            aggregate_ref=task.task_contract_id,
        )
        assert request.ref == task.task_contract_id
        assert duplicate_request.status == "duplicate:claimed"

        with pytest.raises(AgentDomainConflict, match="conflicting idempotency payload"):
            repo.claim_request_idempotency(
                tenant_id=task.tenant_id,
                workspace_id=task.workspace_id,
                idempotency_key=task.idempotency_key,
                payload={"goal": "different"},
                aggregate_ref=task.task_contract_id,
            )

        acceptance = repo.record_action_observation_acceptance(
            tenant_id=task.tenant_id,
            run_id=run.run_id,
            step_run_id="step-run:p08:closure:1",
            owner_port="knowledge",
            proposal={"kind": "retrieve", "query": "evidence"},
            observation={"status": "completed", "evidence": ["doc:1"]},
            acceptance={"accepted": True, "schema": "answer:v1"},
            trace_ref=run.trace_id,
            evidence_refs=["evidence:doc:1"],
        )
        effect = repo.claim_effect(
            effect_claim_id="effect-claim:p08:closure:1",
            tenant_id=task.tenant_id,
            idempotency_key="effect:p08:closure:1",
            payload={"owner_port": "knowledge", "action": "read"},
            owner_port="knowledge",
            effect_ref="effect:p08:closure:1",
        )
        duplicate_effect = repo.claim_effect(
            effect_claim_id="effect-claim:p08:closure:1:dupe",
            tenant_id=task.tenant_id,
            idempotency_key="effect:p08:closure:1",
            payload={"owner_port": "knowledge", "action": "read"},
            owner_port="knowledge",
            effect_ref="effect:p08:closure:1",
        )
        assert acceptance.ref == "acceptance:step-run:p08:closure:1"
        assert effect.ref == "effect-claim:p08:closure:1"
        assert duplicate_effect.status == "duplicate:claimed"

        with pytest.raises(AgentDomainConflict, match="conflicting effect payload"):
            repo.claim_effect(
                effect_claim_id="effect-claim:p08:closure:1:conflict",
                tenant_id=task.tenant_id,
                idempotency_key="effect:p08:closure:1",
                payload={"owner_port": "tool", "action": "write"},
                owner_port="tool",
                effect_ref="effect:p08:closure:1",
            )

        outcome = repo.record_final_gate_and_outcome(
            tenant_id=task.tenant_id,
            run_id=run.run_id,
            decision="approved",
            answer_policy_ref="answer-policy:p08",
            evidence_ref="evidence:doc:1",
            security_decision_ref=task.security_context_ref,
            budget_settlement_ref="budget-settlement:p08",
            step_acceptance_ref=acceptance.ref,
            publication_eligible=True,
            outcome_status="completed",
            publication_ref="publication:p08:closure",
        )
        duplicate_outcome = repo.record_final_gate_and_outcome(
            tenant_id=task.tenant_id,
            run_id=run.run_id,
            decision="approved",
            answer_policy_ref="answer-policy:p08",
            evidence_ref="evidence:doc:1",
            security_decision_ref=task.security_context_ref,
            budget_settlement_ref="budget-settlement:p08",
            step_acceptance_ref=acceptance.ref,
            publication_eligible=True,
            outcome_status="completed",
            publication_ref="publication:p08:closure",
        )
        assert outcome.ref == f"run-outcome:{run.run_id}"
        assert duplicate_outcome.status == "duplicate:completed"


def test_phase08_signal_reconciliation_and_cutover_are_persistent(engine) -> None:
    with AgentDomainUnitOfWork(engine) as repo:
        goal = _goal("goal:p08:signal")
        task = _task(goal, "task-contract:p08:signal")
        run = _run(task, "run:p08:signal")
        repo.record_goal_version(goal)
        repo.record_task_contract(task)
        repo.record_agent_run(run)

        signal = repo.record_signal(
            signal_id="signal:p08:cancel",
            tenant_id=task.tenant_id,
            run_id=run.run_id,
            signal_type="cancel",
            payload={"reason": "user_cancelled"},
            status="accepted",
        )
        finding = repo.record_reconciliation_finding(
            finding_id="reconcile:p08:domain-ahead",
            tenant_id=task.tenant_id,
            run_id=run.run_id,
            status="domain_ahead",
            fact_owner="domain",
            auto_repair=True,
            replay_allowed=False,
            terminate_run=False,
            audit_event_ref="audit:p08:domain-ahead",
            payload={"domain_generation": 3, "checkpoint_generation": 2},
        )
        cutover = repo.record_cutover_audit_event(
            cutover_event_id="cutover:p08:canary",
            tenant_id=task.tenant_id,
            workspace_id=task.workspace_id,
            request_id="request:p08:canary",
            mode="canary",
            primary_runtime="phase08",
            effect_committed=True,
            fallback_allowed=False,
            request_hash=HEX_64,
            trace_ref=run.trace_id,
        )
        assert signal.ref == "signal:p08:cancel"
        assert finding.status == "domain_ahead"
        assert cutover.status == "canary"


def _now() -> datetime:
    return datetime(2026, 7, 23, 21, 0, tzinfo=timezone.utc)


def _goal(goal_version_id: str = "goal:p08:closure") -> GoalVersion:
    return GoalVersion(
        goal_version_id=goal_version_id,
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        principal_id="principal-a",
        goal_sequence=1,
        input_classification=GoalInputClassification.OBJECTIVE_CHANGE,
        objective_hash=HEX_64,
        output_contract_ref="output:answer",
        constraints_hash="b" * 64,
    )


def _task(goal: GoalVersion, task_contract_id: str = "task-contract:p08:closure") -> TaskContract:
    return TaskContract(
        task_contract_id=task_contract_id,
        tenant_id=goal.tenant_id,
        workspace_id=goal.workspace_id,
        principal_id=goal.principal_id,
        goal_version_id=goal.goal_version_id,
        idempotency_key=f"idem:{task_contract_id}",
        security_context_ref="security-context:p08",
        security_epoch_ref="security-epoch:p08",
        deadline_at=_now(),
        budget_ref="budget:p08",
    )


def _run(task: TaskContract, run_id: str = "run:p08:closure") -> AgentRun:
    return AgentRun(
        run_id=run_id,
        tenant_id=task.tenant_id,
        workspace_id=task.workspace_id,
        principal_id=task.principal_id,
        task_contract_id=task.task_contract_id,
        trace_id=f"trace:{run_id}",
    )
