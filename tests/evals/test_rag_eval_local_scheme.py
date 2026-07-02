from zuno.evals.rag_eval.ingest_prepared_corpus import build_eval_knowledge_config
from zuno.evals.rag_eval.run_eval import PROFILE_SETTINGS, resolve_profiles


def test_build_eval_knowledge_config_includes_local_embedding_model_refs():
    config = build_eval_knowledge_config(
        text_embedding_model_id="llm_local_embed_001",
        rerank_model_id="llm_rerank_001",
        index_capability="rag_graph",
        default_mode="rag_graph",
    )

    assert config["index_capability"] == "rag_graph"
    assert config["retrieval_settings"]["default_mode"] == "rag_graph"
    assert config["model_refs"]["text_embedding_model_id"] == "llm_local_embed_001"
    assert config["model_refs"]["rerank_model_id"] == "llm_rerank_001"


def test_resolve_profiles_supports_local_compare_profile_set():
    profiles = resolve_profiles(profile_set="local_compare")
    assert profiles == ["baseline_rag", "rag_rerank", "rag_graph_chunk_backed"]


def test_resolve_profiles_supports_graph_compare_profile_set():
    profiles = resolve_profiles(profile_set="graph_compare")
    assert profiles == ["baseline_rag", "rag_graph_chunk_backed", "rag_graph_chunk_backed_3hop"]


def test_deep_graphrag_compare_includes_measured_agentic_profile():
    profiles = resolve_profiles(profile_set="deep_graphrag_compare")

    assert profiles == ["baseline_rag", "local_graphrag", "deep_graphrag", "agentic_graphrag"]

    agentic = PROFILE_SETTINGS["agentic_graphrag"]
    assert agentic["retrieval_mode"] == "rag_graph_deep"
    assert agentic["retrieval_options"]["route_policy"] == "force_deep"
    assert agentic["retrieval_options"]["product_mode"] == "enhanced"
    assert agentic["retrieval_options"]["fallback_policy"]["allow_retry"] is True
    assert agentic["retrieval_options"]["agentic_floor_fusion"] is True

