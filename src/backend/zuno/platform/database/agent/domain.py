from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from sqlalchemy import Connection, Engine, text
from sqlalchemy.exc import IntegrityError

from zuno.agent.domain import (
    AgentDomainConflict,
    AgentDomainError,
    AgentRun,
    AgentRunStatus,
    BudgetReservation,
    BudgetReservationStatus,
    BudgetSettlement,
    DeterministicStepDefinition,
    ExecutionContextSnapshot,
    GoalInputClassification,
    GoalVersion,
    PlanVersion,
    PlanVersionStatus,
    StepExecutorType,
    TaskContract,
)


class AgentDomainPersistenceError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class AgentDomainReceipt:
    ref: str
    status: str
    aggregate_version: int
    domain_generation: int | None = None


class AgentDomainUnitOfWork:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def __enter__(self) -> "AgentDomainRepository":
        self._connection = self.engine.connect()
        self._transaction = self._connection.begin()
        return AgentDomainRepository(self._connection)

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        try:
            if exc_type is None:
                self._transaction.commit()
            else:
                self._transaction.rollback()
        finally:
            self._connection.close()


class AgentDomainRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def record_goal_version(self, goal: GoalVersion) -> AgentDomainReceipt:
        self.connection.execute(
            text(
                """
                INSERT INTO agent_goal_versions (
                    goal_version_id, tenant_id, workspace_id, principal_id,
                    goal_sequence, input_classification, objective_hash,
                    output_contract_ref, constraints_hash
                )
                VALUES (
                    :goal_version_id, :tenant_id, :workspace_id, :principal_id,
                    :goal_sequence, :input_classification, :objective_hash,
                    :output_contract_ref, :constraints_hash
                )
                """
            ),
            {
                **_goal_params(goal),
                "input_classification": goal.input_classification.value,
            },
        )
        return AgentDomainReceipt(goal.goal_version_id, "RECORDED", 1)

    def record_task_contract(self, task: TaskContract) -> AgentDomainReceipt:
        self.connection.execute(
            text(
                """
                INSERT INTO agent_task_contracts (
                    task_contract_id, tenant_id, workspace_id, principal_id,
                    goal_version_id, idempotency_key, security_context_ref,
                    security_epoch_ref, deadline_at, budget_ref, status, aggregate_version
                )
                VALUES (
                    :task_contract_id, :tenant_id, :workspace_id, :principal_id,
                    :goal_version_id, :idempotency_key, :security_context_ref,
                    :security_epoch_ref, :deadline_at, :budget_ref, :status, :aggregate_version
                )
                """
            ),
            _task_params(task),
        )
        return AgentDomainReceipt(task.task_contract_id, task.status, task.aggregate_version)

    def record_agent_run(self, run: AgentRun) -> AgentDomainReceipt:
        self.connection.execute(
            text(
                """
                INSERT INTO agent_domain_runs (
                    run_id, tenant_id, workspace_id, principal_id, task_contract_id,
                    trace_id, status, aggregate_version, domain_generation,
                    started_at, ended_at, failure_code
                )
                VALUES (
                    :run_id, :tenant_id, :workspace_id, :principal_id, :task_contract_id,
                    :trace_id, :status, :aggregate_version, :domain_generation,
                    :started_at, :ended_at, :failure_code
                )
                """
            ),
            _run_params(run),
        )
        self._record_event(
            run_id=run.run_id,
            tenant_id=run.tenant_id,
            sequence_no=run.domain_generation,
            event_type="agent_run.created",
            from_status=None,
            to_status=run.status.value,
            domain_generation=run.domain_generation,
            payload={"task_contract_id": run.task_contract_id, "trace_id": run.trace_id},
        )
        return AgentDomainReceipt(run.run_id, run.status.value, run.aggregate_version, run.domain_generation)

    def load_run(self, run_id: str) -> AgentRun:
        row = self.connection.execute(
            text("SELECT * FROM agent_domain_runs WHERE run_id = :run_id"),
            {"run_id": run_id},
        ).mappings().one()
        return _run_from_row(row)

    def transition_run(self, next_run: AgentRun, *, expected_version: int) -> AgentDomainReceipt:
        previous = self.load_run(next_run.run_id)
        if previous.aggregate_version != expected_version:
            raise AgentDomainConflict(
                f"expected aggregate_version {expected_version}, observed {previous.aggregate_version}"
            )
        if next_run.aggregate_version != expected_version + 1:
            raise AgentDomainError("next_run aggregate_version must increment exactly once")
        result = self.connection.execute(
            text(
                """
                UPDATE agent_domain_runs
                SET status = :status,
                    aggregate_version = :next_version,
                    domain_generation = :domain_generation,
                    started_at = :started_at,
                    ended_at = :ended_at,
                    failure_code = :failure_code
                WHERE run_id = :run_id
                  AND aggregate_version = :expected_version
                """
            ),
            {
                "run_id": next_run.run_id,
                "status": next_run.status.value,
                "next_version": next_run.aggregate_version,
                "domain_generation": next_run.domain_generation,
                "started_at": next_run.started_at,
                "ended_at": next_run.ended_at,
                "failure_code": next_run.failure_code,
                "expected_version": expected_version,
            },
        )
        if result.rowcount != 1:
            raise AgentDomainConflict(f"stale AgentRun transition for {next_run.run_id}")
        self._record_event(
            run_id=next_run.run_id,
            tenant_id=next_run.tenant_id,
            sequence_no=next_run.domain_generation,
            event_type=f"agent_run.{next_run.status.value.lower()}",
            from_status=previous.status.value,
            to_status=next_run.status.value,
            domain_generation=next_run.domain_generation,
            payload={"aggregate_version": next_run.aggregate_version},
        )
        return AgentDomainReceipt(
            next_run.run_id,
            next_run.status.value,
            next_run.aggregate_version,
            next_run.domain_generation,
        )

    def record_plan_version(self, plan: PlanVersion) -> AgentDomainReceipt:
        self.connection.execute(
            text(
                """
                INSERT INTO agent_plan_versions (
                    plan_version_id, tenant_id, workspace_id, goal_version_id,
                    plan_kind, status, plan_hash, aggregate_version, activated_at
                )
                VALUES (
                    :plan_version_id, :tenant_id, :workspace_id, :goal_version_id,
                    :plan_kind, :status, :plan_hash, :aggregate_version, :activated_at
                )
                """
            ),
            _plan_params(plan),
        )
        for step in plan.steps:
            self.record_step_definition(step)
        return AgentDomainReceipt(plan.plan_version_id, plan.status.value, plan.aggregate_version)

    def record_step_definition(self, step: DeterministicStepDefinition) -> AgentDomainReceipt:
        self.connection.execute(
            text(
                """
                INSERT INTO agent_plan_step_definitions (
                    step_definition_id, plan_version_id, tenant_id, step_no,
                    objective_ref, input_contract_ref, output_contract_ref,
                    acceptance_refs, executor_type, required_evidence_refs,
                    budget_ref, deadline_at, step_hash
                )
                VALUES (
                    :step_definition_id, :plan_version_id, :tenant_id, :step_no,
                    :objective_ref, :input_contract_ref, :output_contract_ref,
                    CAST(:acceptance_refs AS JSON), :executor_type, CAST(:required_evidence_refs AS JSON),
                    :budget_ref, :deadline_at, :step_hash
                )
                """
            ),
            _step_params(step),
        )
        return AgentDomainReceipt(step.step_definition_id, "RECORDED", 1)

    def load_plan_version(self, plan_version_id: str) -> PlanVersion:
        plan_row = self.connection.execute(
            text("SELECT * FROM agent_plan_versions WHERE plan_version_id = :plan_version_id"),
            {"plan_version_id": plan_version_id},
        ).mappings().one()
        step_rows = self.connection.execute(
            text(
                """
                SELECT * FROM agent_plan_step_definitions
                WHERE plan_version_id = :plan_version_id
                ORDER BY step_no
                """
            ),
            {"plan_version_id": plan_version_id},
        ).mappings().all()
        return _plan_from_rows(plan_row, step_rows)

    def activate_plan_version(self, next_plan: PlanVersion, *, expected_version: int) -> AgentDomainReceipt:
        previous = self.load_plan_version(next_plan.plan_version_id)
        if previous.aggregate_version != expected_version:
            raise AgentDomainConflict(
                f"expected aggregate_version {expected_version}, observed {previous.aggregate_version}"
            )
        result = self.connection.execute(
            text(
                """
                UPDATE agent_plan_versions
                SET status = :status,
                    aggregate_version = :next_version,
                    activated_at = :activated_at
                WHERE plan_version_id = :plan_version_id
                  AND aggregate_version = :expected_version
                  AND status = 'DRAFT'
                """
            ),
            {
                "plan_version_id": next_plan.plan_version_id,
                "status": next_plan.status.value,
                "next_version": next_plan.aggregate_version,
                "activated_at": next_plan.activated_at,
                "expected_version": expected_version,
            },
        )
        if result.rowcount != 1:
            raise AgentDomainConflict(f"stale PlanVersion activation for {next_plan.plan_version_id}")
        return AgentDomainReceipt(next_plan.plan_version_id, next_plan.status.value, next_plan.aggregate_version)

    def record_budget_reservation(self, reservation: BudgetReservation) -> AgentDomainReceipt:
        self.connection.execute(
            text(
                """
                INSERT INTO agent_budget_reservations (
                    budget_reservation_id, run_id, tenant_id, budget_ref, reservation_scope,
                    requested_units, reserved_units, status, aggregate_version
                )
                VALUES (
                    :budget_reservation_id, :run_id, :tenant_id, :budget_ref, :reservation_scope,
                    :requested_units, :reserved_units, :status, :aggregate_version
                )
                """
            ),
            _budget_reservation_params(reservation),
        )
        return AgentDomainReceipt(
            reservation.budget_reservation_id,
            reservation.status.value,
            reservation.aggregate_version,
        )

    def load_budget_reservation(self, budget_reservation_id: str) -> BudgetReservation:
        row = self.connection.execute(
            text("SELECT * FROM agent_budget_reservations WHERE budget_reservation_id = :budget_reservation_id"),
            {"budget_reservation_id": budget_reservation_id},
        ).mappings().one()
        return _budget_reservation_from_row(row)

    def settle_budget_reservation(
        self,
        next_reservation: BudgetReservation,
        settlement: BudgetSettlement,
        *,
        expected_version: int,
    ) -> AgentDomainReceipt:
        previous = self.load_budget_reservation(next_reservation.budget_reservation_id)
        if previous.aggregate_version != expected_version:
            raise AgentDomainConflict(
                f"expected aggregate_version {expected_version}, observed {previous.aggregate_version}"
            )
        result = self.connection.execute(
            text(
                """
                UPDATE agent_budget_reservations
                SET status = :status,
                    aggregate_version = :next_version
                WHERE budget_reservation_id = :budget_reservation_id
                  AND aggregate_version = :expected_version
                  AND status = 'RESERVED'
                """
            ),
            {
                "budget_reservation_id": next_reservation.budget_reservation_id,
                "status": next_reservation.status.value,
                "next_version": next_reservation.aggregate_version,
                "expected_version": expected_version,
            },
        )
        if result.rowcount != 1:
            raise AgentDomainConflict(f"stale BudgetReservation settlement for {next_reservation.budget_reservation_id}")
        self.connection.execute(
            text(
                """
                INSERT INTO agent_budget_settlements (
                    budget_settlement_id, budget_reservation_id, run_id, tenant_id,
                    consumed_units, released_units, reason_ref
                )
                VALUES (
                    :budget_settlement_id, :budget_reservation_id, :run_id, :tenant_id,
                    :consumed_units, :released_units, :reason_ref
                )
                """
            ),
            _budget_settlement_params(settlement),
        )
        return AgentDomainReceipt(
            next_reservation.budget_reservation_id,
            next_reservation.status.value,
            next_reservation.aggregate_version,
        )

    def record_execution_context_snapshot(self, snapshot: ExecutionContextSnapshot) -> AgentDomainReceipt:
        self.connection.execute(
            text(
                """
                INSERT INTO agent_execution_context_snapshots (
                    execution_snapshot_id, run_id, tenant_id, workspace_id, principal_id,
                    task_contract_id, security_context_ref, security_epoch_ref, model_policy_ref,
                    capability_profile_ref, knowledge_snapshot_ref, answer_policy_ref,
                    budget_reservation_id, deadline_at, context_hash
                )
                VALUES (
                    :execution_snapshot_id, :run_id, :tenant_id, :workspace_id, :principal_id,
                    :task_contract_id, :security_context_ref, :security_epoch_ref, :model_policy_ref,
                    :capability_profile_ref, :knowledge_snapshot_ref, :answer_policy_ref,
                    :budget_reservation_id, :deadline_at, :context_hash
                )
                """
            ),
            _execution_snapshot_params(snapshot),
        )
        return AgentDomainReceipt(snapshot.execution_snapshot_id, "RECORDED", 1)

    def load_execution_context_snapshot(self, execution_snapshot_id: str) -> ExecutionContextSnapshot:
        row = self.connection.execute(
            text(
                """
                SELECT * FROM agent_execution_context_snapshots
                WHERE execution_snapshot_id = :execution_snapshot_id
                """
            ),
            {"execution_snapshot_id": execution_snapshot_id},
        ).mappings().one()
        return _execution_snapshot_from_row(row)

    def find_task_contract_by_idempotency(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        idempotency_key: str,
    ) -> TaskContract | None:
        row = self.connection.execute(
            text(
                """
                SELECT * FROM agent_task_contracts
                WHERE tenant_id = :tenant_id
                  AND workspace_id = :workspace_id
                  AND idempotency_key = :idempotency_key
                """
            ),
            {"tenant_id": tenant_id, "workspace_id": workspace_id, "idempotency_key": idempotency_key},
        ).mappings().first()
        return None if row is None else _task_from_row(row)

    def claim_request_idempotency(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        idempotency_key: str,
        payload: dict[str, Any],
        aggregate_ref: str,
        status: str = "claimed",
    ) -> AgentDomainReceipt:
        payload_hash = _canonical_hash(payload)
        result = self.connection.execute(
            text(
                """
                INSERT INTO agent_request_idempotency_keys(
                    idempotency_key, tenant_id, workspace_id, payload_hash, aggregate_ref, status
                ) VALUES (
                    :idempotency_key, :tenant_id, :workspace_id, :payload_hash, :aggregate_ref, :status
                )
                ON CONFLICT (tenant_id, idempotency_key) DO NOTHING
                """
            ),
            {
                "idempotency_key": idempotency_key,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "payload_hash": payload_hash,
                "aggregate_ref": aggregate_ref,
                "status": status,
            },
        )
        if result.rowcount != 1:
            existing = self.connection.execute(
                text(
                    """
                    SELECT payload_hash, aggregate_ref, status
                    FROM agent_request_idempotency_keys
                    WHERE tenant_id = :tenant_id AND idempotency_key = :idempotency_key
                    """
                ),
                {"tenant_id": tenant_id, "idempotency_key": idempotency_key},
            ).mappings().first()
            if existing and existing["payload_hash"] == payload_hash:
                return AgentDomainReceipt(str(existing["aggregate_ref"]), f"duplicate:{existing['status']}", 1)
            raise AgentDomainConflict(f"conflicting idempotency payload for {idempotency_key}")
        return AgentDomainReceipt(aggregate_ref, status, 1)

    def claim_effect(
        self,
        *,
        effect_claim_id: str,
        tenant_id: str,
        idempotency_key: str,
        payload: dict[str, Any],
        owner_port: str,
        effect_ref: str,
        status: str = "claimed",
    ) -> AgentDomainReceipt:
        payload_hash = _canonical_hash(payload)
        result = self.connection.execute(
            text(
                """
                INSERT INTO agent_effect_claims(
                    effect_claim_id, tenant_id, idempotency_key, payload_hash,
                    owner_port, status, effect_ref
                ) VALUES (
                    :effect_claim_id, :tenant_id, :idempotency_key, :payload_hash,
                    :owner_port, :status, :effect_ref
                )
                ON CONFLICT (tenant_id, idempotency_key) DO NOTHING
                """
            ),
            {
                "effect_claim_id": effect_claim_id,
                "tenant_id": tenant_id,
                "idempotency_key": idempotency_key,
                "payload_hash": payload_hash,
                "owner_port": owner_port,
                "status": status,
                "effect_ref": effect_ref,
            },
        )
        if result.rowcount != 1:
            existing = self.connection.execute(
                text(
                    """
                    SELECT effect_claim_id, payload_hash, status
                    FROM agent_effect_claims
                    WHERE tenant_id = :tenant_id AND idempotency_key = :idempotency_key
                    """
                ),
                {"tenant_id": tenant_id, "idempotency_key": idempotency_key},
            ).mappings().first()
            if existing and existing["payload_hash"] == payload_hash:
                return AgentDomainReceipt(str(existing["effect_claim_id"]), f"duplicate:{existing['status']}", 1)
            raise AgentDomainConflict(f"conflicting effect payload for {idempotency_key}")
        return AgentDomainReceipt(effect_claim_id, status, 1)

    def has_effect_claim(self, *, tenant_id: str, idempotency_key: str) -> bool:
        return (
            self.connection.execute(
                text(
                    """
                    SELECT 1
                    FROM agent_effect_claims
                    WHERE tenant_id = :tenant_id
                      AND idempotency_key = :idempotency_key
                    LIMIT 1
                    """
                ),
                {"tenant_id": tenant_id, "idempotency_key": idempotency_key},
            ).first()
            is not None
        )

    def record_action_observation_acceptance(
        self,
        *,
        tenant_id: str,
        run_id: str,
        step_run_id: str,
        owner_port: str,
        proposal: dict[str, Any],
        observation: dict[str, Any],
        acceptance: dict[str, Any],
        trace_ref: str,
        evidence_refs: list[str],
        status: str = "accepted",
    ) -> AgentDomainReceipt:
        action_run_id = f"action:{step_run_id}"
        observation_id = f"observation:{step_run_id}"
        acceptance_id = f"acceptance:{step_run_id}"
        proposal_hash = _canonical_hash(proposal)
        observation_hash = _canonical_hash(observation)
        acceptance_hash = _canonical_hash(acceptance)
        result = self.connection.execute(
            text(
                """
                INSERT INTO agent_action_runs(
                    action_run_id, tenant_id, run_id, step_run_id, owner_port,
                    proposal_hash, status, trace_ref
                ) VALUES (
                    :action_run_id, :tenant_id, :run_id, :step_run_id, :owner_port,
                    :proposal_hash, :status, :trace_ref
                )
                ON CONFLICT (action_run_id) DO NOTHING
                """
            ),
            {
                "action_run_id": action_run_id,
                "tenant_id": tenant_id,
                "run_id": run_id,
                "step_run_id": step_run_id,
                "owner_port": owner_port,
                "proposal_hash": proposal_hash,
                "status": status,
                "trace_ref": trace_ref,
            },
        )
        if result.rowcount != 1:
            existing = self.connection.execute(
                text(
                    """
                    SELECT proposal_hash, owner_port, status
                    FROM agent_action_runs
                    WHERE action_run_id = :action_run_id
                    """
                ),
                {"action_run_id": action_run_id},
            ).mappings().first()
            if (
                not existing
                or existing["proposal_hash"] != proposal_hash
                or existing["owner_port"] != owner_port
            ):
                raise AgentDomainConflict(f"conflicting action run for {step_run_id}")

        result = self.connection.execute(
            text(
                """
                INSERT INTO agent_observations(
                    observation_id, tenant_id, action_run_id, observation_hash, status, evidence_refs
                ) VALUES (
                    :observation_id, :tenant_id, :action_run_id, :observation_hash, :status, CAST(:evidence_refs AS JSON)
                )
                ON CONFLICT (observation_id) DO NOTHING
                """
            ),
            {
                "observation_id": observation_id,
                "tenant_id": tenant_id,
                "action_run_id": action_run_id,
                "observation_hash": observation_hash,
                "status": status,
                "evidence_refs": json.dumps(evidence_refs, sort_keys=True, separators=(",", ":")),
            },
        )
        if result.rowcount != 1:
            existing = self.connection.execute(
                text(
                    """
                    SELECT action_run_id, observation_hash, status
                    FROM agent_observations
                    WHERE observation_id = :observation_id
                    """
                ),
                {"observation_id": observation_id},
            ).mappings().first()
            if (
                not existing
                or existing["action_run_id"] != action_run_id
                or existing["observation_hash"] != observation_hash
            ):
                raise AgentDomainConflict(f"conflicting observation for {step_run_id}")

        result = self.connection.execute(
            text(
                """
                INSERT INTO agent_step_acceptances(
                    acceptance_id, tenant_id, step_run_id, observation_id, acceptance_hash, status
                ) VALUES (
                    :acceptance_id, :tenant_id, :step_run_id, :observation_id, :acceptance_hash, :status
                )
                ON CONFLICT (tenant_id, step_run_id) DO NOTHING
                """
            ),
            {
                "acceptance_id": acceptance_id,
                "tenant_id": tenant_id,
                "step_run_id": step_run_id,
                "observation_id": observation_id,
                "acceptance_hash": acceptance_hash,
                "status": status,
            },
        )
        if result.rowcount != 1:
            existing = self.connection.execute(
                text(
                    """
                    SELECT acceptance_id, observation_id, acceptance_hash, status
                    FROM agent_step_acceptances
                    WHERE tenant_id = :tenant_id AND step_run_id = :step_run_id
                    """
                ),
                {"tenant_id": tenant_id, "step_run_id": step_run_id},
            ).mappings().first()
            if (
                not existing
                or existing["observation_id"] != observation_id
                or existing["acceptance_hash"] != acceptance_hash
            ):
                raise AgentDomainConflict(f"conflicting step acceptance for {step_run_id}")
            return AgentDomainReceipt(str(existing["acceptance_id"]), f"duplicate:{existing['status']}", 1)
        return AgentDomainReceipt(acceptance_id, status, 1)

    def record_final_gate_and_outcome(
        self,
        *,
        tenant_id: str,
        run_id: str,
        decision: str,
        answer_policy_ref: str,
        evidence_ref: str,
        security_decision_ref: str,
        budget_settlement_ref: str,
        step_acceptance_ref: str,
        publication_eligible: bool,
        outcome_status: str,
        publication_ref: str | None,
    ) -> AgentDomainReceipt:
        final_gate_id = f"final-gate:{run_id}"
        outcome_id = f"run-outcome:{run_id}"
        decision_payload = {
            "run_id": run_id,
            "decision": decision,
            "answer_policy_ref": answer_policy_ref,
            "evidence_ref": evidence_ref,
            "security_decision_ref": security_decision_ref,
            "budget_settlement_ref": budget_settlement_ref,
            "step_acceptance_ref": step_acceptance_ref,
            "publication_eligible": publication_eligible,
        }
        decision_hash = _canonical_hash(decision_payload)
        result = self.connection.execute(
            text(
                """
                INSERT INTO agent_final_gate_receipts(
                    final_gate_id, tenant_id, run_id, decision, decision_hash,
                    answer_policy_ref, evidence_ref, security_decision_ref,
                    budget_settlement_ref, step_acceptance_ref, publication_eligible
                ) VALUES (
                    :final_gate_id, :tenant_id, :run_id, :decision, :decision_hash,
                    :answer_policy_ref, :evidence_ref, :security_decision_ref,
                    :budget_settlement_ref, :step_acceptance_ref, :publication_eligible
                )
                ON CONFLICT (tenant_id, run_id) DO NOTHING
                """
            ),
            {
                "final_gate_id": final_gate_id,
                "tenant_id": tenant_id,
                "run_id": run_id,
                "decision": decision,
                "decision_hash": decision_hash,
                "answer_policy_ref": answer_policy_ref,
                "evidence_ref": evidence_ref,
                "security_decision_ref": security_decision_ref,
                "budget_settlement_ref": budget_settlement_ref,
                "step_acceptance_ref": step_acceptance_ref,
                "publication_eligible": publication_eligible,
            },
        )
        if result.rowcount != 1:
            existing = self.connection.execute(
                text(
                    """
                    SELECT final_gate_id, decision_hash, decision
                    FROM agent_final_gate_receipts
                    WHERE tenant_id = :tenant_id AND run_id = :run_id
                    """
                ),
                {"tenant_id": tenant_id, "run_id": run_id},
            ).mappings().first()
            if not existing or existing["decision_hash"] != decision_hash:
                raise AgentDomainConflict(f"conflicting final gate for {run_id}")
            final_gate_id = str(existing["final_gate_id"])
        outcome_hash = _canonical_hash(
            {
                "run_id": run_id,
                "status": outcome_status,
                "final_gate_id": final_gate_id,
                "publication_ref": publication_ref,
            }
        )
        result = self.connection.execute(
            text(
                """
                INSERT INTO agent_run_outcomes(
                    run_outcome_id, tenant_id, run_id, final_gate_id, status, outcome_hash, publication_ref
                ) VALUES (
                    :run_outcome_id, :tenant_id, :run_id, :final_gate_id, :status, :outcome_hash, :publication_ref
                )
                ON CONFLICT (tenant_id, run_id) DO NOTHING
                """
            ),
            {
                "run_outcome_id": outcome_id,
                "tenant_id": tenant_id,
                "run_id": run_id,
                "final_gate_id": final_gate_id,
                "status": outcome_status,
                "outcome_hash": outcome_hash,
                "publication_ref": publication_ref,
            },
        )
        if result.rowcount != 1:
            existing = self.connection.execute(
                text(
                    """
                    SELECT run_outcome_id, outcome_hash, status
                    FROM agent_run_outcomes
                    WHERE tenant_id = :tenant_id AND run_id = :run_id
                    """
                ),
                {"tenant_id": tenant_id, "run_id": run_id},
            ).mappings().first()
            if existing and existing["outcome_hash"] == outcome_hash:
                return AgentDomainReceipt(str(existing["run_outcome_id"]), f"duplicate:{existing['status']}", 1)
            raise AgentDomainConflict(f"conflicting run outcome for {run_id}")
        return AgentDomainReceipt(outcome_id, outcome_status, 1)

    def record_signal(
        self,
        *,
        signal_id: str,
        tenant_id: str,
        run_id: str,
        signal_type: str,
        payload: dict[str, Any],
        status: str,
    ) -> AgentDomainReceipt:
        payload_hash = _canonical_hash(payload)
        result = self.connection.execute(
            text(
                """
                INSERT INTO agent_runtime_signals(
                    signal_id, tenant_id, run_id, signal_type, payload_hash, status
                ) VALUES (
                    :signal_id, :tenant_id, :run_id, :signal_type, :payload_hash, :status
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "signal_id": signal_id,
                "tenant_id": tenant_id,
                "run_id": run_id,
                "signal_type": signal_type,
                "payload_hash": payload_hash,
                "status": status,
            },
        )
        if result.rowcount != 1:
            same_id = self.connection.execute(
                text(
                    """
                    SELECT signal_id, tenant_id, run_id, signal_type, payload_hash, status
                    FROM agent_runtime_signals
                    WHERE signal_id = :signal_id
                    """
                ),
                {"signal_id": signal_id},
            ).mappings().first()
            if (
                same_id
                and str(same_id["tenant_id"]) == str(tenant_id)
                and str(same_id["run_id"]) == str(run_id)
                and same_id["signal_type"] == signal_type
                and same_id["payload_hash"] == payload_hash
                and same_id["status"] == status
            ):
                return AgentDomainReceipt(str(same_id["signal_id"]), f"duplicate:{same_id['status']}", 1)
            existing = self.connection.execute(
                text(
                    """
                    SELECT signal_id, status
                    FROM agent_runtime_signals
                    WHERE tenant_id = :tenant_id
                      AND run_id = :run_id
                      AND signal_type = :signal_type
                      AND payload_hash = :payload_hash
                    """
                ),
                {
                    "tenant_id": tenant_id,
                    "run_id": run_id,
                    "signal_type": signal_type,
                    "payload_hash": payload_hash,
                },
            ).mappings().first()
            if existing:
                return AgentDomainReceipt(str(existing["signal_id"]), f"duplicate:{existing['status']}", 1)
            raise AgentDomainConflict(f"conflicting signal for {run_id}")
        return AgentDomainReceipt(signal_id, status, 1)

    def record_reconciliation_finding(
        self,
        *,
        finding_id: str,
        tenant_id: str,
        run_id: str,
        status: str,
        fact_owner: str,
        auto_repair: bool,
        replay_allowed: bool,
        terminate_run: bool,
        audit_event_ref: str,
        payload: dict[str, Any],
    ) -> AgentDomainReceipt:
        payload_hash = _canonical_hash(payload)
        result = self.connection.execute(
            text(
                """
                INSERT INTO agent_reconciliation_findings(
                    finding_id, tenant_id, run_id, status, fact_owner,
                    auto_repair, replay_allowed, terminate_run, audit_event_ref, payload_hash
                ) VALUES (
                    :finding_id, :tenant_id, :run_id, :status, :fact_owner,
                    :auto_repair, :replay_allowed, :terminate_run, :audit_event_ref, :payload_hash
                )
                ON CONFLICT (finding_id) DO NOTHING
                """
            ),
            {
                "finding_id": finding_id,
                "tenant_id": tenant_id,
                "run_id": run_id,
                "status": status,
                "fact_owner": fact_owner,
                "auto_repair": auto_repair,
                "replay_allowed": replay_allowed,
                "terminate_run": terminate_run,
                "audit_event_ref": audit_event_ref,
                "payload_hash": payload_hash,
            },
        )
        if result.rowcount != 1:
            existing = self.connection.execute(
                text(
                    """
                    SELECT tenant_id, run_id, status, fact_owner, auto_repair,
                           replay_allowed, terminate_run, audit_event_ref, payload_hash
                    FROM agent_reconciliation_findings
                    WHERE finding_id = :finding_id
                    """
                ),
                {"finding_id": finding_id},
            ).mappings().first()
            if (
                existing
                and str(existing["tenant_id"]) == str(tenant_id)
                and str(existing["run_id"]) == str(run_id)
                and existing["status"] == status
                and existing["fact_owner"] == fact_owner
                and bool(existing["auto_repair"]) is bool(auto_repair)
                and bool(existing["replay_allowed"]) is bool(replay_allowed)
                and bool(existing["terminate_run"]) is bool(terminate_run)
                and existing["audit_event_ref"] == audit_event_ref
                and existing["payload_hash"] == payload_hash
            ):
                return AgentDomainReceipt(finding_id, f"duplicate:{existing['status']}", 1)
            raise AgentDomainConflict(f"conflicting reconciliation finding: {finding_id}")
        return AgentDomainReceipt(finding_id, status, 1)

    def record_cutover_audit_event(
        self,
        *,
        cutover_event_id: str,
        tenant_id: str,
        workspace_id: str,
        request_id: str,
        mode: str,
        primary_runtime: str,
        effect_committed: bool,
        fallback_allowed: bool,
        request_hash: str,
        trace_ref: str,
    ) -> AgentDomainReceipt:
        result = self.connection.execute(
            text(
                """
                INSERT INTO agent_cutover_audit_events(
                    cutover_event_id, tenant_id, workspace_id, request_id, mode,
                    primary_runtime, effect_committed, fallback_allowed, request_hash, trace_ref
                ) VALUES (
                    :cutover_event_id, :tenant_id, :workspace_id, :request_id, :mode,
                    :primary_runtime, :effect_committed, :fallback_allowed, :request_hash, :trace_ref
                )
                ON CONFLICT (tenant_id, request_id, mode) DO NOTHING
                """
            ),
            {
                "cutover_event_id": cutover_event_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "request_id": request_id,
                "mode": mode,
                "primary_runtime": primary_runtime,
                "effect_committed": effect_committed,
                "fallback_allowed": fallback_allowed,
                "request_hash": request_hash,
                "trace_ref": trace_ref,
            },
        )
        if result.rowcount != 1:
            existing = self.connection.execute(
                text(
                    """
                    SELECT cutover_event_id, primary_runtime, effect_committed,
                           fallback_allowed, request_hash
                    FROM agent_cutover_audit_events
                    WHERE tenant_id = :tenant_id
                      AND request_id = :request_id
                      AND mode = :mode
                    """
                ),
                {"tenant_id": tenant_id, "request_id": request_id, "mode": mode},
            ).mappings().first()
            if (
                existing
                and existing["primary_runtime"] == primary_runtime
                and existing["effect_committed"] == effect_committed
                and existing["fallback_allowed"] == fallback_allowed
                and existing["request_hash"] == request_hash
            ):
                return AgentDomainReceipt(str(existing["cutover_event_id"]), f"duplicate:{mode}", 1)
            raise AgentDomainConflict(f"conflicting cutover audit event for {request_id}:{mode}")
        return AgentDomainReceipt(cutover_event_id, mode, 1)

    def _record_event(
        self,
        *,
        run_id: str,
        tenant_id: str,
        sequence_no: int,
        event_type: str,
        from_status: str | None,
        to_status: str,
        domain_generation: int,
        payload: dict[str, Any],
    ) -> None:
        event_id = f"{run_id}:event:{sequence_no}"
        try:
            self.connection.execute(
                text(
                    """
                    INSERT INTO agent_domain_events (
                        event_id, run_id, tenant_id, sequence_no, event_type,
                        from_status, to_status, domain_generation, payload
                    )
                    VALUES (
                        :event_id, :run_id, :tenant_id, :sequence_no, :event_type,
                        :from_status, :to_status, :domain_generation, CAST(:payload AS JSON)
                    )
                    """
                ),
                {
                    "event_id": event_id,
                    "run_id": run_id,
                    "tenant_id": tenant_id,
                    "sequence_no": sequence_no,
                    "event_type": event_type,
                    "from_status": from_status,
                    "to_status": to_status,
                    "domain_generation": domain_generation,
                    "payload": json.dumps(payload, sort_keys=True, separators=(",", ":")),
                },
            )
        except IntegrityError as exc:
            raise AgentDomainConflict(f"duplicate AgentRun domain event: {event_id}") from exc


def _goal_params(goal: GoalVersion) -> dict[str, Any]:
    return {
        "goal_version_id": goal.goal_version_id,
        "tenant_id": goal.tenant_id,
        "workspace_id": goal.workspace_id,
        "principal_id": goal.principal_id,
        "goal_sequence": goal.goal_sequence,
        "objective_hash": goal.objective_hash,
        "output_contract_ref": goal.output_contract_ref,
        "constraints_hash": goal.constraints_hash,
    }


def _task_params(task: TaskContract) -> dict[str, Any]:
    return {
        "task_contract_id": task.task_contract_id,
        "tenant_id": task.tenant_id,
        "workspace_id": task.workspace_id,
        "principal_id": task.principal_id,
        "goal_version_id": task.goal_version_id,
        "idempotency_key": task.idempotency_key,
        "security_context_ref": task.security_context_ref,
        "security_epoch_ref": task.security_epoch_ref,
        "deadline_at": task.deadline_at,
        "budget_ref": task.budget_ref,
        "status": task.status,
        "aggregate_version": task.aggregate_version,
    }


def _run_params(run: AgentRun) -> dict[str, Any]:
    return {
        "run_id": run.run_id,
        "tenant_id": run.tenant_id,
        "workspace_id": run.workspace_id,
        "principal_id": run.principal_id,
        "task_contract_id": run.task_contract_id,
        "trace_id": run.trace_id,
        "status": run.status.value,
        "aggregate_version": run.aggregate_version,
        "domain_generation": run.domain_generation,
        "started_at": run.started_at,
        "ended_at": run.ended_at,
        "failure_code": run.failure_code,
    }


def _plan_params(plan: PlanVersion) -> dict[str, Any]:
    return {
        "plan_version_id": plan.plan_version_id,
        "tenant_id": plan.tenant_id,
        "workspace_id": plan.workspace_id,
        "goal_version_id": plan.goal_version_id,
        "plan_kind": plan.plan_kind,
        "status": plan.status.value,
        "plan_hash": plan.plan_hash,
        "aggregate_version": plan.aggregate_version,
        "activated_at": plan.activated_at,
    }


def _step_params(step: DeterministicStepDefinition) -> dict[str, Any]:
    return {
        "step_definition_id": step.step_definition_id,
        "plan_version_id": step.plan_version_id,
        "tenant_id": step.tenant_id,
        "step_no": step.step_no,
        "objective_ref": step.objective_ref,
        "input_contract_ref": step.input_contract_ref,
        "output_contract_ref": step.output_contract_ref,
        "acceptance_refs": json.dumps(list(step.acceptance_refs), sort_keys=True, separators=(",", ":")),
        "executor_type": step.executor_type.value,
        "required_evidence_refs": json.dumps(
            list(step.required_evidence_refs),
            sort_keys=True,
            separators=(",", ":"),
        ),
        "budget_ref": step.budget_ref,
        "deadline_at": step.deadline_at,
        "step_hash": step.step_hash,
    }


def _budget_reservation_params(reservation: BudgetReservation) -> dict[str, Any]:
    return {
        "budget_reservation_id": reservation.budget_reservation_id,
        "run_id": reservation.run_id,
        "tenant_id": reservation.tenant_id,
        "budget_ref": reservation.budget_ref,
        "reservation_scope": reservation.reservation_scope,
        "requested_units": reservation.requested_units,
        "reserved_units": reservation.reserved_units,
        "status": reservation.status.value,
        "aggregate_version": reservation.aggregate_version,
    }


def _budget_settlement_params(settlement: BudgetSettlement) -> dict[str, Any]:
    return {
        "budget_settlement_id": settlement.budget_settlement_id,
        "budget_reservation_id": settlement.budget_reservation_id,
        "run_id": settlement.run_id,
        "tenant_id": settlement.tenant_id,
        "consumed_units": settlement.consumed_units,
        "released_units": settlement.released_units,
        "reason_ref": settlement.reason_ref,
    }


def _execution_snapshot_params(snapshot: ExecutionContextSnapshot) -> dict[str, Any]:
    return {
        "execution_snapshot_id": snapshot.execution_snapshot_id,
        "run_id": snapshot.run_id,
        "tenant_id": snapshot.tenant_id,
        "workspace_id": snapshot.workspace_id,
        "principal_id": snapshot.principal_id,
        "task_contract_id": snapshot.task_contract_id,
        "security_context_ref": snapshot.security_context_ref,
        "security_epoch_ref": snapshot.security_epoch_ref,
        "model_policy_ref": snapshot.model_policy_ref,
        "capability_profile_ref": snapshot.capability_profile_ref,
        "knowledge_snapshot_ref": snapshot.knowledge_snapshot_ref,
        "answer_policy_ref": snapshot.answer_policy_ref,
        "budget_reservation_id": snapshot.budget_reservation_id,
        "deadline_at": snapshot.deadline_at,
        "context_hash": snapshot.context_hash,
    }


def _canonical_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    import hashlib

    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _task_from_row(row: Any) -> TaskContract:
    return TaskContract(
        task_contract_id=row["task_contract_id"],
        tenant_id=row["tenant_id"],
        workspace_id=row["workspace_id"],
        principal_id=row["principal_id"],
        goal_version_id=row["goal_version_id"],
        idempotency_key=row["idempotency_key"],
        security_context_ref=row["security_context_ref"],
        security_epoch_ref=row["security_epoch_ref"],
        deadline_at=row["deadline_at"],
        budget_ref=row["budget_ref"],
        status=row["status"],
        aggregate_version=row["aggregate_version"],
    )


def _run_from_row(row: Any) -> AgentRun:
    return AgentRun(
        run_id=row["run_id"],
        tenant_id=row["tenant_id"],
        workspace_id=row["workspace_id"],
        principal_id=row["principal_id"],
        task_contract_id=row["task_contract_id"],
        trace_id=row["trace_id"],
        status=AgentRunStatus(row["status"]),
        aggregate_version=row["aggregate_version"],
        domain_generation=row["domain_generation"],
        started_at=row["started_at"],
        ended_at=row["ended_at"],
        failure_code=row["failure_code"],
    )


def _step_from_row(row: Any) -> DeterministicStepDefinition:
    return DeterministicStepDefinition(
        step_definition_id=row["step_definition_id"],
        plan_version_id=row["plan_version_id"],
        tenant_id=row["tenant_id"],
        step_no=row["step_no"],
        objective_ref=row["objective_ref"],
        input_contract_ref=row["input_contract_ref"],
        output_contract_ref=row["output_contract_ref"],
        acceptance_refs=tuple(row["acceptance_refs"]),
        executor_type=StepExecutorType(row["executor_type"]),
        required_evidence_refs=tuple(row["required_evidence_refs"]),
        budget_ref=row["budget_ref"],
        deadline_at=row["deadline_at"],
        step_hash=row["step_hash"],
    )


def _plan_from_rows(plan_row: Any, step_rows: list[Any]) -> PlanVersion:
    return PlanVersion(
        plan_version_id=plan_row["plan_version_id"],
        tenant_id=plan_row["tenant_id"],
        workspace_id=plan_row["workspace_id"],
        goal_version_id=plan_row["goal_version_id"],
        plan_kind=plan_row["plan_kind"],
        status=PlanVersionStatus(plan_row["status"]),
        steps=tuple(_step_from_row(row) for row in step_rows),
        plan_hash=plan_row["plan_hash"],
        aggregate_version=plan_row["aggregate_version"],
        activated_at=plan_row["activated_at"],
    )


def _budget_reservation_from_row(row: Any) -> BudgetReservation:
    return BudgetReservation(
        budget_reservation_id=row["budget_reservation_id"],
        run_id=row["run_id"],
        tenant_id=row["tenant_id"],
        budget_ref=row["budget_ref"],
        reservation_scope=row["reservation_scope"],
        requested_units=row["requested_units"],
        reserved_units=row["reserved_units"],
        status=BudgetReservationStatus(row["status"]),
        aggregate_version=row["aggregate_version"],
    )


def _execution_snapshot_from_row(row: Any) -> ExecutionContextSnapshot:
    return ExecutionContextSnapshot(
        execution_snapshot_id=row["execution_snapshot_id"],
        run_id=row["run_id"],
        tenant_id=row["tenant_id"],
        workspace_id=row["workspace_id"],
        principal_id=row["principal_id"],
        task_contract_id=row["task_contract_id"],
        security_context_ref=row["security_context_ref"],
        security_epoch_ref=row["security_epoch_ref"],
        model_policy_ref=row["model_policy_ref"],
        capability_profile_ref=row["capability_profile_ref"],
        knowledge_snapshot_ref=row["knowledge_snapshot_ref"],
        answer_policy_ref=row["answer_policy_ref"],
        budget_reservation_id=row["budget_reservation_id"],
        deadline_at=row["deadline_at"],
        context_hash=row["context_hash"],
    )
