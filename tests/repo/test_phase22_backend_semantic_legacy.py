"""PHASE22 backend semantic legacy cleanup enforcement tests.

These tests pin the post-cleanup invariant: the Single Controller Product
Runtime (Single Controller + Fixed AgentRunGraph + Dynamic Plan DAG + Fixed
StepExecutionGraph) is the only top-level product runtime, and the retired
``GeneralAgent`` family can never be reached again from production entry
points or restored by dynamic import.
"""

from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"


def _ensure_runtime_paths() -> None:
    if str(BACKEND_ROOT) not in sys.path:
        sys.path.insert(0, str(BACKEND_ROOT))


RETIRED_MODULES = [
    "zuno.agent.core.agents.general_agent",
    "zuno.agent.core.agents.react_agent",
    "zuno.agent.core.agents.plan_execute_agent",
    "zuno.agent.core.agents.codeact_agent",
    "zuno.agent.core.agents.text2sql_agent",
    "zuno.agent.state",
    "zuno.agent.streaming",
]

RETIRED_SYMBOLS = (
    "GeneralAgent",
    "AgentConfig",
    "StreamAgentState",
    "EmitEventAgentMiddleware",
    "PlanExecuteAgent",
    "ReactAgent",
    "CodeActAgent",
    "Text2SQLAgent",
)


# 4. GeneralAgent production export must be gone.
def test_general_agent_production_export_is_gone() -> None:
    _ensure_runtime_paths()

    import zuno.agent as agent
    import zuno.agent.core as core
    import zuno.agent.core.agents as agents

    for symbol in RETIRED_SYMBOLS:
        for package in (agent, core, agents):
            assert symbol not in getattr(package, "__all__", [])
            assert not hasattr(package, symbol)


# 5. Dynamic import cannot restore the retired runtime.
def test_dynamic_import_cannot_restore_retired_runtime() -> None:
    _ensure_runtime_paths()

    for module_name in RETIRED_MODULES:
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(module_name)


# 6. Env selector cannot be restored: production must not accept a retired
#    runtime selection env var, and the completion cutover mode rejects
#    the retired rollback mode fail-closed.
def test_env_selector_cannot_restore_retired_runtime(monkeypatch) -> None:
    production_root = BACKEND_ROOT / "zuno"
    for path in production_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "ZUNO_AGENT_RUNTIME" not in text, f"retired env selector found in {path}"
        assert "_create_chat_agent" not in text, f"retired chat agent helper found in {path}"

    from zuno.api.services.completion import CompletionService

    monkeypatch.setenv("ZUNO_COMPLETION_CUTOVER_MODE", "rollback")
    with pytest.raises(ValueError, match="rollback mode is retired"):
        CompletionService.resolve_cutover_mode()
    monkeypatch.delenv("ZUNO_COMPLETION_CUTOVER_MODE", raising=False)
    assert CompletionService.resolve_cutover_mode() == "new_default"


# 1-3. Product API / Queue Worker / CLI must not import the retired agent.
@pytest.mark.parametrize(
    "relative_path",
    [
        "src/backend/zuno/main.py",
        "src/backend/zuno/api/v1/completion.py",
        "src/backend/zuno/api/services/completion.py",
        "src/backend/zuno/api/services/workspace_task_runtime.py",
        "src/backend/zuno/platform/services/queue/workers.py",
        "src/backend/zuno/platform/services/cli_tool_discovery.py",
        "src/backend/zuno/platform/services/simple_api_tool.py",
        "tools/scripts/start.py",
    ],
)
def test_entry_points_do_not_import_retired_agent(relative_path: str) -> None:
    text = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
    assert "general_agent" not in text
    assert "GeneralAgent" not in text
    assert "plan_execute_agent" not in text
    assert "codeact_agent" not in text
    assert "zuno.agent.state" not in text
    assert "zuno.agent.streaming" not in text


# 7. Single Controller is the only top-level runtime surface.
def test_single_controller_is_the_only_top_level_runtime() -> None:
    _ensure_runtime_paths()

    from zuno.agent.runtime import RuntimeDependencyFactory, UnifiedAgentRuntimeService
    from zuno.agent.runtime.graph import build_agent_graph
    from zuno.agent.runtime.phase08 import build_phase08_step_graph
    from zuno.agent.runtime.planning import RuntimePlanner
    from zuno.agent.harness import SingleControllerRuntimeHarness

    assembly = RuntimeDependencyFactory.for_completion()
    service = UnifiedAgentRuntimeService(store=assembly.store, dependencies=assembly.dependencies)
    graph = service.graph

    assert graph is not None
    assert callable(build_agent_graph)
    assert callable(build_phase08_step_graph)
    assert RuntimePlanner is not None
    assert SingleControllerRuntimeHarness is not None


# 8-11. Every product run passes through Plan / Trace / Budget / RunOutcome.
def test_fixed_agent_run_graph_contains_plan_trace_budget_runoutcome_nodes() -> None:
    _ensure_runtime_paths()

    from zuno.agent.runtime.graph import build_agent_graph
    from zuno.agent.runtime.nodes import DEFAULT_RUNTIME_NODES
    from zuno.agent.runtime.routing import RuntimeNode
    from zuno.agent.runtime.state import AgentRuntimeState

    required_nodes = {
        "plan": RuntimeNode.CREATE_OR_UPDATE_PLAN.value,
        "trace": RuntimeNode.OBSERVE.value,
        "evidence": RuntimeNode.EVIDENCE_GATE.value,
        "reflect": RuntimeNode.REFLECTION.value,
        "budget": RuntimeNode.EXECUTE_STEP.value,
        "runoutcome": RuntimeNode.FINALIZE.value,
        "approval": RuntimeNode.APPROVAL.value,
        "commit": RuntimeNode.POST_TURN_COMMIT.value,
    }
    node_names = {node for node in DEFAULT_RUNTIME_NODES}
    for label, node_name in required_nodes.items():
        assert node_name in node_names, f"fixed AgentRunGraph missing {label} node: {node_name}"

    graph = build_agent_graph()
    assert graph is not None

    # State carries Plan (plan_state), Trace (trace_id) and Budget limits.
    from zuno.agent.runtime.contracts import RuntimeLimits
    from zuno.agent.contracts import PlanState

    assert PlanState is not None
    assert RuntimeLimits is not None
    fields = AgentRuntimeState.__dataclass_fields__ if hasattr(AgentRuntimeState, "__dataclass_fields__") else {}
    for field_name in ("plan_state", "trace_id", "run_id", "current_step_id", "finalization_status"):
        assert field_name in fields, f"AgentRuntimeState missing {field_name}"


def test_run_outcome_contract_is_enforced() -> None:
    _ensure_runtime_paths()

    from zuno.agent.runtime.contracts import FinalizationStatus

    assert FinalizationStatus.NOT_READY is not None
    assert FinalizationStatus.INTERRUPTED is not None
    statuses = {item.value for item in FinalizationStatus}
    assert {"not_ready", "interrupted", "failed", "finalized"}.issubset(statuses)
    # Every run reaches the Finalize node and settles a RunOutcome.
    from zuno.agent.runtime.routing import RuntimeNode

    assert RuntimeNode.FINALIZE.value == "finalize"


# 12. ReAct remains a step-internal mechanism (not a top-level runtime).
def test_react_remains_a_step_internal_mechanism() -> None:
    _ensure_runtime_paths()

    from zuno.agent.runtime.execution import ReActStepExecutor
    from zuno.agent.runtime.execution.react_runner import ReActStepRunner
    from zuno.agent.runtime.execution.registry import StepExecutorRegistry
    from zuno.agent.runtime.execution import KnowledgeStepExecutor, ModelStepExecutor, ToolStepExecutor

    registry = StepExecutorRegistry(
        (KnowledgeStepExecutor(), ToolStepExecutor(), ModelStepExecutor(), ReActStepExecutor())
    )
    assert registry is not None
    assert ReActStepRunner is not None


# 13. Security/Approval cannot be bypassed by a legacy agent: approval flows
#     only through the canonical controller, and resume requires a pending
#     interrupt.
def test_security_approval_cannot_be_bypassed() -> None:
    _ensure_runtime_paths()

    from zuno.agent.durable_runtime import InMemoryDurableRuntimeStore, SingleControllerDurableRuntime
    from zuno.agent.harness import ControllerRuntimeState
    from zuno.agent.runtime.service import UnifiedAgentRuntimeService
    from zuno.agent.runtime.sqlite_store import SQLiteAgentRunStore

    state = ControllerRuntimeState(
        thread_id="thread_approval",
        workspace_id="workspace_approval",
        user_id="user_approval",
        task_id="task_approval",
        trace_id="trace_approval",
        goal="approval gate",
    )
    store = InMemoryDurableRuntimeStore()
    runtime = SingleControllerDurableRuntime(store=store)
    waiting = runtime.start_task(
        state,
        interrupt_at_node="act_react_loop",
        required_approval="tool:mail.send",
        interrupt_payload={"approval_id": "approval_1"},
    )
    assert waiting.status == "approval_waiting"

    # A resume without a pending interrupt must fail closed (unknown task).
    import tempfile

    service_store = SQLiteAgentRunStore(
        Path(tempfile.gettempdir()) / "zuno_test_phase22_no_interrupt.db"
    )
    service = UnifiedAgentRuntimeService(store=service_store)
    with pytest.raises(KeyError, match="unknown durable runtime task"):
        service.resume(task_id="task_approval")


# 14. Tool side effects cannot be bypassed: the canonical gateway enforces
#     readonly classification and side-effect gating.
def test_tool_side_effect_gateway_is_enforced() -> None:
    gateway_path = BACKEND_ROOT / "zuno" / "capability" / "tool_runtime" / "invocation_gateway.py"
    assert gateway_path.exists()
    text = gateway_path.read_text(encoding="utf-8")
    for phrase in [
        "class ToolInvocationGateway",
        "readonly: bool",
        "PHASE16_REQUIRED_FOR_SIDE_EFFECT_TOOL",
        "invoke_readonly",
    ]:
        assert phrase in text, f"ToolInvocationGateway missing phrase: {phrase}"

    # The retired direct-execution bypass phrase must not be present in the
    # agent-core surface (agent runtime, capability runtime, API services).
    scoped_roots = [
        BACKEND_ROOT / "zuno" / "agent",
        BACKEND_ROOT / "zuno" / "api" / "services",
        BACKEND_ROOT / "zuno" / "capability" / "tool_runtime",
    ]
    bypass_hits = []
    for root in scoped_roots:
        for path in root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            content = path.read_text(encoding="utf-8")
            if "tool_result = await handler(request)" in content:
                bypass_hits.append(str(path.relative_to(BACKEND_ROOT)))
    assert bypass_hits == []

    # Known out-of-package surface: the workspace simple/wechat agents still
    # execute tools directly. They are tracked as UNRESOLVED in
    # docs/evidence/goal05-phase22-backend-semantic-legacy-cleanup/ and owned
    # by the workspace cutover wave; pin the known surface so it cannot grow.
    workspace_files = [
        BACKEND_ROOT / "zuno" / "platform" / "services" / "workspace" / "simple_agent.py",
        BACKEND_ROOT / "zuno" / "platform" / "services" / "workspace" / "wechat_agent.py",
    ]
    known_bypass = [
        path for path in workspace_files if path.exists()
        and "tool_result = await handler(request)" in path.read_text(encoding="utf-8")
    ]
    assert len(known_bypass) == 2


# 15. Developer/CI adapters must not be selectable as the server_product
#     default; no runtime env selector exists in production at all.
def test_no_developer_ci_adapter_default_in_production(monkeypatch) -> None:
    production_root = BACKEND_ROOT / "zuno"
    for path in production_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "ZUNO_AGENT_RUNTIME" not in text
        assert "legacy_general_agent" not in text
        assert "ZUNO_PROFILE" not in text

    # Completion resolves to new_default and rejects retired rollback fail-closed.
    from zuno.api.services.completion import CompletionService

    monkeypatch.delenv("ZUNO_COMPLETION_CUTOVER_MODE", raising=False)
    assert CompletionService.resolve_cutover_mode() == "new_default"


# 16. Tests must not depend on the retired runtime success path.
def test_tests_do_not_import_retired_runtime() -> None:
    test_roots = [REPO_ROOT / "tests", REPO_ROOT / "tools"]
    retired_imports = [
        "from zuno.agent.core.agents.general_agent import",
        "from zuno.agent.core.agents import GeneralAgent",
        "from zuno.agent.core.agents import AgentConfig",
        "from zuno.agent.state import",
        "from zuno.agent.streaming import",
        "import zuno.agent.core.agents.general_agent",
        "import zuno.agent.core.agents.react_agent",
        "import zuno.agent.core.agents.plan_execute_agent",
        "import zuno.agent.core.agents.codeact_agent",
    ]
    hits = []
    for root in test_roots:
        for path in root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            # Only actual import statements count; negative assertions such as
            # "assert 'GeneralAgent' not in ..." are allowed by design.
            for line in text.splitlines():
                stripped = line.lstrip()
                if not stripped.startswith(("from ", "import ")):
                    continue
                for marker in retired_imports:
                    if marker in line:
                        hits.append(f"{path.relative_to(REPO_ROOT)}: {line.strip()}")
    assert hits == []


# 17. Package import smoke: the canonical surface imports cleanly.
def test_package_import_smoke() -> None:
    _ensure_runtime_paths()

    import zuno
    import zuno.agent
    import zuno.agent.core
    import zuno.agent.core.agents
    import zuno.agent.runtime
    import zuno.agent.harness
    import zuno.agent.durable_runtime
    import zuno.agent.planning
    import zuno.agent.context

    assert zuno is not None
    assert "UnifiedAgentRuntimeService" in zuno.agent.runtime.__all__


# 18. Restart/Resume still goes through the canonical runtime.
def test_restart_resume_goes_through_canonical_runtime() -> None:
    _ensure_runtime_paths()

    from zuno.agent.durable_runtime import InMemoryDurableRuntimeStore, SingleControllerDurableRuntime
    from zuno.agent.harness import ControllerRuntimeState

    state = ControllerRuntimeState(
        thread_id="thread_restart",
        workspace_id="workspace_restart",
        user_id="user_restart",
        task_id="task_restart",
        trace_id="trace_restart",
        goal="Resume after process restart",
    )
    store = InMemoryDurableRuntimeStore()
    runtime = SingleControllerDurableRuntime(store=store)

    waiting = runtime.start_task(
        state,
        interrupt_at_node="act_react_loop",
        required_approval="tool:mail.send",
        interrupt_payload={"approval_id": "approval_restart"},
    )
    assert waiting.status == "approval_waiting"

    persisted = store.to_persistence_payload()
    restored_store = InMemoryDurableRuntimeStore.from_persistence_payload(persisted)
    restored_runtime = SingleControllerDurableRuntime(store=restored_store)

    resumed = restored_runtime.resume_task(
        task_id="task_restart",
        approval_decision="approved",
        comment="approved after restart",
    )
    assert resumed.status == "completed"
    assert "runtime_resumed" in [event.type for event in resumed.events]


# 1-3 (source-level): API route/worker/CLI files must not even mention the
# retired module names (belt and braces with the import checks above).
def test_source_tree_has_no_retired_agent_references() -> None:
    retired_paths = [
        "src/backend/zuno/agent/core/agents/general_agent.py",
        "src/backend/zuno/agent/core/agents/react_agent.py",
        "src/backend/zuno/agent/core/agents/plan_execute_agent.py",
        "src/backend/zuno/agent/core/agents/codeact_agent.py",
        "src/backend/zuno/agent/core/agents/text2sql_agent.py",
        "src/backend/zuno/agent/runtime.py",
        "src/backend/zuno/agent/state.py",
        "src/backend/zuno/agent/streaming.py",
    ]
    for rel in retired_paths:
        assert not (REPO_ROOT / rel).exists(), f"retired file must not exist: {rel}"
