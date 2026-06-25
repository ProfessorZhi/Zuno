import asyncio
from pathlib import Path

import pytest


def test_stackless_local_eval_exposes_project_named_payload_loader():
    from zuno.evals.rag_eval.run_stackless_local_eval import _load_graph_project_payload

    payload = _load_graph_project_payload("contract_review")

    assert payload is not None
    assert payload["id"] == "contract_review"
    assert payload["retrieval_policy_data"]["graph_hop_limit"] == 2
    schema_path = Path(payload["schema_path"])
    assert schema_path.parts[-4:] == (
        "examples",
        "graphrag-projects",
        "contract_review",
        "schema.json",
    )


def test_stackless_local_graph_retriever_uses_project_assets_without_domain_pack_loader():
    from zuno.evals.rag_eval.run_stackless_local_eval import _build_local_graph_retriever
    from zuno.schema.chunk import ChunkModel
    with pytest.raises(ModuleNotFoundError):
        __import__("zuno.services.domain_pack.loader")

    chunk = ChunkModel(
        chunk_id="contract_chunk_1",
        content=(
            "# 主服务合同\n\n"
            "甲方：星河科技有限公司\n"
            "乙方：云川数据服务有限公司\n\n"
            "第二条 数据安全\n"
            "发生数据泄露时，乙方应在24小时内通知甲方，并依据《中华人民共和国个人信息保护法》配合处置。"
        ),
        file_id="file_contract_1",
        file_name="contract_001_master_service_agreement.md",
        update_time="2026-06-08T00:00:00",
        knowledge_id="kb_contract",
        summary="数据安全条款",
    )

    retriever = asyncio.run(
        _build_local_graph_retriever(
            [chunk],
            graphrag_project_id="contract_review",
        )
    )

    extracted_documents = retriever.client.extracted_documents
    assert extracted_documents

    relation_types = {
        relation["relation_type"]
        for relation in extracted_documents[0]["relations"]
        if relation.get("relation_type")
    }
    entity_pairs = {
        (entity["name"], entity["type"])
        for entity in extracted_documents[0]["entities"]
        if entity.get("name") and entity.get("type")
    }

    assert "CLAUSE_REFERENCES_REGULATION" in relation_types
    assert ("《中华人民共和国个人信息保护法》", "Regulation") in entity_pairs
