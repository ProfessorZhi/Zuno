import asyncio
from pathlib import Path

from agentchat.schema.chunk import ChunkModel
from agentchat.services.rag.doc_parser.pdf import PDFParser
from agentchat.services.rag.doc_parser.text import text_parser


class _FakeMarkdownParser:
    def __init__(self, chunks):
        self._chunks = chunks

    async def parse_into_chunks(self, file_id, file_path, knowledge_id):
        return self._chunks


class _InspectingMarkdownParser:
    def __init__(self):
        self.last_text = None

    async def parse_into_chunks(self, file_id, file_path, knowledge_id):
        self.last_text = Path(file_path).read_text(encoding="utf-8")
        return [_make_text_chunk(self.last_text)]


def _make_text_chunk(content: str) -> ChunkModel:
    return ChunkModel(
        chunk_id="chunk_1",
        content=content,
        file_id="file_1",
        file_name="resume.pdf",
        knowledge_id="knowledge_1",
        update_time="2026-04-22T00:00:00",
    )


def test_pdf_parser_skips_standalone_image_chunks_for_text_rich_pdf(monkeypatch, tmp_path: Path):
    parser = PDFParser()
    markdown_path = tmp_path / "resume.md"
    markdown_path.write_text("# resume", encoding="utf-8")

    async def fake_convert_markdown(file_path):
        return str(markdown_path), {"page-0.png": "http://example.com/page-0.png"}, {"page-0.png": "full-page screenshot"}

    monkeypatch.setattr(parser, "convert_markdown", fake_convert_markdown)
    text_chunks = [_make_text_chunk("Zuno " * 120)]

    result = asyncio.run(
        parser.parse_into_chunks(
            file_id="file_1",
            file_path="resume.pdf",
            knowledge_id="knowledge_1",
            markdown_parser_instance=_FakeMarkdownParser(text_chunks),
            image_mode="dual",
        )
    )

    assert result == text_chunks
    assert [chunk.modality for chunk in result] == ["text"]


def test_pdf_parser_keeps_image_chunks_for_text_sparse_pdf(monkeypatch, tmp_path: Path):
    parser = PDFParser()
    markdown_path = tmp_path / "resume.md"
    markdown_path.write_text("# resume", encoding="utf-8")

    async def fake_convert_markdown(file_path):
        return str(markdown_path), {"page-0.png": "http://example.com/page-0.png"}, {"page-0.png": "full-page screenshot"}

    monkeypatch.setattr(parser, "convert_markdown", fake_convert_markdown)
    monkeypatch.setattr(parser, "_extract_plain_text", lambda _: "too short")
    text_chunks = [_make_text_chunk("brief summary")]

    result = asyncio.run(
        parser.parse_into_chunks(
            file_id="file_1",
            file_path="resume.pdf",
            knowledge_id="knowledge_1",
            markdown_parser_instance=_FakeMarkdownParser(text_chunks),
            image_mode="dual",
        )
    )

    assert len(result) == 2
    assert [chunk.modality for chunk in result] == ["text", "image"]
    assert result[1].source_url == "http://example.com/page-0.png"


def test_pdf_parser_strips_inline_markdown_images_before_text_chunking(monkeypatch, tmp_path: Path):
    parser = PDFParser()
    markdown_path = tmp_path / "resume.md"
    markdown_path.write_text(
        "![full-page screenshot](http://example.com/page-0.png)\n\n## Zuno\n\nreal body content",
        encoding="utf-8",
    )

    async def fake_convert_markdown(file_path):
        return str(markdown_path), {"page-0.png": "http://example.com/page-0.png"}, {"page-0.png": "full-page screenshot"}

    monkeypatch.setattr(parser, "convert_markdown", fake_convert_markdown)
    inspecting_parser = _InspectingMarkdownParser()

    result = asyncio.run(
        parser.parse_into_chunks(
            file_id="file_1",
            file_path="resume.pdf",
            knowledge_id="knowledge_1",
            markdown_parser_instance=inspecting_parser,
            image_mode="dual",
        )
    )

    assert "![full-page screenshot]" not in inspecting_parser.last_text
    assert "real body content" in inspecting_parser.last_text
    assert result[0].content == inspecting_parser.last_text


def test_pdf_parser_falls_back_to_raw_pdf_text_when_markdown_has_only_images(monkeypatch, tmp_path: Path):
    parser = PDFParser()
    markdown_path = tmp_path / "resume.md"
    markdown_path.write_text("![full-page screenshot](http://example.com/page-0.png)", encoding="utf-8")

    async def fake_convert_markdown(file_path):
        return str(markdown_path), {"page-0.png": "http://example.com/page-0.png"}, {"page-0.png": "full-page screenshot"}

    monkeypatch.setattr(parser, "convert_markdown", fake_convert_markdown)
    monkeypatch.setattr(parser, "_extract_plain_text", lambda _: "Zuno\n" * 120)

    calls: list[str] = []

    async def fake_text_parse(file_id, file_path, knowledge_id):
        calls.append(file_path)
        return [_make_text_chunk(Path(file_path).read_text(encoding="utf-8"))]

    monkeypatch.setattr(text_parser, "parse_into_chunks", fake_text_parse)

    result = asyncio.run(
        parser.parse_into_chunks(
            file_id="file_1",
            file_path="resume.pdf",
            knowledge_id="knowledge_1",
            markdown_parser_instance=_FakeMarkdownParser([]),
            image_mode="dual",
        )
    )

    assert len(result) == 1
    assert result[0].modality == "text"
    assert "Zuno" in result[0].content
    assert calls
