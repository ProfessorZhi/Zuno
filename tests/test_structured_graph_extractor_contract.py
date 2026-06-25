import asyncio
from pathlib import Path


PROJECTS_ROOT = Path(__file__).resolve().parents[1] / "examples" / "graphrag-projects"


def _contract_review_project_payload():
    from zuno.services.graphrag.project.loader import GraphRAGProjectLoader

    project = GraphRAGProjectLoader(projects_root=PROJECTS_ROOT).load("contract_review")
    assert project is not None
    return project.to_project_payload()


def test_structured_graph_extractor_accepts_project_payload_as_primary_contract():
    from zuno.services.graphrag.extractors.structured_extractor import StructuredGraphExtractor

    project_payload = _contract_review_project_payload()
    chunk = {
        "chunk_id": "contract_project_payload",
        "file_name": "loan_contract_001.md",
        "content": "# 借款合同\n\n第八条 违约责任：借款人未按约定期限还款的，应承担违约责任。\n",
    }

    result = asyncio.run(
        StructuredGraphExtractor().extract_from_chunk(
            chunk,
            "kb_contract",
            project_payload=project_payload,
        )
    )

    entity_pairs = {(item["name"], item["type"]) for item in result["entities"]}
    assert ("借款合同", "Contract") in entity_pairs
    assert ("第八条 违约责任", "Clause") in entity_pairs
    assert ("违约责任", "Risk") in entity_pairs


def test_cached_graph_extractor_accepts_project_payload_as_primary_contract():
    from zuno.services.graphrag.extractors.cached_extractor import CachedGraphExtractor

    project_payload = _contract_review_project_payload()
    chunk = {
        "chunk_id": "cached_contract_project_payload",
        "file_name": "loan_contract_001.md",
        "content": "# 借款合同\n\n第八条 违约责任：借款人未按约定期限还款的，应承担违约责任。\n",
    }

    result = asyncio.run(
        CachedGraphExtractor().extract_from_chunk(
            chunk,
            "kb_contract",
            project_payload=project_payload,
        )
    )

    assert any(item["type"] == "Risk" for item in result["entities"])


def test_structured_graph_extractor_builds_contract_entities_and_relations():
    from zuno.services.graphrag.extractors.structured_extractor import StructuredGraphExtractor

    project_payload = _contract_review_project_payload()

    chunk = {
        "chunk_id": "contract_chunk_1",
        "file_name": "master_service_agreement.md",
        "content": (
            "# \u4e3b\u670d\u52a1\u5408\u540c\n"
            "\u7532\u65b9\uff1a\u661f\u6cb3\u79d1\u6280\u6709\u9650\u516c\u53f8\n"
            "\u4e59\u65b9\uff1a\u4e91\u5ddd\u6570\u636e\u670d\u52a1\u6709\u9650\u516c\u53f8\n"
            "\u7b2c\u4e00\u6761 \u670d\u52a1\u8303\u56f4\n"
            "\u4e59\u65b9\u5e94\u6309\u7167\u9879\u76ee\u8ba1\u5212\u5411\u7532\u65b9\u63d0\u4f9b\u6570\u636e\u5e73\u53f0\u5b9e\u65bd\u670d\u52a1\uff0c\u5e76\u5728\u4e0a\u7ebf\u524d\u5b8c\u6210\u4ea4\u4ed8\u3002\n"
            "\u7b2c\u4e8c\u6761 \u4fdd\u5bc6\u4e0e\u6570\u636e\u5b89\u5168\n"
            "\u53cc\u65b9\u5e94\u5bf9\u5728\u5c65\u7ea6\u8fc7\u7a0b\u4e2d\u77e5\u6089\u7684\u5546\u4e1a\u79d8\u5bc6\u4e25\u683c\u4fdd\u5bc6\u3002"
            "\u53d1\u751f\u6570\u636e\u6cc4\u9732\u65f6\uff0c\u4e59\u65b9\u5e94\u572824\u5c0f\u65f6\u5185\u901a\u77e5\u7532\u65b9\uff0c"
            "\u5e76\u4f9d\u636e\u300a\u4e2d\u534e\u4eba\u6c11\u5171\u548c\u56fd\u4e2a\u4eba\u4fe1\u606f\u4fdd\u62a4\u6cd5\u300b\u914d\u5408\u5904\u7f6e\u3002\n"
            "\u7b2c\u4e09\u6761 \u4ed8\u6b3e\u5b89\u6392\n"
            "\u7532\u65b9\u5e94\u5728\u6536\u5230\u5408\u683c\u53d1\u7968\u540e10\u4e2a\u5de5\u4f5c\u65e5\u5185\u652f\u4ed8\u4eba\u6c11\u5e01120\u4e07\u5143\u3002\n"
            "\u7b2c\u56db\u6761 \u8fdd\u7ea6\u8d23\u4efb\n"
            "\u4efb\u4e00\u65b9\u8fdd\u7ea6\u7684\uff0c\u5e94\u627f\u62c5\u8fdd\u7ea6\u8d23\u4efb\u5e76\u8d54\u507f\u5b88\u7ea6\u65b9\u635f\u5931\u3002"
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

    assert ("\u4e3b\u670d\u52a1\u5408\u540c", "Contract") in entity_pairs
    assert ("\u661f\u6cb3\u79d1\u6280\u6709\u9650\u516c\u53f8", "Party") in entity_pairs
    assert ("\u4e91\u5ddd\u6570\u636e\u670d\u52a1\u6709\u9650\u516c\u53f8", "Party") in entity_pairs
    assert ("\u7b2c\u4e00\u6761 \u670d\u52a1\u8303\u56f4", "Clause") in entity_pairs
    assert ("\u7b2c\u4e8c\u6761 \u4fdd\u5bc6\u4e0e\u6570\u636e\u5b89\u5168", "Clause") in entity_pairs
    assert ("\u4ed8\u6b3e\u4e49\u52a1", "Obligation") in entity_pairs
    assert ("\u4fdd\u5bc6\u4e49\u52a1", "Obligation") in entity_pairs
    assert ("24\u5c0f\u65f6", "Term") in entity_pairs
    assert ("\u4eba\u6c11\u5e01120\u4e07\u5143", "Amount") in entity_pairs
    assert ("\u300a\u4e2d\u534e\u4eba\u6c11\u5171\u548c\u56fd\u4e2a\u4eba\u4fe1\u606f\u4fdd\u62a4\u6cd5\u300b", "Regulation") in entity_pairs
    assert ("\u8fdd\u7ea6\u8d23\u4efb", "Risk") in entity_pairs
    assert ("\u6570\u636e\u6cc4\u9732\u98ce\u9669", "Risk") in entity_pairs

    assert ("\u661f\u6cb3\u79d1\u6280\u6709\u9650\u516c\u53f8", "\u4e3b\u670d\u52a1\u5408\u540c", "PARTY_SIGNS_CONTRACT") in relation_pairs
    assert ("\u4e3b\u670d\u52a1\u5408\u540c", "\u7b2c\u4e8c\u6761 \u4fdd\u5bc6\u4e0e\u6570\u636e\u5b89\u5168", "CONTRACT_HAS_CLAUSE") in relation_pairs
    assert ("\u7b2c\u4e8c\u6761 \u4fdd\u5bc6\u4e0e\u6570\u636e\u5b89\u5168", "\u4fdd\u5bc6\u4e49\u52a1", "CLAUSE_HAS_OBLIGATION") in relation_pairs
    assert (
        "\u7b2c\u4e8c\u6761 \u4fdd\u5bc6\u4e0e\u6570\u636e\u5b89\u5168",
        "\u300a\u4e2d\u534e\u4eba\u6c11\u5171\u548c\u56fd\u4e2a\u4eba\u4fe1\u606f\u4fdd\u62a4\u6cd5\u300b",
        "CLAUSE_REFERENCES_REGULATION",
    ) in relation_pairs
    assert ("\u7b2c\u56db\u6761 \u8fdd\u7ea6\u8d23\u4efb", "\u8fdd\u7ea6\u8d23\u4efb", "CLAUSE_HAS_RISK") in relation_pairs


def test_structured_graph_extractor_recovers_contract_title_from_file_name():
    from zuno.services.graphrag.extractors.structured_extractor import StructuredGraphExtractor

    project_payload = _contract_review_project_payload()
    chunk = {
        "chunk_id": "contract_chunk_2",
        "file_name": "contract_008_outsourcing_service_agreement__variant_2.md",
        "content": (
            "\u7b2c\u4e09\u6761 \u5b89\u5168\u4e8b\u4ef6\u4e0e\u534f\u52a9\n"
            "\u53d1\u751f\u9ad8\u5371\u5b89\u5168\u4e8b\u4ef6\u540e\uff0c\u4e59\u65b9\u5e94\u57281\u5c0f\u65f6\u5185\u542f\u52a8\u5e94\u6025\u54cd\u5e94\uff0c"
            "\u57284\u5c0f\u65f6\u5185\u63d0\u4ea4\u521d\u6b65\u4e8b\u4ef6\u62a5\u544a\uff0c\u5e76\u914d\u5408\u7532\u65b9\u5b8c\u6210"
            "\u53d6\u8bc1\u3001\u9694\u79bb\u548c\u4fee\u590d\u3002"
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

    assert ("\u5916\u5305\u8fd0\u7ef4\u670d\u52a1\u5408\u540c", "Contract") in entity_pairs
    assert (
        "\u5916\u5305\u8fd0\u7ef4\u670d\u52a1\u5408\u540c",
        "\u7b2c\u4e09\u6761 \u5b89\u5168\u4e8b\u4ef6\u4e0e\u534f\u52a9",
        "CONTRACT_HAS_CLAUSE",
    ) in relation_pairs


def test_structured_graph_extractor_supports_inline_clause_body_format():
    from zuno.services.graphrag.extractors.structured_extractor import StructuredGraphExtractor

    project_payload = _contract_review_project_payload()
    chunk = {
        "chunk_id": "contract_chunk_inline",
        "file_name": "loan_contract_001.md",
        "content": "# 借款合同\n\n第八条 违约责任：借款人未按约定期限还款的，应承担违约责任。\n",
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

    assert ("第八条 违约责任", "Clause") in entity_pairs
    assert ("违约责任", "Risk") in entity_pairs
    assert ("借款合同", "第八条 违约责任", "CONTRACT_HAS_CLAUSE") in relation_pairs
    assert ("第八条 违约责任", "违约责任", "CLAUSE_HAS_RISK") in relation_pairs
