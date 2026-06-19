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
            "community_report_prompt_id": "prompt_a",
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


def test_rerank_change_only_has_immediate_effect():
    from zuno.api.services.knowledge import KnowledgeService

    previous = _config()
    next_config = _config(model_refs={**previous["model_refs"], "rerank_model_id": "rerank_b"})

    impact = KnowledgeService.analyze_config_impact(previous, next_config)

    assert impact["text_reindex_required"] is False
    assert impact["image_reindex_required"] is False
    assert impact["graph_update_required"] is False
    assert "model_refs.rerank_model_id" in impact["immediate_effect_fields"]


def test_text_embedding_change_requires_text_reindex():
    from zuno.api.services.knowledge import KnowledgeService

    previous = _config()
    next_config = _config(model_refs={**previous["model_refs"], "text_embedding_model_id": "embed_b"})

    impact = KnowledgeService.analyze_config_impact(previous, next_config)

    assert impact["text_reindex_required"] is True
    assert impact["image_reindex_required"] is False
    assert impact["recommended_action"] == "text_index"


def test_vl_embedding_change_requires_image_reindex():
    from zuno.api.services.knowledge import KnowledgeService

    previous = _config()
    next_config = _config(model_refs={**previous["model_refs"], "vl_embedding_model_id": "vl_b"})

    impact = KnowledgeService.analyze_config_impact(previous, next_config)

    assert impact["image_reindex_required"] is True
    assert impact["recommended_action"] == "image_index"


def test_image_indexing_mode_change_requires_image_reindex():
    from zuno.api.services.knowledge import KnowledgeService

    previous = _config()
    next_config = _config(index_settings={**previous["index_settings"], "image_indexing_mode": "vl_only"})

    impact = KnowledgeService.analyze_config_impact(previous, next_config)

    assert impact["image_reindex_required"] is True
    assert impact["recommended_action"] == "image_index"


def test_domain_pack_change_still_requires_graph_and_community_updates():
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


def test_community_report_prompt_change_requires_only_community_report_refresh():
    from zuno.api.services.knowledge import KnowledgeService

    previous = _config(
        index_capability="rag_graph",
        retrieval_settings={**_config()["retrieval_settings"], "default_mode": "rag_graph"},
    )
    next_config = _config(
        index_capability="rag_graph",
        retrieval_settings={**_config()["retrieval_settings"], "default_mode": "rag_graph"},
        graph_index_settings={
            **previous["graph_index_settings"],
            "community_report_prompt_id": "prompt_b",
        },
    )

    impact = KnowledgeService.analyze_config_impact(previous, next_config)

    assert impact["graph_update_required"] is False
    assert impact["community_detection_required"] is False
    assert impact["community_report_required"] is True
    assert impact["recommended_action"] == "community_report"


def test_image_index_reindex_action_is_accepted():
    from zuno.api.services.knowledge import KnowledgeService
    import asyncio

    result = asyncio.run(KnowledgeService.run_reindex_action("kb_1", "image_index"))

    assert result["action"] == "image_index"
    assert result["status"] == "accepted"
