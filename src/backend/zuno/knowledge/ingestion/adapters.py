from __future__ import annotations

import re
from dataclasses import dataclass

from .contracts import (
    DocumentBlock,
    DocumentFigure,
    DocumentTable,
    ParseDocumentRequest,
    ParserDiagnostic,
    SourceSpan,
)


@dataclass(frozen=True)
class ParserAdapter:
    parser_id: str

    def supports(self, format_name: str) -> bool:
        return format_name in self.capabilities()

    def capabilities(self) -> list[str]:
        from .router import PARSER_ADAPTER_CONTRACTS

        contract = PARSER_ADAPTER_CONTRACTS[self.parser_id]
        return list(contract.supported_formats)

    def diagnostics(self, format_name: str) -> list[ParserDiagnostic]:
        if self.supports(format_name):
            return [
                ParserDiagnostic(
                    code="adapter_supports_format",
                    message=f"{self.parser_id} supports {format_name}.",
                    parser_id=self.parser_id,
                    format=format_name,
                )
            ]
        return [
            ParserDiagnostic(
                code="adapter_unsupported_format",
                message=f"{self.parser_id} does not support {format_name}.",
                severity="warning",
                parser_id=self.parser_id,
                format=format_name,
            )
        ]

    def parse(
        self,
        *,
        format_name: str,
        text: str,
        request: ParseDocumentRequest,
    ) -> tuple[list[DocumentBlock], list[DocumentTable], list[DocumentFigure], list[str], float]:
        if format_name == "pdf":
            return _parse_pdf(text, request)
        if format_name in {"docx", "xlsx"}:
            return _parse_structured_markdown(text, request, table_cells=True)
        if format_name == "pptx":
            return _parse_pptx(text, request)
        if format_name == "image":
            return _parse_image_ocr(text, request)
        if format_name == "code":
            return _parse_code(text, request)
        return _parse_markdown_or_text(text, request, markdown=format_name in {"md", "html"})


PARSER_ADAPTER_REGISTRY = {
    "native": ParserAdapter(parser_id="native"),
    "docling_pymupdf": ParserAdapter(parser_id="docling_pymupdf"),
    "mineru_ocr_vlm": ParserAdapter(parser_id="mineru_ocr_vlm"),
    "unstructured_markitdown": ParserAdapter(parser_id="unstructured_markitdown"),
}


def get_parser_adapter(parser_id: str) -> ParserAdapter:
    try:
        return PARSER_ADAPTER_REGISTRY[parser_id]
    except KeyError as exc:
        raise KeyError(f"parser adapter not registered: {parser_id}") from exc


def _parse_pdf(
    text: str,
    request: ParseDocumentRequest,
) -> tuple[list[DocumentBlock], list[DocumentTable], list[DocumentFigure], list[str], float]:
    blocks: list[DocumentBlock] = []
    table_rows: list[list[str]] = []
    for line_number, line in enumerate(_lines(text), start=1):
        if "|" in line:
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            table_rows.append(cells)
            blocks.append(
                _block(
                    request,
                    block_id=f"block_table_{len(table_rows)}",
                    block_type="table",
                    text=line,
                    source_span=SourceSpan(page=1, bbox=[0.0, float(line_number), 600.0, float(line_number + 1)], table_cell=f"row:{len(table_rows)}"),
                )
            )
        else:
            blocks.append(
                _block(
                    request,
                    block_id=f"block_p{line_number}",
                    block_type="paragraph",
                    text=line,
                    source_span=SourceSpan(page=1, bbox=[0.0, float(line_number), 600.0, float(line_number + 1)]),
                )
            )
    tables = [
        DocumentTable(
            table_id="table_1",
            rows=table_rows,
            source_span=SourceSpan(page=1, bbox=[0.0, 1.0, 600.0, float(len(table_rows) + 1)], table_cell="row:1"),
            caption="Extracted PDF table",
        )
    ] if table_rows else []
    return _ensure_blocks(blocks, text, request), tables, [], [], 0.94


def _parse_structured_markdown(
    text: str,
    request: ParseDocumentRequest,
    *,
    table_cells: bool,
) -> tuple[list[DocumentBlock], list[DocumentTable], list[DocumentFigure], list[str], float]:
    blocks: list[DocumentBlock] = []
    table_rows: list[list[str]] = []
    current_section: list[str] = []
    for line_number, line in enumerate(_lines(text), start=1):
        if line.startswith("#"):
            title = line.lstrip("#").strip()
            current_section = [title]
            blocks.append(
                _block(request, block_id=f"block_heading_{line_number}", block_type="heading", text=title, source_span=SourceSpan(line_range=[line_number, line_number], section_path=list(current_section)))
            )
        elif "|" in line:
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            table_rows.append(cells)
            blocks.append(
                _block(request, block_id=f"block_table_{line_number}", block_type="table", text=line, source_span=SourceSpan(line_range=[line_number, line_number], section_path=list(current_section), table_cell=f"row:{len(table_rows)}" if table_cells else None))
            )
        else:
            blocks.append(
                _block(request, block_id=f"block_paragraph_{line_number}", block_type="paragraph", text=line, source_span=SourceSpan(line_range=[line_number, line_number], section_path=list(current_section)))
            )
    tables = [
        DocumentTable(
            table_id="table_1",
            rows=table_rows,
            source_span=SourceSpan(section_path=list(current_section), table_cell="row:1"),
        )
    ] if table_rows else []
    return _ensure_blocks(blocks, text, request), tables, [], [], 0.96


def _parse_pptx(
    text: str,
    request: ParseDocumentRequest,
) -> tuple[list[DocumentBlock], list[DocumentTable], list[DocumentFigure], list[str], float]:
    blocks: list[DocumentBlock] = []
    figures: list[DocumentFigure] = []
    for line_number, line in enumerate(_lines(text), start=1):
        if line.startswith("#"):
            block_type = "slide_title"
            content = line.lstrip("#").strip()
        elif line.startswith("!") or line.startswith("!["):
            block_type = "figure"
            content = line
            figures.append(DocumentFigure(figure_id=f"figure_{line_number}", description=line, source_span=SourceSpan(slide=1, bbox=[10.0, 10.0, 300.0, 200.0])))
        else:
            block_type = "slide_body"
            content = line.lstrip("- ").strip()
        blocks.append(
            _block(request, block_id=f"block_slide_{line_number}", block_type=block_type, text=content, source_span=SourceSpan(slide=1, bbox=[10.0, float(line_number * 20), 500.0, float(line_number * 20 + 16)]))
        )
    return _ensure_blocks(blocks, text, request), [], figures, [], 0.91


def _parse_markdown_or_text(
    text: str,
    request: ParseDocumentRequest,
    *,
    markdown: bool,
) -> tuple[list[DocumentBlock], list[DocumentTable], list[DocumentFigure], list[str], float]:
    blocks: list[DocumentBlock] = []
    current_section: list[str] = []
    for line_number, line in enumerate(_lines(text), start=1):
        if markdown and line.startswith("#"):
            title = line.lstrip("#").strip()
            current_section = [title]
            block_type = "heading"
            content = title
        elif markdown and re.search(r"\[[^\]]+\]\([^)]+\)", line):
            block_type = "link"
            content = line
        else:
            block_type = "paragraph"
            content = line
        blocks.append(
            _block(request, block_id=f"block_line_{line_number}", block_type=block_type, text=content, source_span=SourceSpan(line_range=[line_number, line_number], section_path=list(current_section)))
        )
    return _ensure_blocks(blocks, text, request), [], [], [], 1.0


def _parse_image_ocr(
    text: str,
    request: ParseDocumentRequest,
) -> tuple[list[DocumentBlock], list[DocumentTable], list[DocumentFigure], list[str], float]:
    block = _block(
        request,
        block_id="block_ocr_1",
        block_type="ocr_text",
        text=text.strip(),
        source_span=SourceSpan(page=1, bbox=[0.0, 0.0, 1024.0, 768.0]),
        confidence=0.86,
    )
    figure = DocumentFigure(
        figure_id="figure_1",
        description="OCR source image",
        source_span=SourceSpan(page=1, bbox=[0.0, 0.0, 1024.0, 768.0]),
        uri=request.source_uri,
    )
    return [block], [], [figure], ["OCR confidence should be reviewed before high-risk use."], 0.86


def _parse_code(
    text: str,
    request: ParseDocumentRequest,
) -> tuple[list[DocumentBlock], list[DocumentTable], list[DocumentFigure], list[str], float]:
    lines = _lines(text)
    return [
        _block(
            request,
            block_id="block_code_1",
            block_type="code_block",
            text="\n".join(lines),
            source_span=SourceSpan(line_range=[1, max(len(lines), 1)]),
        )
    ], [], [], [], 1.0


def _lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _ensure_blocks(
    blocks: list[DocumentBlock],
    text: str,
    request: ParseDocumentRequest,
) -> list[DocumentBlock]:
    if blocks:
        return blocks
    return [
        _block(
            request,
            block_id="block_1",
            block_type="paragraph",
            text=text.strip(),
            source_span=SourceSpan(line_range=[1, 1]),
        )
    ]


def _block(
    request: ParseDocumentRequest,
    *,
    block_id: str,
    block_type: str,
    text: str,
    source_span: SourceSpan,
    confidence: float = 1.0,
) -> DocumentBlock:
    return DocumentBlock(
        block_id=block_id,
        type=block_type,
        text=text,
        source_span=source_span,
        acl_scope=request.acl_scope,
        sensitivity_tags=list(request.sensitivity_tags),
        confidence=confidence,
    )


__all__ = ["PARSER_ADAPTER_REGISTRY", "ParserAdapter", "get_parser_adapter"]
