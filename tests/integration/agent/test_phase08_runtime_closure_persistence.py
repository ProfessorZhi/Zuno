from __future__ import annotations

import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from sqlalchemy import text

from zuno.agent.domain import AgentDomainConflict, AgentRun, GoalInputClassification, GoalVersion, TaskContract
from zuno.agent.runtime import (
    Phase08CutoverController,
    Phase08RuntimeRequest,
    Phase08RuntimeResponse,
    Phase08SideEffectClaimError,
    Phase08RunService,
    Phase08StepService,
    PostgresPhase08CutoverLedger,
    PostgresPhase08FinalGatePort,
    PostgresPhase08OwnerPort,
    build_phase08_run_graph,
    build_phase08_step_graph,
    build_phase08_test_checkpointer,
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
        duplicate_acceptance = repo.record_action_observation_acceptance(
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
        assert duplicate_acceptance.status == "duplicate:accepted"
        assert effect.ref == "effect-claim:p08:closure:1"
        assert duplicate_effect.status == "duplicate:claimed"

        with pytest.raises(AgentDomainConflict, match="conflicting action run"):
            repo.record_action_observation_acceptance(
                tenant_id=task.tenant_id,
                run_id=run.run_id,
                step_run_id="step-run:p08:closure:1",
                owner_port="knowledge",
                proposal={"kind": "retrieve", "query": "different"},
                observation={"status": "completed", "evidence": ["doc:1"]},
                acceptance={"accepted": True, "schema": "answer:v1"},
                trace_ref=run.trace_id,
                evidence_refs=["evidence:doc:1"],
            )

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


def test_phase08_product_cutover_uses_persistent_effect_and_audit_ledgers(engine) -> None:
    request = Phase08RuntimeRequest(
        request_id="request:p08:cutover:postgres",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        user_id="principal-a",
        task_id="task-p08-cutover-postgres",
        trace_id="trace:p08:cutover:postgres",
        goal="answer through phase08 cutover",
        idempotency_key="idem:p08:cutover:postgres",
    )
    calls: list[tuple[str, bool]] = []

    def legacy_runner(request: Phase08RuntimeRequest, allow_side_effect: bool) -> Phase08RuntimeResponse:
        calls.append((request.idempotency_key, allow_side_effect))
        return Phase08RuntimeResponse(
            runtime="legacy",
            request_hash=request.request_hash,
            output_ref=f"answer:{request.request_hash[:16]}",
            trace_ref=f"legacy-trace:{request.trace_id}",
            side_effect_ref=f"legacy-side-effect:{request.idempotency_key}" if allow_side_effect else None,
        )

    first = Phase08CutoverController(
        mode="canary",
        legacy_runner=legacy_runner,
        new_runtime=Phase08RunService(graph=build_phase08_run_graph(checkpointer=build_phase08_test_checkpointer())),
        side_effect_ledger=PostgresPhase08CutoverLedger(engine),
        audit=PostgresPhase08CutoverLedger(engine),
    )
    second = Phase08CutoverController(
        mode="canary",
        legacy_runner=legacy_runner,
        new_runtime=Phase08RunService(graph=build_phase08_run_graph(checkpointer=build_phase08_test_checkpointer())),
        side_effect_ledger=PostgresPhase08CutoverLedger(engine),
        audit=PostgresPhase08CutoverLedger(engine),
    )

    first_response = first.handle(request)
    second_response = second.handle(request)

    assert first_response.runtime == "phase08"
    assert second_response.side_effect_ref == first_response.side_effect_ref
    assert calls == [(request.idempotency_key, False), (request.idempotency_key, False)]
    with engine.connect() as conn:
        counts = conn.execute(
            text(
                """
                SELECT
                    (SELECT count(*) FROM agent_effect_claims
                     WHERE tenant_id = :tenant_id AND idempotency_key = :idempotency_key) AS effects,
                    (SELECT count(*) FROM agent_cutover_audit_events
                     WHERE tenant_id = :tenant_id AND request_id = :request_id AND mode = 'canary') AS audits
                """
            ),
            {
                "tenant_id": request.tenant_id,
                "idempotency_key": request.idempotency_key,
                "request_id": request.request_id,
            },
        ).mappings().one()
    assert dict(counts) == {"effects": 1, "audits": 1}

    conflicting = Phase08RuntimeRequest(
        request_id="request:p08:cutover:postgres:conflict",
        tenant_id=request.tenant_id,
        workspace_id=request.workspace_id,
        user_id=request.user_id,
        task_id=request.task_id,
        trace_id=request.trace_id,
        goal="different payload must conflict",
        idempotency_key=request.idempotency_key,
    )
    with pytest.raises(Phase08SideEffectClaimError, match="conflicting effect payload"):
        second.handle(conflicting)
    assert calls == [(request.idempotency_key, False), (request.idempotency_key, False)]


def test_phase08_graph_owner_port_and_final_gate_write_postgres_ledgers(engine) -> None:
    goal = _goal("goal:p08:graph-ledger")
    task = _task(goal, "task-contract:p08:graph-ledger")
    run = _run(task, "run:p08:graph-ledger")
    with AgentDomainUnitOfWork(engine) as repo:
        repo.record_goal_version(goal)
        repo.record_task_contract(task)
        repo.record_agent_run(run)

    step_service = Phase08StepService(
        graph=build_phase08_step_graph(
            checkpointer=build_phase08_test_checkpointer(),
            owner_port=PostgresPhase08OwnerPort(engine),
        )
    )
    step_state = step_service.run(
        {
            "tenant_id": task.tenant_id,
            "run_id": run.run_id,
            "thread_id": "thread:p08:graph-ledger:step",
            "trace_id": run.trace_id,
            "step_run_id": "step-run:p08:graph-ledger:1",
            "step_definition_id": "step-def:p08:graph-ledger:1",
            "plan_version_id": "plan:p08:graph-ledger:1",
            "controller_epoch": 1,
            "execution_epoch": 1,
            "owner_port": "knowledge",
            "owner_port_proposal": {"kind": "retrieve", "query": "phase08 graph ledger"},
            "owner_port_observation": {"status": "completed", "documents": ["doc:p08"]},
            "owner_port_acceptance": {"accepted": True, "schema": "phase08-answer-v1"},
            "evidence_refs": ["evidence:p08:graph-ledger"],
        }
    )

    assert step_state["owner_port_committed"] is True
    assert step_state["latest_acceptance_ref"] == "acceptance:step-run:p08:graph-ledger:1"
    assert step_state["effect_claim_ref"] == "effect-claim:step-run:p08:graph-ledger:1:knowledge"

    run_service = Phase08RunService(
        graph=build_phase08_run_graph(
            checkpointer=build_phase08_test_checkpointer(),
            final_gate_port=PostgresPhase08FinalGatePort(engine),
        )
    )
    final_state = run_service.start(
        {
            "tenant_id": task.tenant_id,
            "run_id": run.run_id,
            "thread_id": "thread:p08:graph-ledger:run",
            "trace_id": run.trace_id,
            "task_contract_id": task.task_contract_id,
            "active_goal_version_id": goal.goal_version_id,
            "security_context_ref": task.security_context_ref,
            "security_epoch_ref": task.security_epoch_ref,
            "current_security_epoch_ref": task.security_epoch_ref,
            "deadline_at": _now(),
            "observed_at": _now() - timedelta(hours=1),
            "budget_requested_units": 1,
            "budget_available_units": 10,
            "latest_acceptance_ref": step_state["latest_acceptance_ref"],
            "evidence_refs": ["evidence:p08:graph-ledger"],
            "budget_settlement_ref": "budget-settlement:p08:graph-ledger",
        }
    )

    assert final_state["final_gate_receipt_ref"] == f"final-gate:{run.run_id}"
    assert final_state["outcome_ref"] == f"run-outcome:{run.run_id}"
    with engine.connect() as conn:
        counts = conn.execute(
            text(
                """
                SELECT
                    (SELECT count(*) FROM agent_action_runs WHERE run_id = :run_id) AS actions,
                    (SELECT count(*) FROM agent_observations WHERE action_run_id = :action_run_id) AS observations,
                    (SELECT count(*) FROM agent_step_acceptances WHERE step_run_id = :step_run_id) AS acceptances,
                    (SELECT count(*) FROM agent_effect_claims WHERE effect_claim_id = :effect_claim_id) AS effects,
                    (SELECT count(*) FROM agent_final_gate_receipts WHERE run_id = :run_id) AS final_gates,
                    (SELECT count(*) FROM agent_run_outcomes WHERE run_id = :run_id) AS outcomes
                """
            ),
            {
                "run_id": run.run_id,
                "action_run_id": "action:step-run:p08:graph-ledger:1",
                "step_run_id": "step-run:p08:graph-ledger:1",
                "effect_claim_id": "effect-claim:step-run:p08:graph-ledger:1:knowledge",
            },
        ).mappings().one()
    assert dict(counts) == {
        "actions": 1,
        "observations": 1,
        "acceptances": 1,
        "effects": 1,
        "final_gates": 1,
        "outcomes": 1,
    }


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
