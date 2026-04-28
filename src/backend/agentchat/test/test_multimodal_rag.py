import asyncio
from pathlib import Path


def test_doc_parser_turns_image_file_into_image_chunk(monkeypatch, tmp_path):
    from agentchat.services.rag.parser import doc_parser

    image_path = tmp_path / "demo.png"
    image_path.write_bytes(b"fake-image")

    monkeypatch.setattr(
        "agentchat.services.rag.parser.describe_image",
        lambda _path: "一张带有流程图的系统截图",
    )

    chunks = asyncio.run(
        doc_parser.parse_doc_into_chunks(
            file_id="file_1",
            file_path=str(image_path),
            knowledge_id="knowledge_1",
            source_url="https://example.com/demo.png",
        )
    )

    assert len(chunks) == 1
    assert chunks[0].modality == "image"
    assert chunks[0].source_url == "https://example.com/demo.png"
    assert "流程图" in chunks[0].content


def test_retrieval_combines_text_and_image_results(monkeypatch):
    from agentchat.services.rag.retrieval import MixRetrival
    from types import SimpleNamespace

    async def fake_search(_query, _knowledge_id):
        return []

    async def fake_search_image(query, knowledge_id):
        return [f"{knowledge_id}:{query}:image"]

    monkeypatch.setattr(
        "agentchat.services.rag.retrieval.milvus_client",
        SimpleNamespace(search=fake_search, search_image=fake_search_image, search_summary=fake_search),
    )

    results = asyncio.run(MixRetrival.retrival_milvus_documents("架构图", ["k1"], "content"))

    assert results == ["k1:架构图:image"]
