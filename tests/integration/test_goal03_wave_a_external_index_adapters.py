from __future__ import annotations

import socket
import urllib.request
from uuid import uuid4

import pytest


def _sample_document():
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    result = ParseGateway.parse_document(
        ParseDocumentRequest(
            document_id=f"doc_neo4j_{uuid4().hex[:8]}",
            workspace_id="workspace_external_index",
            source_uri="file://contracts/neo4j-index.md",
            mime_type="text/markdown",
            source_text="# Neo4j Graph Evidence\nSupplier renewal graph visibility is externally verified.",
            sensitivity_tags=["internal"],
        )
    )
    assert result.document is not None
    return result.document


def _neo4j_available() -> bool:
    try:
        with socket.create_connection(("localhost", 7687), timeout=2):
            return True
    except OSError:
        return False


def _elasticsearch_available() -> bool:
    try:
        with urllib.request.urlopen("http://localhost:9200/_cluster/health", timeout=3) as response:
            return response.status == 200
    except OSError:
        return False


@pytest.mark.skipif(
    not _elasticsearch_available(),
    reason="Elasticsearch integration service is not available on localhost:9200",
)
def test_phase12_elasticsearch_bm25_adapter_requires_real_service_readback() -> None:
    from zuno.knowledge.indexing import ElasticsearchBm25IndexClient, KnowledgeIndexRuntime, external_adapter_bindings

    document = _sample_document()
    runtime = KnowledgeIndexRuntime(
        adapter_bindings=external_adapter_bindings(
            elasticsearch_client=ElasticsearchBm25IndexClient(base_url="http://localhost:9200"),
            index_prefix=f"goal03_{uuid4().hex[:8]}",
        )
    )
    runtime.create_knowledge_space("ks_es_external", "workspace_external_index")

    manifest = runtime.index_document(
        "ks_es_external",
        document,
        targets=["bm25"],
    )
    payload = runtime.to_retrieval_payload("ks_es_external", "supplier renewal graph visibility")

    assert manifest.adapter_status == {"bm25": "elasticsearch:current"}
    assert manifest.adapter_dispatch_receipts["bm25"]["adapter_id"] == "elasticsearch"
    assert manifest.adapter_visibility_receipts["bm25"]["visibility"] == "visible"
    assert manifest.adapter_visibility_receipts["bm25"]["sample_match_count"] > 0
    assert manifest.target_status["bm25"] == "ready"
    assert payload["retrievers_used"] == ["bm25"]
    assert payload["documents_by_source"]["bm25"]


@pytest.mark.skipif(not _neo4j_available(), reason="Neo4j integration service is not available on localhost:7687")
def test_phase12_neo4j_graph_adapter_requires_real_service_readback() -> None:
    from zuno.knowledge.indexing import KnowledgeIndexRuntime, Neo4jGraphIndexClient, external_adapter_bindings

    document = _sample_document()
    runtime = KnowledgeIndexRuntime(
        adapter_bindings=external_adapter_bindings(
            neo4j_client=Neo4jGraphIndexClient(
                uri="bolt://localhost:7687",
                username="neo4j",
                password="neo4j12345",
            ),
            index_prefix=f"goal03_{uuid4().hex[:8]}",
        )
    )
    runtime.create_knowledge_space("ks_neo4j_external", "workspace_external_index")

    manifest = runtime.index_document(
        "ks_neo4j_external",
        document,
        targets=["graph"],
    )
    payload = runtime.to_retrieval_payload("ks_neo4j_external", "supplier renewal graph visibility")

    assert manifest.adapter_status == {"graph": "neo4j:current"}
    assert manifest.adapter_dispatch_receipts["graph"]["adapter_id"] == "neo4j"
    assert manifest.adapter_visibility_receipts["graph"]["visibility"] == "visible"
    assert manifest.adapter_visibility_receipts["graph"]["sample_match_count"] > 0
    assert manifest.target_status["graph"] == "ready"
    assert payload["retrievers_used"] == ["graph"]
    assert payload["documents_by_source"]["graph"]
