from __future__ import annotations

"""PHASE22 workspace / wechat single-controller cutover composition adapter.

Product adapters (``WorkSpaceSimpleAgent`` / ``WeChatAgent``) drive the
canonical Single Controller Runtime through this composition adapter instead
of owning a top-level ReAct product runtime:

    Product Request
      -> Product Adapter (astream / ainvoke, product SSE contract)
      -> WorkspaceAgentRuntime (this module — composition ADAPTER only)
      -> UnifiedAgentRuntimeService (canonical Agent Core facade)
      -> Fixed AgentRunGraph
      -> explicit deterministic plan (single-step / tool / DAG or blocked)
      -> StepExecutionGraph -> ReActStepRunner (inside a step only)
      -> Capability Resolution (session tool manifests)
      -> Security Gate -> Approval Gate -> Budget Gate
      -> ToolInvocationGateway / Tool Control Plane
      -> Observation / Acceptance -> Final Gate -> RunOutcome

PHASE22 architecture repair invariants (per Coordinator review):

- The workspace runtime never owns a second store / checkpointer / security /
  budget / plan activation / tool fact owner: everything is injected from the
  server composition root (``WorkspaceRuntimeComposition``).
- Product mode requires a durable injected store; SQLite exists only behind
  the explicit ``DEVELOPER_TEST_PROFILE``. Missing product bindings fail
  closed with ``BLOCKED_CONFIGURATION`` — never a silent temp-SQLite fallback.
- Tool policy comes from authoritative per-tool declarations (the tool owner
  declares the manifest); unknown tools fail closed with
  ``UNRESOLVED_TOOL_POLICY`` — never a name-based guess defaulting to READ.
- Side-effect tools require the formal ToolInvocationGateway binding and a
  reachable product approval flow; otherwise they fail closed with
  ``SIDE_EFFECT_GATEWAY_NOT_BOUND`` / ``PRODUCT_APPROVAL_FLOW_NOT_BOUND``.
- Security / Budget facts are owner decision refs verified by Agent Core;
  raw caller dicts are never owner decisions.
- Every task has a formal plan; complex tasks use the bound Dynamic DAG
  planner or fail closed with ``DYNAMIC_PLAN_RUNTIME_NOT_BOUND``.

No direct tool handler calls, no direct model answers, no legacy fallback:
every request is planned, gated (security / approval / budget), traced and
finalized to a RunOutcome through the canonical runtime.
"""

import asyncio
import threading
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Awaitable, Callable

from zuno.agent.contracts import (
    BudgetDecisionRef,
    CapabilityPlan,
    PlanState,
    PlanStep,
    SecurityDecisionRef,
)
from zuno.agent.runtime import (
    PROFILE_DEVELOPER_TEST,
    PROFILE_PRODUCT,
    RuntimeStartRequest,
    SQLiteAgentRunStore,
    UnifiedAgentRuntimeService,
)
from zuno.agent.runtime.contracts import FinalizationStatus, StrategyMode
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.owner_refs import (
    BudgetDecisionResolver,
    SecurityDecisionResolver,
    budget_ref_hash,
    security_ref_hash,
    validate_budget_decision_ref,
    validate_security_decision_ref,
)
from zuno.agent.runtime.state import AgentRuntimeSnapshot
from zuno.agent.runtime.store import AgentRunStore
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
    manifest_policy_hash,
)
from zuno.platform.model_gateway import (
    ModelCategory,
    ModelGateway,
    ModelGatewayRequest,
    ModelGatewayResult,
    ModelProvider,
)

UNRESOLVED_TOOL_POLICY = "UNRESOLVED_TOOL_POLICY"
SIDE_EFFECT_GATEWAY_NOT_BOUND = "SIDE_EFFECT_GATEWAY_NOT_BOUND"
PRODUCT_APPROVAL_FLOW_NOT_BOUND = "PRODUCT_APPROVAL_FLOW_NOT_BOUND"
DYNAMIC_PLAN_RUNTIME_NOT_BOUND = "DYNAMIC_PLAN_RUNTIME_NOT_BOUND"


class BlockedConfiguration(RuntimeError):
    """A required product binding is missing; the run must fail closed."""


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
class DeclaredToolPolicy:
    """Tool-owner-declared policy (PHASE22 repair, B2).

    The tool owner declares the policy at registration time; nothing is
    inferred from the tool name. An undeclared tool stays unresolved and
    fails closed with ``UNRESOLVED_TOOL_POLICY`` at execution.
    """

    side_effect_level: ToolSideEffectLevel
    execution_mode: ToolExecutionMode = ToolExecutionMode.LOCAL_FUNCTION
    network_policy: str = "deny"
    credential_policy: str = "none"

    def to_metadata(self) -> dict[str, str]:
        return {
            "tool_policy_side_effect_level": self.side_effect_level.value,
            "tool_policy_execution_mode": self.execution_mode.value,
            "tool_policy_network_policy": self.network_policy,
            "tool_policy_credential_policy": self.credential_policy,
            "tool_policy_resolved": "true",
        }


def declared_policy_from_metadata(metadata: dict[str, Any] | None) -> DeclaredToolPolicy | None:
    """Resolve a tool-owner declaration from structured metadata.

    ``None`` means the tool has no owner-declared policy (unresolved -> the
    tool fails closed at execution).
    """
    if not metadata:
        return None
    if str(metadata.get("tool_policy_resolved") or "").lower() != "true":
        return None
    raw_level = str(metadata.get("tool_policy_side_effect_level") or "").lower()
    if raw_level not in ToolSideEffectLevel._value2member_map_:
        return None
    raw_mode = str(metadata.get("tool_policy_execution_mode") or "").lower()
    try:
        execution_mode = ToolExecutionMode(raw_mode)
    except ValueError:
        execution_mode = ToolExecutionMode.LOCAL_FUNCTION
    return DeclaredToolPolicy(
        side_effect_level=ToolSideEffectLevel(raw_level),
        execution_mode=execution_mode,
        network_policy=str(metadata.get("tool_policy_network_policy") or "deny"),
        credential_policy=str(metadata.get("tool_policy_credential_policy") or "none"),
    )


@dataclass(frozen=True, slots=True)
class WorkspaceToolBinding:
    """One session tool bound to an authoritative owner-declared manifest.

    PHASE22 repair (B2): the policy is declared by the tool owner at
    registration time — never inferred from the tool name. A binding without
    a resolved policy (``policy_resolution="unresolved"``) fails closed with
    ``UNRESOLVED_TOOL_POLICY`` at execution instead of defaulting to READ.
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
    credential_policy: str = "none"
    timeout_seconds: int = 30
    policy_resolution: str = "resolved"
    manifest_version: str = "v1"


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
    tenant_id: str,
    workspace_id: str,
    security_approval_sink: SecurityApprovalFactSink | None = None,
    tool_unit_of_work_factory: Callable[[], Any] | None = None,
    security_unit_of_work_factory: Callable[[], Any] | None = None,
    infrastructure_unit_of_work_factory: Callable[[str], Any] | None = None,
) -> ToolControlPlaneRuntime:
    """Compose the formal Tool Control Plane for one session's tool set.

    Every tool call must pass Security -> Network Policy -> Approval gates
    inside ``ToolControlPlaneRuntime``; side-effect tools additionally flow
    through ``ToolInvocationGateway`` when the persistence factories are
    bound. Missing gateway factories block side-effect execution
    (``SIDE_EFFECT_GATEWAY_NOT_BOUND``) — never direct executor fallback.
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
            credential_policy=binding.credential_policy,
            network_policy=binding.network_policy,
            audit_policy="trace",
            budget={"timeout_seconds": binding.timeout_seconds},
            executor_adapter=adapter_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            manifest_version=binding.manifest_version,
            policy_resolution=binding.policy_resolution,
        )
        # Authoritative policy hash over the declared policy fields; a forged
        # or tampered manifest fails closed at execution.
        manifest = replace(
            manifest,
            policy_hash=manifest_policy_hash(manifest),
        )
        runtime.register_manifest(manifest)
        runtime.register_executor_adapter(
            ExecutorAdapterContract(
                adapter_id=adapter_id,
                execution_mode=binding.execution_mode,
                sandbox_profile=str(risk.get("default_sandbox_profile") or "read_only"),
                network_policy=binding.network_policy,
                credential_policy=binding.credential_policy,
                timeout_seconds=binding.timeout_seconds,
            ),
            _binding_executor(binding),
        )
    return runtime


# ---------------------------------------------------------------------------
# Server composition root binding
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class WorkspaceRuntimeComposition:
    """Formal server-product composition binding (PHASE22 repair).

    The workspace agent never constructs its own durable store, security /
    budget owner facts, plan activation, side-effect gateway or approval
    flow: every one of these is injected from the server composition root.
    Missing product bindings fail closed — the adapter never degrades to a
    per-session temp SQLite runtime.

    The composition binds infrastructure only. It does NOT own a tenant /
    workspace identity: tenant, workspace and principal come from the real
    product request / auth context and flow through every runtime ref (never
    a synthetic ``tenant:default``).
    """

    store: AgentRunStore | None = None
    tool_unit_of_work_factory: Callable[[], Any] | None = None
    security_unit_of_work_factory: Callable[[], Any] | None = None
    infrastructure_unit_of_work_factory: Callable[[str], Any] | None = None
    security_approval_sink: SecurityApprovalFactSink | None = None
    # Security owner fact: the epoch the server security layer currently
    # certifies. Product requests may only reference this epoch.
    security_epoch_ref: str = ""
    # Product approval flow binding: "none" -> side-effect tools fail closed
    # with PRODUCT_APPROVAL_FLOW_NOT_BOUND (read-only cutover only).
    approval_flow: str = "none"
    # Security / Budget owner fact resolvers (owner ports). Product adapters
    # carry only opaque decision ids; Agent Core / Composition resolves the
    # formal owner fact through these injected ports. Unbound resolvers make
    # the corresponding admission fail closed (never caller self-attestation).
    security_decision_resolver: "SecurityDecisionResolver | None" = None
    budget_decision_resolver: "BudgetDecisionResolver | None" = None
    # Formal Dynamic DAG planner binding; unbound -> complex tasks fail
    # closed with DYNAMIC_PLAN_RUNTIME_NOT_BOUND.
    dynamic_dag_planner: Callable[[Any], list[PlanStep]] | None = None


_workspace_product_composition: WorkspaceRuntimeComposition | None = None


def configure_workspace_product_composition(composition: WorkspaceRuntimeComposition | None) -> None:
    """Bind the server composition root for workspace product adapters.

    ``None`` clears the binding. In product mode a missing binding is a
    ``BLOCKED_CONFIGURATION`` at adapter initialization — never a silent
    fallback to temp SQLite.
    """
    global _workspace_product_composition
    _workspace_product_composition = composition


def get_workspace_product_composition() -> WorkspaceRuntimeComposition | None:
    return _workspace_product_composition


# ---------------------------------------------------------------------------
# Per-session composition adapter
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class WorkspaceRunRequest:
    """One product request converted to the canonical runtime contract.

    PHASE22 repair (B6): identity is the product submission —
    ``client_request_id`` / ``submission_id`` bound to tenant / workspace /
    principal. The request content hash is only a ``content_fingerprint`` and
    is never the business request identity.

    ``plan_kind`` selects the plan contract:

    - ``simple`` — explicit deterministic single-step plan
      (``answer_from_context``), still traced / budgeted / gated.
    - ``tool`` — explicit tool step (bound ``tool_id`` + ``tool_arguments``)
      followed by a grounded answer step.
    - ``complex`` — bound Dynamic DAG planner; unbound fails closed with
      ``DYNAMIC_PLAN_RUNTIME_NOT_BOUND``.
    """

    task_id: str
    thread_id: str
    tenant_id: str
    workspace_id: str
    principal_id: str
    submission_id: str
    client_request_id: str
    user_id: str
    trace_id: str
    goal: str
    conversation_id: str = ""
    agent_version: str = ""
    content_fingerprint: str = ""
    tool_id: str | None = None
    tool_arguments: dict[str, Any] | None = None
    plan_kind: str = "auto"
    budget_limits: dict[str, Any] | None = None
    security_epoch_ref: str = ""
    # Opaque owner fact references (PHASE22 repair): the Product Adapter
    # carries only opaque decision ids; the formal facts are resolved through
    # the injected Security / Budget owner resolvers. Caller-supplied full
    # refs are never trusted in the product profile.
    security_decision_id: str = ""
    budget_decision_id: str = ""
    # Untrusted envelopes in the product profile: only ``decision_id`` is
    # used to locate the owner fact; the caller may not mint its own allow.
    security_decision_ref: dict[str, Any] | None = None
    budget_decision_ref: dict[str, Any] | None = None
    idempotency_key: str = ""


class WorkspaceAgentRuntime:
    """Composition adapter: canonical runtime with product dependencies bound.

    One instance per product session (tenant + user + workspace + tool set).
    It never falls back to another runtime, never executes a tool outside the
    control plane, and never owns a second store / security / budget / plan
    activation / side-effect gateway.
    """

    def __init__(
        self,
        *,
        model: Any,
        bindings: list[WorkspaceToolBinding],
        tenant_id: str,
        workspace_id: str,
        principal_id: str,
        profile: str = PROFILE_PRODUCT,
        store: AgentRunStore | None = None,
        sqlite_store_path: Path | None = None,
        security_approval_sink: SecurityApprovalFactSink | None = None,
        tool_unit_of_work_factory: Callable[[], Any] | None = None,
        security_unit_of_work_factory: Callable[[], Any] | None = None,
        infrastructure_unit_of_work_factory: Callable[[str], Any] | None = None,
        security_epoch_ref: str = "",
        approval_flow: str = "none",
        security_decision_resolver: "SecurityDecisionResolver | None" = None,
        budget_decision_resolver: "BudgetDecisionResolver | None" = None,
        dynamic_dag_planner: Callable[[Any], list[PlanStep]] | None = None,
    ) -> None:
        # PHASE22 repair (B7): real tenant / workspace / principal identity
        # must be supplied from the product request / auth context. Missing
        # identity fails closed — never a synthetic tenant:default and never
        # a workspace guessed from user_id.
        if not str(tenant_id or "").strip():
            raise BlockedConfiguration(
                "BLOCKED_CONFIGURATION: product runtime requires a real tenant_id "
                "from the product request/auth context"
            )
        if not str(workspace_id or "").strip():
            raise BlockedConfiguration(
                "BLOCKED_CONFIGURATION: product runtime requires a real workspace_id "
                "from the product request/auth context"
            )
        self._tenant_id = tenant_id
        self._workspace_id = workspace_id
        self._principal_id = principal_id
        self._profile = profile
        self._security_epoch_ref = security_epoch_ref
        self._approval_flow = approval_flow
        self._security_decision_resolver = security_decision_resolver
        self._budget_decision_resolver = budget_decision_resolver
        self._dynamic_dag_planner = dynamic_dag_planner
        self.bindings = tuple(bindings)
        self._side_effect_tool_ids = tuple(
            binding.tool_id
            for binding in self.bindings
            if binding.side_effect_level not in {ToolSideEffectLevel.NONE, ToolSideEffectLevel.READ}
        )

        # PHASE22 repair (B1): the durable store comes from the server
        # composition root. SQLite is only an explicit developer test profile;
        # a product runtime without an injected store is BLOCKED_CONFIGURATION.
        if store is not None:
            self._store = store
        elif profile == PROFILE_DEVELOPER_TEST:
            if sqlite_store_path is None:
                raise BlockedConfiguration(
                    "BLOCKED_CONFIGURATION: DEVELOPER_TEST_PROFILE requires an explicit sqlite_store_path"
                )
            self._store = SQLiteAgentRunStore(sqlite_store_path)
        else:
            raise BlockedConfiguration(
                "BLOCKED_CONFIGURATION: product runtime requires an injected durable AgentRunStore "
                "from the server composition root"
            )

        # PHASE22 repair (B3): side-effect bindings require the formal
        # ToolInvocationGateway UoW factories; fail closed at composition in
        # product mode (the control plane also fails closed per tool).
        if self._side_effect_tool_ids and not (
            tool_unit_of_work_factory
            and security_unit_of_work_factory
            and infrastructure_unit_of_work_factory
        ):
            if profile == PROFILE_PRODUCT:
                raise BlockedConfiguration(
                    "BLOCKED_CONFIGURATION: side-effect tools require Tool/Security/Infrastructure "
                    "UoW factories from the server composition root"
                )

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
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            security_approval_sink=security_approval_sink,
            tool_unit_of_work_factory=tool_unit_of_work_factory,
            security_unit_of_work_factory=security_unit_of_work_factory,
            infrastructure_unit_of_work_factory=infrastructure_unit_of_work_factory,
        )
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

    def resume(
        self,
        *,
        task_id: str,
        approval_decision: str = "approved",
    ) -> AgentRuntimeSnapshot:
        return self._service.resume(
            task_id=task_id,
            approval_decision=approval_decision,
            tenant_id=self._tenant_id,
            workspace_id=self._workspace_id,
        )

    def cancel(self, *, task_id: str, reason: str) -> Any:
        self._assert_scope(task_id)
        return self._service.cancel(task_id=task_id, reason=reason)

    def snapshot(self, task_id: str) -> AgentRuntimeSnapshot | None:
        return self._service.get_snapshot(
            task_id,
            tenant_id=self._tenant_id,
            workspace_id=self._workspace_id,
        )

    def events(self, task_id: str) -> list[dict[str, Any]]:
        self._assert_scope(task_id)
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

        Same ``client_request_id`` -> same task id -> same facts, and the
        event stream is never duplicated. A different ``client_request_id``
        (even with the same text) creates a new run.
        """
        existing = self.snapshot(request.task_id)
        if existing is not None:
            return existing
        return self._service.start(self._to_runtime_request(request))

    def store(self) -> AgentRunStore:
        return self._store

    def tool_control_plane(self) -> ToolControlPlaneRuntime:
        return self._tool_control_plane

    def _assert_scope(self, task_id: str) -> None:
        if not self._store.has_task(task_id):
            return
        snapshot = self._service.get_snapshot(
            task_id,
            tenant_id=self._tenant_id,
            workspace_id=self._workspace_id,
        )
        if snapshot is None:
            raise PermissionError(
                f"runtime task outside tenant/workspace scope: {task_id} "
                f"(tenant={self._tenant_id}, workspace={self._workspace_id})"
            )

    # -- product -> runtime conversion -------------------------------------

    def _to_runtime_request(self, request: WorkspaceRunRequest) -> RuntimeStartRequest:
        tool_ids = tuple(binding.tool_id for binding in self.bindings)
        approval_required = tuple(
            binding.tool_id
            for binding in self.bindings
            if binding.side_effect_level
            not in {ToolSideEffectLevel.NONE, ToolSideEffectLevel.READ}
        )
        foreign_tool = bool(
            request.plan_kind == "tool"
            and request.tool_id
            and request.tool_id not in tool_ids
        )
        unresolved_tool = bool(
            request.plan_kind == "tool"
            and request.tool_id
            and not any(
                binding.tool_id == request.tool_id and binding.policy_resolution == "resolved"
                for binding in self.bindings
            )
        )
        side_effect_flow_blocked = bool(
            request.plan_kind == "tool"
            and request.tool_id
            and request.tool_id in self._side_effect_tool_ids
            and self._approval_flow == "none"
        )
        complex_unbound = bool(
            request.plan_kind == "complex" and self._dynamic_dag_planner is None
        )

        # PHASE22 repair (B7): real tenant / workspace identity from the
        # product request. Missing identity fails closed at admission (the
        # adapter also fails closed at composition); never tenant:default.
        if not str(request.tenant_id or "").strip():
            return self._blocked_request(
                request=request,
                reason="BLOCKED_CONFIGURATION:missing_product_tenant_context",
            )
        if not str(request.workspace_id or "").strip():
            return self._blocked_request(
                request=request,
                reason="BLOCKED_CONFIGURATION:missing_product_workspace_context",
            )

        # PHASE22 repair (B4): Security / Budget owner facts. The adapter
        # carries only opaque decision ids; the owner resolvers produce the
        # formal facts. Caller-supplied full refs are never trusted in the
        # product profile (a resolver must produce the fact).
        security_ref, security_error = self._resolve_security_ref(request)
        budget_ref, budget_error = self._resolve_budget_ref(request)
        security_verdict = validate_security_decision_ref(
            security_ref,
            tenant_id=request.tenant_id,
            workspace_id=request.workspace_id,
            principal_id=request.principal_id or request.user_id,
            action="tool.execute",
            resource=",".join(tool_ids if request.plan_kind == "tool" else ()),
            bound_security_epoch_ref=self._security_epoch_ref,
            required=(
                self._profile == PROFILE_PRODUCT
                and bool(request.plan_kind == "tool")
                and bool(request.tool_id)
            ),
        )
        budget_verdict = validate_budget_decision_ref(
            budget_ref,
            tenant_id=request.tenant_id,
            workspace_id=request.workspace_id,
            run_id=f"run:{request.task_id}",
            required=(
                self._profile == PROFILE_PRODUCT
                and bool(request.plan_kind in {"simple", "tool", "complex"})
            ),
        )

        admission_reason = ""
        if (
            request.security_epoch_ref
            and self._security_epoch_ref
            and request.security_epoch_ref != self._security_epoch_ref
        ):
            # Security epoch fail-closed: a stale caller-supplied epoch blocks
            # the plan at planning admission, before any tool execution.
            admission_reason = "stale_security_epoch"
        elif security_error:
            admission_reason = security_error
        elif not security_verdict.allowed:
            admission_reason = security_verdict.reason
        elif budget_error:
            admission_reason = budget_error
        elif not budget_verdict.allowed:
            admission_reason = budget_verdict.reason
        elif foreign_tool:
            # PHASE22 repair (B7): a tool outside this session's tenant /
            # workspace bindings fails closed at planning admission.
            admission_reason = "unknown_tool_for_workspace"
        elif unresolved_tool:
            admission_reason = UNRESOLVED_TOOL_POLICY
        elif side_effect_flow_blocked:
            # PHASE22 repair (B9): side effects require a reachable product
            # approval flow; otherwise they fail closed (read-only cutover).
            admission_reason = PRODUCT_APPROVAL_FLOW_NOT_BOUND
        elif complex_unbound:
            # PHASE22 repair (B5): complex tasks require the formal Dynamic
            # DAG planner; an unbound composition must never fake a fixed
            # three-step DAG or fall back to a direct answer.
            admission_reason = DYNAMIC_PLAN_RUNTIME_NOT_BOUND

        plan_steps = None
        if not admission_reason:
            plan_steps = self._plan_steps(request)

        if admission_reason:
            return self._blocked_request(
                request=request,
                reason=admission_reason,
                security_ref=security_ref,
                budget_ref=budget_ref,
            )

        capability_ids = tool_ids if (plan_steps and request.plan_kind == "tool") else ()
        return RuntimeStartRequest(
            run_id=f"run:{request.task_id}",
            thread_id=request.thread_id,
            tenant_id=request.tenant_id,
            workspace_id=request.workspace_id,
            principal_id=request.principal_id,
            user_id=request.user_id,
            task_id=request.task_id,
            trace_id=request.trace_id,
            goal=request.goal,
            submission_id=request.submission_id,
            client_request_id=request.client_request_id,
            conversation_id=request.conversation_id,
            agent_version=request.agent_version,
            content_fingerprint=request.content_fingerprint,
            capability_ids=capability_ids,
            allowed_tools=capability_ids,
            approval_required_tools=approval_required if (plan_steps and request.plan_kind == "tool") else (),
            budget_limits=request.budget_limits,
            security_decision_ref=security_ref.to_dict() if security_ref else None,
            budget_decision_ref=budget_ref.to_dict() if budget_ref else None,
            security_epoch_ref=self._security_epoch_ref,
            profile=self._profile,
            strategy_mode=_strategy_mode_for(request),
            plan_steps=tuple(step.model_dump(mode="json") for step in plan_steps) if plan_steps else (),
            security_summary=self._security_summary(request, security_ref),
            budget_verdict=self._budget_verdict_payload(request, budget_ref),
        )

    def _blocked_request(
        self,
        *,
        request: WorkspaceRunRequest,
        reason: str,
        security_ref: SecurityDecisionRef | None = None,
        budget_ref: BudgetDecisionRef | None = None,
    ) -> RuntimeStartRequest:
        """Fail-closed RuntimeStartRequest: no plan, no tools, reason visible."""
        return RuntimeStartRequest(
            run_id=f"run:{request.task_id}",
            thread_id=request.thread_id,
            tenant_id=request.tenant_id,
            workspace_id=request.workspace_id,
            principal_id=request.principal_id,
            user_id=request.user_id,
            task_id=request.task_id,
            trace_id=request.trace_id,
            goal=request.goal,
            submission_id=request.submission_id,
            client_request_id=request.client_request_id,
            conversation_id=request.conversation_id,
            agent_version=request.agent_version,
            content_fingerprint=request.content_fingerprint,
            capability_ids=(),
            allowed_tools=(),
            approval_required_tools=(),
            budget_limits=request.budget_limits,
            security_decision_ref=security_ref.to_dict() if security_ref else None,
            budget_decision_ref=budget_ref.to_dict() if budget_ref else None,
            security_epoch_ref=self._security_epoch_ref,
            profile=self._profile,
            strategy_mode=None,
            plan_steps=(),
            security_summary={
                "decision": "block",
                "recommended_action": "refuse",
                "reason": reason,
            },
            budget_verdict={"allowed": False, "reason": reason},
        )

    def _security_summary(
        self,
        request: WorkspaceRunRequest,
        ref: SecurityDecisionRef | None,
    ) -> dict[str, Any]:
        """Owner fact trace refs for the resolved Security decision."""
        summary: dict[str, Any] = {
            "decision": "allow",
            "recommended_action": "proceed",
            "reason": "security_owner_fact_resolved",
        }
        if ref is not None:
            summary["decision_ref"] = ref.decision_id
            summary["trace_ref"] = f"security-decision:{ref.decision_id}"
        return summary

    def _budget_verdict_payload(
        self,
        request: WorkspaceRunRequest,
        ref: BudgetDecisionRef | None,
    ) -> dict[str, Any] | None:
        """Owner fact trace refs for the resolved Budget admission."""
        if ref is None:
            return {"allowed": True, "reason": "no_budget_decision_required"}
        payload: dict[str, Any] = {
            "allowed": bool(ref.allowed),
            "reason": "budget_owner_fact_resolved",
            "owner": ref.owner,
        }
        if ref.budget_decision_id:
            payload["decision_ref"] = ref.budget_decision_id
            payload["trace_ref"] = f"budget-decision:{ref.budget_decision_id}"
        return payload

    def _resolve_security_ref(
        self,
        request: WorkspaceRunRequest,
    ) -> tuple[SecurityDecisionRef | None, str | None]:
        """Resolve the Security-owner fact from an opaque decision id.

        Product profile: the caller-supplied full ref is never trusted — only
        ``decision_id`` locates the owner fact through the injected resolver;
        an unbound resolver or a missing owner fact fails closed. Developer
        test profile: caller-supplied refs are explicitly accepted (test-only,
        still hash / scope / expiry-validated by Agent Core).
        """
        decision_id = str(request.security_decision_id or "").strip()
        envelope = dict(request.security_decision_ref or {})
        if not decision_id and envelope.get("decision_id"):
            decision_id = str(envelope["decision_id"]).strip()
        resolver = self._security_decision_resolver
        if self._profile == PROFILE_PRODUCT:
            if not decision_id:
                # No owner fact requested; whether one is *required* is
                # decided by validation (tool plans in the product profile).
                return None, None
            if resolver is None:
                return None, "security_owner_resolver_unbound"
            fact = resolver.resolve(
                decision_id,
                self._security_owner_context(request),
            )
            if not fact:
                return None, "security_owner_fact_not_found"
            return SecurityDecisionRef(**fact), None
        # Developer test profile: caller-supplied refs are trusted (test
        # profile only — never product evidence).
        if request.security_decision_ref:
            try:
                return SecurityDecisionRef(**request.security_decision_ref), None
            except Exception:
                return None, "security_ref_invalid"
        if decision_id and resolver is not None:
            fact = resolver.resolve(
                decision_id,
                self._security_owner_context(request),
            )
            if fact:
                return SecurityDecisionRef(**fact), None
        return None, None

    def _security_owner_context(self, request: WorkspaceRunRequest) -> dict[str, Any]:
        return {
            "tenant_id": request.tenant_id,
            "workspace_id": request.workspace_id,
            "principal_id": request.principal_id or request.user_id,
            "action": "tool.execute",
            "resource": ",".join(
                binding.tool_id
                for binding in self.bindings
                if binding.tool_id == request.tool_id
            )
            or request.tool_id
            or "",
            "security_epoch_ref": request.security_epoch_ref or self._security_epoch_ref,
            "run_id": f"run:{request.task_id}",
            "task_id": request.task_id,
            "trace_id": request.trace_id,
        }

    def _resolve_budget_ref(
        self,
        request: WorkspaceRunRequest,
    ) -> tuple[BudgetDecisionRef | None, str | None]:
        """Resolve the Budget-owner admission fact from an opaque decision id.

        Product profile: the Budget owner resolver is mandatory for planned
        runs (formal Budget Admission); an unbound resolver fails closed.
        ``decision_id`` may be empty when the resolver admits from the request
        context. Developer test profile: caller-supplied refs are accepted
        (test profile only).
        """
        decision_id = str(request.budget_decision_id or "").strip()
        envelope = dict(request.budget_decision_ref or {})
        if not decision_id and envelope.get("budget_decision_id"):
            decision_id = str(envelope["budget_decision_id"]).strip()
        resolver = self._budget_decision_resolver
        if self._profile == PROFILE_PRODUCT:
            if resolver is None:
                return None, "budget_owner_resolver_unbound"
            fact = resolver.resolve(
                decision_id,
                {
                    "tenant_id": request.tenant_id,
                    "workspace_id": request.workspace_id,
                    "principal_id": request.principal_id or request.user_id,
                    "run_id": f"run:{request.task_id}",
                    "task_id": request.task_id,
                    "trace_id": request.trace_id,
                    "budget_limits": dict(request.budget_limits or {}),
                },
            )
            if not fact:
                if decision_id:
                    return None, "budget_owner_fact_not_found"
                return None, None
            return BudgetDecisionRef(**fact), None
        # Developer test profile.
        if request.budget_decision_ref:
            try:
                return BudgetDecisionRef(**request.budget_decision_ref), None
            except Exception:
                return None, "budget_ref_invalid"
        if resolver is not None:
            fact = resolver.resolve(
                decision_id,
                {
                    "tenant_id": request.tenant_id,
                    "workspace_id": request.workspace_id,
                    "principal_id": request.principal_id or request.user_id,
                    "run_id": f"run:{request.task_id}",
                    "task_id": request.task_id,
                    "trace_id": request.trace_id,
                    "budget_limits": dict(request.budget_limits or {}),
                },
            )
            if fact:
                return BudgetDecisionRef(**fact), None
        return None, None

    def _plan_steps(self, request: WorkspaceRunRequest) -> list[PlanStep] | None:
        # PHASE22 repair (B5): every task has a formal plan. Simple tasks get
        # an explicit deterministic single-step plan (no direct-answer
        # bypass); tool tasks bind real tool id + arguments in the plan.
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
            # The formal Dynamic DAG planner binding owns complex plans.
            # ``_to_runtime_request`` fails closed before reaching here when
            # the planner is not bound (DYNAMIC_PLAN_RUNTIME_NOT_BOUND).
            if self._dynamic_dag_planner is None:
                return None
            steps = self._dynamic_dag_planner(request)
            if not steps:
                return None
            return steps
        return [
            PlanStep(
                step_id="step_1",
                goal="Answer the user from current context.",
                action_type="answer_from_context",
                model_role="synthesis",
                expected_output="grounded answer",
                acceptance_criteria=["step status completed"],
            ),
        ]

    # -- final state classification ----------------------------------------

    @staticmethod
    def classify_final_state(snapshot: AgentRuntimeSnapshot) -> str:
        """PHASE22 failure contract for the canonical run.

        - ``EFFECT_COMMITTED`` — a durable side-effect receipt was recorded
          (effect certainty CONFIRMED_EFFECT); no second runtime may execute.
        - ``RECONCILIATION_REQUIRED`` — a side effect was dispatched but its
          outcome is unknown (UNKNOWN_EFFECT); no automatic retry.
        - ``COMPLETED`` — finalized with an outcome.
        - ``FAILED/BLOCKED`` — failed or blocked before any side effect.
        """
        effect_certainties = [
            str(obs.metadata.get("effect_certainty") or "")
            for obs in snapshot.observations
            if obs.kind == "tool"
        ]
        if any(certainty == "CONFIRMED_EFFECT" for certainty in effect_certainties):
            return "EFFECT_COMMITTED"
        if any(certainty == "UNKNOWN_EFFECT" for certainty in effect_certainties):
            return "RECONCILIATION_REQUIRED"
        # A tool step that failed or was blocked (permanent failure, sandbox
        # denial, missing manifest, unbound gateway) marks the run
        # FAILED/BLOCKED even when the graph reaches a nominal finalize
        # boundary.
        if any(
            obs.kind == "tool" and obs.status in {"blocked", "failed"}
            for obs in snapshot.observations
        ):
            return "FAILED/BLOCKED"
        # Planning-admission denials (security / budget / unresolved policy /
        # unbound approval flow / unbound dynamic DAG) produce a blocked plan.
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


def _strategy_mode_for(request: WorkspaceRunRequest) -> StrategyMode | str | None:
    if request.plan_kind == "tool":
        return StrategyMode.REACT
    if request.plan_kind == "complex":
        return StrategyMode.PLAN_EXECUTE_WITH_REPLAN
    return None


__all__ = [
    "BlockedConfiguration",
    "DeclaredToolPolicy",
    "DYNAMIC_PLAN_RUNTIME_NOT_BOUND",
    "PRODUCT_APPROVAL_FLOW_NOT_BOUND",
    "SIDE_EFFECT_GATEWAY_NOT_BOUND",
    "UNRESOLVED_TOOL_POLICY",
    "WorkspaceAgentRuntime",
    "WorkspaceChatModelProvider",
    "WorkspaceRunRequest",
    "WorkspaceRuntimeComposition",
    "WorkspaceToolBinding",
    "build_workspace_tool_control_plane",
    "configure_workspace_product_composition",
    "declared_policy_from_metadata",
    "get_workspace_product_composition",
]
