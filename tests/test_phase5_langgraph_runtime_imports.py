import importlib
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"


def _ensure_backend_path() -> None:
    backend_path = str(BACKEND_ROOT)
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)


def test_langgraph_runtime_modules_import_from_zuno_mainline():
    _ensure_backend_path()

    domain_graph_module = importlib.import_module("zuno.core.graphs.domain_qa_graph")
    retrieval_models_module = importlib.import_module("zuno.services.retrieval.models")
    planner_module = importlib.import_module("zuno.services.retrieval.planner")
    loader_module = importlib.import_module("zuno.services.domain_pack.loader")

    assert hasattr(domain_graph_module, "DomainQAGraph")
    assert hasattr(retrieval_models_module, "RetrievalRequest")
    assert hasattr(planner_module, "RetrievalPlanner")
    assert hasattr(loader_module, "DomainPackLoader")


def test_domain_pack_loader_can_load_contract_review_from_zuno_runtime():
    _ensure_backend_path()

    DomainPackLoader = importlib.import_module("zuno.services.domain_pack.loader").DomainPackLoader

    pack = DomainPackLoader().load("contract_review")

    assert pack is not None
    assert pack.id == "contract_review"
    assert pack.retrieval_policy_data["graph_hop_limit"] == 2


def test_domain_qa_graph_build_initial_state_remains_available_after_direct_import():
    _ensure_backend_path()

    DomainQAGraph = importlib.import_module("zuno.core.graphs.domain_qa_graph").DomainQAGraph

    graph = DomainQAGraph(retrieval_runner=None)
    state = graph.build_initial_state(
        user_id="u1",
        agent_id="a1",
        dialog_id="d1",
        query="review this contract",
        knowledge_ids=["k1"],
        domain_pack_id="contract_review",
    )

    assert state["domain_pack_id"] == "contract_review"
    assert state["rewritten_queries"] == ["review this contract"]
    assert state["status"] == "pending"
