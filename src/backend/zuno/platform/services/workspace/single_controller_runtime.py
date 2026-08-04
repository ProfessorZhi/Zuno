from __future__ import annotations

"""PHASE22 workspace / wechat single-controller cutover composition root.

Product adapters (``WorkSpaceSimpleAgent`` / ``WeChatAgent``) drive the
canonical Single Controller Runtime through this composition root instead of
owning a top-level ReAct product runtime:

    Product Request
      -> Product Adapter (astream / ainvoke, product SSE contract)
      -> WorkspaceAgentRuntime (this module)
      -> UnifiedAgentRuntimeService (canonical)
      -> Fixed AgentRunGraph
      -> deterministic plan (single-step or multi-step with bound tools)
      -> StepExecutionGraph -> ReActStepRunner (inside a step only)
      -> Capability Resolution (session tool manifests)
      -> Security Gate -> Approval Gate -> Budget Gate
      -> ToolInvocationGateway / Tool Control Plane
      -> Observation / Acceptance -> Final Gate -> RunOutcome

No direct tool handler calls, no direct model answers, no legacy fallback:
every request is planned, gated (security / approval / budget), traced and
finalized to a RunOutcome through the canonical runtime.
"""

import asyncio
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable

from zuno.agent.contracts import CapabilityPlan, PlanState, PlanStep
from zuno.agent.runtime import (
    RuntimeStartRequest,
    SQLiteAgentRunStore,
    UnifiedAgentRuntimeService,
)
from zuno.agent.runtime.contracts import FinalizationStatus, StrategyMode
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.state import AgentRuntimeSnapshot
from zuno.capability.control_plane import (
    SIDE_EFFECT_RISK_MATRIX,
    ExecutorAdapterContract,
    ToolApprovalPolicy,
    ToolCardManifest,
    ToolExecutionMode,
    ToolSideEffectLevel,
    ToolTrustTier,
)
from zuno.capability.runtime import (
    SecurityApprovalFactSink,
    ToolControlPlaneRuntime,
    ToolRuntimeRequest,
)
from zuno.platform.model_gateway import (
    ModelCategory,
    ModelGateway,
    ModelGatewayRequest,
    ModelGatewayResult,
    ModelProvider,
)


# ---------------------------------------------------------------------------
# Model gateway: the product chat model behind the canonical ModelGateway
# ---------------------------------------------------------------------------


def _run_coroutine_sync(coro: Awaitable[Any]) -> Any:
    """Bridge an async tool/model call into the synchronous gateway contract.

    The canonical runtime executes synchronously (``graph.invoke``). When the
    adapter runs the runtime inside ``asyncio.to_thread`` there is no running
    loop here and ``asyncio.run`` works; otherwise (a live loop on the caller
    thread) the coroutine is run in a dedicated worker thread.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    outcome: dict[str, Any] = {}

    def runner() -> None:
        try:
            outcome["result"] = asyncio.run(coro)
        except BaseException as exc:  # pragma: no cover - re-raised on caller thread
            outcome["error"] = exc

    thread = threading.Thread(target=runner, name="workspace-runtime-bridge", daemon=False)
    thread.start()
    thread.join()
    if "error" in outcome:
        raise outcome["error"]
    return outcome["result"]


class WorkspaceChatModelProvider:
    """ModelProvider adapter over the product chat model.

    Implements the ``ModelProvider`` protocol consumed by ``ModelGateway`` so
    the canonical model steps (``ModelStepExecutor`` / ``ReActStepRunner``)
    run against the same user-configured model the product previously invoked
    directly.
    """

    def __init__(
        self,
        *,
        model: Any,
        provider_id: str = "workspace_chat",
        model_id: str = "workspace-user-model",
    ) -> None:
        self.model = model
        self.provider_id = provider_id
        self.model_id = model_id

    def supports(self, category: ModelCategory) -> bool:
        return category == ModelCategory.CHAT

    def estimate_completion_tokens(self, prompt_tokens: int, max_output_tokens: int) -> int:
        return max(1, min(max_output_tokens, max(4, prompt_tokens // 2)))

    def invoke(self, request: ModelGatewayRequest) -> str:
        prompt = request.prompt
        response = _run_coroutine_sync(self.model.ainvoke(prompt))
        content = getattr(response, "content", response)
        if content is None:
            content = ""
        return str(content).strip()


# ---------------------------------------------------------------------------
# Tool control plane: session tools as governed manifests + executors
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class WorkspaceToolBinding:
    """One session tool bound to a governed manifest.

    ``side_effect_level`` classifies the effect:

    - ``READ`` — security gate + budget + trace; auto-executed.
    - ``WRITE_LOCAL`` (reversible write) — approval policy + idempotency.
    - ``WRITE_EXTERNAL`` / ``DESTRUCTIVE`` (irreversible effect) — explicit
      approval + side-effect claim; never auto-fallback; unknown state goes
      to reconciliation.
    """

    tool_id: str
    display_name: str
    description: str
    input_schema: dict[str, Any]
    side_effect_level: ToolSideEffectLevel
    executor: Callable[[dict[str, Any]], Awaitable[Any] | Any]
    capability_domain: str = "workspace_tool"
    execution_mode: ToolExecutionMode = ToolExecutionMode.LOCAL_FUNCTION
    network_policy: str = "deny"
    timeout_seconds: int = 30


def _binding_executor(binding: WorkspaceToolBinding) -> Callable[[dict[str, Any], Any], Any]:
    def execute(args: dict[str, Any], context: Any) -> Any:
        result = binding.executor(args)
        if asyncio.iscoroutine(result):
            return _run_coroutine_sync(result)
        return result

    return execute


def build_workspace_tool_control_plane(
    *,
    bindings: list[WorkspaceToolBinding],
    security_approval_sink: SecurityApprovalFactSink | None = None,
    tool_unit_of_work_factory: Callable[[], Any] | None = None,
    security_unit_of_work_factory: Callable[[], Any] | None = None,
    infrastructure_unit_of_work_factory: Callable[[str], Any] | None = None,
) -> ToolControlPlaneRuntime:
    """Compose the formal Tool Control Plane for one session's tool set.

    Every tool call must pass Security -> Network Policy -> Approval gates
    inside ``ToolControlPlaneRuntime``; side-effect tools additionally flow
    through ``ToolInvocationGateway`` when the persistence factories are
    provided (production wiring).
    """
    runtime = ToolControlPlaneRuntime(
        security_approval_sink=security_approval_sink,
        tool_unit_of_work_factory=tool_unit_of_work_factory,
        security_unit_of_work_factory=security_unit_of_work_factory,
        infrastructure_unit_of_work_factory=infrastructure_unit_of_work_factory,
    )
    for binding in bindings:
        is_read_only = binding.side_effect_level in {
            ToolSideEffectLevel.NONE,
            ToolSideEffectLevel.READ,
        }
        risk = SIDE_EFFECT_RISK_MATRIX.get(binding.side_effect_level.value, {})
        adapter_id = f"workspace.adapter.{binding.tool_id}"
        manifest = ToolCardManifest(
            tool_id=binding.tool_id,
            owner="platform.services.workspace",
            capability_domain=binding.capability_domain,
            description_for_model=binding.description,
            input_schema=dict(binding.input_schema),
            output_schema={"type": "object"},
            execution_mode=binding.execution_mode,
            trust_tier=ToolTrustTier.WORKSPACE,
            side_effect_level=binding.side_effect_level,
            approval_policy=(
                ToolApprovalPolicy.AUTO if is_read_only else ToolApprovalPolicy.APPROVAL_REQUIRED
            ),
            sandbox_profile=str(risk.get("default_sandbox_profile") or "read_only"),
            credential_policy="none",
            network_policy=binding.network_policy,
            audit_policy="trace",
            budget={"timeout_seconds": binding.timeout_seconds},
            executor_adapter=adapter_id,
        )
        runtime.register_manifest(manifest)
        runtime.register_executor_adapter(
            ExecutorAdapterContract(
                adapter_id=adapter_id,
                execution_mode=binding.execution_mode,
                sandbox_profile=str(risk.get("default_sandbox_profile") or "read_only"),
                network_policy=binding.network_policy,
                credential_policy="none",
                timeout_seconds=binding.timeout_seconds,
            ),
            _binding_executor(binding),
        )
    return runtime


# ---------------------------------------------------------------------------
# Per-session composition root
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class WorkspaceRunRequest:
    """One product request converted to the canonical runtime contract.

    ``plan_kind`` selects the deterministic plan contract:

    - ``simple`` — single-step direct-answer plan (selector-driven).
    - ``tool`` — explicit tool step (bound ``tool_id`` + ``tool_arguments``)
      followed by a grounded answer step.
    - ``complex`` — multi-step deterministic plan (analysis / reflection
      boundary / grounded answer).
    """

    task_id: str
    thread_id: str
    workspace_id: str
    user_id: str
    trace_id: str
    goal: str
    tool_id: str | None = None
    tool_arguments: dict[str, Any] | None = None
    plan_kind: str = "auto"
    budget_limits: dict[str, Any] | None = None
    security_summary: dict[str, Any] | None = None
    budget_verdict: dict[str, Any] | None = None
    idempotency_key: str | None = None
    security_epoch_ref: str | None = None


class WorkspaceAgentRuntime:
    """Composition root: canonical runtime with product dependencies bound.

    One instance per product session (user + workspace + tool set). It never
    falls back to another runtime and never executes a tool outside the
    control plane.
    """

    def __init__(
        self,
        *,
        model: Any,
        bindings: list[WorkspaceToolBinding],
        store_path: Path,
        security_approval_sink: SecurityApprovalFactSink | None = None,
        tool_unit_of_work_factory: Callable[[], Any] | None = None,
        security_unit_of_work_factory: Callable[[], Any] | None = None,
        infrastructure_unit_of_work_factory: Callable[[str], Any] | None = None,
        security_epoch_ref: str = "security-epoch:workspace-v1",
    ) -> None:
        self.bindings = tuple(bindings)
        self._security_epoch_ref = security_epoch_ref
        self._model_gateway = ModelGateway(
            providers=[
                WorkspaceChatModelProvider(
                    model=model,
                    provider_id="workspace_chat",
                    model_id="workspace-user-model",
                )
            ]
        )
        self._tool_control_plane = build_workspace_tool_control_plane(
            bindings=list(bindings),
            security_approval_sink=security_approval_sink,
            tool_unit_of_work_factory=tool_unit_of_work_factory,
            security_unit_of_work_factory=security_unit_of_work_factory,
            infrastructure_unit_of_work_factory=infrastructure_unit_of_work_factory,
        )
        self._store = SQLiteAgentRunStore(store_path)
        self._service = UnifiedAgentRuntimeService(
            store=self._store,
            dependencies=RuntimeDependencies(
                model_gateway=self._model_gateway,
                tool_control_plane=self._tool_control_plane,
                capability_runtime=None,
                memory_engine=None,
                knowledge_runtime=None,
            ),
        )

    # -- canonical surface -------------------------------------------------

    def start(self, request: WorkspaceRunRequest) -> AgentRuntimeSnapshot:
        return self._service.start(self._to_runtime_request(request))

    def resume(self, *, task_id: str, approval_decision: str = "approved") -> AgentRuntimeSnapshot:
        return self._service.resume(task_id=task_id, approval_decision=approval_decision)

    def cancel(self, *, task_id: str, reason: str) -> Any:
        return self._service.cancel(task_id=task_id, reason=reason)

    def snapshot(self, task_id: str) -> AgentRuntimeSnapshot | None:
        return self._service.get_snapshot(task_id)

    def events(self, task_id: str) -> list[dict[str, Any]]:
        return [
            {
                "event_type": event.type,
                "status": event.status,
                "node": event.node,
                "payload": dict(event.payload),
            }
            for event in self._store.events(task_id)
        ]

    def start_with_replay(self, request: WorkspaceRunRequest) -> AgentRuntimeSnapshot:
        """Idempotent product entry: replay a run that already produced a
        snapshot instead of executing a second time.

        Same request -> same task id -> same facts, and the event stream is
        never duplicated. Explicit retry of a FAILED/BLOCKED run (before any
        committed effect) goes through :meth:`start` with the original plan.
        """
        existing = self.snapshot(request.task_id)
        if existing is not None:
            return existing
        return self._service.start(self._to_runtime_request(request))

    def store(self) -> SQLiteAgentRunStore:
        return self._store

    def tool_control_plane(self) -> ToolControlPlaneRuntime:
        return self._tool_control_plane

    # -- product -> runtime conversion -------------------------------------

    def _to_runtime_request(self, request: WorkspaceRunRequest) -> RuntimeStartRequest:
        tool_ids = tuple(binding.tool_id for binding in self.bindings)
        approval_required = tuple(
            binding.tool_id
            for binding in self.bindings
            if binding.side_effect_level
            not in {ToolSideEffectLevel.NONE, ToolSideEffectLevel.READ}
        )
        plan_steps = self._plan_steps(request)
        # Security epoch fail-closed: a stale epoch blocks the plan at
        # planning admission (canonical security gate) before any tool
        # execution or side effect.
        security_summary = dict(request.security_summary or {})
        if (
            request.security_epoch_ref is not None
            and request.security_epoch_ref != self._security_epoch_ref
        ):
            security_summary = {
                **security_summary,
                "decision": "block",
                "recommended_action": "refuse",
                "reason": "stale_security_epoch",
            }
        security_blocked = _is_security_blocked(security_summary)
        budget_blocked = _is_budget_blocked(request.budget_verdict)
        foreign_tool = bool(
            request.plan_kind == "tool"
            and request.tool_id
            and request.tool_id not in tool_ids
        )
        if foreign_tool:
            # Cross-tenant / cross-workspace isolation: a tool id outside this
            # session's bindings fails closed at planning admission (never a
            # KeyError deep inside tool execution).
            security_summary = {
                **security_summary,
                "decision": "block",
                "recommended_action": "refuse",
                "reason": "unknown_tool_for_workspace",
            }
            security_blocked = True
        if security_blocked or budget_blocked:
            # Planning admission blocks the plan: the canonical selector
            # produces a blocked plan (no steps) instead of a tool plan.
            return RuntimeStartRequest(
                run_id=f"run:{request.task_id}",
                thread_id=request.thread_id,
                workspace_id=request.workspace_id,
                user_id=request.user_id,
                task_id=request.task_id,
                trace_id=request.trace_id,
                goal=request.goal,
                capability_ids=(),
                allowed_tools=(),
                approval_required_tools=(),
                budget_limits=request.budget_limits,
                security_summary=security_summary,
                budget_verdict=request.budget_verdict,
                strategy_mode=None,
                plan_steps=(),
            )
        return RuntimeStartRequest(
            run_id=f"run:{request.task_id}",
            thread_id=request.thread_id,
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            task_id=request.task_id,
            trace_id=request.trace_id,
            goal=request.goal,
            capability_ids=tool_ids if plan_steps else (),
            allowed_tools=tool_ids if plan_steps else (),
            approval_required_tools=approval_required if plan_steps else (),
            budget_limits=request.budget_limits,
            security_summary=security_summary,
            budget_verdict=request.budget_verdict,
            strategy_mode=_strategy_mode_for(request),
            plan_steps=tuple(step.model_dump(mode="json") for step in plan_steps) if plan_steps else (),
        )

    def _plan_steps(self, request: WorkspaceRunRequest) -> list[PlanStep] | None:
        if request.plan_kind == "tool" and request.tool_id:
            return [
                PlanStep(
                    step_id="step_1",
                    goal=f"Execute {request.tool_id} and return its governed result.",
                    action_type="tool_call",
                    allowed_capabilities=[request.tool_id],
                    tool_id=request.tool_id,
                    tool_arguments=dict(request.tool_arguments or {}),
                    expected_output="tool result observation",
                    acceptance_criteria=["step status completed"],
                ),
                PlanStep(
                    step_id="step_2",
                    goal="Answer the user from the tool observation only.",
                    action_type="answer_with_evidence",
                    model_role="synthesis",
                    expected_output="grounded answer",
                    acceptance_criteria=["step status completed"],
                ),
            ]
        if request.plan_kind == "complex":
            return [
                PlanStep(
                    step_id="step_1",
                    goal="Analyze the request and decompose it into sub-questions.",
                    action_type="model_transform",
                    expected_output="analysis",
                    acceptance_criteria=["step status completed"],
                ),
                PlanStep(
                    step_id="step_2",
                    goal="Reconcile partial evidence before answering; prepare replan when evidence is low.",
                    action_type="prepare_replan_if_evidence_low",
                    expected_output="reflection note",
                    acceptance_criteria=["step status completed"],
                ),
                PlanStep(
                    step_id="step_3",
                    goal="Produce the final grounded answer.",
                    action_type="answer_from_context",
                    model_role="synthesis",
                    expected_output="grounded answer",
                    acceptance_criteria=["step status completed"],
                ),
            ]
        return None

    # -- final state classification ----------------------------------------

    @staticmethod
    def classify_final_state(snapshot: AgentRuntimeSnapshot) -> str:
        """PHASE22 failure contract for the canonical run.

        - ``EFFECT_COMMITTED`` — a side-effect claim was recorded; no second
          runtime may execute; return the committed facts or reconcile.
        - ``COMPLETED`` — finalized with an outcome.
        - ``FAILED/BLOCKED`` — failed or blocked before any side effect.
        - ``RECONCILIATION_REQUIRED`` — effect state unknown (no terminal
          shape); operator/coordinator confirmation required.
        """
        observations = list(snapshot.observations)
        approval_required = set(snapshot.capability_plan.approval_required_tools)
        committed = any(
            obs.kind == "tool"
            and obs.status == "completed"
            and obs.tool_id in approval_required
            for obs in observations
        )
        if committed:
            return "EFFECT_COMMITTED"
        # A tool step that failed or was blocked (permanent failure, sandbox
        # denial, missing manifest) marks the run FAILED/BLOCKED even when the
        # graph reaches a nominal finalize boundary.
        if any(
            obs.kind == "tool" and obs.status in {"blocked", "failed"}
            for obs in observations
        ):
            return "FAILED/BLOCKED"
        # Planning-admission denials (security / budget) produce a blocked
        # plan and a "direct_answer"-strategy run with the denial reason.
        strategy_reason = str(snapshot.strategy.reason) if snapshot.strategy is not None else ""
        if strategy_reason in {"security_blocked", "budget_guard_blocked"}:
            return "FAILED/BLOCKED"
        if (
            snapshot.plan_state is not None
            and snapshot.plan_state.status == "blocked"
            and not snapshot.plan_state.steps
        ):
            return "FAILED/BLOCKED"
        if snapshot.finalization_status == FinalizationStatus.FINALIZED.value:
            return "COMPLETED"
        if snapshot.finalization_status in {
            FinalizationStatus.FAILED.value,
            FinalizationStatus.BLOCKED.value,
            FinalizationStatus.ABSTAINED.value,
        }:
            return "FAILED/BLOCKED"
        return "RECONCILIATION_REQUIRED"


def _is_security_blocked(security_summary: dict[str, Any]) -> bool:
    decision = str(security_summary.get("decision") or "").lower()
    recommended = str(security_summary.get("recommended_action") or "").lower()
    return decision in {"block", "blocked", "deny", "refuse"} or recommended in {"refuse", "ask_user"}


def _is_budget_blocked(verdict: dict[str, Any] | None) -> bool:
    if verdict is None:
        return False
    return verdict.get("allowed") is False


def _strategy_mode_for(request: WorkspaceRunRequest) -> StrategyMode | str | None:
    if request.plan_kind == "tool":
        return StrategyMode.REACT
    if request.plan_kind == "complex":
        return StrategyMode.PLAN_EXECUTE_WITH_REPLAN
    return None


__all__ = [
    "WorkspaceAgentRuntime",
    "WorkspaceChatModelProvider",
    "WorkspaceRunRequest",
    "WorkspaceToolBinding",
    "build_workspace_tool_control_plane",
]
