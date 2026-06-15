import asyncio
import tempfile
from pathlib import Path


def test_doc_parser_turns_image_file_into_image_chunk(monkeypatch):
    from zuno.services.rag.parser import doc_parser

    with tempfile.TemporaryDirectory(dir=Path.cwd()) as temp_dir:
        image_path = Path(temp_dir) / "demo.png"
        image_path.write_bytes(b"fake-image")

        monkeypatch.setattr(
            "zuno.services.rag.parser.describe_image",
            lambda _path: "an image containing a system flow chart",
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
        assert "flow chart" in chunks[0].content


def test_retrieval_combines_text_and_image_results(monkeypatch):
    from types import SimpleNamespace

    from zuno.services.rag.retrieval import MixRetrival

    async def fake_search(_query, _knowledge_id, top_k=10, config_override=None):
        return []

    async def fake_search_image(query, knowledge_id, top_k=10, config_override=None):
        return [f"{knowledge_id}:{query}:image"]

    monkeypatch.setattr(
        "zuno.services.rag.retrieval.milvus_client",
        SimpleNamespace(search=fake_search, search_image=fake_search_image, search_summary=fake_search),
    )

    results = asyncio.run(MixRetrival.retrival_milvus_documents("architecture", ["k1"], "content"))

    assert results == ["k1:architecture:image"]
