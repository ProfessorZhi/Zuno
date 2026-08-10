import importlib

import pytest


def test_legacy_graphs_are_not_core_public_exports():
    for module_name in ["zuno.core", "zuno.core.graphs"]:
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(module_name)


def test_legacy_graph_sources_are_retired_from_current_backend_modules():
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("zuno.core.graphs.domain_qa_graph")
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("zuno.core.graphs.multi_agent_supervisor_graph")
