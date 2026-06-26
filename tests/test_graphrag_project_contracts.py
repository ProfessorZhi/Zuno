from pydantic import ValidationError


def test_graphrag_project_contract_has_explicit_defaults():
    from zuno.services.graphrag.models import GraphRAGProjectContract

    contract = GraphRAGProjectContract(graphrag_project_id="contract_review")
    payload = contract.model_dump()

    assert payload == {
        "graphrag_project_id": "contract_review",
        "settings_path": None,
        "prompt_version": "default",
        "index_version": "v1",
        "query_method": "auto",
        "query_prompt_version": "default",
        "community_version": "v0",
        "document_hash": None,
        "chunk_hash": None,
        "status": "not_configured",
    }


def test_graphrag_project_contract_validates_target_enums():
    from zuno.services.graphrag.models import GraphRAGProjectContract

    contract = GraphRAGProjectContract(
        graphrag_project_id="legal",
        settings_path="projects/legal/settings.yaml",
        prompt_version="extract-v2",
        index_version="idx-v7",
        query_method="drift",
        query_prompt_version="query-v3",
        community_version="community-v2",
        document_hash="doc-sha",
        chunk_hash="chunk-sha",
        status="ready",
    )

    assert contract.query_method == "drift"
    assert contract.status == "ready"

    try:
        GraphRAGProjectContract(graphrag_project_id="legal", query_method="community_global")
    except ValidationError as err:
        assert "query_method" in str(err)
    else:
        raise AssertionError("expected legacy query method to be rejected")


def test_knowledge_config_embeds_graphrag_project_contract_and_normalizes_identity():
    from zuno.api.services.knowledge import KnowledgeService
    from zuno.schema.knowledge import KnowledgeConfig

    config = KnowledgeConfig.model_validate(
        {
            "graphrag_project_id": "legal",
            "graphrag_project": {
                "graphrag_project_id": "legacy",
                "settings_path": "projects/legal/settings.yaml",
                "prompt_version": "extract-v2",
                "query_method": "local",
                "query_prompt_version": "query-v1",
                "status": "ready",
            },
            "retrieval_settings": {"default_mode": "rag_graph"},
        }
    ).model_dump()

    normalized = KnowledgeService._normalize_knowledge_config(config)

    assert normalized["graphrag_project_id"] == "legal"
    assert "domain_pack_id" not in normalized
    assert normalized["graphrag_project"]["graphrag_project_id"] == "legal"
    assert normalized["graphrag_project"]["settings_path"] == "projects/legal/settings.yaml"
    assert normalized["graphrag_project"]["prompt_version"] == "extract-v2"
    assert normalized["graphrag_project"]["query_method"] == "local"
    assert normalized["graphrag_project"]["query_prompt_version"] == "query-v1"
    assert normalized["graphrag_project"]["index_version"] == "v1"
    assert normalized["graphrag_project"]["community_version"] == "v0"
    assert normalized["graphrag_project"]["document_hash"] is None
    assert normalized["graphrag_project"]["chunk_hash"] is None
    assert normalized["graphrag_project"]["status"] == "ready"


def test_retrieval_contracts_can_carry_graphrag_project_metadata():
    from zuno.services.retrieval.models import RetrievalPlan, RetrievalRequest

    project = {
        "graphrag_project_id": "legal",
        "prompt_version": "extract-v2",
        "index_version": "idx-v7",
        "query_method": "global",
        "query_prompt_version": "query-v3",
        "community_version": "community-v2",
        "document_hash": "doc-sha",
        "chunk_hash": "chunk-sha",
        "status": "ready",
    }
    request = RetrievalRequest(query="q", knowledge_ids=["kb"], graphrag_project=project)
    plan = RetrievalPlan(
        requested_mode="rag_graph",
        resolved_mode="rag_graph",
        internal_route="enhanced",
        route_trace={},
        requested_profile="auto",
        resolved_profile="auto",
        enabled_retrievers=["vector", "graph"],
        retriever_configs={},
        fusion_policy={},
        rerank_policy={},
        budget_policy={},
        fallback_policy={},
        trace_policy={},
        scope_policy={},
        index_version={},
        index_health={},
        graphrag_project=project,
    )

    assert request.graphrag_project["graphrag_project_id"] == "legal"
    assert plan.to_dict()["graphrag_project"] == project
