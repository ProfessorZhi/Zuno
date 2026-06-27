import asyncio
from types import SimpleNamespace


def _sample_knowledge_config():
    return {
        "index_capability": "rag_graph",
        "model_refs": {
            "text_embedding_model_id": "llm_embed_text",
            "vl_embedding_model_id": "llm_embed_vl",
            "rerank_model_id": "llm_rerank",
        },
        "index_settings": {
            "chunk_mode": "parent_child",
            "chunk_size": 768,
            "overlap": 128,
            "separator": "\n\n",
            "replace_consecutive_spaces": True,
            "remove_urls_emails": True,
            "image_indexing_mode": "dual",
            "vector_backend": "milvus",
            "index_version": "vector_v2",
            "status": "active",
            "health_status": "ready",
        },
        "graph_index_settings": {
            "entity_extraction_mode": "rule_llm",
            "relation_schema": "open",
            "entity_normalization": True,
            "evidence_backlink": True,
            "use_rag_entry_chunk": True,
            "index_version": "graph_v2",
            "health_status": "ready",
        },
        "retrieval_settings": {
            "default_mode": "rag_graph",
            "refill_policy": "smart",
            "top_k": 6,
            "rerank_enabled": True,
            "rerank_top_k": 4,
            "score_threshold": 0.42,
            "graph_hop_limit": 2,
            "max_paths_per_entity": 5,
        },
    }


def test_knowledge_create_request_accepts_knowledge_config_and_ignores_legacy_default_retrieval_mode():
    from zuno.schema.knowledge import KnowledgeCreateRequest

    request = KnowledgeCreateRequest(
        knowledge_name="PyIndex",
        knowledge_desc="Python knowledge base for tests.",
        knowledge_config=_sample_knowledge_config(),
        default_retrieval_mode="graphrag",
    )

    dumped = request.model_dump()

    assert dumped["knowledge_name"] == "PyIndex"
    assert dumped["knowledge_desc"] == "Python knowledge base for tests."
    assert dumped["knowledge_config"]["retrieval_settings"]["default_mode"] == "rag_graph"
    assert "default_retrieval_mode" not in dumped


def test_knowledge_config_prefers_graphrag_project_id_without_public_legacy_output():
    from zuno.api.services.knowledge import KnowledgeService
    from zuno.schema.knowledge import KnowledgeConfig

    request_config = KnowledgeConfig.model_validate(
        {
            "graphrag_project_id": "contract_review_project",
            "domain_pack_id": "legacy_contract_review",
            "retrieval_settings": {"default_mode": "rag_graph"},
        }
    ).model_dump()

    normalized = KnowledgeService._normalize_knowledge_config(request_config)

    assert normalized["graphrag_project_id"] == "contract_review_project"
    assert "domain_pack_id" not in normalized


def test_legacy_domain_pack_id_is_bounded_migration_input_for_project_id():
    from zuno.api.services.knowledge import KnowledgeService

    normalized = KnowledgeService._normalize_knowledge_config(
        {
            "domain_pack_id": "contract_review",
            "retrieval_settings": {"default_mode": "rag_graph"},
        }
    )

    assert normalized["graphrag_project_id"] == "contract_review"
    assert "domain_pack_id" not in normalized


def test_create_knowledge_endpoint_passes_knowledge_config(monkeypatch):
    from zuno.api.v1.knowledge import upload_knowledge
    from zuno.schema.knowledge import KnowledgeCreateRequest

    captured = {}

    async def fake_create_knowledge(knowledge_name, knowledge_desc, user_id, knowledge_config=None):
        captured["knowledge_name"] = knowledge_name
        captured["knowledge_desc"] = knowledge_desc
        captured["user_id"] = user_id
        captured["knowledge_config"] = knowledge_config

    monkeypatch.setattr(
        "zuno.api.v1.knowledge.KnowledgeService.create_knowledge",
        fake_create_knowledge,
    )

    login_user = SimpleNamespace(user_id="u_test")
    request = KnowledgeCreateRequest(
        knowledge_name="PyIndex",
        knowledge_desc="Python knowledge base for tests.",
        knowledge_config=_sample_knowledge_config(),
        default_retrieval_mode="hybrid",
    )

    response = asyncio.run(upload_knowledge(knowledge_req=request, login_user=login_user))

    assert response.status_code == 200
    assert captured["knowledge_name"] == "PyIndex"
    assert captured["knowledge_desc"] == "Python knowledge base for tests."
    assert captured["user_id"] == "u_test"
    assert captured["knowledge_config"]["retrieval_settings"]["default_mode"] == "rag_graph"
    assert captured["knowledge_config"]["index_settings"]["index_version"] == "vector_v2"
    assert captured["knowledge_config"]["index_settings"]["status"] == "active"
    assert captured["knowledge_config"]["graph_index_settings"]["index_version"] == "graph_v2"


def test_update_knowledge_endpoint_passes_knowledge_config_patch(monkeypatch):
    from zuno.api.v1.knowledge import update_knowledge
    from zuno.schema.knowledge import KnowledgeUpdateRequest

    captured = {}

    async def fake_verify_user_permission(knowledge_id, user_id):
        captured["permission_check"] = (knowledge_id, user_id)

    async def fake_update_knowledge(knowledge_id, knowledge_name, knowledge_desc, knowledge_config=None):
        captured["update"] = (knowledge_id, knowledge_name, knowledge_desc, knowledge_config)

    monkeypatch.setattr(
        "zuno.api.v1.knowledge.KnowledgeService.verify_user_permission",
        fake_verify_user_permission,
    )
    monkeypatch.setattr(
        "zuno.api.v1.knowledge.KnowledgeService.update_knowledge",
        fake_update_knowledge,
    )

    login_user = SimpleNamespace(user_id="u_test")
    request = KnowledgeUpdateRequest(
        knowledge_id="k_test",
        knowledge_name="PyIndex2",
        knowledge_desc="Updated Python knowledge base.",
        knowledge_config={
            "retrieval_settings": {
                "default_mode": "graphrag",
                "top_k": 8,
            }
        },
        default_retrieval_mode="graphrag",
    )

    response = asyncio.run(update_knowledge(knowledge_req=request, login_user=login_user))

    assert response.status_code == 200
    assert captured["permission_check"] == ("k_test", "u_test")
    assert captured["update"] == (
        "k_test",
        "PyIndex2",
        "Updated Python knowledge base.",
        {
            "retrieval_settings": {
                "default_mode": "graphrag",
                "top_k": 8,
            }
        },
    )


def test_select_knowledge_exposes_normalized_knowledge_config(monkeypatch):
    from zuno.api.services.knowledge import KnowledgeService

    async def fake_get_knowledge_by_user(_user_id):
        return [
            SimpleNamespace(
                to_dict=lambda: {
                    "id": "k1",
                    "name": "PyIndex",
                    "description": "Knowledge description",
                    "default_retrieval_mode": "graphrag",
                    "knowledge_config": {
                        "retrieval_settings": {
                            "top_k": 9,
                        }
                    },
                }
            )
        ]

    async def fake_select_knowledge_file(_knowledge_id):
        return []

    monkeypatch.setattr(
        "zuno.api.services.knowledge.KnowledgeDao.get_knowledge_by_user",
        fake_get_knowledge_by_user,
    )
    monkeypatch.setattr(
        "zuno.api.services.knowledge.KnowledgeFileDao.select_knowledge_file",
        fake_select_knowledge_file,
    )

    results = asyncio.run(KnowledgeService.select_knowledge("u_test"))

    assert len(results) == 1
    assert results[0]["name"] == "PyIndex"
    assert "default_retrieval_mode" not in results[0]
    assert results[0]["knowledge_config"]["index_capability"] == "rag_graph"
    assert results[0]["knowledge_config"]["retrieval_settings"]["default_mode"] == "rag_graph"
    assert results[0]["knowledge_config"]["retrieval_settings"]["top_k"] == 9
    assert results[0]["knowledge_config"]["index_settings"]["chunk_mode"] == "general"
    assert results[0]["knowledge_config"]["index_settings"]["vector_backend"] == "milvus"
    assert results[0]["knowledge_config"]["index_settings"]["status"] == "active"
    assert results[0]["knowledge_config"]["index_settings"]["index_version"] == "v1"


def test_update_knowledge_service_merges_partial_knowledge_config(monkeypatch):
    from zuno.api.services.knowledge import KnowledgeService

    captured = {}

    async def fake_select_user_by_id(_knowledge_id):
        return SimpleNamespace(
            to_dict=lambda: {
                "id": "k_test",
                "knowledge_config": _sample_knowledge_config(),
                "default_retrieval_mode": "rag",
            }
        )

    async def fake_update_knowledge_by_id(
        knowledge_id,
        knowledge_desc,
        knowledge_name,
        default_retrieval_mode=None,
        knowledge_config=None,
    ):
        captured["update"] = (
            knowledge_id,
            knowledge_desc,
            knowledge_name,
            default_retrieval_mode,
            knowledge_config,
        )

    monkeypatch.setattr(
        "zuno.api.services.knowledge.KnowledgeDao.select_user_by_id",
        fake_select_user_by_id,
    )
    monkeypatch.setattr(
        "zuno.api.services.knowledge.KnowledgeDao.update_knowledge_by_id",
        fake_update_knowledge_by_id,
    )

    asyncio.run(
        KnowledgeService.update_knowledge(
            "k_test",
            "PyIndex2",
            "Updated Python knowledge base.",
            {
                "retrieval_settings": {
                    "top_k": 2,
                },
                "index_settings": {
                    "chunk_size": 512,
                },
            },
        )
    )

    assert captured["update"][3] == "rag_graph"
    merged_config = captured["update"][4]
    assert merged_config["retrieval_settings"]["default_mode"] == "rag_graph"
    assert merged_config["retrieval_settings"]["top_k"] == 2
    assert merged_config["index_settings"]["chunk_size"] == 512
    assert merged_config["index_settings"]["overlap"] == 128
    assert merged_config["index_settings"]["status"] == "active"
    assert merged_config["model_refs"]["rerank_model_id"] == "llm_rerank"


def test_knowledge_service_rejects_encoding_damaged_text(monkeypatch):
    from zuno.api.services.knowledge import KnowledgeService

    async def fake_create_knowledge(*_args, **_kwargs):
        raise AssertionError("damaged text should be rejected before database write")

    monkeypatch.setattr(
        "zuno.api.services.knowledge.KnowledgeDao.create_knowledge",
        fake_create_knowledge,
    )

    try:
        asyncio.run(
            KnowledgeService.create_knowledge(
                "??5479",
                "?????? Zuno ??????????????????",
                "u_test",
            )
        )
    except ValueError as err:
        assert "编码损坏" in str(err)
    else:
        raise AssertionError("expected encoding damage validation error")


def test_reindex_knowledge_action_endpoint_passes_knowledge_id(monkeypatch):
    from zuno.api.v1.knowledge import reindex_knowledge_action

    captured = {}

    async def fake_verify_user_permission(knowledge_id, user_id):
        captured["permission"] = (knowledge_id, user_id)

    async def fake_run_reindex_action(knowledge_id, action):
        captured["reindex"] = (knowledge_id, action)
        return {
            "knowledge_id": knowledge_id,
            "action": action,
            "status": "accepted",
        }

    monkeypatch.setattr(
        "zuno.api.v1.knowledge_file.KnowledgeService.verify_user_permission",
        fake_verify_user_permission,
    )
    monkeypatch.setattr(
        "zuno.api.v1.knowledge.KnowledgeService.run_reindex_action",
        fake_run_reindex_action,
    )

    login_user = SimpleNamespace(user_id="u_test")

    response = asyncio.run(
        reindex_knowledge_action(
            knowledge_id="k_test",
            action="full_rebuild",
            login_user=login_user,
        )
    )

    assert response.status_code == 200
    assert captured["permission"] == ("k_test", "u_test")
    assert captured["reindex"] == ("k_test", "full_rebuild")
    assert response.data["status"] == "accepted"


def test_search_knowledge_endpoint_returns_retrieval_metadata(monkeypatch):
    from zuno.api.v1.knowledge import search_knowledge
    from zuno.services.graphrag.query_service import KnowledgeQueryResult

    async def fake_verify_user_permission(knowledge_id, user_id):
        assert (knowledge_id, user_id) == ("k_test", "u_test")

    captured = {}

    async def fake_project_query(self, *, user_id, knowledge_ids, query, query_method=None, top_k=None):
        captured["query"] = {
            "user_id": user_id,
            "knowledge_ids": knowledge_ids,
            "query": query,
            "query_method": query_method,
            "top_k": top_k,
        }
        return KnowledgeQueryResult(
            graphrag_project_id="contract_review",
            answer="final-context",
            requested_query_method="auto",
            resolved_query_method="local",
            fallback_reason="too_few_documents",
            documents=[{"id": "doc-1", "score": 0.91}],
            evidence={"chunks": ["doc-1"]},
            citations=["doc-1#p1"],
            retrievers_used=["vector", "graph"],
            graph_paths=[],
            communities=[],
            prompt_version="extract-v1",
            query_prompt_version="local-v1",
            index_version={"vector": "v1"},
            community_version="v0",
            trace_metadata={
                "second_pass_used": True,
                "fallback_triggered": True,
            },
            raw_result={"content": "raw-context"},
        )

    async def fail_legacy_rag_handler(*args, **kwargs):
        raise AssertionError("legacy RagHandler search path should not be used")

    monkeypatch.setattr(
        "zuno.api.v1.knowledge.KnowledgeService.verify_user_permission",
        fake_verify_user_permission,
    )
    monkeypatch.setattr(
        "zuno.services.rag.handler.RagHandler.retrieve_ranked_documents_with_metadata",
        fail_legacy_rag_handler,
    )
    monkeypatch.setattr(
        "zuno.services.application.knowledge.KnowledgeQueryService.query",
        fake_project_query,
    )

    response = asyncio.run(
        search_knowledge(
            query="请补充知识库内容",
            knowledge_ids=["k_test"],
            top_k=5,
            login_user=SimpleNamespace(user_id="u_test"),
        )
    )

    assert response.status_code == 200
    assert response.data["content"] == "final-context"
    assert response.data["second_pass_used"] is True
    assert response.data["final_mode"] == "local"
    assert response.data["fallback_triggered"] is True
    assert response.data["fallback_reason"] == "too_few_documents"
    assert response.data["citations"] == ["doc-1#p1"]
    assert captured["query"] == {
        "user_id": "u_test",
        "knowledge_ids": ["k_test"],
        "query": "请补充知识库内容",
        "query_method": None,
        "top_k": 5,
    }
