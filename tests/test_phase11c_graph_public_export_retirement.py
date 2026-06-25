import importlib


def test_legacy_graphs_are_not_core_public_exports():
    core_module = importlib.import_module("zuno.core")
    graphs_module = importlib.import_module("zuno.core.graphs")

    assert "DomainQAGraph" not in getattr(core_module, "__all__", [])
    assert "MultiAgentSupervisorGraph" not in getattr(core_module, "__all__", [])
    assert "DomainQAGraph" not in getattr(graphs_module, "__all__", [])
    assert "MultiAgentSupervisorGraph" not in getattr(graphs_module, "__all__", [])
    assert not hasattr(core_module, "DomainQAGraph")
    assert not hasattr(core_module, "MultiAgentSupervisorGraph")
    assert not hasattr(graphs_module, "DomainQAGraph")
    assert not hasattr(graphs_module, "MultiAgentSupervisorGraph")


def test_legacy_graph_sources_remain_as_direct_blocked_legacy_modules():
    domain_graph_module = importlib.import_module("zuno.core.graphs.domain_qa_graph")
    supervisor_module = importlib.import_module(
        "zuno.core.graphs.multi_agent_supervisor_graph"
    )

    assert domain_graph_module.DomainQAGraph is not None
    assert supervisor_module.MultiAgentSupervisorGraph is not None
