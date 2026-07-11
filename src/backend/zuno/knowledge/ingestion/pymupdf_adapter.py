from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlparse

from .contracts import DocumentBlock, ParseDocumentRequest, SourceSpan


PYMUPDF_PARSER_VERSION = "pymupdf-source-span-v1"


def parse_pdf_source_spans(request: ParseDocumentRequest) -> tuple[list[DocumentBlock], list[str], float]:
    """Parse a real PDF byte stream with PyMuPDF and preserve page/block spans."""

    try:
        import fitz
    except Exception as exc:  # pragma: no cover - depends on optional local runtime
        raise RuntimeError("PyMuPDF dependency is not available") from exc

    source_bytes = _source_bytes(request)
    try:
        document = fitz.open(stream=source_bytes, filetype="pdf")
    except Exception as exc:
        raise ValueError(f"PyMuPDF failed to open PDF: {exc}") from exc

    blocks: list[DocumentBlock] = []
    warnings: list[str] = []
    char_offset = 0
    try:
        for page_index, page in enumerate(document, start=1):
            page_blocks = list(page.get_text("blocks"))
            text_block_count = 0
            for raw_block_index, raw_block in enumerate(page_blocks):
                if len(raw_block) < 5:
                    continue
                x0, y0, x1, y1, raw_text, *rest = raw_block
                block_type = int(rest[1]) if len(rest) > 1 and isinstance(rest[1], int) else 0
                if block_type != 0:
                    continue
                normalized_text = _normalize_text(str(raw_text))
                if not normalized_text:
                    continue
                text_block_count += 1
                char_start = char_offset
                char_end = char_start + len(normalized_text)
                char_offset = char_end + 1
                block_id = f"block_p{page_index}_b{raw_block_index + 1}"
                blocks.append(
                    DocumentBlock(
                        block_id=block_id,
                        type="paragraph",
                        text=normalized_text,
                        source_span=SourceSpan(
                            page=page_index,
                            page_number=page_index,
                            bbox=[float(x0), float(y0), float(x1), float(y1)],
                            char_start=char_start,
                            char_end=char_end,
                            raw_text=str(raw_text),
                            normalized_text=normalized_text,
                        ),
                        metadata={
                            "parser_adapter": "pymupdf",
                            "page_number": page_index,
                            "block_index": raw_block_index + 1,
                        },
                    )
                )
            if page_blocks and text_block_count == 0:
                warnings.append(f"page {page_index} has no extractable text blocks; OCR/VLM required")
    finally:
        document.close()

    if not blocks:
        raise ValueError("PDF contains no extractable text blocks; needs_ocr")
    return blocks, warnings, 0.96


def has_real_pdf_source(request: ParseDocumentRequest) -> bool:
    if request.source_bytes:
        return request.source_bytes.lstrip().startswith(b"%PDF")
    parsed = urlparse(request.source_uri)
    if parsed.scheme != "file":
        return False
    path = Path(_file_uri_path(parsed.path))
    if not path.exists():
        return False
    with path.open("rb") as handle:
        return handle.read(8).lstrip().startswith(b"%PDF")


def _source_bytes(request: ParseDocumentRequest) -> bytes:
    if request.source_bytes:
        return request.source_bytes
    parsed = urlparse(request.source_uri)
    if parsed.scheme == "file":
        return Path(_file_uri_path(parsed.path)).read_bytes()
    raise ValueError("PyMuPDF parser requires source_bytes or a file:// source_uri")


def _file_uri_path(path_text: str) -> str:
    decoded = unquote(path_text)
    if re.match(r"^/[A-Za-z]:/", decoded):
        return decoded[1:]
    return decoded


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


__all__ = ["PYMUPDF_PARSER_VERSION", "has_real_pdf_source", "parse_pdf_source_spans"]
