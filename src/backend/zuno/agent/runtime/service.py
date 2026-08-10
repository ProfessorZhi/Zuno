from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Iterable

from zuno.agent.durable_runtime import DurableRuntimeTaskSnapshot
from zuno.agent.contracts import CapabilityPlan, ContextPack, PlanState, PlanStep
from zuno.agent.runtime.checkpointer import RuntimeGraphCheckpointer
from zuno.agent.runtime.plan_owner import build_capability_plan_from_request
from zuno.agent.runtime.contracts import (
    FinalizationStatus,
    ReflectionDecision,
    RuntimeLimits,
    StrategyDecision,
    StrategyMode,
)
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.factory import RuntimeDependencyFactory
from zuno.agent.runtime.graph import build_agent_graph
from zuno.agent.runtime.owner_refs import (
    OwnerRefVerification,
    resolve_budget_ref,
    resolve_security_ref,
    validate_budget_decision_ref,
    validate_security_decision_ref,
)
from zuno.agent.runtime.routing import (
    RuntimeNode,
    hard_limit_route,
    route_after_reflection,
    route_after_strategy,
)
from zuno.agent.runtime.state import AgentRuntimeSnapshot, AgentRuntimeState
from zuno.agent.runtime.store import AgentRunStore

# Runtime composition profile: the product (server) composition must inject
# durable stores and owner bindings; only the explicit developer test profile
# may fall back to SQLite stores.
PROFILE_PRODUCT = "server_product"
PROFILE_DEVELOPER_TEST = "developer_test_profile"


@dataclass(frozen=True, slots=True)
class RuntimeStartRequest:
    run_id: str
    thread_id: str
    workspace_id: str
    user_id: str
    task_id: str
    trace_id: str
    goal: str
    # The task id is bound to the product submission, never to a content hash.
    # Tenant identity is supplied by authenticated server context; missing
    # product context fails closed at the composition boundary.
    tenant_id: str = ""
    principal_id: str = ""
    submission_id: str = ""
    client_request_id: str = ""
    conversation_id: str = ""
    agent_version: str = ""
    content_fingerprint: str = ""
    profile: str = PROFILE_PRODUCT
    knowledge_space_ids: tuple[str, ...] = ()
    strategy_mode: StrategyMode | str | None = None
    reflection_decision: ReflectionDecision | str | None = None
    # The application boundary may seed capabilities and a plan, but execution
    # always goes through the graph's planning, security, approval, budget and
    # run-outcome stages.
    capability_ids: tuple[str, ...] = ()
    allowed_tools: tuple[str, ...] = ()
    approval_required_tools: tuple[str, ...] = ()
    budget_limits: dict[str, Any] | None = None
    # Only owner decision references are accepted; raw caller dictionaries are
    # never treated as authorization facts.
    security_decision_ref: dict[str, Any] | None = None
    budget_decision_ref: dict[str, Any] | None = None
    security_epoch_ref: str = ""
    security_summary: dict[str, Any] | None = None
    budget_verdict: dict[str, Any] | None = None
    plan_steps: tuple[dict[str, Any], ...] = ()


@dataclass(frozen=True, slots=True)
class RuntimeStreamEvent:
    event_type: str
    run_id: str
    task_id: str
    trace_id: str
    node: str
    status: str
    payload: dict


class AgentRuntimeService:
    """Canonical Agent Run execution and recovery surface."""

    def __init__(
        self,
        *,
        dependencies: RuntimeDependencies | None = None,
        store: AgentRunStore,
        graph=None,
    ) -> None:
        self.dependencies = dependencies or RuntimeDependencyFactory().dependencies()
        self.store = store
        self.checkpointer = RuntimeGraphCheckpointer(store)
        self.graph = graph or build_agent_graph(dependencies=self.dependencies, checkpointer=self.checkpointer)

    def start(self, request: RuntimeStartRequest) -> AgentRuntimeSnapshot:
        # Security and Budget facts come from owner decision references verified
        # by Agent Core. Invalid, missing or stale references fail closed.
        security_verdict = _verify_security_owner_ref(request)
        budget_verdict = _verify_budget_owner_ref(request)
        admission_blocked = not security_verdict.allowed or not budget_verdict.allowed
        state = AgentRuntimeState(
            run_id=request.run_id,
            thread_id=request.thread_id,
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            tenant_id=request.tenant_id,
            task_id=request.task_id,
            trace_id=request.trace_id,
            goal=request.goal,
            submission_id=request.submission_id,
            client_request_id=request.client_request_id,
            conversation_id=request.conversation_id,
            agent_version=request.agent_version,
            content_fingerprint=request.content_fingerprint,
            capability_plan=_capability_plan_from_request(request),
            plan_state=_plan_state_from_request(request, blocked=admission_blocked),
            limits=_limits_from_request(request),
            security_summary=dict(request.security_summary or {})
            if not admission_blocked
            else {
                **dict(request.security_summary or {}),
                "decision": "block",
                "recommended_action": "refuse",
                "reason": (
                    security_verdict.reason
                    if not security_verdict.allowed
                    else budget_verdict.reason
                ),
            },
            budget_verdict=(
                dict(request.budget_verdict)
                if request.budget_verdict and not admission_blocked
                else {"allowed": False, "reason": budget_verdict.reason}
                if not budget_verdict.allowed
                else dict(request.budget_verdict)
                if request.budget_verdict
                else None
            ),
            context_pack=(
                ContextPack(
                    context_pack_id=f"context:{request.run_id}",
                    user_goal=request.goal,
                    task_state={
                        "thread_id": request.thread_id,
                        "task_id": request.task_id,
                        "tenant_id": request.tenant_id,
                        "client_request_id": request.client_request_id,
                        "submission_id": request.submission_id,
                        "knowledge_space_ids": list(request.knowledge_space_ids),
                    },
                    output_contract={"runtime": "unified_graph_request_context"},
                )
                if request.knowledge_space_ids
                else None
            ),
            strategy=(
                StrategyDecision(mode=StrategyMode(request.strategy_mode), reason="preset by caller")
                if request.strategy_mode
                else None
            ),
            reflection_decision=(
                ReflectionDecision(request.reflection_decision)
                if request.reflection_decision
                else None
            ),
        )
        self.checkpointer.ensure_run(state)
        self.checkpointer.append_event(state, event_type="runtime_started", status="running")
        final_payload = self.graph.invoke(state.to_snapshot().model_dump(mode="json"))
        final_state = AgentRuntimeState.from_snapshot(AgentRuntimeSnapshot.from_payload(dict(final_payload)))
        return final_state.to_snapshot()

    def stream(self, request: RuntimeStartRequest) -> Iterable[RuntimeStreamEvent]:
        snapshot = self.start(request)
        for event in self.store.events(request.task_id):
            yield RuntimeStreamEvent(
                event_type=event.type,
                run_id=request.run_id,
                task_id=event.task_id,
                trace_id=event.trace_id,
                node=event.node,
                status=event.status,
                payload=dict(event.payload),
            )
        if snapshot.finalization_status == FinalizationStatus.INTERRUPTED:
            return

    def resume(
        self,
        *,
        task_id: str,
        approval_decision: str = "approved",
        tenant_id: str = "",
        workspace_id: str = "",
    ) -> AgentRuntimeSnapshot:
        _assert_scope(task_id, self.store, tenant_id=tenant_id, workspace_id=workspace_id)
        interrupt = self.store.pending_interrupt(task_id)
        if interrupt is None:
            raise ValueError(f"runtime task is not waiting for interrupt resume: {task_id}")
        if approval_decision.strip().lower() != "approved":
            snapshot = self.store.snapshot(task_id)
            self.store.clear_interrupt(task_id)
            self.store.update_status(task_id, "failed")
            rejected_state = _runtime_state_from_task_snapshot(snapshot)
            rejected_state.finalization_status = FinalizationStatus.FAILED
            return rejected_state.to_snapshot()
        latest = self.store.latest_checkpoint(task_id)
        if latest is None:
            raise ValueError(f"runtime task has no checkpoint to resume: {task_id}")
        state = AgentRuntimeState.from_snapshot(AgentRuntimeSnapshot.from_payload(dict(latest.state)))
        interrupt_payload = dict(interrupt.payload or {})
        idempotency_key = str(interrupt_payload.get("idempotency_key") or "")
        if idempotency_key and f"approved:{idempotency_key}" not in state.interrupt_refs:
            if hasattr(self.store, "claim_tool_execution"):
                claimed = self.store.claim_tool_execution(
                    task_id=state.task_id,
                    workspace_id=state.workspace_id,
                    user_id=state.user_id,
                    idempotency_key=idempotency_key,
                    tool_name=str(interrupt_payload.get("required_approval") or "tool").removeprefix("tool:"),
                    payload={"step_id": state.current_step_id or "", "status": "claimed"},
                )
                if not claimed:
                    return state.to_snapshot()
            state = replace(
                state,
                interrupt_refs=[*state.interrupt_refs, f"approved:{idempotency_key}"],
                finalization_status=FinalizationStatus.NOT_READY,
            )
        else:
            state = replace(state, finalization_status=FinalizationStatus.NOT_READY)
        self.store.clear_interrupt(task_id)
        self.store.update_status(task_id, "running")
        resume_payload = {
            "interrupt_id": interrupt.interrupt_id,
            "decision": approval_decision,
            "approved_by": "runtime_resume",
            "idempotency_key": idempotency_key,
        }
        self.checkpointer.append_event(
            state,
            event_type="runtime_resumed",
            status="running",
            node=interrupt.node,
            payload=resume_payload,
        )
        final_payload = self.graph.invoke(state.to_snapshot().model_dump(mode="json"))
        final_state = AgentRuntimeState.from_snapshot(AgentRuntimeSnapshot.from_payload(dict(final_payload)))
        return final_state.to_snapshot()

    def cancel(self, *, task_id: str, reason: str) -> DurableRuntimeTaskSnapshot:
        self.checkpointer.cancel(task_id, reason=reason)
        return self.store.snapshot(task_id)

    def get_snapshot(
        self,
        task_id: str,
        *,
        tenant_id: str = "",
        workspace_id: str = "",
    ) -> AgentRuntimeSnapshot | None:
        if not self.store.has_task(task_id):
            return None
        snapshot = _runtime_state_from_task_snapshot(self.store.snapshot(task_id)).to_snapshot()
        if tenant_id and snapshot.tenant_id != tenant_id:
            return None
        if workspace_id and snapshot.workspace_id != workspace_id:
            return None
        return snapshot


def _capability_plan_from_request(request: RuntimeStartRequest) -> CapabilityPlan | None:
    """Delegate plan construction to the canonical plan owner.

    The actual ``CapabilityPlan`` construction lives in
    ``zuno.agent.runtime.plan_owner`` so the public adapter body never
    instantiates the data class directly.
    """
    return build_capability_plan_from_request(
        task_id=request.task_id,
        capability_ids=request.capability_ids,
        allowed_tools=request.allowed_tools,
        approval_required_tools=request.approval_required_tools,
    )


def _plan_state_from_request(request: RuntimeStartRequest, *, blocked: bool = False) -> PlanState | None:
    """Activate the deterministic plan carried by the product surface.

    Every task has a formal plan (INV-AGENT-001). The application supplies
    step definitions only; activation status and plan version belong to Agent
    Core. A request without steps becomes blocked rather than bypassing the
    planning boundary.
    """
    if blocked:
        return PlanState(
            plan_id=f"plan:{request.run_id}",
            status="blocked",
            steps=[],
            current_step_id=None,
            plan_version=0,
        )
    if not request.plan_steps:
        return PlanState(
            plan_id=f"plan:{request.run_id}",
            status="blocked",
            steps=[],
            current_step_id=None,
            plan_version=0,
        )
    steps = [PlanStep(**step) for step in request.plan_steps]
    return PlanState(
        plan_id=f"plan:{request.run_id}",
        status="planned",
        steps=steps,
        current_step_id=steps[0].step_id if steps else None,
        plan_version=1,
        activation_status="activated",
        activated_by="agent_core",
    )


def _verify_security_owner_ref(request: RuntimeStartRequest) -> OwnerRefVerification:
    """Agent Core verifies the Security-owner decision reference.

    In the product profile the ref is required only for a plan that actually
    executes a tool (``tool.execute`` security decision). A simple no-tool
    plan never requires a tool-execution security decision, so simple
    read-only questions are not blocked by a missing security ref. The
    explicit developer test profile may omit refs entirely.
    """
    ref = resolve_security_ref(request.security_decision_ref)
    required = (
        request.profile == PROFILE_PRODUCT
        and bool(request.allowed_tools or request.capability_ids)
    )
    return validate_security_decision_ref(
        ref,
        tenant_id=request.tenant_id,
        workspace_id=request.workspace_id,
        principal_id=request.principal_id or request.user_id,
        action="tool.execute",
        resource=",".join(request.allowed_tools),
        bound_security_epoch_ref=request.security_epoch_ref,
        required=required,
    )


def _verify_budget_owner_ref(request: RuntimeStartRequest) -> OwnerRefVerification:
    """Agent Core verifies the Budget-owner decision reference.

    Every product run with a formal plan must pass Budget Admission: the
    budget ref is required for any planned product run (simple no-tool runs
    included). No plan -> no budget decision required.
    """
    ref = resolve_budget_ref(request.budget_decision_ref)
    required = (
        request.profile == PROFILE_PRODUCT
        and bool(request.plan_steps)
    )
    return validate_budget_decision_ref(
        ref,
        tenant_id=request.tenant_id,
        workspace_id=request.workspace_id,
        run_id=request.run_id,
        required=required,
    )


def _limits_from_request(request: RuntimeStartRequest) -> RuntimeLimits:
    """Apply product budget limits (max steps / tokens / cost / timeout)."""
    if not request.budget_limits:
        return RuntimeLimits()
    allowed = {
        name
        for name in RuntimeLimits.model_fields
    }
    return RuntimeLimits(**{key: value for key, value in request.budget_limits.items() if key in allowed})


def _assert_scope(
    task_id: str,
    store: AgentRunStore,
    *,
    tenant_id: str,
    workspace_id: str,
) -> None:
    """Enforce tenant and workspace isolation for read and resume paths.

    The store may be shared across tenants (e.g. the server's durable store);
    a run recovered from the store whose owner scope does not match the
    caller's scope fails closed instead of leaking the run.
    """
    if not tenant_id and not workspace_id:
        return
    if not store.has_task(task_id):
        return
    snapshot = _runtime_state_from_task_snapshot(store.snapshot(task_id)).to_snapshot()
    if tenant_id and snapshot.tenant_id != tenant_id:
        raise PermissionError(f"runtime task outside tenant scope: {task_id}")
    if workspace_id and snapshot.workspace_id != workspace_id:
        raise PermissionError(f"runtime task outside workspace scope: {task_id}")


def _runtime_state_from_task_snapshot(snapshot: DurableRuntimeTaskSnapshot) -> AgentRuntimeState:
    checkpoint = snapshot.latest_checkpoint
    if checkpoint is not None and dict(checkpoint.state).get("state_version"):
        return AgentRuntimeState.from_snapshot(AgentRuntimeSnapshot.from_payload(dict(checkpoint.state)))
    context_pack = dict(snapshot.state.context_pack or {})
    if context_pack.get("state_version"):
        return AgentRuntimeState.from_snapshot(AgentRuntimeSnapshot.from_payload(context_pack))
    return AgentRuntimeState(
        run_id=f"run:{snapshot.task_id}",
        thread_id=snapshot.thread_id,
        workspace_id=snapshot.workspace_id,
        user_id=snapshot.state.user_id,
        task_id=snapshot.task_id,
        trace_id=snapshot.trace_id,
        goal=snapshot.state.goal,
        tenant_id=str(context_pack.get("tenant_id") or ""),
        current_node=snapshot.state.current_step,
    )


__all__ = [
    "PROFILE_DEVELOPER_TEST",
    "PROFILE_PRODUCT",
    "RuntimeStartRequest",
    "RuntimeStreamEvent",
    "AgentRuntimeService",
]
