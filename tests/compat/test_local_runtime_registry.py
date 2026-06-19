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
        assert "status" not in payload["knowledge_config"]["index_settings"]
        assert "index_version" not in payload["knowledge_config"]["index_settings"]
        assert "health_status" not in payload["knowledge_config"]["graph_index_settings"]
        assert payload["knowledge_config"]["graph_index_settings"]["use_rag_entry_chunk"] is True
        assert payload["text_embedding_config"]["model_name"] == "bge-m3"
    finally:
        clear_local_runtime_settings(knowledge_id)
