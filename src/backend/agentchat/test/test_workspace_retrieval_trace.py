from types import SimpleNamespace


def test_build_retrieval_event_payload_includes_round_trace(monkeypatch):
    from agentchat.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        knowledge_ids=["kb_1"],
        retrieval_mode="auto",
    )

    payload = agent._build_retrieval_event_payload(
        {
            "actual_mode": "hybrid",
            "first_mode": "rag",
            "final_mode": "hybrid",
            "fallback_reason": "too_few_documents",
            "second_pass_used": True,
            "round_count": 3,
            "metadata": {
                "first_mode": "rag",
                "final_mode": "hybrid",
                "fallback_reason": "too_few_documents",
                "second_pass_used": True,
                "round_count": 3,
                "rewritten_query_used": True,
                "query_variants": ["original", "expanded"],
                "rounds": [
                    {"round": 1, "mode": "rag", "trigger": "initial"},
                    {"round": 2, "mode": "hybrid", "trigger": "route_broadening"},
                    {"round": 3, "mode": "hybrid", "trigger": "query_rewrite_retry"},
                ],
            },
        }
    )

    assert payload["retrieval_mode"] == "hybrid"
    assert payload["first_mode"] == "rag"
    assert payload["final_mode"] == "hybrid"
    assert payload["round_count"] == 3
    assert payload["second_pass_used"] is True
    assert payload["rewritten_query_used"] is True
    assert payload["rounds"][-1]["trigger"] == "query_rewrite_retry"
    assert "共 3 轮" in payload["message"]
    assert "改写后的问题再次补检" in payload["message"]
