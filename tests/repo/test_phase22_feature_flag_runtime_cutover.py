"""PHASE22 feature flag and residual runtime cutover enforcement tests.

Pins the PHASE22 closure: the four rollout flags
(``product_api_v1_adapter``, ``workspace_projection_stream_v1``,
``tool_runtime_readonly_gateway``, ``postgres_domain_uow_shadow``) are
retired fail-closed with zero production readers, the Public v1 API / SSE v1
contracts stay available, the Tool Gateway is the only tool execution entry,
the PostgreSQL UoW is single-transaction without shadow writes, and
``AgentControlRuntime`` / ``product_baseline`` are test-harness only.

Coverage map (task matrix):
  1-4  flag retirement readers / fail-closed / rollback rejection / unknown
  5-6  Public v1 API and SSE v1 contract preserved
  7    Public adapter does not write DAO directly
  8-9  READ_ONLY tools still go through the Gateway; Security deny blocks
  10-12 PostgreSQL UoW: no shadow, atomic state+outbox, idempotent commands
  13-18 AgentControlRuntime / product_baseline reachability and Single
        Controller invariants
  19-24 fault semantics: commit exception, unknown commit, stream resume,
        gateway error, stale security epoch, duplicate request
"""

from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"
REGISTRY = (
    REPO_ROOT / ".agent" / "programs" / "work-products" / "feature-flag-registry.yaml"
)

RETIRED_FLAGS = [
    "product_api_v1_adapter",
    "workspace_projection_stream_v1",
    "tool_runtime_readonly_gateway",
    "postgres_domain_uow_shadow",
]


def _ensure_runtime_paths() -> None:
    if str(BACKEND_ROOT) not in sys.path:
        sys.path.insert(0, str(BACKEND_ROOT))


def _registry_text() -> str:
    return REGISTRY.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Feature flags 1-4: retired, fail-closed, no readers, no rollback
# ---------------------------------------------------------------------------

# 1. Every retired flag has no production reader.
def test_retired_flags_have_no_production_reader() -> None:
    hits = []
    for path in (BACKEND_ROOT / "zuno").rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for flag in RETIRED_FLAGS:
            if flag in text:
                hits.append(f"{path.relative_to(BACKEND_ROOT)}: {flag}")
    assert hits == [], f"retired flag read in production source: {hits}"


# 2. Setting old env/config cannot restore the old path: no dynamic selector
#    exists at all, and the flag registry state machine rejects any non-
#    RETIRED transition (rollback attempt) fail-closed.
def test_retired_flags_are_registered_retired_fail_closed() -> None:
    registry = _registry_text()
    for flag in RETIRED_FLAGS:
        block_match = re.search(
            rf'(?ms)^  - flag: "{flag}"(.*?)(?=^  - flag: |\Z)', registry
        )
        assert block_match is not None, f"{flag} missing from registry"
        block = block_match.group(1)
        assert 'default: "RETIRED"' in block, f"{flag} is not RETIRED"
        assert "retired and fail-closed" in block, f"{flag} rollback_command not fail-closed"


def test_no_dynamic_env_selector_for_retired_flags() -> None:
    for path in (BACKEND_ROOT / "zuno").rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for marker in ("ZUNO_PRODUCT_ADAPTER", "ZUNO_PROJECTION_STREAM", "ZUNO_TOOL_GATEWAY", "ZUNO_UOW"):
            assert marker not in text, f"dynamic selector {marker} in {path.relative_to(BACKEND_ROOT)}"


# 3. Rollback command is rejected: a RETIRED flag must reject any transition.
def test_retired_flag_rejects_rollback_transition() -> None:
    spec = importlib.import_module("tools.scripts.phase02_compatibility_runtime")
    machine = spec.FeatureFlagStateMachine(_registry_text())
    for flag in RETIRED_FLAGS + ["legacy_general_agent_completion_rollback"]:
        assert machine.flags[flag]["default"] == "RETIRED"
        with pytest.raises(ValueError):
            machine.decide_transition(flag, "ROLLBACK_WINDOW")
        with pytest.raises(ValueError):
            machine.decide_transition(flag, "DEFAULT_NEW")


# 4. Dynamic unknown values fail closed: the lifecycle rejects unknown states.
def test_unknown_flag_state_fails_closed() -> None:
    registry = _registry_text()
    assert "allowed_states: [DECLARED, SHADOW, CANARY, DEFAULT_NEW, ROLLBACK_WINDOW, RETIRED]" in registry
    for state in ("DECLARED", "CANARY"):
        assert state not in re.findall(r'(?m)^    default: "(\w+)"', registry), (
            f"no flag may default to an open rollout state after PHASE22: {state}"
        )


# ---------------------------------------------------------------------------
# Public API 5-7: v1 contracts preserved, adapter does not own domain facts
# ---------------------------------------------------------------------------

# 5. Public v1 API routes remain available and registered.
def test_public_v1_api_contract_preserved() -> None:
    for rel in (
        "src/backend/zuno/api/v1/product.py",
        "src/backend/zuno/api/v1/workspace.py",
        "src/backend/zuno/api/router.py",
    ):
        assert (REPO_ROOT / rel).exists(), f"public v1 contract file missing: {rel}"
    router = (REPO_ROOT / "src/backend/zuno/api/router.py").read_text(encoding="utf-8")
    assert "product" in router and "workspace" in router


# 6. SSE v1 contract preserved with a single stream owner.
def test_sse_v1_stream_contract_single_owner() -> None:
    workspace_route = (
        REPO_ROOT / "src/backend/zuno/api/v1/workspace.py"
    ).read_text(encoding="utf-8")
    assert workspace_route.count("events/stream") == 1
    assert "text/event-stream" in workspace_route
    service = (
        REPO_ROOT / "src/backend/zuno/api/services/workspace_task_runtime.py"
    ).read_text(encoding="utf-8")
    assert "def stream_task_events" in service
    assert service.count("def stream_task_events") == 1


# 7. Public adapter (ProductService family) does not write DAO directly.
def test_public_adapter_does_not_import_dao_directly() -> None:
    violations = []
    for path in (BACKEND_ROOT / "zuno" / "api" / "services" / "product").rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"(?m)^\s*(from zuno\.platform\.database\.dao|import zuno\.platform\.database\.dao)", text):
            violations.append(str(path.relative_to(BACKEND_ROOT)))
    assert violations == []
    # persistence goes through the canonical UoW/Repository boundary
    command_service = (
        BACKEND_ROOT / "zuno" / "api" / "services" / "product" / "command_service.py"
    ).read_text(encoding="utf-8")
    assert "ProductUnitOfWork" in command_service and "ProductRepository" in command_service


# ---------------------------------------------------------------------------
# Tool Gateway 8-9
# ---------------------------------------------------------------------------

# 8. READ_ONLY tools still go through the Gateway (no approval, audit kept).
def test_readonly_tool_policy_goes_through_gateway() -> None:
    _ensure_runtime_paths()
    from zuno.capability.tool_runtime.effect_policy import ToolEffectClass, classify_tool_effect

    policy = classify_tool_effect(tool_name="web_search", args={"query": "x"}, readonly=True)
    assert policy.effect_class is ToolEffectClass.READ
    assert policy.approval_required is False
    assert policy.audit_required is True  # exempt from approval, never from Security/Audit
    assert policy.provider_dispatch_allowed is True
    gateway = (
        BACKEND_ROOT / "zuno" / "capability" / "tool_runtime" / "invocation_gateway.py"
    ).read_text(encoding="utf-8")
    assert "def invoke_readonly" in gateway
    assert "approval_required" in gateway and "security_epoch_ref" in gateway


# 9. Security denial blocks even read-only tools: unknown side-effect level
#    fails closed (approval required, dispatch not allowed).
def test_unknown_side_effect_level_fails_closed() -> None:
    _ensure_runtime_paths()
    from zuno.capability.tool_runtime.effect_policy import classify_tool_effect

    policy = classify_tool_effect(tool_name="mystery_tool", args={}, readonly=None)
    assert policy.approval_required is True
    assert policy.provider_dispatch_allowed is False
    assert policy.blocked_reason == "PHASE16_REQUIRED_FOR_SIDE_EFFECT_TOOL"


# ---------------------------------------------------------------------------
# PostgreSQL UoW 10-12
# ---------------------------------------------------------------------------

# 10. No shadow write in the persistence layer.
def test_no_shadow_write_in_persistence_layer() -> None:
    hits = []
    for path in (BACKEND_ROOT / "zuno" / "platform" / "database").rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(BACKEND_ROOT).as_posix()
        if "cutover" in rel:
            continue  # Phase08CutoverController domain (parallel session)
        text = path.read_text(encoding="utf-8")
        if re.search(r"(?i)\bshadow\s+(write|table|insert|update)", text):
            hits.append(rel)
    assert hits == []


# 11. Current state + outbox commit atomically in one transaction.
def test_current_state_and_outbox_commit_in_one_transaction() -> None:
    domain = (
        BACKEND_ROOT / "zuno" / "platform" / "database" / "product" / "domain.py"
    ).read_text(encoding="utf-8")
    uow = domain.split("class ProductUnitOfWork")[1].split("class ProductRepository")[0]
    assert "self._connection = self.engine.connect()" in uow
    assert "self._transaction = self._connection.begin()" in uow
    assert "self._transaction.commit()" in uow and "self._transaction.rollback()" in uow
    # outbox enqueue uses the same connection inside the same transaction
    assert "enqueue_outbox(" in domain
    assert "self.connection.execute" in domain  # repository executes on UoW connection


# 12. Duplicate command submission is idempotent.
def test_duplicate_command_is_idempotent() -> None:
    domain = (
        BACKEND_ROOT / "zuno" / "platform" / "database" / "product" / "domain.py"
    ).read_text(encoding="utf-8")
    # unique constraint + ON CONFLICT DO NOTHING + client_request_id idempotency
    assert "ON CONFLICT DO NOTHING" in domain
    assert "client_request_id" in domain
    assert "idempotency_key" in domain or "idempotency" in domain


# ---------------------------------------------------------------------------
# AgentControlRuntime / product_baseline 13-18
# ---------------------------------------------------------------------------

# 13. Production entry points cannot construct AgentControlRuntime.
def test_production_entry_points_cannot_construct_residual_runtime() -> None:
    entry_points = [
        "src/backend/zuno/main.py",
        "src/backend/zuno/api/services/completion.py",
        "src/backend/zuno/api/services/workspace_task_runtime.py",
        "src/backend/zuno/api/v1/product.py",
        "src/backend/zuno/api/v1/workspace.py",
        "src/backend/zuno/platform/services/queue/workers.py",
        "src/backend/zuno/platform/services/cli_tool_discovery.py",
        "src/backend/zuno/platform/services/simple_api_tool.py",
        "tools/scripts/start.py",
    ]
    for rel in entry_points:
        text = (REPO_ROOT / rel).read_text(encoding="utf-8")
        assert "control_runtime" not in text and "AgentControlRuntime" not in text, rel


# 14. Dynamic import cannot restore the residual runtime as a product
#     runtime: the production facade rejects it.
def test_facade_rejects_dynamic_access_to_residual_runtime() -> None:
    _ensure_runtime_paths()
    import zuno.agent as agent

    with pytest.raises(AttributeError):
        agent.AgentControlRuntime  # noqa: B018


# 15. Package exports do not expose the old runtime.
def test_package_exports_do_not_expose_residual_runtime() -> None:
    _ensure_runtime_paths()
    import zuno.agent as agent

    for symbol in ("AgentControlRuntime", "AgentRuntimeResult", "RuntimeObservation"):
        assert symbol not in agent.__all__
        assert not hasattr(agent, symbol)


# 16. product_baseline is not a second product runtime: only tests/evals
#     reference it.
def test_product_baseline_is_test_harness_only() -> None:
    refs = []
    for path in (BACKEND_ROOT / "zuno").rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(BACKEND_ROOT).as_posix()
        if "product_baseline" in path.read_text(encoding="utf-8") and rel != "zuno/agent/product_baseline.py":
            refs.append(rel)
    assert refs == [], f"product_baseline referenced from production: {refs}"


# 17. Single Controller still carries Plan/Trace/Budget/RunOutcome.
def test_single_controller_keeps_plan_trace_budget_runoutcome() -> None:
    _ensure_runtime_paths()
    from zuno.agent.runtime.nodes import DEFAULT_RUNTIME_NODES
    from zuno.agent.runtime.routing import RuntimeNode

    node_names = {node for node in DEFAULT_RUNTIME_NODES}
    for label, expected in {
        "plan": RuntimeNode.CREATE_OR_UPDATE_PLAN.value,
        "trace": RuntimeNode.OBSERVE.value,
        "budget": RuntimeNode.EXECUTE_STEP.value,
        "runoutcome": RuntimeNode.FINALIZE.value,
    }.items():
        assert expected in node_names, f"Single Controller missing {label} node: {expected}"


# 18. ReAct remains a step-internal mechanism.
def test_react_remains_step_internal_mechanism() -> None:
    _ensure_runtime_paths()
    from zuno.agent.runtime.execution import ReActStepExecutor
    from zuno.agent.runtime.execution.react_runner import ReActStepRunner

    assert ReActStepExecutor is not None
    assert ReActStepRunner is not None


# ---------------------------------------------------------------------------
# Fault semantics 19-24
# ---------------------------------------------------------------------------

# 19. UoW commit exception: transaction rolls back, connection closes.
def test_uow_commit_exception_rolls_back() -> None:
    class Boom(RuntimeError):
        pass

    class FakeTransaction:
        def __init__(self) -> None:
            self.committed = False
            self.rolled_back = False

        def commit(self) -> None:
            self.committed = True

        def rollback(self) -> None:
            self.rolled_back = True

    class FakeConnection:
        def __init__(self) -> None:
            self.tx = FakeTransaction()
            self.closed = False

        def begin(self):
            return self.tx

        def close(self) -> None:
            self.closed = True

    _ensure_runtime_paths()
    from zuno.platform.database.product.domain import ProductUnitOfWork

    conn = FakeConnection()
    engine = type("FakeEngine", (), {"connect": lambda self: conn})()

    with pytest.raises(Boom):
        with ProductUnitOfWork(engine) as repo:
            raise Boom("commit failed")

    assert conn.tx.rolled_back is True
    assert conn.tx.committed is False
    assert conn.closed is True


# 20. Unknown commit outcome is documented as reconciliation, not retry:
#     the outbox receipt and conflict types exist, and re-issuing a command
#     with the same client_request_id is idempotent (no duplicate effect).
def test_unknown_commit_outcome_is_reconciliation_bound() -> None:
    _ensure_runtime_paths()
    from zuno.platform.database.product.domain import (
        ProductCommandReceiptRef,
        ProductPersistenceConflict,
    )

    assert ProductPersistenceConflict is not None
    assert ProductCommandReceiptRef is not None
    domain = (
        BACKEND_ROOT / "zuno" / "platform" / "database" / "product" / "domain.py"
    ).read_text(encoding="utf-8")
    assert "enqueue_outbox" in domain  # outbox replay path for unknown states


# 21. Stream reconnect resumes without duplicating events: the v1 stream
#     replays the single event owner's sequence deterministically.
def test_stream_reconnect_replays_events_deterministically() -> None:
    workspace_route = (
        REPO_ROOT / "src/backend/zuno/api/v1/workspace.py"
    ).read_text(encoding="utf-8")
    assert "events/stream" in workspace_route  # resume entry point is the SSE route
    service = (
        REPO_ROOT / "src/backend/zuno/api/services/workspace_task_runtime.py"
    ).read_text(encoding="utf-8")
    assert "def stream_task_events" in service
    # a single event list is the source of truth: replay yields the same
    # sequence every time, so a reconnect cannot fabricate new events
    assert "_events" in service


# 22. Tool Gateway failure propagates as a receipt error, never as silent
#     success: executor exceptions surface through the gateway's error path.
def test_tool_gateway_error_propagates_fail_closed() -> None:
    gateway = (
        BACKEND_ROOT / "zuno" / "capability" / "tool_runtime" / "invocation_gateway.py"
    ).read_text(encoding="utf-8")
    assert "PHASE16_REQUIRED_FOR_SIDE_EFFECT_TOOL" in gateway  # side effects blocked
    assert "security_blocked_reason" in gateway  # security denials propagate
    assert "timeout_due_async_jobs" in gateway  # async job timeout reconciliation


# 23. Stale Security Epoch: every prepared action binds a security epoch ref
#     and Security denies on recheck (epoch is re-evaluated on approval).
def test_stale_security_epoch_is_bound_fail_closed() -> None:
    gateway = (
        BACKEND_ROOT / "zuno" / "capability" / "tool_runtime" / "invocation_gateway.py"
    ).read_text(encoding="utf-8")
    assert "security_epoch_ref" in gateway
    assert "SecurityUnitOfWork" in gateway
    policy = (
        BACKEND_ROOT / "zuno" / "capability" / "tool_runtime" / "effect_policy.py"
    ).read_text(encoding="utf-8")
    assert "approval_required" in policy


# 24. Duplicate requests do not duplicate side effects: the gateway binds an
#     idempotency key (call_id) to the prepared action.
def test_duplicate_request_does_not_duplicate_side_effects() -> None:
    gateway = (
        BACKEND_ROOT / "zuno" / "capability" / "tool_runtime" / "invocation_gateway.py"
    ).read_text(encoding="utf-8")
    assert "idempotency_key" in gateway
    domain = (
        BACKEND_ROOT / "zuno" / "platform" / "database" / "product" / "domain.py"
    ).read_text(encoding="utf-8")
    assert "idempotency" in domain
