import asyncio
import importlib
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICE_API_ROOT = REPO_ROOT / "src" / "backend"
BACKEND_ROOT = REPO_ROOT / "src" / "backend"


def _ensure_runtime_paths() -> None:
    for runtime_root in (str(BACKEND_ROOT),):
        if runtime_root not in sys.path:
            sys.path.insert(0, runtime_root)


def _contract_review_query_policy() -> dict:
    _ensure_runtime_paths()

    GraphRAGProjectLoader = importlib.import_module("zuno.services.graphrag.project.loader").GraphRAGProjectLoader
    projects_root = Path(__file__).resolve().parents[2] / "examples" / "graphrag-projects"
    project = GraphRAGProjectLoader(projects_root=projects_root).load("contract_review")
    return dict(project.settings["retrieval_policy"])


def _contract_review_project_payload() -> dict:
    _ensure_runtime_paths()

    GraphRAGProjectLoader = importlib.import_module("zuno.services.graphrag.project.loader").GraphRAGProjectLoader
    projects_root = Path(__file__).resolve().parents[2] / "examples" / "graphrag-projects"
    project = GraphRAGProjectLoader(projects_root=projects_root).load("contract_review")
    assert project is not None
    return project.to_project_payload()


def test_contract_review_project_payload_matches_legacy_shape():
    payload = _contract_review_project_payload()

    assert payload["id"] == "contract_review"
    assert payload["schema"] == "schema.json"
    assert payload["retrieval_policy_data"]["graph_hop_limit"] == 2
    assert "结论" in (payload["answer_template_text"] or "")
    assert payload["schema_data"] is not None


def test_structured_graph_extractor_builds_contract_review_entities_and_relations():
    _ensure_runtime_paths()

    StructuredGraphExtractor = importlib.import_module(
        "zuno.services.graphrag.extractors.structured_extractor"
    ).StructuredGraphExtractor

    project_payload = _contract_review_project_payload()

    chunk = {
        "chunk_id": "contract_chunk_1",
        "file_name": "master_service_agreement.md",
        "content": (
            "# 主服务合同\n"
            "甲方：星河科技有限公司\n"
            "乙方：云川数据服务有限公司\n"
            "第一条 服务范围\n"
            "乙方应按照项目计划向甲方提供数据平台实施服务，并在上线前完成交付。\n"
            "第二条 保密与数据安全\n"
            "双方应对在履约过程中知悉的商业秘密严格保密。"
            "发生数据泄露时，乙方应在24小时内通知甲方，"
            "并依据《中华人民共和国个人信息保护法》配合处置。\n"
            "第三条 付款安排\n"
            "甲方应在收到合格发票后10个工作日内支付人民币120万元。\n"
            "第四条 违约责任\n"
            "任一方违约的，应承担违约责任并赔偿守约方损失。"
        ),
    }

    result = asyncio.run(
        StructuredGraphExtractor().extract_from_chunk(
            chunk,
            "kb_contract",
            project_payload=project_payload,
        )
    )

    entity_pairs = {(item["name"], item["type"]) for item in result["entities"]}
    relation_pairs = {(item["source"], item["target"], item["relation_type"]) for item in result["relations"]}

    assert ("主服务合同", "Contract") in entity_pairs
    assert ("星河科技有限公司", "Party") in entity_pairs
    assert ("云川数据服务有限公司", "Party") in entity_pairs
    assert ("第一条 服务范围", "Clause") in entity_pairs
    assert ("第二条 保密与数据安全", "Clause") in entity_pairs
    assert ("付款义务", "Obligation") in entity_pairs
    assert ("保密义务", "Obligation") in entity_pairs
    assert ("24小时", "Term") in entity_pairs
    assert ("人民币120万元", "Amount") in entity_pairs
    assert ("《中华人民共和国个人信息保护法》", "Regulation") in entity_pairs
    assert ("违约责任", "Risk") in entity_pairs
    assert ("数据泄露风险", "Risk") in entity_pairs

    assert ("星河科技有限公司", "主服务合同", "PARTY_SIGNS_CONTRACT") in relation_pairs
    assert ("主服务合同", "第二条 保密与数据安全", "CONTRACT_HAS_CLAUSE") in relation_pairs
    assert ("第二条 保密与数据安全", "保密义务", "CLAUSE_HAS_OBLIGATION") in relation_pairs
    assert (
        "第二条 保密与数据安全",
        "《中华人民共和国个人信息保护法》",
        "CLAUSE_REFERENCES_REGULATION",
    ) in relation_pairs
    assert ("第四条 违约责任", "违约责任", "CLAUSE_HAS_RISK") in relation_pairs
    assert all(item.get("graphrag_project_id") == "contract_review" for item in result["entities"])
    assert all("domain_pack_id" not in item for item in result["entities"])
    assert all(item.get("graphrag_project_id") == "contract_review" for item in result["relations"])
    assert all("domain_pack_id" not in item for item in result["relations"])


def test_structured_graph_extractor_recovers_contract_title_from_file_name():
    _ensure_runtime_paths()

    StructuredGraphExtractor = importlib.import_module(
        "zuno.services.graphrag.extractors.structured_extractor"
    ).StructuredGraphExtractor

    project_payload = _contract_review_project_payload()
    chunk = {
        "chunk_id": "contract_chunk_2",
        "file_name": "contract_008_outsourcing_service_agreement__variant_2.md",
        "content": (
            "第三条 安全事件与协助\n"
            "发生高危安全事件后，乙方应在1小时内启动应急响应，"
            "在4小时内提交初步事件报告，并配合甲方完成"
            "取证、隔离和修复。"
        ),
    }

    result = asyncio.run(
        StructuredGraphExtractor().extract_from_chunk(
            chunk,
            "kb_contract",
            project_payload=project_payload,
        )
    )

    entity_pairs = {(item["name"], item["type"]) for item in result["entities"]}
    relation_pairs = {(item["source"], item["target"], item["relation_type"]) for item in result["relations"]}

    assert ("外包运维服务合同", "Contract") in entity_pairs
    assert (
        "外包运维服务合同",
        "第三条 安全事件与协助",
        "CONTRACT_HAS_CLAUSE",
    ) in relation_pairs


def test_graph_retriever_handles_contract_review_chinese_query():
    _ensure_runtime_paths()

    GraphRetriever = importlib.import_module("zuno.services.graphrag.retriever").GraphRetriever

    class FakeClient:
        async def query_neighbors(
            self,
            entity_name,
            knowledge_id,
            hops=1,
            limit=10,
            domain_pack_id=None,
            index_version=None,
            status=None,
        ):
            if entity_name != "违约责任":
                return []
            return [
                {
                    "source": "第八条 违约责任",
                    "target": "违约责任",
                    "chunk_ids": ["contract_chunk_1"],
                }
            ]

    class FakeChunkStore:
        async def get_documents_by_chunk_ids(self, collection_name, chunk_ids):
            return [
                {
                    "chunk_id": "contract_chunk_1",
                    "file_name": "loan_contract_001.md",
                    "content": "第八条 违约责任：借款人未按约定期限还款的，应承担违约责任。",
                    "summary": "",
                }
            ]

    result = asyncio.run(
        GraphRetriever(client=FakeClient(), chunk_store=FakeChunkStore()).retrieve(
            "这份合同是否约定了违约责任？",
            "k_contract",
            graph_hop_limit=2,
            max_paths_per_entity=5,
            domain_pack_id="contract_review",
            query_policy=_contract_review_query_policy(),
        )
    )

    assert result["paths"] == ["第八条 违约责任 -> 违约责任"]
    assert result["structured_paths"][0]["source"] == "第八条 违约责任"
    assert result["documents"][0]["chunk_id"] == "contract_chunk_1"
