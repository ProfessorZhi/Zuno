import asyncio
import importlib
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_product_wiring_domain_pack_api_service_is_retired() -> None:
    assert not (REPO_ROOT / "src/backend/zuno/api/services/domain_pack.py").exists()
    assert "domain_pack" not in getattr(importlib.import_module("zuno.api.services"), "__all__", [])


def _config(default_mode="rag", graphrag_project_id=None, domain_pack_id=None):
    project_id = graphrag_project_id or domain_pack_id
    return {
        "index_capability": "rag_graph" if default_mode == "rag_graph" else "rag",
        "graphrag_project_id": project_id,
        "graphrag_project": (
            {
                "graphrag_project_id": project_id,
                "settings_path": "projects/contract_review/settings.yaml",
                "prompt_version": "default",
                "index_version": "v1",
                "query_method": "auto",
                "query_prompt_version": "default",
                "community_version": "v0",
                "document_hash": None,
                "chunk_hash": None,
                "status": "not_configured",
            }
            if project_id
            else None
        ),
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


def test_product_wiring_domain_pack_endpoint_module_is_retired() -> None:
    assert not (REPO_ROOT / "src/backend/zuno/api/v1/domain_packs.py").exists()
    assert "domain_packs" not in getattr(importlib.import_module("zuno.api.v1"), "__all__", [])


def test_product_wiring_knowledge_config_endpoints_delegate_to_service(monkeypatch):
    from zuno.api.v1 import knowledge

    captured = {}

    async def fake_verify(knowledge_id, user_id):
        captured.setdefault("permissions", []).append((knowledge_id, user_id))

    async def fake_get_config(knowledge_id):
        captured["get_config"] = knowledge_id
        return _config(default_mode="rag_graph", graphrag_project_id="contract_review")

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
            next_config=_config(default_mode="rag_graph", graphrag_project_id="contract_review"),
            login_user=login_user,
        )
    )

    assert get_response.status_code == 200
    assert get_response.data["retrieval_settings"]["default_mode"] == "rag_graph"
    assert put_response.status_code == 200
    assert captured["update"][0] == "kb_1"
    assert captured["update"][3]["graphrag_project_id"] == "contract_review"
    assert "domain_pack_id" not in captured["update"][3]


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
                    _config(default_mode="rag_graph", graphrag_project_id="contract_review")
                ),
            ),
            login_user=login_user,
        )
    )

    assert response.status_code == 200
    assert response.data["id"] == "kb_new"
    assert captured["create"][2] == "u_test"
    assert captured["create"][3]["graphrag_project_id"] == "contract_review"
    assert captured["create"][3]["retrieval_settings"]["default_mode"] == "rag_graph"
    assert "domain_pack_id" not in captured["create"][3]


def test_product_wiring_frontend_pages_use_real_api_contracts():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    knowledge_api = (root / "apps/web/src/apis/knowledge.ts").read_text(encoding="utf-8")
    retrieval_utils = (root / "apps/web/src/utils/retrieval.ts").read_text(encoding="utf-8")
    knowledge_config_utils = (root / "apps/web/src/utils/knowledge-config.ts").read_text(encoding="utf-8")
    create_page = (root / "apps/web/src/pages/knowledge/knowledge-create.vue").read_text(encoding="utf-8")
    settings_page = (root / "apps/web/src/pages/knowledge/knowledge-settings.vue").read_text(encoding="utf-8")

    assert not (root / "apps/web/src/apis/domain-packs.ts").exists()

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
    assert "domain_pack_id:" not in knowledge_api
    assert "domain_pack_id?:" not in knowledge_api
    assert "GraphRAGProjectPayload" in knowledge_api
    assert "graphrag_project" in knowledge_api
    assert "query_method: 'auto' | 'basic' | 'local' | 'global' | 'drift'" in knowledge_api
    assert "requested_query_method?: 'auto' | 'basic' | 'local' | 'global' | 'drift'" in knowledge_api
    assert "pipeline_trace?" in knowledge_api
    assert "citation_coverage?" in knowledge_api
    assert "graphrag_project_id" in knowledge_config_utils
    assert "domain_pack_id: config.domain_pack_id" not in knowledge_config_utils
    assert "changedQueryFields.push('domain_pack_id')" not in knowledge_config_utils
    assert "config.retrieval_settings.default_mode = 'rag_graph'" in knowledge_config_utils
    for frontend_surface in [knowledge_api, retrieval_utils, knowledge_config_utils, create_page, settings_page]:
        assert "rag_graph_deep" not in frontend_surface
        assert "local_graphrag" not in frontend_surface
        assert "community_global" not in frontend_surface
        assert "drift_like" not in frontend_surface
    assert "GraphRAG Project" in create_page
    assert "analyzeKnowledgeConfigImpactAPI" in settings_page
    assert "runKnowledgeReindexActionAPI" in settings_page
