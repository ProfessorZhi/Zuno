import asyncio
from types import SimpleNamespace


def test_product_wiring_domain_pack_update_preserves_existing_assets(monkeypatch, tmp_path):
    from zuno.api.services import domain_pack

    class FakeLoader:
        def __init__(self):
            self.packs_root = tmp_path

    monkeypatch.setattr(domain_pack, "DomainPackLoader", FakeLoader)

    draft = asyncio.run(
        domain_pack.DomainPackService.create_draft(
            {
                "pack_id": "legal_v1",
                "name": "Legal",
                "schema_data": {"entities": ["Clause"], "relations": ["TRIGGERS"]},
                "extraction_prompt_text": "Keep this extraction prompt.",
                "retrieval_policy_data": {"graph_hop_limit": 3},
            }
        )
    )
    updated = asyncio.run(
        domain_pack.DomainPackService.update_domain_pack(
            draft["pack_id"],
            {"description": "metadata only"},
        )
    )
    detail = asyncio.run(domain_pack.DomainPackService.get_domain_pack(draft["pack_id"]))

    assert updated["description"] == "metadata only"
    assert detail["schema_data"]["entities"] == ["Clause"]
    assert detail["retrieval_policy_data"]["graph_hop_limit"] == 3
    assert detail["extraction_prompt_text"] == "Keep this extraction prompt."


def _config(default_mode="rag", domain_pack_id=None):
    return {
        "index_capability": "rag_graph" if default_mode == "rag_graph_deep" else "rag",
        "graphrag_project_id": domain_pack_id,
        "domain_pack_id": domain_pack_id,
        "eval_profile_id": None,
        "model_refs": {
            "text_embedding_model_id": "embed_text",
            "vl_embedding_model_id": "embed_vl",
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
        },
        "graph_index_settings": {
            "entity_extraction_mode": "rule_llm",
            "relation_schema": "open",
            "entity_normalization": True,
            "evidence_backlink": True,
            "use_rag_entry_chunk": True,
            "community_report_prompt_id": "community-default",
            "index_version": "v1",
            "health_status": "ready",
            "graph_index_status": "ready",
            "community_detection_status": "ready",
            "community_report_status": "stale",
            "community_version": "v0",
        },
        "retrieval_settings": {
            "default_mode": default_mode,
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


def test_product_wiring_domain_pack_endpoints_delegate_to_service(monkeypatch):
    from zuno.api.v1 import domain_packs

    captured = {}

    async def fake_get(pack_id):
        captured["get"] = pack_id
        return {"pack_id": pack_id, "name": "contract review", "status": "published"}

    async def fake_draft(payload):
        captured["draft"] = payload
        return {"pack_id": payload["pack_id"], "status": "draft"}

    async def fake_from_knowledge(payload):
        captured["from_knowledge"] = payload
        return {"pack_id": payload["pack_id"], "source_knowledge_id": payload["knowledge_id"], "status": "draft"}

    async def fake_update(pack_id, payload):
        captured["update"] = (pack_id, payload)
        return {"pack_id": pack_id, "status": "draft"}

    monkeypatch.setattr(domain_packs.DomainPackService, "get_domain_pack", fake_get)
    monkeypatch.setattr(domain_packs.DomainPackService, "create_draft", fake_draft)
    monkeypatch.setattr(domain_packs.DomainPackService, "create_draft_from_knowledge", fake_from_knowledge)
    monkeypatch.setattr(domain_packs.DomainPackService, "update_domain_pack", fake_update)

    detail = asyncio.run(domain_packs.get_domain_pack(pack_id="contract_review"))
    draft = asyncio.run(domain_packs.create_domain_pack_draft(payload={"pack_id": "legal_v1", "name": "法务"}))
    from_knowledge = asyncio.run(
        domain_packs.create_domain_pack_draft_from_knowledge(
            payload={"pack_id": "legal_from_kb", "knowledge_id": "kb_1", "file_ids": ["f1"]}
        )
    )
    update = asyncio.run(domain_packs.update_domain_pack(pack_id="legal_v1", payload={"description": "updated"}))

    assert detail.status_code == 200
    assert detail.data["pack_id"] == "contract_review"
    assert draft.data["status"] == "draft"
    assert from_knowledge.data["source_knowledge_id"] == "kb_1"
    assert update.data["pack_id"] == "legal_v1"
    assert captured["update"] == ("legal_v1", {"description": "updated"})


def test_product_wiring_knowledge_config_endpoints_delegate_to_service(monkeypatch):
    from zuno.api.v1 import knowledge

    captured = {}

    async def fake_verify(knowledge_id, user_id):
        captured.setdefault("permissions", []).append((knowledge_id, user_id))

    async def fake_get_config(knowledge_id):
        captured["get_config"] = knowledge_id
        return _config(default_mode="rag_graph_deep", domain_pack_id="contract_review")

    async def fake_update(knowledge_id, knowledge_name, knowledge_desc, knowledge_config=None):
        captured["update"] = (knowledge_id, knowledge_name, knowledge_desc, knowledge_config)

    monkeypatch.setattr(knowledge.KnowledgeService, "verify_user_permission", fake_verify)
    monkeypatch.setattr(knowledge.KnowledgeService, "get_knowledge_config", fake_get_config)
    monkeypatch.setattr(knowledge.KnowledgeService, "update_knowledge", fake_update)

    login_user = SimpleNamespace(user_id="u_test")
    get_response = asyncio.run(
        knowledge.get_knowledge_config(knowledge_id="kb_1", login_user=login_user)
    )
    put_response = asyncio.run(
        knowledge.update_knowledge_config(
            knowledge_id="kb_1",
            next_config=_config(default_mode="rag_graph_deep", domain_pack_id="contract_review"),
            login_user=login_user,
        )
    )

    assert get_response.status_code == 200
    assert get_response.data["retrieval_settings"]["default_mode"] == "rag_graph_deep"
    assert put_response.status_code == 200
    assert captured["update"][0] == "kb_1"
    assert captured["update"][3]["graphrag_project_id"] == "contract_review"
    assert captured["update"][3]["domain_pack_id"] == "contract_review"


def test_product_wiring_knowledge_create_returns_created_knowledge_with_config(monkeypatch):
    from zuno.api.v1 import knowledge
    from zuno.schema.knowledge import KnowledgeConfig, KnowledgeCreateRequest

    captured = {}

    async def fake_create(knowledge_name, knowledge_desc, user_id, knowledge_config=None):
        captured["create"] = (knowledge_name, knowledge_desc, user_id, knowledge_config)
        return {
            "id": "kb_new",
            "name": knowledge_name,
            "description": knowledge_desc,
            "knowledge_config": knowledge_config,
        }

    monkeypatch.setattr(knowledge.KnowledgeService, "create_knowledge", fake_create)

    login_user = SimpleNamespace(user_id="u_test")
    response = asyncio.run(
        knowledge.upload_knowledge(
            knowledge_req=KnowledgeCreateRequest(
                knowledge_name="产品知识库",
                knowledge_desc="用于 Product Wiring V1 的测试知识库",
                knowledge_config=KnowledgeConfig.model_validate(
                    _config(default_mode="rag_graph_deep", domain_pack_id="contract_review")
                ),
            ),
            login_user=login_user,
        )
    )

    assert response.status_code == 200
    assert response.data["id"] == "kb_new"
    assert captured["create"][2] == "u_test"
    assert captured["create"][3]["graphrag_project_id"] == "contract_review"
    assert captured["create"][3]["retrieval_settings"]["default_mode"] == "rag_graph_deep"
    assert captured["create"][3]["domain_pack_id"] == "contract_review"


def test_product_wiring_frontend_pages_use_real_api_contracts():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    domain_api = (root / "apps/web/src/apis/domain-packs.ts").read_text(encoding="utf-8")
    knowledge_api = (root / "apps/web/src/apis/knowledge.ts").read_text(encoding="utf-8")
    create_page = (root / "apps/web/src/pages/knowledge/knowledge-create.vue").read_text(encoding="utf-8")
    settings_page = (root / "apps/web/src/pages/knowledge/knowledge-settings.vue").read_text(encoding="utf-8")

    for phrase in [
        "getDomainPackDetailAPI",
        "createDomainPackDraftAPI",
        "createDomainPackDraftFromKnowledgeAPI",
        "updateDomainPackAPI",
        "publishDomainPackAPI",
    ]:
        assert phrase in domain_api

    for phrase in [
        "getKnowledgeConfigAPI",
        "updateKnowledgeConfigAPI",
        "analyzeKnowledgeConfigImpactAPI",
        "runKnowledgeReindexActionAPI",
    ]:
        assert phrase in knowledge_api

    assert "createKnowledgeAPI" in create_page
    assert "toProductKnowledgeConfig" in create_page
    assert "workspaceSettingsKnowledgeFile" in create_page
    assert "graphrag_project_id" in knowledge_api
    assert "graphrag_project_id" in (root / "apps/web/src/utils/knowledge-config.ts").read_text(encoding="utf-8")
    assert "rag_graph_deep" not in create_page
    assert "rag_graph_deep" not in settings_page
    assert "analyzeKnowledgeConfigImpactAPI" in settings_page
    assert "runKnowledgeReindexActionAPI" in settings_page
