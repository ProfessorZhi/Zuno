from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


EXPECTED_EXPORTS = {
    "zuno.agent.runtime": [
        "AgentConfig",
        "GeneralAgent",
    ],
    "zuno.agent.context": [
        "AgentExecutionContext",
        "ContextItem",
        "ContextOrchestrator",
        "ContextPackPolicy",
        "ContextPreparationInput",
        "ContextSelectionReason",
        "ContextSource",
        "ContextTrace",
        "ModelContextPacket",
        "TokenBudgetPolicy",
    ],
    "zuno.agent.harness": [
        "ControllerRuntimeState",
        "RuntimeCheckpoint",
        "RuntimeInterrupt",
        "RuntimeNodeContract",
        "SingleControllerRuntimeHarness",
        "build_single_controller_runtime_harness",
    ],
    "zuno.agent.durable_runtime": [
        "DurableRuntimeEvent",
        "DurableRuntimeTaskSnapshot",
        "InMemoryDurableRuntimeStore",
        "SingleControllerDurableRuntime",
    ],
    "zuno.agent.post_turn": [
        "InMemoryLayerStore",
        "MemoryScope",
        "RawMemoryEvent",
        "RuntimeTurnLedger",
        "TaskMemorySummary",
    ],
    "zuno.agent.state": [
        "StreamAgentState",
    ],
    "zuno.agent.streaming": [
        "EmitEventAgentMiddleware",
        "StreamAgentState",
    ],
    "zuno.agent.tool_bridge": [
        "CapabilityRecord",
        "CapabilityRegistry",
        "CapabilitySelectionRequest",
        "DynamicCapabilitySelector",
    ],
}


def test_agent_layer_modules_expose_runtime_boundaries() -> None:
    for module_name, expected_exports in EXPECTED_EXPORTS.items():
        module = importlib.import_module(module_name)
        assert module.__all__ == expected_exports


def test_general_agent_core_uses_target_layer_contract_imports() -> None:
    content = (
        REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "core" / "agents" / "general_agent.py"
    ).read_text(encoding="utf-8")
    forbidden_imports = [
        "from zuno.services.application.capabilities import",
        "from zuno.services.application.context import",
        "from zuno.services.application.knowledge import",
        "from zuno.services.memory import",
        "from zuno.services.retrieval.trace_artifacts import",
    ]

    assert [snippet for snippet in forbidden_imports if snippet in content] == []


def test_agent_layer_modules_reuse_legacy_runtime_objects() -> None:
    from zuno.agent.context import ContextOrchestrator
    from zuno.agent.post_turn import RawMemoryEvent
    from zuno.agent.post_turn import RuntimeTurnLedger
    from zuno.agent.runtime import GeneralAgent
    from zuno.agent.state import StreamAgentState
    from zuno.agent.tool_bridge import DynamicCapabilitySelector
    from zuno.core.agents import GeneralAgent as LegacyGeneralAgent
    from zuno.core.agents import StreamAgentState as LegacyStreamAgentState
    from zuno.services.application.capabilities import (
        DynamicCapabilitySelector as LegacyDynamicCapabilitySelector,
    )
    from zuno.services.application.context import ContextOrchestrator as LegacyContextOrchestrator
    from zuno.services.memory.layers import RawMemoryEvent as LegacyRawMemoryEvent

    assert GeneralAgent is LegacyGeneralAgent
    assert StreamAgentState is LegacyStreamAgentState
    assert ContextOrchestrator is LegacyContextOrchestrator
    assert RawMemoryEvent is LegacyRawMemoryEvent
    assert RuntimeTurnLedger(trace_id="t").to_dict()["trace_id"] == "t"
    assert DynamicCapabilitySelector is LegacyDynamicCapabilitySelector


def test_agent_package_facade_points_at_layer_modules() -> None:
    import zuno.agent as agent
    from zuno.agent.context import ContextOrchestrator
    from zuno.agent.durable_runtime import SingleControllerDurableRuntime
    from zuno.agent.harness import ControllerRuntimeState
    from zuno.agent.runtime import GeneralAgent
    from zuno.agent.state import StreamAgentState

    assert agent.GeneralAgent is GeneralAgent
    assert agent.ContextOrchestrator is ContextOrchestrator
    assert agent.StreamAgentState is StreamAgentState
    assert agent.ControllerRuntimeState is ControllerRuntimeState
    assert agent.SingleControllerDurableRuntime is SingleControllerDurableRuntime


def test_durable_runtime_store_persists_approval_wait_and_resumes_after_restart() -> None:
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
    assert waiting.pending_interrupt is not None

    persisted = json.loads(json.dumps(store.to_persistence_payload()))
    restored_store = InMemoryDurableRuntimeStore.from_persistence_payload(persisted)
    restored_runtime = SingleControllerDurableRuntime(store=restored_store)

    resumed = restored_runtime.resume_task(
        task_id="task_restart",
        approval_decision="approved",
        comment="approved after restart",
    )

    assert resumed.status == "completed"
    assert resumed.task_id == "task_restart"
    assert resumed.trace_id == "trace_restart"
    assert resumed.pending_interrupt is None
    assert resumed.latest_checkpoint is not None
    assert resumed.latest_checkpoint.node == "post_turn_commit"
    assert "runtime_resumed" in [event.type for event in resumed.events]


def test_importing_agent_surfaces_does_not_load_heavy_runtime_modules() -> None:
    code = """
import importlib
import json
import sys

sys.path.insert(0, r"__BACKEND_PATH__")

for name in __MODULES__:
    importlib.import_module(name)

prefixes = [
    "zuno.database",
    "zuno.api.services",
    "zuno.services.rag.vector_db",
]
print(json.dumps({
    prefix: sorted(name for name in sys.modules if name == prefix or name.startswith(prefix + "."))
    for prefix in prefixes
}, sort_keys=True))
"""
    env = dict(os.environ)
    backend_path = str(REPO_ROOT / "src" / "backend")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        backend_path
        if not existing_pythonpath
        else os.pathsep.join([backend_path, existing_pythonpath])
    )
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            code.replace("__BACKEND_PATH__", backend_path).replace(
                "__MODULES__", repr(sorted(EXPECTED_EXPORTS))
            ),
        ],
        check=True,
        capture_output=True,
        cwd=REPO_ROOT,
        env=env,
        text=True,
    )

    loaded_modules = json.loads(result.stdout)
    assert loaded_modules == {prefix: [] for prefix in loaded_modules}
