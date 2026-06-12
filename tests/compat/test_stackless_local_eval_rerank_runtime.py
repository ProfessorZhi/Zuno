import asyncio


def test_stackless_local_eval_uses_explicit_local_rerank_config():
    from agentchat.evals.rag_eval.run_stackless_local_eval import _build_local_rerank_config
    from agentchat.services.rag.rerank import Reranker

    rerank_config = _build_local_rerank_config(
        model_name="zuno-local-rerank-dev",
        base_url="http://127.0.0.1:11435/rerank",
    )
    assert Reranker._is_configured(rerank_config) is True


def test_stackless_local_eval_disabled_rerank_config_short_circuits():
    from agentchat.evals.rag_eval.run_stackless_local_eval import _build_disabled_rerank_config
    from agentchat.services.rag.rerank import Reranker

    rerank_config = _build_disabled_rerank_config()
    assert Reranker._is_configured(rerank_config) is False


def test_reranker_request_can_hit_local_rerank_dev_server():
    from agentchat.evals.rag_eval.local_rerank_server import run_dev_server
    from agentchat.evals.rag_eval.run_stackless_local_eval import _build_local_rerank_config
    from agentchat.services.rag.rerank import Reranker

    with run_dev_server(model_name="zuno-local-rerank-dev", port=0) as server:
        rerank_config = _build_local_rerank_config(
            model_name=server["model_name"],
            base_url=server["base_url"],
        )
        results = asyncio.run(
            Reranker.request_rerank(
                "python keyword variable",
                ["calendar event reminder", "python keyword variable name rule"],
                config_override=rerank_config,
                top_n=2,
            )
        )
    assert results[0]["index"] == 1


def test_override_profile_thresholds_restores_original_value():
    from agentchat.evals.rag_eval.run_eval import PROFILE_SETTINGS
    from agentchat.evals.rag_eval.run_stackless_local_eval import _override_profile_thresholds

    original = PROFILE_SETTINGS["rag_rerank"]["retrieval_options"]["score_threshold"]
    with _override_profile_thresholds(
        profiles=["rag_rerank"],
        rerank_score_threshold_override=0.0,
    ):
        assert PROFILE_SETTINGS["rag_rerank"]["retrieval_options"]["score_threshold"] == 0.0
    assert PROFILE_SETTINGS["rag_rerank"]["retrieval_options"]["score_threshold"] == original
