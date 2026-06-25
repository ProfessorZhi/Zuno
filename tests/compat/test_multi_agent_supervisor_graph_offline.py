import importlib
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_multi_agent_supervisor_graph_source_is_retired_from_current_backend():
    assert not (
        REPO_ROOT / "src/backend/zuno/core/graphs/multi_agent_supervisor_graph.py"
    ).exists(), "MultiAgentSupervisorGraph should not remain as current backend source"


def test_multi_agent_supervisor_graph_module_import_stays_retired():
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("zuno.core.graphs.multi_agent_supervisor_graph")
