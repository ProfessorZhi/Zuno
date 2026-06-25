import importlib
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_agent_runtime_facade_is_retired_from_current_backend_source():
    assert not (
        REPO_ROOT / "src/backend/zuno/core/runtime/agent_runtime.py"
    ).exists(), "AgentRuntime facade should not remain as current backend source"

    core_module = importlib.import_module("zuno.core")
    runtime_module = importlib.import_module("zuno.core.runtime")

    assert "AgentRuntime" not in getattr(core_module, "__all__", [])
    assert "AgentRuntime" not in vars(core_module)
    assert "AgentRuntime" not in getattr(runtime_module, "__all__", [])
    assert "AgentRuntime" not in vars(runtime_module)


def test_graph_sources_track_current_phase11c_retirement_status():
    assert not (
        REPO_ROOT / "src/backend/zuno/core/graphs/domain_qa_graph.py"
    ).exists(), "DomainQAGraph should not remain as current backend source"
    assert not (
        REPO_ROOT / "src/backend/zuno/core/graphs/states.py"
    ).exists(), "legacy graph states should not remain without current graph source"
    assert not (
        REPO_ROOT / "src/backend/zuno/core/graphs/multi_agent_supervisor_graph.py"
    ).exists(), "MultiAgentSupervisorGraph should not remain as current backend source"


def test_retired_runtime_modules_stay_unimportable():
    for module_name in [
        "zuno.core.runtime.agent_runtime",
        "zuno.core.graphs.domain_qa_graph",
        "zuno.core.graphs.states",
        "zuno.core.graphs.multi_agent_supervisor_graph",
        "zuno.services.domain_pack",
        "zuno.services.domain_pack.loader",
    ]:
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(module_name)
