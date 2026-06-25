import asyncio


def test_knowledge_service_prefers_local_runtime_registry():
    from zuno.api.services.knowledge import KnowledgeService
    from zuno.services.runtime_registry import clear_local_runtime_settings, register_local_runtime_settings

    knowledge_id = "stackless_test_knowledge"
    register_local_runtime_settings(
        knowledge_id,
        {
            "knowledge_config": {
                "index_capability": "rag_graph",
                "index_settings": {"vector_backend": "chroma"},
                "graph_index_settings": {"use_rag_entry_chunk": True},
                "retrieval_settings": {"default_mode": "rag_graph"},
            },
            "text_embedding_config": {"model_name": "bge-m3", "base_url": "http://127.0.0.1:11434/v1", "api_key": ""},
        },
    )
    try:
        payload = asyncio.run(KnowledgeService.get_runtime_settings(knowledge_id))
        assert payload["knowledge_id"] == knowledge_id
        assert payload["knowledge_config"]["index_settings"]["vector_backend"] == "chroma"
        assert payload["knowledge_config"]["index_settings"]["status"] == "active"
        assert payload["knowledge_config"]["index_settings"]["index_version"] == "v1"
        assert payload["knowledge_config"]["graph_index_settings"]["health_status"] == "ready"
        assert payload["knowledge_config"]["graph_index_settings"]["use_rag_entry_chunk"] is True
        assert payload["text_embedding_config"]["model_name"] == "bge-m3"
    finally:
        clear_local_runtime_settings(knowledge_id)


def test_knowledge_service_normalizes_local_project_payload_runtime_settings():
    from zuno.api.services.knowledge import KnowledgeService
    from zuno.services.runtime_registry import clear_local_runtime_settings, register_local_runtime_settings

    knowledge_id = "project_payload_runtime"
    project_payload = {
        "id": "contract_review",
        "default_retrieval_profile": "graph_heavy",
        "default_eval_profile_id": "contract_eval",
    }
    register_local_runtime_settings(
        knowledge_id,
        {
            "knowledge_config": {
                "index_capability": "rag_graph",
                "retrieval_settings": {"profile": "auto"},
            },
            "domain_pack_id": "contract_review",
            "project_payload": project_payload,
        },
    )
    try:
        payload = asyncio.run(KnowledgeService.get_runtime_settings(knowledge_id))

        assert payload["domain_pack_id"] == "contract_review"
        assert payload["project_payload"] == project_payload
        assert "domain_pack" not in payload
        assert payload["knowledge_config"]["retrieval_settings"]["profile"] == "graph_heavy"
        assert payload["knowledge_config"]["eval_profile_id"] == "contract_eval"
    finally:
        clear_local_runtime_settings(knowledge_id)
