import importlib
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_agent_runtime_facade_module_is_retired():
    assert not (REPO_ROOT / "src/backend/zuno/core/runtime/agent_runtime.py").exists()
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("zuno.core.runtime.agent_runtime")


def test_legacy_graph_sources_remain_for_direct_blocker_coverage():
    assert (REPO_ROOT / "src/backend/zuno/core/graphs/domain_qa_graph.py").exists()
    assert not (REPO_ROOT / "src/backend/zuno/core/graphs/multi_agent_supervisor_graph.py").exists()
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("zuno.core.graphs.multi_agent_supervisor_graph")
