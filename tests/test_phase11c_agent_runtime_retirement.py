import importlib
from pathlib import Path


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
