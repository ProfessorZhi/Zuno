import importlib
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"


def _ensure_runtime_paths() -> None:
    for runtime_root in (str(BACKEND_ROOT),):
        if runtime_root not in sys.path:
            sys.path.insert(0, runtime_root)


def test_project_query_runtime_modules_import_from_zuno_mainline():
    _ensure_runtime_paths()

    knowledge_query_module = importlib.import_module("zuno.api.services.knowledge_query")
    query_service_module = importlib.import_module("zuno.services.graphrag.query_service")
    retrieval_models_module = importlib.import_module("zuno.services.retrieval.models")
    planner_module = importlib.import_module("zuno.services.retrieval.planner")

    assert hasattr(knowledge_query_module, "KnowledgeQueryService")
    assert hasattr(knowledge_query_module, "KnowledgeQueryResult")
    assert hasattr(query_service_module, "GraphRAGProjectSnapshot")
    assert hasattr(query_service_module, "GraphRAGQueryService")
    assert hasattr(retrieval_models_module, "RetrievalRequest")
    assert hasattr(planner_module, "RetrievalPlanner")


def test_legacy_runtime_import_coverage_lives_in_root_phase11c_tests():
    assert (REPO_ROOT / "tests/test_phase11c_agent_runtime_retirement.py").exists()
    assert not (
        REPO_ROOT / "tests/compat/test_domain_pack_runtime_service_retirement.py"
    ).exists()
    assert not (REPO_ROOT / "tests/compat/test_domain_qa_graph_retirement.py").exists()
