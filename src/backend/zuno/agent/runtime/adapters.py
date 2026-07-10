from __future__ import annotations

import hashlib
from typing import Any

from zuno.agent.contracts import ContextPack, PlannerOutput
from zuno.agent.runtime.contracts import (
    NormalizedObservation,
    ObservationKind,
    ObservationStatus,
    ReflectionDecision,
    StrategyDecision,
    StrategyMode,
)
from zuno.agent.runtime.state import AgentRuntimeState

_SENSITIVE_KEYS = ("password", "secret", "token", "api_key", "credential", "authorization")


def normalized_observation_from_runtime_observation(observation: Any) -> NormalizedObservation:
    evidence = getattr(observation, "evidence", None)
    metadata = _safe_metadata(getattr(observation, "metadata", {}) or {})
    return NormalizedObservation(
        observation_id=_stable_id("obs", getattr(observation, "step_id", ""), getattr(observation, "status", "")),
        step_id=str(getattr(observation, "step_id", "") or ""),
        kind=_kind_from_observation(observation),
        status=_status(str(getattr(observation, "status", "completed") or "completed")),
        source="AgentControlRuntime.RuntimeObservation",
        summary=str(getattr(observation, "output", "") or getattr(observation, "failure_reason", "") or ""),
        payload_ref=_payload_ref("runtime_observation", getattr(observation, "step_id", ""), metadata),
        evidence_ids=list(getattr(evidence, "evidence_ids", []) or []),
        citation_ids=list(getattr(evidence, "citation_ids", []) or []),
        tool_id=getattr(observation, "tool_id", None),
        failure_reason=getattr(observation, "failure_reason", None),
        metadata=metadata,
    )


def normalized_observation_from_controller_payload(payload: dict[str, Any], *, index: int = 0) -> NormalizedObservation:
    safe_payload = _safe_metadata(payload)
    node = str(payload.get("node") or payload.get("step_id") or f"observation_{index}")
    status = _status(str(payload.get("status") or "completed"))
    return NormalizedObservation(
        observation_id=_stable_id("obs", node, str(index), str(payload.get("result") or "")),
        step_id=str(payload.get("step_id") or node),
        kind=_kind_from_payload(payload),
        status=status,
        source="ControllerRuntimeState.observations",
        summary=str(payload.get("summary") or payload.get("result") or payload.get("reflection") or ""),
        payload_ref=_payload_ref("controller_observation", node, safe_payload),
        failure_reason=payload.get("failure_reason"),
        metadata=safe_payload,
    )


def runtime_state_from_controller_state(controller_state: Any) -> AgentRuntimeState:
    observations = [
        normalized_observation_from_controller_payload(dict(item), index=index)
        for index, item in enumerate(getattr(controller_state, "observations", ()) or ())
    ]
    context_payload = dict(getattr(controller_state, "context_pack", {}) or {})
    context_pack = ContextPack(
        context_pack_id=str(context_payload.get("context_pack_id") or f"context:{controller_state.task_id}"),
        user_goal=str(getattr(controller_state, "goal", "") or ""),
        task_state=dict(context_payload.get("task_state") or {}),
        selected_memory_refs=list(context_payload.get("selected_memory_refs") or []),
        selected_evidence_refs=list(context_payload.get("selected_evidence_refs") or []),
        allowed_capabilities=list(context_payload.get("allowed_capabilities") or []),
        safety_policy=dict(context_payload.get("safety_policy") or {}),
        output_contract=dict(context_payload.get("output_contract") or {}),
        budget=dict(context_payload.get("budget") or {}),
    )
    return AgentRuntimeState(
        run_id=f"run:{controller_state.task_id}",
        thread_id=str(controller_state.thread_id),
        workspace_id=str(controller_state.workspace_id),
        user_id=str(controller_state.user_id),
        task_id=str(controller_state.task_id),
        trace_id=str(controller_state.trace_id),
        goal=str(controller_state.goal),
        current_node=str(controller_state.current_step),
        current_step_id=str(controller_state.current_step or "") or None,
        context_pack=context_pack,
        observations=observations,
        artifact_refs=list(getattr(controller_state, "artifact_refs", ()) or ()),
        memory_candidate_refs=list(getattr(controller_state, "memory_candidates", ()) or ()),
        interrupt_refs=[str(item.get("interrupt_id") or item.get("id") or index) for index, item in enumerate(getattr(controller_state, "approval_interrupts", ()) or ())],
        checkpoint_refs=list(getattr(controller_state, "checkpoints", ()) or ()),
    )


def runtime_state_from_planner_output(
    planner_output: PlannerOutput,
    *,
    thread_id: str = "",
    workspace_id: str = "",
    user_id: str = "",
    goal: str = "",
) -> AgentRuntimeState:
    strategy = planner_output.strategy
    trace_event_ids = [event.event_id for event in planner_output.trace_events]
    reflection = _reflection_decision(planner_output.reflection_verdict.decision)
    return AgentRuntimeState(
        run_id=f"run:{planner_output.task_id}",
        thread_id=thread_id,
        workspace_id=workspace_id,
        user_id=user_id,
        task_id=planner_output.task_id,
        trace_id=planner_output.trace_id,
        goal=goal,
        current_step_id=planner_output.plan_state.current_step_id,
        strategy=StrategyDecision(
            mode=StrategyMode(strategy.strategy),
            reason=strategy.reason,
            selected_skill_id=strategy.selected_skill,
            retrieval_profile=strategy.retrieval_profile.value if strategy.retrieval_profile else None,
            trace_event_ids=trace_event_ids,
        ),
        plan_state=planner_output.plan_state,
        retrieval_plan=planner_output.retrieval_plan,
        capability_plan=planner_output.capability_plan,
        reflection_decision=reflection,
        trace_event_ids=trace_event_ids,
    )


def _kind_from_observation(observation: Any) -> ObservationKind:
    if getattr(observation, "tool_id", None):
        return ObservationKind.TOOL
    metadata = getattr(observation, "metadata", {}) or {}
    if metadata.get("retriever") or metadata.get("evidence_ref"):
        return ObservationKind.RETRIEVAL
    if getattr(observation, "failure_reason", None):
        return ObservationKind.GATE
    return ObservationKind.SYSTEM


def _kind_from_payload(payload: dict[str, Any]) -> ObservationKind:
    node = str(payload.get("node") or "").lower()
    if "tool" in node:
        return ObservationKind.TOOL
    if "retrieval" in node or "evidence" in node:
        return ObservationKind.RETRIEVAL
    if "reflection" in payload or "reflect" in node:
        return ObservationKind.REFLECTION
    return ObservationKind.SYSTEM


def _reflection_decision(value: str) -> ReflectionDecision:
    mapping = {
        "finish": ReflectionDecision.PASS,
        "continue": ReflectionDecision.RETRIEVE_MORE,
        "retrieve_more": ReflectionDecision.RETRIEVE_MORE,
        "replan": ReflectionDecision.REPLAN,
        "ask_user": ReflectionDecision.ASK_USER,
        "refuse": ReflectionDecision.REFUSE,
    }
    return mapping.get(value, ReflectionDecision.RETRIEVE_MORE)


def _status(value: str) -> ObservationStatus:
    if value in {item.value for item in ObservationStatus}:
        return ObservationStatus(value)
    return ObservationStatus.COMPLETED


def _safe_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    safe: dict[str, Any] = {}
    for key, value in dict(payload).items():
        lower = str(key).lower()
        if any(marker in lower for marker in _SENSITIVE_KEYS):
            safe[key] = "[redacted]"
        elif isinstance(value, (str, int, float, bool)) or value is None:
            safe[key] = value
        else:
            safe[key] = f"<{type(value).__name__}>"
    return safe


def _payload_ref(prefix: str, key: Any, payload: dict[str, Any]) -> str | None:
    if not payload:
        return None
    return _stable_id(prefix, str(key), repr(sorted(payload.items())))


def _stable_id(prefix: str, *parts: str) -> str:
    source = "|".join(str(part) for part in parts)
    return f"{prefix}_{hashlib.sha256(source.encode('utf-8')).hexdigest()[:12]}"


__all__ = [
    "normalized_observation_from_controller_payload",
    "normalized_observation_from_runtime_observation",
    "runtime_state_from_controller_state",
    "runtime_state_from_planner_output",
]
