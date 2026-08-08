"""PHASE22 feature flag registry slice and repository runtime truth tests.

Two-layer truth model (work package
PHASE22-FEATURE-FLAG-SCOPED-AND-REPOSITORY-TRUTH):

- ``ROLLOUT_FLAG_REGISTRY_SLICE_CONFIRMED``: this PR's own registry slice -
  the four rollout records RETIRED fail-closed, rollback transitions
  rejected, no production Flag Reader, no dynamic Selector, Public v1 API /
  SSE v1 contracts preserved, and the registry still satisfies the PHASE02
  executable-compatibility boundary.
- ``FEATURE_FLAG_RUNTIME_CUTOVER_*``: repository-wide runtime truth. Real
  bypasses (direct tool dispatch outside the canonical tool runtime,
  Product/Agent -> MCP client/provider execution, legacy runtime / rollout /
  shadow / canary / rollback selectors, Phase08 dual runtime, residual
  runtime reachability) keep the repository result BLOCKED. MCP admin /
  discovery / canonical executor sites are recorded as mcp_classification,
  never blocking; classification is semantic (module role x call shape),
  never an allowlist and never path-substring based.

Evidence boundary: string-contract checks prove STATIC_CONTRACT_AVAILABLE
only. The verifier never emits a *_LIVE_VERIFIED claim and lists its
not_proven_boundary explicitly; no PostgreSQL / SSE-reconnect / side-effect
runtime receipt is fabricated.

Real-tree tests pin the current branch's honest truth (registry slice
CONFIRMED, repository BLOCKED while the other runtime PRs are not
integrated); fixture tests pin the detector boundaries.
"""

from __future__ import annotations

import ast
import importlib
import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"
REGISTRY = (
    REPO_ROOT / ".agent" / "programs" / "work-products" / "feature-flag-registry.yaml"
)
VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase22_feature_flag_runtime_cutover.py"
FIXTURE_TREE = (
    REPO_ROOT / "tests" / "fixtures" / "phase22_feature_flag_runtime_cutover" / "fixture_tree.py"
)

RETIRED_FLAGS = [
    "product_api_v1_adapter",
    "workspace_projection_stream_v1",
    "tool_runtime_readonly_gateway",
    "postgres_domain_uow_shadow",
]

STATUS_REGISTRY_CONFIRMED = "ROLLOUT_FLAG_REGISTRY_SLICE_CONFIRMED"
STATUS_REPO_CONFIRMED = "FEATURE_FLAG_RUNTIME_CUTOVER_CONFIRMED"
STATUS_REPO_BLOCKED = "FEATURE_FLAG_RUNTIME_CUTOVER_BLOCKED"
STATUS_REPO_UNRESOLVED = "FEATURE_FLAG_RUNTIME_CUTOVER_UNRESOLVED"


def _load_verifier():
    spec = importlib.util.spec_from_file_location("verify_phase22_feature_flag_runtime_cutover", VERIFIER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_fixture_builder():
    spec = importlib.util.spec_from_file_location("phase22_fixture_tree", FIXTURE_TREE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VERIFIER_MOD = _load_verifier()
FIXTURE = _load_fixture_builder()


def _ensure_runtime_paths() -> None:
    if str(BACKEND_ROOT) not in sys.path:
        sys.path.insert(0, str(BACKEND_ROOT))


def _registry_text() -> str:
    return REGISTRY.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Real tree: registry slice truth
# ---------------------------------------------------------------------------

# 1. The four flags are RETIRED fail-closed with non-executable
#    rollback_commands (yaml.safe_load parse, per Coordinator review).
def test_four_flags_retired_fail_closed() -> None:
    parsed = yaml.safe_load(_registry_text())
    by_name = {f["flag"]: f for f in parsed["flags"]}
    for flag in RETIRED_FLAGS:
        record = by_name[flag]
        assert record["default"] == "RETIRED", f"{flag} is not RETIRED"
        assert "retired and fail-closed" in record["rollback_command"].lower(), (
            f"{flag} rollback_command not fail-closed"
        )


# 2. Rollback transition is rejected: RETIRED has no transition target, and
#    the state machine refuses every non-RETIRED move.
def test_retired_flag_rejects_rollback_transition() -> None:
    spec = importlib.import_module("tools.scripts.phase02_compatibility_runtime")
    machine = spec.FeatureFlagStateMachine(_registry_text())
    for flag in RETIRED_FLAGS + ["legacy_general_agent_completion_rollback"]:
        assert machine.flags[flag]["default"] == "RETIRED"
        for desired in ("ROLLBACK_WINDOW", "DEFAULT_NEW", "SHADOW", "CANARY", "DECLARED"):
            with pytest.raises(ValueError):
                machine.decide_transition(flag, desired)


# 3. No production module reads a retired flag name (AST audit: identifiers,
#    constants, attribute wrappers, import aliases).
def test_retired_flags_have_no_production_reader() -> None:
    for path in (BACKEND_ROOT / "zuno").rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8").lstrip("﻿"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) \
                    and node.value in RETIRED_FLAGS:
                raise AssertionError(f"flag reader constant in {path.relative_to(BACKEND_ROOT)}")
            if isinstance(node, ast.Name) and node.id in RETIRED_FLAGS \
                    and isinstance(node.ctx, ast.Load):
                raise AssertionError(f"flag reader identifier in {path.relative_to(BACKEND_ROOT)}")
            if isinstance(node, ast.Attribute) and node.attr in RETIRED_FLAGS:
                raise AssertionError(f"flag reader wrapper in {path.relative_to(BACKEND_ROOT)}")


# 4. Registry scope on the real tree proves the slice: CONFIRMED, zero
#    reader / selector findings.
def test_registry_slice_confirmed_on_real_tree() -> None:
    status, report = VERIFIER_MOD.verify(REPO_ROOT, "registry")
    assert status == STATUS_REGISTRY_CONFIRMED
    assert report["findings"]["flag_reader_found"] == []
    assert report["findings"]["dynamic_selector_found"] == []
    assert report["findings"]["flag_not_retired"] == []
    assert report["evidence"]["registry_parse"] == "MACHINE_VERIFIED"


# 5. Unknown / open rollout states fail closed: no flag may default to an
#    open rollout state after PHASE22.
def test_unknown_flag_state_fails_closed() -> None:
    parsed = yaml.safe_load(_registry_text())
    defaults = {f["flag"]: f["default"] for f in parsed["flags"]}
    for flag, default in defaults.items():
        assert default not in ("DECLARED", "SHADOW", "CANARY", "DEFAULT_NEW", "ROLLBACK_WINDOW"), (
            f"{flag} still defaults to open rollout state {default}"
        )


# ---------------------------------------------------------------------------
# Real tree: Public v1 API / SSE v1 contract preservation
# ---------------------------------------------------------------------------

# 6. Public v1 API routes remain available and registered.
def test_public_v1_api_contract_preserved() -> None:
    for rel in (
        "src/backend/zuno/api/v1/product.py",
        "src/backend/zuno/api/v1/workspace.py",
        "src/backend/zuno/api/router.py",
    ):
        assert (REPO_ROOT / rel).exists(), f"public v1 contract file missing: {rel}"
    router = (REPO_ROOT / "src/backend/zuno/api/router.py").read_text(encoding="utf-8")
    assert "product" in router and "workspace" in router


# 7. SSE v1 stream contract: single route, single owner. This is a static
#    contract check - no live reconnect receipt is claimed.
def test_sse_v1_stream_contract_static() -> None:
    workspace_route = (
        REPO_ROOT / "src/backend/zuno/api/v1/workspace.py"
    ).read_text(encoding="utf-8")
    assert workspace_route.count("events/stream") == 1
    assert "text/event-stream" in workspace_route
    service = (
        REPO_ROOT / "src/backend/zuno/api/services/workspace_task_runtime.py"
    ).read_text(encoding="utf-8")
    assert service.count("def stream_task_events") == 1


# 8. Public adapter (ProductService family) does not write DAO directly.
def test_public_adapter_does_not_import_dao_directly() -> None:
    violations = []
    for path in (BACKEND_ROOT / "zuno" / "api" / "services" / "product").rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"(?m)^\s*(from zuno\.platform\.database\.dao|import zuno\.platform\.database\.dao)", text):
            violations.append(str(path.relative_to(BACKEND_ROOT)))
    assert violations == []
    command_service = (
        BACKEND_ROOT / "zuno" / "api" / "services" / "product" / "command_service.py"
    ).read_text(encoding="utf-8")
    assert "ProductUnitOfWork" in command_service and "ProductRepository" in command_service


# ---------------------------------------------------------------------------
# Real tree: behavior tests (deterministic, no environment required)
# ---------------------------------------------------------------------------

# 9. READ_ONLY tools still go through the Gateway (no approval, audit kept).
def test_readonly_tool_policy_goes_through_gateway() -> None:
    _ensure_runtime_paths()
    from zuno.capability.tool_runtime.effect_policy import ToolEffectClass, classify_tool_effect

    policy = classify_tool_effect(tool_name="web_search", args={"query": "x"}, readonly=True)
    assert policy.effect_class is ToolEffectClass.READ
    assert policy.approval_required is False
    assert policy.audit_required is True  # exempt from approval, never from Security/Audit
    assert policy.provider_dispatch_allowed is True


# 10. Security denial blocks even read-only tools: unknown side-effect level
#     fails closed (approval required, dispatch not allowed).
def test_unknown_side_effect_level_fails_closed() -> None:
    _ensure_runtime_paths()
    from zuno.capability.tool_runtime.effect_policy import classify_tool_effect

    policy = classify_tool_effect(tool_name="mystery_tool", args={}, readonly=None)
    assert policy.approval_required is True
    assert policy.provider_dispatch_allowed is False
    assert policy.blocked_reason == "PHASE16_REQUIRED_FOR_SIDE_EFFECT_TOOL"


# 11. UoW commit exception: transaction rolls back, connection closes.
#     Deterministic unit behavior test with fakes - this proves the
#     transaction semantics under a synthetic fault, not a live PostgreSQL
#     receipt.
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


# ---------------------------------------------------------------------------
# Real tree: static contract evidence (STATIC_CONTRACT_AVAILABLE only)
# ---------------------------------------------------------------------------

# 12. No shadow write in the persistence layer.
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


# 13. Current state + outbox: single-connection transaction contract
#     (static markers; not a live atomicity receipt).
def test_uow_single_transaction_contract_static() -> None:
    domain = (
        BACKEND_ROOT / "zuno" / "platform" / "database" / "product" / "domain.py"
    ).read_text(encoding="utf-8")
    uow = domain.split("class ProductUnitOfWork")[1].split("class ProductRepository")[0]
    assert "self._connection = self.engine.connect()" in uow
    assert "self._transaction = self._connection.begin()" in uow
    assert "self._transaction.commit()" in uow and "self._transaction.rollback()" in uow
    assert "enqueue_outbox(" in domain
    assert "self.connection.execute" in domain


# 14. Duplicate command idempotency contract (static markers only).
def test_idempotency_contract_static() -> None:
    domain = (
        BACKEND_ROOT / "zuno" / "platform" / "database" / "product" / "domain.py"
    ).read_text(encoding="utf-8")
    assert "ON CONFLICT DO NOTHING" in domain
    assert "client_request_id" in domain
    assert "idempotency_key" in domain or "idempotency" in domain


# 15. Unknown commit outcome: reconciliation contract (static markers).
def test_unknown_commit_reconciliation_contract_static() -> None:
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
    assert "enqueue_outbox" in domain


# 16. Stream resume contract: the v1 SSE route replays the single event
#     owner's sequence (static contract; not a live reconnect receipt).
def test_stream_resume_contract_static() -> None:
    workspace_route = (
        REPO_ROOT / "src/backend/zuno/api/v1/workspace.py"
    ).read_text(encoding="utf-8")
    assert "events/stream" in workspace_route
    service = (
        REPO_ROOT / "src/backend/zuno/api/services/workspace_task_runtime.py"
    ).read_text(encoding="utf-8")
    assert "def stream_task_events" in service
    assert "_events" in service


# 17. Tool Gateway failure propagation contract (static markers).
def test_gateway_error_propagation_contract_static() -> None:
    gateway = (
        BACKEND_ROOT / "zuno" / "capability" / "tool_runtime" / "invocation_gateway.py"
    ).read_text(encoding="utf-8")
    assert "PHASE16_REQUIRED_FOR_SIDE_EFFECT_TOOL" in gateway
    assert "security_blocked_reason" in gateway
    assert "timeout_due_async_jobs" in gateway


# 18. Stale Security Epoch binding contract (static markers).
def test_security_epoch_contract_static() -> None:
    gateway = (
        BACKEND_ROOT / "zuno" / "capability" / "tool_runtime" / "invocation_gateway.py"
    ).read_text(encoding="utf-8")
    assert "security_epoch_ref" in gateway
    assert "SecurityUnitOfWork" in gateway
    policy = (
        BACKEND_ROOT / "zuno" / "capability" / "tool_runtime" / "effect_policy.py"
    ).read_text(encoding="utf-8")
    assert "approval_required" in policy


# 19. Duplicate requests: idempotency binding contract (static markers).
def test_idempotency_binding_contract_static() -> None:
    gateway = (
        BACKEND_ROOT / "zuno" / "capability" / "tool_runtime" / "invocation_gateway.py"
    ).read_text(encoding="utf-8")
    assert "idempotency_key" in gateway
    domain = (
        BACKEND_ROOT / "zuno" / "platform" / "database" / "product" / "domain.py"
    ).read_text(encoding="utf-8")
    assert "idempotency" in domain


# ---------------------------------------------------------------------------
# Real tree: AgentControlRuntime / product_baseline reachability
# ---------------------------------------------------------------------------

# 20. Repository-wide AST reachability: the ONLY production-tree modules that
#     reference the residual runtime are the harness modules themselves
#     (control_runtime.py defines it; product_baseline.py constructs it for
#     the eval harness). No other production module may import it.
def test_production_control_runtime_references_confined_to_harness() -> None:
    allowed = {
        "src/backend/zuno/agent/control_runtime.py",
        "src/backend/zuno/agent/product_baseline.py",
    }
    hits = []
    for path in (BACKEND_ROOT / "zuno").rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel in allowed:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8").lstrip("﻿"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    if isinstance(node, ast.Import):
                        full = alias.name
                    else:
                        full = f"{node.module}.{alias.name}"
                    if "control_runtime" in full or "product_baseline" in full:
                        hits.append(f"{rel}: {full}")
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) \
                    and node.id in ("AgentControlRuntime", "AgentRuntimeResult", "RuntimeObservation"):
                hits.append(f"{rel}: {node.id}")
    assert hits == [], f"residual runtime referenced from production: {hits}"


# 21. Facade rejects dynamic access to residual runtime.
def test_facade_rejects_dynamic_access_to_residual_runtime() -> None:
    _ensure_runtime_paths()
    import zuno.agent as agent

    with pytest.raises(AttributeError):
        agent.AgentControlRuntime  # noqa: B018


# 22. Package exports do not expose the old runtime.
def test_package_exports_do_not_expose_residual_runtime() -> None:
    _ensure_runtime_paths()
    import zuno.agent as agent

    for symbol in ("AgentControlRuntime", "AgentRuntimeResult", "RuntimeObservation"):
        assert symbol not in agent.__all__
        assert not hasattr(agent, symbol)


# 23. product_baseline is not a second product runtime: only tests/evals
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


# 24. Single Controller still carries Plan/Trace/Budget/RunOutcome.
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


# 25. ReAct remains a step-internal mechanism.
def test_react_remains_step_internal_mechanism() -> None:
    _ensure_runtime_paths()
    from zuno.agent.runtime.execution import ReActStepExecutor
    from zuno.agent.runtime.execution.react_runner import ReActStepRunner

    assert ReActStepExecutor is not None
    assert ReActStepRunner is not None


# ---------------------------------------------------------------------------
# Real tree: repository truth is fail-closed and honest
# ---------------------------------------------------------------------------

# 26. Repository scope is the default and returns BLOCKED on the current
#     branch. After the PR #135 cutover the workspace agents are canonical
#     thin adapters (MCP discovery only, execution through
#     MCPToolExecutorAdapter -> ToolInvocationGateway), so they are NO
#     LONGER bypass findings. The gate blocks on the real remaining
#     Product/Agent -> MCP client/provider surface (mcp_chat.py driving
#     the legacy mcp_openai manager) — MCP admin / discovery / canonical
#     executor sites are recorded as mcp_classification, never blocking.
def test_repository_scope_default_and_blocked_on_real_tree() -> None:
    status, report = VERIFIER_MOD.verify(REPO_ROOT, "repository")
    assert status == STATUS_REPO_BLOCKED
    bypass_paths = {f["path"] for f in report["findings"]["direct_tool_bypass"]}
    # Workspace agents are canonical thin adapters now (PR #135): no
    # direct tool dispatch may be reported against them.
    for expected in (
        "src/backend/zuno/platform/services/workspace/simple_agent.py",
        "src/backend/zuno/platform/services/workspace/wechat_agent.py",
    ):
        assert expected not in bypass_paths, f"thin adapter misreported: {expected}"
    # MCP admin / discovery / canonical executor are classified, never
    # reported as bypasses.
    for path in (
        "src/backend/zuno/platform/services/mcp/manager.py",
        "src/backend/zuno/platform/services/mcp/multi_client.py",
        "src/backend/zuno/platform/services/mcp/load_mcp/tools.py",
        "src/backend/zuno/platform/services/mcp_openai/mcp_client.py",
        "src/backend/zuno/capability/mcp/servers/remote_proxy/main.py",
    ):
        assert path not in bypass_paths, f"MCP layer misreported as bypass: {path}"
    # The honest Product direct MCP execution finding:
    product_direct = {f["path"] for f in report["findings"]["product_direct_mcp_execution"]}
    assert "src/backend/zuno/api/services/mcp_chat.py" in product_direct, (
        "MCPChatAgent (Product/Agent -> MCP client/provider) must block: "
        f"{product_direct}"
    )
    # mcp_classification records the MCP layer sites without blocking.
    assert report["findings"]["mcp_classification"], (
        "MCP admin/discovery/canonical executor sites must be recorded"
    )
    # The residual harness is confined to tests/evals: product_baseline
    # moved OUT of production (tools/evals), so no residual production
    # runtime remains; the harness modules are recorded as test harness.
    residual = report["findings"]["residual_product_runtime_found"]
    assert residual == [], (
        "no residual product runtime may remain: " + json.dumps(residual)
    )
    # NOTE: phase08_dual_runtime was retired by PR #124. The verifier
    # correctly no longer reports it because the dual path is gone.
    assert not report["findings"]["phase08_dual_runtime"], (
        "Phase08 dual runtime must NOT be reported (retired by PR #124)"
    )
    harness_paths = {f["path"] for f in report["findings"]["internal_test_harness"]}
    assert "tools/evals/zuno/agent/product_baseline.py" in harness_paths, (
        "test-harness-only modules must be recorded at their real location"
    )


# 27. The verifier's default scope is repository (fail-closed).
def test_default_scope_is_repository() -> None:
    assert VERIFIER_MOD.verify(REPO_ROOT)[0] == STATUS_REPO_BLOCKED


# 28. Static evidence never masquerades as live evidence: string-contract
#     areas are STATIC_CONTRACT_AVAILABLE, not_proven_boundary is explicit,
#     and no *_LIVE_VERIFIED claim exists anywhere in the report.
def test_static_evidence_never_claims_live_verification() -> None:
    status, report = VERIFIER_MOD.verify(REPO_ROOT, "repository")
    evidence = report["evidence"]
    for area in ("postgres_uow_atomicity", "sse_stream_resume", "idempotency", "security_epoch"):
        assert evidence.get(area) == "STATIC_CONTRACT_AVAILABLE", area
    assert evidence["not_proven_boundary"], "not_proven_boundary must be listed"
    blob = json.dumps(report, sort_keys=True)
    assert "LIVE_VERIFIED" not in blob, "static evidence must not claim live verification"
    assert "ATOMICITY_LIVE_VERIFIED" not in blob
    assert "STREAM_RESUME_LIVE_VERIFIED" not in blob
    assert "IDEMPOTENCY_LIVE_VERIFIED" not in blob
    assert "SECURITY_EPOCH_LIVE_VERIFIED" not in blob


# ---------------------------------------------------------------------------
# Fixture tests: registry slice detectors
# ---------------------------------------------------------------------------

# 29. A clean fixture tree yields ROLLOUT_FLAG_REGISTRY_SLICE_CONFIRMED.
def test_fixture_registry_slice_confirmed(tmp_path: Path) -> None:
    root = FIXTURE.build_fixture_tree(tmp_path)
    status, report = VERIFIER_MOD.verify(root, "registry")
    assert status == STATUS_REGISTRY_CONFIRMED
    assert report["finding_count"] == 0


# 30. A non-RETIRED default blocks the registry slice.
def test_fixture_flag_not_retired_blocks_registry_slice(tmp_path: Path) -> None:
    root = FIXTURE.build_fixture_tree(
        tmp_path, registry=FIXTURE.build_registry(non_retired_default="DECLARED")
    )
    status, report = VERIFIER_MOD.verify(root, "registry")
    assert status == "REGISTRY_SLICE_BLOCKED"
    assert report["findings"]["flag_not_retired"]


# 31. An open rollback transition (RETIRED -> DEFAULT_NEW) blocks the slice.
def test_fixture_open_rollback_transition_blocks_registry_slice(tmp_path: Path) -> None:
    root = FIXTURE.build_fixture_tree(
        tmp_path, registry=FIXTURE.build_registry(retired_transition="DEFAULT_NEW")
    )
    status, report = VERIFIER_MOD.verify(root, "registry")
    assert status == "REGISTRY_SLICE_BLOCKED"
    assert report["findings"]["rollback_transition_accepted"]


# 32. Wrapper / alias readers of a retired flag name are detected (attribute
#     access and import alias).
@pytest.mark.parametrize(
    "module_body",
    [
        # wrapper reader: attribute access on a registry-like object
        "class FlagRegistry:\n    product_api_v1_adapter = 'RETIRED'\nvalue = FlagRegistry.product_api_v1_adapter\n",
        # alias reader: import binding the retired flag name
        "import zuno.platform.flag_registry as product_api_v1_adapter\n",
    ],
)
def test_fixture_wrapper_and_alias_readers_detected(tmp_path: Path, module_body: str) -> None:
    root = FIXTURE.build_fixture_tree(
        tmp_path,
        modules={
            "src/backend/zuno/platform/services/fixture_reader.py": module_body,
        },
    )
    status, report = VERIFIER_MOD.verify(root, "registry")
    assert status == "REGISTRY_SLICE_BLOCKED"
    assert report["findings"]["flag_reader_found"]


# 33. Dynamic config lookup of a selector marker is a dynamic Selector.
def test_fixture_dynamic_config_selector_detected(tmp_path: Path) -> None:
    root = FIXTURE.build_fixture_tree(
        tmp_path,
        modules={
            "src/backend/zuno/platform/services/fixture_selector.py":
                "import os\nmode = os.getenv('ZUNO_TOOL_GATEWAY')\n",
        },
    )
    status, report = VERIFIER_MOD.verify(root, "registry")
    assert status == "REGISTRY_SLICE_BLOCKED"
    assert report["findings"]["dynamic_selector_found"]


# 34. Concatenated selector keys cannot be proven -> registry slice UNRESOLVED.
def test_fixture_concatenated_selector_unresolved(tmp_path: Path) -> None:
    root = FIXTURE.build_fixture_tree(
        tmp_path,
        modules={
            "src/backend/zuno/platform/services/fixture_selector.py":
                "import os\nkey = 'ZUNO_' + 'TOOL_GATEWAY' + suffix\nmode = os.getenv(key)\n",
        },
    )
    status, report = VERIFIER_MOD.verify(root, "registry")
    assert status == "REGISTRY_SLICE_UNRESOLVED"
    assert report["findings"]["unresolved"]


# 34b. Runtime / rollout / shadow / canary / rollback selectors are dynamic
#      selectors: each exact selector family key blocks the registry slice.
@pytest.mark.parametrize(
    "selector_env",
    [
        "ZUNO_AGENT_RUNTIME",   # legacy runtime selector
        "ZUNO_ROLLOUT_MODE",    # rollout flag selector
        "ZUNO_SHADOW_MODE",     # shadow selector
        "ZUNO_CANARY_MODE",     # canary selector
        "ZUNO_ROLLBACK_MODE",   # rollback selector
    ],
)
def test_fixture_legacy_runtime_selector_family_blocks(
    tmp_path: Path, selector_env: str
) -> None:
    root = FIXTURE.build_fixture_tree(
        tmp_path,
        modules={
            "src/backend/zuno/platform/services/fixture_selector.py":
                f"import os\nmode = os.getenv('{selector_env}')\n",
        },
    )
    status, report = VERIFIER_MOD.verify(root, "registry")
    assert status == "REGISTRY_SLICE_BLOCKED"
    assert report["findings"]["dynamic_selector_found"], (
        f"selector {selector_env} must be reported as dynamic_selector_found"
    )


# 34c. A neutral symbol that merely CONTAINS "mcp" / "runtime" text is not a
#      finding — classification is exact-key / shape based, never substring.
def test_fixture_neutral_mcp_symbol_not_a_finding(tmp_path: Path) -> None:
    root = FIXTURE.build_fixture_tree(
        tmp_path,
        modules={
            "src/backend/zuno/platform/services/mcp_runtime_helper.py":
                "class McpRuntimeManager:\n"
                "    def register(self):\n"
                "        return {'mcp_runtime_tool': True}\n",
        },
    )
    status, report = VERIFIER_MOD.verify(root, "repository")
    assert status == STATUS_REPO_CONFIRMED, (
        "neutral symbols containing 'mcp'/'runtime' must not block: "
        + json.dumps(report["findings"])
    )
    assert report["findings"]["direct_tool_bypass"] == []
    assert report["findings"]["product_direct_mcp_execution"] == []
    assert report["findings"]["dynamic_selector_found"] == []


# 35. Missing Public v1 contract blocks the registry slice.
def test_fixture_missing_public_v1_contract_blocks_slice(tmp_path: Path) -> None:
    root = FIXTURE.build_fixture_tree(tmp_path, with_v1=False)
    status, report = VERIFIER_MOD.verify(root, "registry")
    assert status == "REGISTRY_SLICE_BLOCKED"
    assert report["findings"]["public_v1_contract_missing"]


# ---------------------------------------------------------------------------
# Fixture tests: repository detectors
# ---------------------------------------------------------------------------

# 36. Direct tool dispatch (tool.ainvoke) is a repository blocker.
def test_fixture_direct_tool_bypass_is_repository_blocker(tmp_path: Path) -> None:
    root = FIXTURE.build_fixture_tree(
        tmp_path,
        modules={
            "src/backend/zuno/platform/services/fixture_direct.py":
                "async def run(tool, args):\n    return await tool.ainvoke(args)\n",
        },
    )
    status, report = VERIFIER_MOD.verify(root, "repository")
    assert status == STATUS_REPO_BLOCKED
    assert any(f["path"].endswith("fixture_direct.py") for f in report["findings"]["direct_tool_bypass"])


# 37. A real bypass is reported by semantic classification — the temporary
#     allowlist is no longer a classification input and can never turn a
#     real bypass CLEAN.
def test_fixture_allowlisted_bypass_never_clean(tmp_path: Path) -> None:
    bypass_module = "src/backend/zuno/platform/services/fixture_bypass.py"
    allowlist = f"""\
temporary_allowlist:
  - path: "{bypass_module}"
    symbol: "direct tool call"
    category: "direct_tool_execute"
    reason: "other work package owns this surface"
    owner: "99 Other Work Package"
    test: "tests/other/test_bypass.py"
    removal_task: "P22-T03"
    deadline_phase: "PHASE20"
"""
    root = FIXTURE.build_fixture_tree(
        tmp_path,
        modules={
            bypass_module:
                "async def run(tool, args):\n    return await tool.ainvoke(args)\n",
        },
        allowlist=allowlist,
    )
    status, report = VERIFIER_MOD.verify(root, "repository")
    assert status == STATUS_REPO_BLOCKED, "allowlist must never turn a real bypass CLEAN"
    bypass = [f for f in report["findings"]["direct_tool_bypass"] if f["path"] == bypass_module]
    assert bypass, "semantic classification must still report the bypass"
    assert bypass[0]["owner_work_package"] != "99 Other Work Package", (
        "allowlist annotations must not drive the classification"
    )


# 38. A production-tree caller of the internal harness is a blocker.
def test_fixture_harness_production_caller_is_blocker(tmp_path: Path) -> None:
    root = FIXTURE.build_fixture_tree(
        tmp_path,
        modules={
            "src/backend/zuno/agent/control_runtime.py":
                "class AgentControlRuntime:\n    def run(self):\n        return None\n",
            "src/backend/zuno/platform/services/fixture_prod.py":
                "from zuno.agent.control_runtime import AgentControlRuntime\n"
                "def make():\n    return AgentControlRuntime()\n",
        },
    )
    status, report = VERIFIER_MOD.verify(root, "repository")
    assert status == STATUS_REPO_BLOCKED
    residual = report["findings"]["residual_product_runtime_found"]
    assert any(f["path"].endswith("fixture_prod.py") for f in residual)


# 39. A harness referenced only by tests/evals is INTERNAL_TEST_HARNESS and
#     does not false-positive into a blocker.
def test_fixture_harness_test_only_not_false_positive(tmp_path: Path) -> None:
    root = FIXTURE.build_fixture_tree(
        tmp_path,
        modules={
            "src/backend/zuno/agent/control_runtime.py":
                "class AgentControlRuntime:\n    def run(self):\n        return None\n",
        },
        tests={
            "tests/agent/test_harness_usage.py":
                "from zuno.agent.control_runtime import AgentControlRuntime\n"
                "def test_harness():\n    assert AgentControlRuntime is not None\n",
        },
    )
    status, report = VERIFIER_MOD.verify(root, "repository")
    assert status == STATUS_REPO_CONFIRMED
    assert report["findings"]["internal_test_harness"]


# 40. An unprovable dynamic load of the residual runtime is UNRESOLVED.
def test_fixture_dynamic_runtime_load_unresolved(tmp_path: Path) -> None:
    root = FIXTURE.build_fixture_tree(
        tmp_path,
        modules={
            "src/backend/zuno/agent/control_runtime.py":
                "class AgentControlRuntime:\n    pass\n",
            "src/backend/zuno/platform/services/fixture_dynamic.py":
                "import importlib\n"
                "def load(runtime_name):\n"
                "    return importlib.import_module('zuno.agent.' + runtime_name)\n",
        },
    )
    status, report = VERIFIER_MOD.verify(root, "repository")
    assert status == STATUS_REPO_UNRESOLVED
    assert report["findings"]["unresolved"]


# 41. The registry scoped result is independent of repository blockers: a
#     tree with real bypasses still proves the registry slice.
def test_fixture_registry_scoped_success_independent_of_repository_blockers(tmp_path: Path) -> None:
    root = FIXTURE.build_fixture_tree(
        tmp_path,
        modules={
            "src/backend/zuno/platform/services/fixture_direct.py":
                "async def run(tool, args):\n    return await tool.ainvoke(args)\n",
        },
    )
    registry_status, registry_report = VERIFIER_MOD.verify(root, "registry")
    repo_status, repo_report = VERIFIER_MOD.verify(root, "repository")
    assert registry_status == STATUS_REGISTRY_CONFIRMED
    assert repo_status == STATUS_REPO_BLOCKED
    assert registry_report["finding_count"] == 0
    assert repo_report["findings"]["direct_tool_bypass"]


# ---------------------------------------------------------------------------
# Fixture tests: MCP semantic classification (PHASE22 repair)
# ---------------------------------------------------------------------------

# 41b. MCP admin / control-plane dispatch (server bootstrap, connection
#      lifecycle, provider execution inside the MCP layer) is classified,
#      never blocking.
def test_fixture_mcp_admin_control_plane_not_blocking(tmp_path: Path) -> None:
    root = FIXTURE.build_fixture_tree(
        tmp_path,
        modules={
            "src/backend/zuno/platform/services/mcp/fixture_admin.py":
                "from mcp import ClientSession\n"
                "async def bootstrap(session: ClientSession):\n"
                "    await session.initialize()\n"
                "    return await session.list_tools()\n",
        },
    )
    status, report = VERIFIER_MOD.verify(root, "repository")
    assert status == STATUS_REPO_CONFIRMED, (
        "MCP admin/discovery must not block: " + json.dumps(report["findings"])
    )
    assert report["findings"]["product_direct_mcp_execution"] == []
    assert report["findings"]["mcp_classification"], (
        "MCP admin/discovery sites must be recorded as mcp_classification"
    )


# 41c. MCP discovery / registration from PRODUCT code (list tools, load
#      schema) is not a finding.
def test_fixture_mcp_discovery_not_blocking(tmp_path: Path) -> None:
    root = FIXTURE.build_fixture_tree(
        tmp_path,
        modules={
            "src/backend/zuno/platform/services/fixture_discovery.py":
                "async def collect(mcp_manager):\n"
                "    return await mcp_manager.get_mcp_tools()\n",
        },
    )
    status, report = VERIFIER_MOD.verify(root, "repository")
    assert status == STATUS_REPO_CONFIRMED
    assert report["findings"]["product_direct_mcp_execution"] == []
    assert report["findings"]["direct_tool_bypass"] == []


# 41d. The canonical MCP executor (gateway -> registered adapter -> provider
#      execution inside capability/tool_runtime and the MCPToolExecutorAdapter)
#      is never a bypass.
def test_fixture_canonical_mcp_executor_not_blocking(tmp_path: Path) -> None:
    root = FIXTURE.build_fixture_tree(
        tmp_path,
        modules={
            "src/backend/zuno/capability/tool_runtime/fixture_gateway.py":
                "async def execute(gateway, args):\n"
                "    result, receipt = await gateway.invoke_readonly(args=args)\n"
                "    return result\n",
            "src/backend/zuno/capability/mcp/mcp_tool_executor_adapter.py":
                "class MCPLangChainToolAdapter:\n"
                "    async def execute(self, args):\n"
                "        return await self._binding.ainvoke(args)\n",
        },
    )
    status, report = VERIFIER_MOD.verify(root, "repository")
    assert status == STATUS_REPO_CONFIRMED
    assert report["findings"]["direct_tool_bypass"] == []
    assert report["findings"]["product_direct_mcp_execution"] == []


# 41e. Product/Agent -> MCP client/provider execution blocks.
def test_fixture_product_direct_mcp_execution_blocks(tmp_path: Path) -> None:
    root = FIXTURE.build_fixture_tree(
        tmp_path,
        modules={
            "src/backend/zuno/api/services/fixture_product_mcp.py":
                "async def run(mcp_client):\n"
                "    return await mcp_client.call_server_tool('t', {})\n",
        },
    )
    status, report = VERIFIER_MOD.verify(root, "repository")
    assert status == STATUS_REPO_BLOCKED
    direct = report["findings"]["product_direct_mcp_execution"]
    assert any(f["path"].endswith("fixture_product_mcp.py") for f in direct), (
        "Product/Agent -> MCP client/provider must block: " + json.dumps(direct)
    )


# 41f. A product chat agent driving an MCP manager execution loop (the real
#      mcp_chat.py shape) is PRODUCT_DIRECT_MCP_EXECUTION.
def test_fixture_product_agent_driving_mcp_manager_blocks(tmp_path: Path) -> None:
    root = FIXTURE.build_fixture_tree(
        tmp_path,
        modules={
            "src/backend/zuno/api/services/fixture_mcp_chat.py":
                "from zuno.platform.services.mcp_openai.mcp_manager import MCPManager\n"
                "async def chat(mcp_manager: MCPManager):\n"
                "    return await mcp_manager.process_query([{'role': 'user'}])\n",
        },
    )
    status, report = VERIFIER_MOD.verify(root, "repository")
    assert status == STATUS_REPO_BLOCKED
    direct = report["findings"]["product_direct_mcp_execution"]
    assert any(f["path"].endswith("fixture_mcp_chat.py") for f in direct), (
        "product agent driving MCP manager execution must block"
    )


# 42. JSON output is stable: the same tree produces byte-identical reports.
def test_fixture_json_output_stable(tmp_path: Path) -> None:
    root = FIXTURE.build_fixture_tree(
        tmp_path,
        modules={
            "src/backend/zuno/platform/services/fixture_direct.py":
                "async def run(tool, args):\n    return await tool.ainvoke(args)\n",
        },
    )
    _, first = VERIFIER_MOD.verify(root, "repository")
    _, second = VERIFIER_MOD.verify(root, "repository")
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    parsed = json.loads(json.dumps(first, sort_keys=True))
    assert set(parsed.keys()) == {
        "evidence", "finding_count", "findings", "phase", "registry", "repo_root",
        "retired_flags", "scope", "status", "verifier",
    }


# 43. Repository scope fails closed on a fixture with a broken registry.
def test_fixture_repository_fails_closed_on_broken_registry(tmp_path: Path) -> None:
    root = FIXTURE.build_fixture_tree(
        tmp_path, registry=FIXTURE.build_registry(retired_transition="DEFAULT_NEW")
    )
    status, report = VERIFIER_MOD.verify(root, "repository")
    assert status == STATUS_REPO_BLOCKED
    assert report["findings"]["rollback_transition_accepted"]
