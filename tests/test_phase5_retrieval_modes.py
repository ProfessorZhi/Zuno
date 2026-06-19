from pathlib import Path
import importlib.util
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SERVICE_API_ROOT = REPO_ROOT / "src" / "backend"
BACKEND_ROOT = REPO_ROOT / "src/backend"
PLANNER_PATH = SERVICE_API_ROOT / "zuno/services/retrieval/planner.py"
RETRIEVAL_MODELS_PATH = SERVICE_API_ROOT / "zuno/services/retrieval/models.py"
GRAPHRAG_MODELS_PATH = BACKEND_ROOT / "zuno/services/graphrag/models.py"
CORE_ROOT = SERVICE_API_ROOT / "zuno/core"


def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _load_planner_runtime():
    graphrag_models = _load_module("phase5_graphrag_models", GRAPHRAG_MODELS_PATH)
    retrieval_models = _load_module("phase5_retrieval_models", RETRIEVAL_MODELS_PATH)
    sys.modules["zuno.services.graphrag.models"] = graphrag_models
    sys.modules["zuno.services.retrieval.models"] = retrieval_models
    planner_module = _load_module("phase5_retrieval_planner", PLANNER_PATH)
    return planner_module.RetrievalPlanner, retrieval_models.ProcessedQuery, retrieval_models.RetrievalRequest


def _processed(ProcessedQuery, query: str, *, relation: bool = False, keyword: bool = False):
    return ProcessedQuery(
        original_query=query,
        normalized_query=query,
        rewritten_queries=[query],
        intent_labels=[],
        query_features={
            "relation_question": relation,
            "keyword_heavy": keyword,
        },
        route_hints=[],
    )


def test_normal_retrieval_mode_stays_on_vector_keyword_path():
    RetrievalPlanner, ProcessedQuery, RetrievalRequest = _load_planner_runtime()
    planner = RetrievalPlanner(enable_keyword_recall=True)

    plan = planner.build_plan(
        RetrievalRequest(query="redis persistence mode", knowledge_ids=["kb_1"], mode="rag"),
        _processed(ProcessedQuery, "redis persistence mode"),
        knowledge_capability="rag",
    )

    assert plan.requested_mode == "rag"
    assert plan.resolved_mode == "rag"
    assert plan.resolved_profile == "vector_rerank"
    assert plan.enabled_retrievers == ["vector", "bm25"]


def test_enhanced_retrieval_mode_enables_graph_path_for_relation_questions():
    RetrievalPlanner, ProcessedQuery, RetrievalRequest = _load_planner_runtime()
    planner = RetrievalPlanner(enable_keyword_recall=True)

    plan = planner.build_plan(
        RetrievalRequest(query="终止条款和通知期限是什么关系", knowledge_ids=["kb_1"], mode="rag_graph"),
        _processed(ProcessedQuery, "终止条款和通知期限是什么关系", relation=True),
        knowledge_capability="rag_graph",
    )

    assert plan.requested_mode == "rag_graph_deep"
    assert plan.resolved_mode == "rag_graph_deep"
    assert plan.internal_route == "local_graphrag"
    assert plan.resolved_profile == "graph_relation"
    assert plan.enabled_retrievers == ["vector", "bm25", "graph"]


def test_enhanced_retrieval_mode_degrades_to_normal_when_graph_is_unavailable():
    RetrievalPlanner, ProcessedQuery, RetrievalRequest = _load_planner_runtime()
    planner = RetrievalPlanner(enable_keyword_recall=True)

    plan = planner.build_plan(
        RetrievalRequest(
            query="赔偿责任链路",
            knowledge_ids=["kb_1"],
            mode="rag_graph",
            scope_policy={"status": "active"},
            index_health={"graph": "unavailable"},
            index_version={"vector": "vector_v2", "graph": "graph_v2"},
        ),
        _processed(ProcessedQuery, "赔偿责任链路", relation=True),
        knowledge_capability="rag_graph",
    )

    assert plan.requested_mode == "rag_graph_deep"
    assert plan.resolved_mode == "rag"
    assert plan.internal_route == "standard_rag"
    assert "graph" not in plan.enabled_retrievers
    assert plan.fallback_policy["graph_degraded"] is True
    assert plan.index_version["graph"] == "graph_v2"


def test_domain_graph_runner_preserves_knowledge_default_mode_contract():
    content = (CORE_ROOT / "graphs/domain_qa_graph.py").read_text(encoding="utf-8")

    assert 'default_mode = retrieval_settings.get("default_mode") or "rag"' in content
    assert 'return str(default_mode), merged' in content
    assert '"mode": custom_result.get("actual_mode") or retrieval_plan.get("resolved_mode"),' in content


def test_enhanced_orchestrator_contract_keeps_graph_path_and_trace_metadata():
    orchestrator = (SERVICE_API_ROOT / "zuno/services/retrieval/orchestrator.py").read_text(encoding="utf-8")
    frontend_utils = (REPO_ROOT / "apps/web/src/utils/retrieval.ts").read_text(encoding="utf-8")

    assert 'if "graph" in plan.enabled_retrievers:' in orchestrator
    assert 'retriever_runs.append({"source": "graph", "result_count": len(docs), "mode": mode})' in orchestrator
    assert '"resolved_mode": final_plan.get("resolved_mode") or final_mode,' in orchestrator
    assert "value: 'rag'," in frontend_utils
    assert "value: 'rag_graph'," in frontend_utils
    assert "graphrag: 'rag_graph'" in frontend_utils
