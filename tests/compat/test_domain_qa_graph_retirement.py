import importlib
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_domain_qa_graph_source_is_retired_from_current_backend():
    assert not (REPO_ROOT / "src/backend/zuno/core/graphs/domain_qa_graph.py").exists()
    assert not (REPO_ROOT / "src/backend/zuno/core/graphs/states.py").exists()


def test_domain_qa_graph_module_import_stays_retired():
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("zuno.core.graphs.domain_qa_graph")

    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("zuno.core.graphs.states")
