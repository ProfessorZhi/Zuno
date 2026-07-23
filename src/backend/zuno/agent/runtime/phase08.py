from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


PHASE08_RUN_SCHEMA = "phase08-run-v1"
PHASE08_STEP_SCHEMA = "phase08-step-v1"


class Phase08RuntimeError(ValueError):
    pass


class Phase08Conflict(Phase08RuntimeError):
    pass


def build_phase08_run_graph(*, checkpointer: Any | None = None) -> Any:
    graph = StateGraph(dict)
    graph.add_node("initialize", _initialize_run)
    graph.add_node("authorize", _authorize_run)
    graph.add_node("context", _build_execution_context)
    graph.add_node("plan", _plan_run)
    graph.add_node("activate", _activate_plan)
    graph.add_node("execute", _execute_run)
    graph.add_node("finalize", _finalize_run)
    graph.add_edge(START, "initialize")
    graph.add_edge("initialize", "authorize")
    graph.add_edge("authorize", "context")
    graph.add_edge("context", "plan")
    graph.add_edge("plan", "activate")
    graph.add_edge("activate", "execute")
    graph.add_edge("execute", "finalize")
    graph.add_edge("finalize", END)
    return graph.compile(checkpointer=checkpointer or InMemorySaver())


def build_phase08_step_graph(*, checkpointer: Any | None = None) -> Any:
    graph = StateGraph(dict)
    graph.add_node("load_step", _load_step)
    graph.add_node("resolve_input", _resolve_step_input)
    graph.add_node("security", _step_security)
    graph.add_node("proposal", _step_proposal)
    graph.add_node("execute_owner_port", _execute_owner_port)
    graph.add_node("observation", _step_observation)
    graph.add_node("evaluation", _step_evaluation)
    graph.add_node("acceptance", _step_acceptance)
    graph.add_edge(START, "load_step")
    graph.add_edge("load_step", "resolve_input")
    graph.add_edge("resolve_input", "security")
    graph.add_edge("security", "proposal")
    graph.add_edge("proposal", "execute_owner_port")
    graph.add_edge("execute_owner_port", "observation")
    graph.add_edge("observation", "evaluation")
    graph.add_edge("evaluation", "acceptance")
    graph.add_edge("acceptance", END)
    return graph.compile(checkpointer=checkpointer or InMemorySaver())


@dataclass
class Phase08RunService:
    graph: Any = field(default_factory=build_phase08_run_graph)

    def start(self, state: dict[str, Any]) -> dict[str, Any]:
        return self.graph.invoke(dict(state), config=_thread_config(state))

    def resume(self, state: dict[str, Any]) -> dict[str, Any]:
        next_state = dict(state)
        next_state["resume_requested"] = True
        next_state["interrupt_requested"] = False
        next_state["pending_interrupt_refs"] = []
        next_state["phase"] = "initialize"
        next_state["finalization_status"] = "not_ready"
        return self.graph.invoke(next_state, config=_thread_config(state))

    def cancel(self, state: dict[str, Any], *, reason: str) -> dict[str, Any]:
        next_state = dict(state)
        next_state["cancel_requested"] = True
        next_state["interrupt_requested"] = False
        next_state["pending_interrupt_refs"] = []
        next_state["cancel_reason"] = reason
        next_state["finalization_status"] = "cancelled"
        next_state["phase"] = "initialize"
        return self.graph.invoke(next_state, config=_thread_config(state))

    def get_state(self, state: dict[str, Any]) -> dict[str, Any]:
        snapshot = self.graph.get_state(_thread_config(state))
        return dict(snapshot.values)


@dataclass
class Phase08StepService:
    graph: Any = field(default_factory=build_phase08_step_graph)

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        return self.graph.invoke(dict(state), config=_thread_config(state))


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


def reconcile_generations(*, domain_generation: int, checkpoint_generation: int, schema_version: str) -> dict[str, Any]:
    if schema_version != PHASE08_RUN_SCHEMA:
        return {"status": "stale_schema", "reason": schema_version}
    if checkpoint_generation < domain_generation:
        return {"status": "checkpoint_fail", "reason": "checkpoint behind domain"}
    if checkpoint_generation > domain_generation:
        return {"status": "checkpoint_ahead", "reason": "checkpoint ahead of domain"}
    if checkpoint_generation == 0:
        return {"status": "orphan_run", "reason": "no checkpoint"}
    return {"status": "reconciled", "reason": "aligned"}


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
    return _advance(next_state, "context")


def _build_execution_context(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    if not next_state.get("execution_snapshot_id"):
        next_state["execution_snapshot_id"] = f"execution-snapshot:{next_state.get('run_id', 'run')}"
    return _advance(next_state, "plan")


def _plan_run(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    available = int(next_state.get("budget_available_units", 0))
    requested = int(next_state.get("budget_requested_units", 0))
    if requested and available < requested:
        next_state["latest_control_decision_ref"] = "budget_insufficient"
        next_state["phase"] = "finalize"
        next_state["finalization_status"] = "blocked"
        return _advance(next_state, "finalize")
    next_state.setdefault("active_plan_version_id", f"plan:{next_state.get('run_id', 'run')}")
    return _advance(next_state, "activate")


def _activate_plan(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    next_state.setdefault("current_dispatch_group_id", f"dispatch:{next_state.get('run_id', 'run')}")
    return _advance(next_state, "execute")


def _execute_run(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
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
        next_state["branch_result_refs"].append(f"branch:{next_state.get('run_id', 'run')}:result")
    next_state.setdefault("final_candidate_ref", f"candidate:{next_state.get('run_id', 'run')}")
    return _advance(next_state, "finalize")


def _finalize_run(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    next_state.setdefault("finalization_status", "finalized")
    if next_state["finalization_status"] == "interrupted":
        next_state["outcome_ref"] = None
    elif next_state["finalization_status"] == "cancelled":
        next_state["outcome_ref"] = f"outcome:{next_state.get('run_id', 'run')}:cancelled"
    elif next_state["finalization_status"] == "blocked":
        next_state["outcome_ref"] = f"outcome:{next_state.get('run_id', 'run')}:blocked"
    elif next_state["finalization_status"] == "abstained":
        next_state["outcome_ref"] = f"outcome:{next_state.get('run_id', 'run')}:abstained"
    elif next_state["finalization_status"] == "failed":
        next_state["outcome_ref"] = f"outcome:{next_state.get('run_id', 'run')}:failed"
    else:
        next_state["finalization_status"] = "finalized"
        next_state["publication_ref"] = f"publication:{next_state.get('run_id', 'run')}"
        next_state["outcome_ref"] = f"outcome:{next_state.get('run_id', 'run')}"
    return _advance(next_state, "finalize")


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
        return _advance_step(next_state, "acceptance")
    next_state.setdefault("resolved_input_ref", f"input:{next_state.get('step_run_id', 'step')}")
    return _advance_step(next_state, "security")


def _step_security(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    if next_state.get("security_denied"):
        next_state["failure_ref"] = "denied"
        next_state["outcome_status"] = "denied"
        return _advance_step(next_state, "acceptance")
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
        return _advance_step(next_state, "acceptance")
    if next_state.get("invalid_proposal"):
        next_state["failure_ref"] = "invalid_proposal"
        next_state["outcome_status"] = "failed"
        return _advance_step(next_state, "acceptance")
    next_state["latest_action_run_id"] = f"action:{next_state.get('step_run_id', 'step')}"
    return _advance_step(next_state, "execute_owner_port")


def _execute_owner_port(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    if next_state.get("outcome_status") == "retryable":
        return next_state
    next_state.setdefault("latest_action_run_id", f"action:{next_state.get('step_run_id', 'step')}")
    return _advance_step(next_state, "observation")


def _step_observation(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    if next_state.get("outcome_status") == "retryable":
        return next_state
    next_state.setdefault("latest_observation_ref", f"observation:{next_state.get('step_run_id', 'step')}")
    return _advance_step(next_state, "evaluation")


def _step_evaluation(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    if next_state.get("outcome_status") == "retryable":
        return next_state
    if next_state.get("outcome_status") in {"blocked", "denied", "abstained"}:
        return _advance_step(next_state, "acceptance")
    if next_state.get("retryable_failure") and int(next_state.get("retry_count", 0)) > 0:
        next_state["outcome_status"] = "completed"
    return _advance_step(next_state, "acceptance")


def _step_acceptance(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    status = next_state.get("outcome_status") or "completed"
    if status == "retryable":
        return next_state
    if status == "completed":
        next_state["latest_acceptance_ref"] = f"acceptance:{next_state.get('step_run_id', 'step')}"
        next_state["output_ref"] = f"output:{next_state.get('step_run_id', 'step')}"
    elif status == "blocked":
        next_state["failure_ref"] = next_state.get("failure_ref") or "blocked"
    elif status == "denied":
        next_state["failure_ref"] = next_state.get("failure_ref") or "denied"
    elif status == "abstained":
        next_state["latest_reflection_ref"] = next_state.get("latest_reflection_ref") or "abstain"
    return _advance_step(next_state, "acceptance")


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


__all__ = [
    "PHASE08_RUN_SCHEMA",
    "PHASE08_STEP_SCHEMA",
    "Phase08Conflict",
    "Phase08RuntimeError",
    "Phase08RunService",
    "Phase08SignalRecord",
    "Phase08StepService",
    "append_signal",
    "build_phase08_run_graph",
    "build_phase08_step_graph",
    "reconcile_generations",
]
