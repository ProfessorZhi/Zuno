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
        "ContextOrchestrator",
        "ContextTrace",
        "ModelContextPacket",
    ],
    "zuno.agent.post_turn": [
        "InMemoryLayerStore",
        "MemoryScope",
        "RawMemoryEvent",
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


def test_agent_layer_modules_reuse_legacy_runtime_objects() -> None:
    from zuno.agent.context import ContextOrchestrator
    from zuno.agent.post_turn import RawMemoryEvent
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
    assert DynamicCapabilitySelector is LegacyDynamicCapabilitySelector


def test_agent_package_facade_points_at_layer_modules() -> None:
    import zuno.agent as agent
    from zuno.agent.context import ContextOrchestrator
    from zuno.agent.runtime import GeneralAgent
    from zuno.agent.state import StreamAgentState

    assert agent.GeneralAgent is GeneralAgent
    assert agent.ContextOrchestrator is ContextOrchestrator
    assert agent.StreamAgentState is StreamAgentState


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
