import importlib
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_multi_agent_supervisor_runtime_source_is_retired_from_current_backend():
    assert not (
        REPO_ROOT / "src/backend/zuno/core/graphs/multi_agent_supervisor_graph.py"
    ).exists(), "MultiAgentSupervisorGraph should not remain as current backend source"


def test_multi_agent_supervisor_runtime_module_import_stays_retired():
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("zuno.core.graphs.multi_agent_supervisor_graph")


def test_domain_qa_graph_remains_direct_blocked_legacy_until_asset_migration():
    domain_graph_module = importlib.import_module("zuno.core.graphs.domain_qa_graph")

    assert domain_graph_module.DomainQAGraph is not None
