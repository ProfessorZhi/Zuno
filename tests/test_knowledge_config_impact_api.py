import asyncio
from types import SimpleNamespace


def _config(**overrides):
    base = {
        "index_capability": "rag",
        "domain_pack_id": None,
        "eval_profile_id": None,
        "model_refs": {
            "text_embedding_model_id": "embed_a",
            "vl_embedding_model_id": "vl_a",
            "rerank_model_id": "rerank_a",
        },
        "index_settings": {
            "chunk_mode": "general",
            "chunk_size": 1024,
            "overlap": 120,
            "separator": "\n\n",
            "replace_consecutive_spaces": True,
            "remove_urls_emails": False,
            "image_indexing_mode": "dual",
            "vector_backend": "milvus",
            "index_version": "v1",
            "status": "active",
            "health_status": "ready",
            "text_index_status": "ready",
            "bm25_index_status": "ready",
            "last_build_time": None,
            "last_error": None,
        },
        "graph_index_settings": {
            "entity_extraction_mode": "rule_llm",
            "relation_schema": "open",
            "entity_normalization": True,
            "evidence_backlink": True,
            "use_rag_entry_chunk": True,
            "index_version": "v1",
            "health_status": "ready",
            "graph_index_status": "ready",
            "community_detection_status": "not_built",
            "community_report_status": "not_built",
            "community_version": "v0",
        },
        "retrieval_settings": {
            "default_mode": "rag",
            "profile": "auto",
            "refill_policy": "smart",
            "top_k": 5,
            "rerank_enabled": True,
            "rerank_top_k": 4,
            "score_threshold": None,
            "graph_hop_limit": 2,
            "max_paths_per_entity": 5,
        },
    }
    for key, value in overrides.items():
        base[key] = value
    return base


def test_config_impact_marks_embedding_change_as_text_reindex() -> None:
    from zuno.api.services.knowledge import KnowledgeService

    previous = _config()
    next_config = _config(model_refs={**previous["model_refs"], "text_embedding_model_id": "embed_b"})

    impact = KnowledgeService.analyze_config_impact(previous, next_config)

    assert impact["text_reindex_required"] is True
    assert impact["recommended_action"] == "text_index"
    assert "model_refs.text_embedding_model_id" in impact["changed_fields"]


def test_config_impact_marks_rerank_change_as_immediate_effect() -> None:
    from zuno.api.services.knowledge import KnowledgeService

    previous = _config()
    next_config = _config(model_refs={**previous["model_refs"], "rerank_model_id": "rerank_b"})

    impact = KnowledgeService.analyze_config_impact(previous, next_config)

    assert impact["text_reindex_required"] is False
    assert impact["graph_update_required"] is False
    assert impact["recommended_action"] == "save_only"
    assert "model_refs.rerank_model_id" in impact["immediate_effect_fields"]


def test_config_impact_marks_domain_pack_schema_change_for_graph_and_community() -> None:
    from zuno.api.services.knowledge import KnowledgeService

    previous = _config(
        index_capability="rag_graph",
        domain_pack_id="contract_review@v1",
        retrieval_settings={**_config()["retrieval_settings"], "default_mode": "rag_graph"},
    )
    next_config = _config(
        index_capability="rag_graph",
        domain_pack_id="contract_review@v2",
        retrieval_settings={**_config()["retrieval_settings"], "default_mode": "rag_graph"},
    )

    impact = KnowledgeService.analyze_config_impact(previous, next_config)

    assert impact["graph_update_required"] is True
    assert impact["community_detection_required"] is True
    assert impact["community_report_required"] is True


def test_knowledge_config_impact_endpoint_returns_service_analysis(monkeypatch):
    from zuno.api.v1.knowledge import analyze_knowledge_config_impact

    captured = {}

    async def fake_verify(knowledge_id, user_id):
        captured["permission"] = (knowledge_id, user_id)

    async def fake_get_config(knowledge_id):
        captured["knowledge_id"] = knowledge_id
        return _config()

    def fake_analyze(previous_config, next_config):
        captured["previous"] = previous_config
        captured["next"] = next_config
        return {"recommended_action": "text_index", "text_reindex_required": True}

    monkeypatch.setattr("zuno.api.v1.knowledge.KnowledgeService.verify_user_permission", fake_verify)
    monkeypatch.setattr("zuno.api.v1.knowledge.KnowledgeService.get_knowledge_config", fake_get_config)
    monkeypatch.setattr("zuno.api.v1.knowledge.KnowledgeService.analyze_config_impact", fake_analyze)

    login_user = SimpleNamespace(user_id="u_test")
    response = asyncio.run(
        analyze_knowledge_config_impact(
            knowledge_id="kb_1",
            next_config=_config(),
            login_user=login_user,
        )
    )

    assert response.status_code == 200
    assert captured["permission"] == ("kb_1", "u_test")
    assert response.data["recommended_action"] == "text_index"


def test_knowledge_reindex_action_endpoint_uses_explicit_action(monkeypatch):
    from zuno.api.v1.knowledge import reindex_knowledge_action

    captured = {}

    async def fake_verify(knowledge_id, user_id):
        captured["permission"] = (knowledge_id, user_id)

    async def fake_reindex(knowledge_id, action):
        captured["reindex"] = (knowledge_id, action)
        return {"knowledge_id": knowledge_id, "action": action, "status": "accepted"}

    monkeypatch.setattr("zuno.api.v1.knowledge.KnowledgeService.verify_user_permission", fake_verify)
    monkeypatch.setattr("zuno.api.v1.knowledge.KnowledgeService.run_reindex_action", fake_reindex)

    login_user = SimpleNamespace(user_id="u_test")
    response = asyncio.run(
        reindex_knowledge_action(
            knowledge_id="kb_1",
            action="community_report",
            login_user=login_user,
        )
    )

    assert response.status_code == 200
    assert captured["reindex"] == ("kb_1", "community_report")
    assert response.data["status"] == "accepted"
