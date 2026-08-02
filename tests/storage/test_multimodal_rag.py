import asyncio


def test_parse_gateway_turns_image_input_into_canonical_ocr_ir():
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    result = ParseGateway.parse_document(
        ParseDocumentRequest(
            document_id="image_doc_1",
            workspace_id="workspace_1",
            source_uri="file://demo.png",
            mime_type="image/png",
            source_text="an image containing a system flow chart",
        )
    )

    assert result.status == "succeeded"
    assert result.document is not None
    assert result.document.blocks[0].type == "ocr_text"
    assert result.document.figures[0].uri == "file://demo.png"
    assert "flow chart" in result.document.blocks[0].text


def test_retrieval_combines_text_and_image_results(monkeypatch):
    from types import SimpleNamespace

    from zuno.platform.services.rag.retrieval import MixRetrival

    async def fake_search(_query, _knowledge_id, top_k=10, config_override=None):
        return []

    async def fake_search_image(query, knowledge_id, top_k=10, config_override=None):
        return [f"{knowledge_id}:{query}:image"]

    monkeypatch.setattr(
        "zuno.platform.services.rag.retrieval.milvus_client",
        SimpleNamespace(search=fake_search, search_image=fake_search_image, search_summary=fake_search),
    )

    results = asyncio.run(MixRetrival.retrival_milvus_documents("architecture", ["k1"], "content"))

    assert results == ["k1:architecture:image"]
