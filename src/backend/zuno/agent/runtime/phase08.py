from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterator, Protocol

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


PHASE08_RUN_SCHEMA = "phase08-run-v1"
PHASE08_STEP_SCHEMA = "phase08-step-v1"


class Phase08RuntimeError(ValueError):
    pass


class Phase08Conflict(Phase08RuntimeError):
    pass


class Phase08OwnerPort(Protocol):
    def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        ...


class Phase08FinalGatePort(Protocol):
    def commit(self, state: dict[str, Any]) -> dict[str, Any]:
        ...


@contextmanager
def phase08_postgres_checkpointer(*, conn_string: str) -> Iterator[Any]:
    if not conn_string:
        raise Phase08RuntimeError("PHASE08 production checkpointer requires a PostgreSQL connection string")
    with PostgresSaver.from_conn_string(conn_string) as saver:
        saver.setup()
        yield saver


def build_phase08_test_checkpointer() -> InMemorySaver:
    return InMemorySaver()


def build_phase08_run_graph(
    *,
    checkpointer: Any | None = None,
    final_gate_port: Phase08FinalGatePort | None = None,
) -> Any:
    if checkpointer is None:
        raise Phase08RuntimeError("PHASE08 run graph requires an explicit durable checkpointer")
    graph = StateGraph(dict)
    graph.add_node("initialize", _initialize_run)
    graph.add_node("authorize", _authorize_run)
    graph.add_node("context_snapshot", _build_execution_context)
    graph.add_node("create_plan", _plan_run)
    graph.add_node("validate_plan", _validate_plan)
    graph.add_node("activate_plan", _activate_plan)
    graph.add_node("execute_step", _execute_run)
    graph.add_node("final_gate", lambda state: _final_gate_run(state, final_gate_port=final_gate_port))
    graph.add_node("finalize", _finalize_run)
    graph.add_node("run_outcome", _run_outcome)
    graph.add_edge(START, "initialize")
    graph.add_edge("initialize", "authorize")
    graph.add_edge("authorize", "context_snapshot")
    graph.add_edge("context_snapshot", "create_plan")
    graph.add_edge("create_plan", "validate_plan")
    graph.add_edge("validate_plan", "activate_plan")
    graph.add_edge("activate_plan", "execute_step")
    graph.add_edge("execute_step", "final_gate")
    graph.add_edge("final_gate", "finalize")
    graph.add_edge("finalize", "run_outcome")
    graph.add_edge("run_outcome", END)
    return graph.compile(checkpointer=checkpointer)


def build_phase08_step_graph(
    *,
    checkpointer: Any | None = None,
    owner_port: Phase08OwnerPort | None = None,
) -> Any:
    if checkpointer is None:
        raise Phase08RuntimeError("PHASE08 step graph requires an explicit durable checkpointer")
    graph = StateGraph(dict)
    graph.add_node("load_step", _load_step)
    graph.add_node("resolve_input", _resolve_step_input)
    graph.add_node("security_gate", _step_security_gate)
    graph.add_node("proposal", _step_proposal)
    graph.add_node("deterministic_validation", _deterministic_validation)
    graph.add_node("execute_owner_port", lambda state: _execute_owner_port(state, owner_port=owner_port))
    graph.add_node("observation", _step_observation)
    graph.add_node("action_evaluation", _step_evaluation)
    graph.add_node("step_acceptance", _step_acceptance)
    graph.add_node("commit_step_result", _commit_step_result)
    graph.add_edge(START, "load_step")
    graph.add_edge("load_step", "resolve_input")
    graph.add_edge("resolve_input", "security_gate")
    graph.add_edge("security_gate", "proposal")
    graph.add_edge("proposal", "deterministic_validation")
    graph.add_edge("deterministic_validation", "execute_owner_port")
    graph.add_edge("execute_owner_port", "observation")
    graph.add_edge("observation", "action_evaluation")
    graph.add_edge("action_evaluation", "step_acceptance")
    graph.add_edge("step_acceptance", "commit_step_result")
    graph.add_edge("commit_step_result", END)
    return graph.compile(checkpointer=checkpointer)


@dataclass
class Phase08RunService:
    graph: Any

    def start(self, state: dict[str, Any]) -> dict[str, Any]:
        result = self.graph.invoke(dict(state), config=_thread_config(state))
        return _interrupted_state(self.graph, state, result)

    def resume(self, state: dict[str, Any]) -> dict[str, Any]:
        config = _thread_config(state)
        snapshot = self.graph.get_state(config)
        if not _snapshot_has_interrupt(snapshot):
            current_state = dict(snapshot.values or {})
            if not current_state:
                raise Phase08Conflict("resume requires an existing interrupt checkpoint")
            if current_state.get("phase") == "run_outcome" or current_state.get("finalization_status") in {
                "finalized",
                "cancelled",
                "blocked",
                "failed",
                "abstained",
            }:
                current_state["resume_status"] = "terminal:no_interrupt"
                return current_state
            raise Phase08Conflict("resume requires an active interrupt")
        return self.graph.invoke(Command(resume={"decision": "approved"}), config=config)

    def cancel(self, state: dict[str, Any], *, reason: str) -> dict[str, Any]:
        config = _thread_config(state)
        snapshot = self.graph.get_state(config)
        if _snapshot_has_interrupt(snapshot):
            return self.graph.invoke(Command(resume={"decision": "cancelled", "reason": reason}), config=config)
        next_state = dict(snapshot.values or state)
        signal = Phase08SignalRecord(
            signal_id=str(next_state.get("cancel_signal_id") or f"signal:{next_state.get('run_id', 'run')}:cancel"),
            run_id=str(next_state.get("run_id") or state.get("run_id")),
            security_epoch_ref=str(next_state.get("security_epoch_ref") or state.get("security_epoch_ref")),
            decision="deny",
            reason=reason,
            status="accepted",
        )
        next_state = append_signal(next_state, signal)
        next_state["interrupt_requested"] = False
        next_state["pending_interrupt_refs"] = []
        next_state["cancel_reason"] = reason
        next_state["finalization_status"] = "cancelled"
        next_state["phase"] = "finalize"
        return next_state

    def get_state(self, state: dict[str, Any]) -> dict[str, Any]:
        snapshot = self.graph.get_state(_thread_config(state))
        return dict(snapshot.values)


@dataclass
class Phase08StepService:
    graph: Any

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        return self.graph.invoke(dict(state), config=_thread_config(state))


@dataclass(frozen=True, slots=True)
class PostgresPhase08OwnerPort:
    engine: Any

    def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        tenant_id = _required_state_ref(state, "tenant_id")
        run_id = _required_state_ref(state, "run_id")
        step_run_id = _required_state_ref(state, "step_run_id")
        owner_port = str(state.get("owner_port") or "knowledge")
        trace_ref = str(state.get("trace_id") or state.get("trace_ref") or f"trace:{run_id}")
        proposal = dict(state.get("owner_port_proposal") or {"action_run_id": state.get("latest_action_run_id")})
        observation = dict(state.get("owner_port_observation") or {"status": "completed", "owner_port": owner_port})
        acceptance = dict(state.get("owner_port_acceptance") or {"accepted": True, "schema": "phase08-owner-port-v1"})
        evidence_refs = [str(item) for item in state.get("evidence_refs") or [f"evidence:{step_run_id}"]]
        effect_idempotency_key = str(state.get("effect_idempotency_key") or f"effect:{step_run_id}:{owner_port}")
        effect_claim_id = str(state.get("effect_claim_id") or f"effect-claim:{step_run_id}:{owner_port}")
        effect_ref = str(state.get("effect_ref") or effect_idempotency_key)
        from zuno.platform.database.agent import AgentDomainUnitOfWork

        with AgentDomainUnitOfWork(self.engine) as repo:
            effect = repo.claim_effect(
                effect_claim_id=effect_claim_id,
                tenant_id=tenant_id,
                idempotency_key=effect_idempotency_key,
                payload={
                    "owner_port": owner_port,
                    "step_run_id": step_run_id,
                    "proposal": proposal,
                    "effect_ref": effect_ref,
                },
                owner_port=owner_port,
                effect_ref=effect_ref,
            )
            acceptance_receipt = repo.record_action_observation_acceptance(
                tenant_id=tenant_id,
                run_id=run_id,
                step_run_id=step_run_id,
                owner_port=owner_port,
                proposal=proposal,
                observation=observation,
                acceptance=acceptance,
                trace_ref=trace_ref,
                evidence_refs=evidence_refs,
            )
        next_state = dict(state)
        next_state["owner_port"] = owner_port
        next_state["latest_action_run_id"] = f"action:{step_run_id}"
        next_state["latest_observation_ref"] = f"observation:{step_run_id}"
        next_state["latest_acceptance_ref"] = acceptance_receipt.ref
        next_state["effect_claim_ref"] = effect.ref
        next_state["owner_port_committed"] = True
        next_state["evidence_refs"] = evidence_refs
        return next_state


@dataclass(frozen=True, slots=True)
class PostgresPhase08FinalGatePort:
    engine: Any

    def commit(self, state: dict[str, Any]) -> dict[str, Any]:
        tenant_id = _required_state_ref(state, "tenant_id")
        run_id = _required_state_ref(state, "run_id")
        publication_ref = str(state.get("publication_receipt_ref") or f"publication:{run_id}")
        evidence_refs = list(state.get("evidence_refs") or [])
        evidence_ref = str(state.get("evidence_ref") or (evidence_refs[0] if evidence_refs else f"evidence:{run_id}"))
        step_acceptance_ref = str(
            state.get("latest_acceptance_ref")
            or state.get("step_acceptance_ref")
            or f"acceptance:{state.get('step_run_id', run_id)}"
        )
        from zuno.platform.database.agent import AgentDomainUnitOfWork

        with AgentDomainUnitOfWork(self.engine) as repo:
            outcome = repo.record_final_gate_and_outcome(
                tenant_id=tenant_id,
                run_id=run_id,
                decision=str(state.get("final_gate_decision") or "approved"),
                answer_policy_ref=str(state.get("answer_policy_ref") or "answer-policy:phase08"),
                evidence_ref=evidence_ref,
                security_decision_ref=str(
                    state.get("security_decision_ref")
                    or state.get("security_context_ref")
                    or state.get("security_epoch_ref")
                    or "security-decision:phase08"
                ),
                budget_settlement_ref=str(state.get("budget_settlement_ref") or f"budget-settlement:{run_id}"),
                step_acceptance_ref=step_acceptance_ref,
                publication_eligible=bool(state.get("publication_eligible", True)),
                outcome_status=str(state.get("outcome_status") or "completed"),
                publication_ref=publication_ref,
            )
        next_state = dict(state)
        next_state["final_gate_receipt_ref"] = f"final-gate:{run_id}"
        next_state["publication_receipt_ref"] = publication_ref
        next_state["outcome_receipt_ref"] = outcome.ref
        next_state["run_outcome_committed"] = True
        return next_state


@dataclass(frozen=True, slots=True)
class Phase08SignalRecord:
    signal_id: str
    run_id: str
    security_epoch_ref: str
    decision: str
    reason: str = ""
    status: str = "pending"
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def append_signal(state: dict[str, Any], signal: Phase08SignalRecord) -> dict[str, Any]:
    _require_refs(state)
    if signal.signal_id in {item["signal_id"] for item in state.get("signal_journal", [])}:
        raise Phase08Conflict("duplicate signal")
    if signal.run_id != state.get("run_id"):
        raise Phase08RuntimeError("wrong run for signal")
    if signal.security_epoch_ref != state.get("security_epoch_ref"):
        raise Phase08RuntimeError("wrong security epoch for signal")
    next_state = dict(state)
    journal = list(next_state.get("signal_journal") or [])
    journal.append(
        {
            "signal_id": signal.signal_id,
            "run_id": signal.run_id,
            "security_epoch_ref": signal.security_epoch_ref,
            "decision": signal.decision,
            "reason": signal.reason,
            "status": signal.status,
            "observed_at": signal.observed_at.astimezone(timezone.utc).isoformat(),
        }
    )
    next_state["signal_journal"] = journal
    if signal.decision == "deny":
        next_state["cancel_requested"] = True
        next_state["latest_control_decision_ref"] = "security-denied"
    return next_state


def reconcile_generations(
    *,
    domain_generation: int,
    checkpoint_generation: int,
    schema_version: str,
    controller_epoch: int | None = None,
    expected_controller_epoch: int | None = None,
) -> dict[str, Any]:
    if schema_version != PHASE08_RUN_SCHEMA:
        return _reconciliation_decision(
            status="stale_schema",
            reason=schema_version,
            fact_owner="domain",
            auto_repair=False,
            replay_allowed=False,
            terminate_run=True,
        )
    if (
        controller_epoch is not None
        and expected_controller_epoch is not None
        and controller_epoch != expected_controller_epoch
    ):
        return _reconciliation_decision(
            status="stale_controller_epoch",
            reason=f"{controller_epoch}!={expected_controller_epoch}",
            fact_owner="domain",
            auto_repair=False,
            replay_allowed=False,
            terminate_run=True,
        )
    if domain_generation < 0 or checkpoint_generation < 0:
        return _reconciliation_decision(
            status="unrecoverable_conflict",
            reason="negative generation",
            fact_owner="none",
            auto_repair=False,
            replay_allowed=False,
            terminate_run=True,
        )
    if domain_generation == 0 and checkpoint_generation == 0:
        return _reconciliation_decision(
            status="orphan_domain",
            reason="no domain fact or checkpoint generation",
            fact_owner="domain",
            auto_repair=False,
            replay_allowed=False,
            terminate_run=True,
        )
    if domain_generation == 0:
        return _reconciliation_decision(
            status="orphan_checkpoint",
            reason="checkpoint without domain fact",
            fact_owner="domain",
            auto_repair=False,
            replay_allowed=False,
            terminate_run=True,
        )
    if checkpoint_generation == 0:
        return _reconciliation_decision(
            status="orphan_domain",
            reason="domain fact without checkpoint",
            fact_owner="domain",
            auto_repair=True,
            replay_allowed=False,
            terminate_run=False,
        )
    if checkpoint_generation < domain_generation:
        return _reconciliation_decision(
            status="domain_ahead",
            reason="checkpoint behind domain",
            fact_owner="domain",
            auto_repair=True,
            replay_allowed=False,
            terminate_run=False,
        )
    if checkpoint_generation > domain_generation:
        return _reconciliation_decision(
            status="checkpoint_ahead",
            reason="checkpoint ahead of domain",
            fact_owner="checkpoint",
            auto_repair=False,
            replay_allowed=False,
            terminate_run=True,
        )
    return _reconciliation_decision(
        status="aligned",
        reason="domain and checkpoint generations match",
        fact_owner="domain",
        auto_repair=False,
        replay_allowed=True,
        terminate_run=False,
    )


def _initialize_run(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    next_state.setdefault("schema_version", PHASE08_RUN_SCHEMA)
    next_state.setdefault("phase", "initialize")
    next_state.setdefault("domain_generation", 1)
    next_state.setdefault("checkpoint_generation", 1)
    next_state.setdefault("controller_epoch", 1)
    next_state.setdefault("pending_interrupt_refs", [])
    next_state.setdefault("branch_result_refs", [])
    next_state.setdefault("signal_journal", [])
    return _advance(next_state, "authorize")


def _authorize_run(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    observed_at = _parse_dt(next_state.get("observed_at")) or _utc_now()
    deadline_at = _parse_dt(next_state.get("deadline_at"))
    if next_state.get("cancel_requested"):
        next_state["latest_control_decision_ref"] = "cancelled"
        next_state["phase"] = "finalize"
        next_state["finalization_status"] = "cancelled"
        return _advance(next_state, "finalize")
    if deadline_at is not None and observed_at >= deadline_at:
        next_state["latest_control_decision_ref"] = "deadline_expired"
        next_state["phase"] = "finalize"
        next_state["finalization_status"] = "failed"
        return _advance(next_state, "finalize")
    current_epoch = next_state.get("current_security_epoch_ref", next_state.get("security_epoch_ref"))
    if current_epoch != next_state.get("security_epoch_ref"):
        next_state["latest_control_decision_ref"] = "stale_security_epoch"
        next_state["phase"] = "finalize"
        next_state["finalization_status"] = "failed"
        return _advance(next_state, "finalize")
    return _advance(next_state, "context_snapshot")


def _build_execution_context(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    if not next_state.get("execution_snapshot_id"):
        next_state["execution_snapshot_id"] = f"execution-snapshot:{next_state.get('run_id', 'run')}"
    return _advance(next_state, "create_plan")


def _plan_run(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    next_state["plan_created_count"] = int(next_state.get("plan_created_count", 0)) + 1
    available = int(next_state.get("budget_available_units", 0))
    requested = int(next_state.get("budget_requested_units", 0))
    if requested and available < requested:
        next_state["latest_control_decision_ref"] = "budget_insufficient"
        next_state["phase"] = "finalize"
        next_state["finalization_status"] = "blocked"
        return _advance(next_state, "finalize")
    next_state.setdefault("active_plan_version_id", f"plan:{next_state.get('run_id', 'run')}")
    return _advance(next_state, "validate_plan")


def _validate_plan(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    if not next_state.get("active_plan_version_id"):
        next_state["latest_control_decision_ref"] = "plan_validation_failed"
        next_state["finalization_status"] = "failed"
        return _advance(next_state, "finalize")
    next_state["plan_validation_ref"] = _domain_ref(next_state, "plan-validation")
    return _advance(next_state, "activate_plan")


def _activate_plan(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    next_state.setdefault("current_dispatch_group_id", f"dispatch:{next_state.get('run_id', 'run')}")
    return _advance(next_state, "execute_step")


def _execute_run(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    if next_state.get("interrupt_requested"):
        resume_value = interrupt(
            {
                "run_id": next_state.get("run_id"),
                "kind": "approval",
                "pending_interrupt_refs": list(next_state.get("pending_interrupt_refs") or []),
            }
        )
        next_state["resume_signal_ref"] = f"signal:{next_state.get('run_id', 'run')}:resume"
        next_state["resume_payload"] = resume_value
        next_state["interrupt_requested"] = False
        next_state["pending_interrupt_refs"] = []
        if isinstance(resume_value, dict) and resume_value.get("decision") == "cancelled":
            next_state["latest_control_decision_ref"] = "cancelled"
            next_state["cancel_reason"] = resume_value.get("reason") or "cancelled"
            next_state["finalization_status"] = "cancelled"
            return _advance(next_state, "finalize")
        next_state["finalization_status"] = "not_ready"
    if next_state.get("interrupt_requested"):
        interrupt_ref = f"interrupt:{next_state.get('run_id', 'run')}:approval"
        next_state.setdefault("pending_interrupt_refs", [])
        if interrupt_ref not in next_state["pending_interrupt_refs"]:
            next_state["pending_interrupt_refs"].append(interrupt_ref)
        next_state["latest_control_decision_ref"] = "interrupt"
        next_state["finalization_status"] = "interrupted"
        return _advance(next_state, "finalize")
    if next_state.get("abstain_requested"):
        next_state["latest_control_decision_ref"] = "abstain"
        next_state["finalization_status"] = "abstained"
        return _advance(next_state, "finalize")
    next_state.setdefault("branch_result_refs", [])
    if not next_state["branch_result_refs"]:
        next_state["branch_result_refs"].append(_domain_ref(next_state, "branch-result"))
    next_state.setdefault("final_candidate_ref", _domain_ref(next_state, "final-candidate"))
    return _advance(next_state, "final_gate")


def _final_gate_run(state: dict[str, Any], *, final_gate_port: Phase08FinalGatePort | None = None) -> dict[str, Any]:
    next_state = dict(state)
    if next_state.get("finalization_status") in {"interrupted", "cancelled", "blocked", "abstained", "failed"}:
        return _advance(next_state, "finalize")
    candidate_ref = next_state.get("final_candidate_ref")
    branch_result_refs = next_state.get("branch_result_refs") or []
    if not candidate_ref or not branch_result_refs:
        next_state["latest_control_decision_ref"] = "final_gate_missing_domain_refs"
        next_state["finalization_status"] = "failed"
        return _advance(next_state, "finalize")
    if final_gate_port is not None:
        next_state = final_gate_port.commit(next_state)
    else:
        next_state["final_gate_receipt_ref"] = _domain_ref(next_state, "final-gate")
        next_state["publication_receipt_ref"] = _domain_ref(next_state, "publication")
        next_state["outcome_receipt_ref"] = _domain_ref(next_state, "run-outcome")
    return _advance(next_state, "finalize")


def _finalize_run(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    next_state.setdefault("finalization_status", "finalized")
    if next_state["finalization_status"] == "interrupted":
        next_state["outcome_ref"] = None
    elif next_state["finalization_status"] == "cancelled":
        next_state["outcome_ref"] = _domain_ref(next_state, "run-outcome-cancelled")
    elif next_state["finalization_status"] == "blocked":
        next_state["outcome_ref"] = _domain_ref(next_state, "run-outcome-blocked")
    elif next_state["finalization_status"] == "abstained":
        next_state["outcome_ref"] = _domain_ref(next_state, "run-outcome-abstained")
    elif next_state["finalization_status"] == "failed":
        next_state["outcome_ref"] = next_state.get("outcome_receipt_ref") or _domain_ref(next_state, "run-outcome-failed")
    else:
        next_state["finalization_status"] = "finalized"
        next_state["publication_ref"] = next_state["publication_receipt_ref"]
        next_state["outcome_ref"] = next_state["outcome_receipt_ref"]
    return _advance(next_state, "run_outcome")


def _run_outcome(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    next_state["run_outcome_committed"] = next_state.get("outcome_ref") is not None
    return _advance(next_state, "run_outcome")


def _load_step(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    next_state.setdefault("step_phase", "load_step")
    if next_state.get("invalid_proposal"):
        next_state["failure_ref"] = "invalid_proposal"
        next_state["outcome_status"] = "failed"
        return next_state
    return _advance_step(next_state, "resolve_input")


def _resolve_step_input(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    if next_state.get("blocked_reason"):
        next_state["outcome_status"] = "blocked"
        next_state["latest_acceptance_ref"] = None
        return _advance_step(next_state, "step_acceptance")
    next_state.setdefault("resolved_input_ref", f"input:{next_state.get('step_run_id', 'step')}")
    return _advance_step(next_state, "security_gate")


def _step_security_gate(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    if next_state.get("security_denied"):
        next_state["failure_ref"] = "denied"
        next_state["outcome_status"] = "denied"
        return _advance_step(next_state, "step_acceptance")
    return _advance_step(next_state, "proposal")


def _step_proposal(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    if next_state.get("retryable_failure") and int(next_state.get("retry_count", 0)) < 1:
        next_state["retry_count"] = int(next_state.get("retry_count", 0)) + 1
        next_state["latest_reflection_ref"] = "retryable_failure"
        next_state["outcome_status"] = "retryable"
        return _advance_step(next_state, "load_step")
    if next_state.get("abstain_requested"):
        next_state["outcome_status"] = "abstained"
        return _advance_step(next_state, "step_acceptance")
    if next_state.get("invalid_proposal"):
        next_state["failure_ref"] = "invalid_proposal"
        next_state["outcome_status"] = "failed"
        return _advance_step(next_state, "step_acceptance")
    next_state["latest_action_run_id"] = f"action:{next_state.get('step_run_id', 'step')}"
    return _advance_step(next_state, "deterministic_validation")


def _deterministic_validation(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    if next_state.get("outcome_status") in {"blocked", "denied", "abstained", "failed"}:
        return _advance_step(next_state, "step_acceptance")
    required = ("step_definition_id", "plan_version_id", "controller_epoch", "execution_epoch")
    if any(not next_state.get(key) for key in required):
        next_state["failure_ref"] = "deterministic_validation_failed"
        next_state["outcome_status"] = "failed"
        return _advance_step(next_state, "step_acceptance")
    next_state["validation_ref"] = _step_domain_ref(next_state, "deterministic-validation")
    return _advance_step(next_state, "execute_owner_port")


def _execute_owner_port(state: dict[str, Any], *, owner_port: Phase08OwnerPort | None = None) -> dict[str, Any]:
    next_state = dict(state)
    if next_state.get("outcome_status") == "retryable":
        return next_state
    next_state.setdefault("latest_action_run_id", f"action:{next_state.get('step_run_id', 'step')}")
    if owner_port is not None:
        next_state = owner_port.execute(next_state)
    return _advance_step(next_state, "observation")


def _step_observation(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    if next_state.get("outcome_status") == "retryable":
        return next_state
    next_state.setdefault("latest_observation_ref", f"observation:{next_state.get('step_run_id', 'step')}")
    return _advance_step(next_state, "action_evaluation")


def _step_evaluation(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    if next_state.get("outcome_status") == "retryable":
        return next_state
    if next_state.get("outcome_status") in {"blocked", "denied", "abstained"}:
        return _advance_step(next_state, "step_acceptance")
    if next_state.get("retryable_failure") and int(next_state.get("retry_count", 0)) > 0:
        next_state["outcome_status"] = "completed"
    return _advance_step(next_state, "step_acceptance")


def _step_acceptance(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    status = next_state.get("outcome_status") or "completed"
    if status == "retryable":
        return next_state
    if status == "completed":
        next_state.setdefault("latest_acceptance_ref", _step_domain_ref(next_state, "acceptance"))
        next_state.setdefault("output_ref", _step_domain_ref(next_state, "output"))
    elif status == "blocked":
        next_state["failure_ref"] = next_state.get("failure_ref") or "blocked"
    elif status == "denied":
        next_state["failure_ref"] = next_state.get("failure_ref") or "denied"
    elif status == "abstained":
        next_state["latest_reflection_ref"] = next_state.get("latest_reflection_ref") or "abstain"
    return _advance_step(next_state, "commit_step_result")


def _commit_step_result(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    status = next_state.get("outcome_status") or "completed"
    if status == "retryable":
        return next_state
    next_state["step_result_commit_ref"] = _step_domain_ref(next_state, f"step-result-{status}")
    return _advance_step(next_state, "commit_step_result")


def _advance(state: dict[str, Any], phase: str) -> dict[str, Any]:
    next_state = dict(state)
    next_state["phase"] = phase
    next_state["checkpoint_generation"] = int(next_state.get("checkpoint_generation", 0)) + 1
    return next_state


def _advance_step(state: dict[str, Any], phase: str) -> dict[str, Any]:
    next_state = dict(state)
    next_state["step_phase"] = phase
    next_state["execution_epoch"] = int(next_state.get("execution_epoch", 0)) + 1
    return next_state


def _thread_config(state: dict[str, Any]) -> dict[str, Any]:
    return {"configurable": {"thread_id": str(state.get("thread_id") or state.get("run_id") or state.get("step_run_id") or "phase08")}}


def _snapshot_has_interrupt(snapshot: Any) -> bool:
    return bool(getattr(snapshot, "tasks", None) and any(getattr(task, "interrupts", None) for task in snapshot.tasks))


def _interrupted_state(graph: Any, state: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    if "__interrupt__" not in result:
        return result
    snapshot = graph.get_state(_thread_config(state))
    values = dict(snapshot.values)
    interrupt_ref = f"interrupt:{values.get('run_id', state.get('run_id', 'run'))}:approval"
    pending = list(values.get("pending_interrupt_refs") or [])
    if interrupt_ref not in pending:
        pending.append(interrupt_ref)
    values["pending_interrupt_refs"] = pending
    values["latest_control_decision_ref"] = "interrupt"
    values["finalization_status"] = "interrupted"
    values["phase"] = "execute_step"
    values["checkpoint_generation"] = int(values.get("checkpoint_generation", 0)) + 1
    return values


def _domain_ref(state: dict[str, Any], kind: str) -> str:
    run_id = str(state.get("run_id", "run"))
    generation = int(state.get("domain_generation", 1))
    return f"agent-domain:{kind}:{run_id}:generation:{generation}"


def _step_domain_ref(state: dict[str, Any], kind: str) -> str:
    step_run_id = str(state.get("step_run_id", "step"))
    execution_epoch = int(state.get("execution_epoch", 1))
    return f"agent-domain:{kind}:{step_run_id}:epoch:{execution_epoch}"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_dt(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value))


def _require_refs(state: dict[str, Any]) -> None:
    if not state.get("run_id") or not state.get("security_epoch_ref"):
        raise Phase08RuntimeError("run state incomplete")


def _required_state_ref(state: dict[str, Any], field_name: str) -> str:
    value = str(state.get(field_name) or "")
    if not value.strip():
        raise Phase08RuntimeError(f"PHASE08 state missing required field: {field_name}")
    return value


def _reconciliation_decision(
    *,
    status: str,
    reason: str,
    fact_owner: str,
    auto_repair: bool,
    replay_allowed: bool,
    terminate_run: bool,
) -> dict[str, Any]:
    return {
        "status": status,
        "reason": reason,
        "fact_owner": fact_owner,
        "auto_repair": auto_repair,
        "replay_allowed": replay_allowed,
        "terminate_run": terminate_run,
        "audit_event_ref": f"audit:phase08-reconcile:{status}",
        "idempotency_key": f"phase08-reconcile:{status}:{reason}",
    }


__all__ = [
    "PHASE08_RUN_SCHEMA",
    "PHASE08_STEP_SCHEMA",
    "Phase08Conflict",
    "Phase08RuntimeError",
    "Phase08FinalGatePort",
    "Phase08OwnerPort",
    "Phase08RunService",
    "Phase08SignalRecord",
    "Phase08StepService",
    "PostgresPhase08FinalGatePort",
    "PostgresPhase08OwnerPort",
    "append_signal",
    "build_phase08_run_graph",
    "build_phase08_step_graph",
    "build_phase08_test_checkpointer",
    "phase08_postgres_checkpointer",
    "reconcile_generations",
]
