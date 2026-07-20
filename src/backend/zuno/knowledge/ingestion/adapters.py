from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from io import StringIO
from typing import Any
from urllib.parse import unquote, urlparse

from .contracts import (
    DocumentBlock,
    DocumentFigure,
    DocumentTable,
    ParseDocumentRequest,
    ParserDiagnostic,
    SourceSpan,
)
from .pymupdf_adapter import has_real_pdf_source, parse_pdf_source_spans


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

    def dependency_probe(self) -> ParserDiagnostic:
        from .router import PARSER_ADAPTER_CONTRACTS, adapter_boundary_metadata

        contract = PARSER_ADAPTER_CONTRACTS[self.parser_id]
        severity = "info" if contract.dependency_status == "present" else "warning"
        return ParserDiagnostic(
            code="adapter_dependency_probe",
            message=f"{self.parser_id} dependency status: {contract.dependency_status}.",
            severity=severity,
            parser_id=self.parser_id,
            metadata=adapter_boundary_metadata(self.parser_id),
        )

    def parse(
        self,
        *,
        format_name: str,
        text: str,
        request: ParseDocumentRequest,
    ) -> tuple[list[DocumentBlock], list[DocumentTable], list[DocumentFigure], list[str], float]:
        if format_name == "pdf":
            if has_real_pdf_source(request):
                blocks, warnings, confidence = parse_pdf_source_spans(request)
                return blocks, [], [], warnings, confidence
            return _parse_pdf(text, request)
        if format_name in {"docx", "xlsx"}:
            return _parse_structured_markdown(text, request, table_cells=True)
        if format_name == "pptx":
            return _parse_pptx(text, request)
        if format_name == "image":
            return _parse_image_ocr(text, request)
        if format_name == "csv":
            return _parse_csv(text, request)
        if format_name == "json":
            return _parse_json(text, request)
        if format_name == "html":
            return _parse_html(text, request)
        if format_name == "code":
            return _parse_code(text, request)
        return _parse_markdown_or_text(text, request, markdown=format_name == "md")


PARSER_ADAPTER_REGISTRY = {
    "native": ParserAdapter(parser_id="native"),
    "docling_pymupdf": ParserAdapter(parser_id="docling_pymupdf"),
    "mineru_ocr_vlm": ParserAdapter(parser_id="mineru_ocr_vlm"),
    "local_ocr_vlm": ParserAdapter(parser_id="local_ocr_vlm"),
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
    if markdown:
        return _parse_markdown(text, request)

    blocks: list[DocumentBlock] = []
    current_section: list[str] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        content = line.strip()
        if not content:
            continue
        blocks.append(
            _block(
                request,
                block_id=f"block_line_{line_number}",
                block_type="paragraph",
                text=content,
                source_span=SourceSpan(
                    line_range=[line_number, line_number],
                    section_path=list(current_section),
                ),
            )
        )
    return _ensure_blocks(blocks, text, request), [], [], [], 1.0


def _parse_markdown(
    text: str,
    request: ParseDocumentRequest,
) -> tuple[list[DocumentBlock], list[DocumentTable], list[DocumentFigure], list[str], float]:
    blocks: list[DocumentBlock] = []
    tables: list[DocumentTable] = []
    warnings: list[str] = []
    section_stack: list[str] = []
    raw_lines = text.splitlines()
    index = 0
    table_index = 0
    while index < len(raw_lines):
        line_number = index + 1
        line = raw_lines[index].rstrip()
        stripped = line.strip()
        if not stripped:
            index += 1
            continue

        fence_match = re.match(r"^```(?P<language>[\w.+-]*)\s*$", stripped)
        if fence_match:
            language = fence_match.group("language") or None
            start_line = line_number
            index += 1
            code_lines: list[str] = []
            closed = False
            while index < len(raw_lines):
                candidate = raw_lines[index]
                if candidate.strip().startswith("```"):
                    closed = True
                    break
                code_lines.append(candidate)
                index += 1
            end_line = index + 1 if closed else len(raw_lines)
            if not closed:
                warnings.append(f"malformed_markdown: unclosed code fence at line {start_line}")
            blocks.append(
                _block(
                    request,
                    block_id=f"block_code_{start_line}",
                    block_type="code_block",
                    text="\n".join(code_lines).rstrip(),
                    source_span=SourceSpan(
                        line_range=[start_line, end_line],
                        section_path=list(section_stack),
                    ),
                    language=language,
                    code_fence=language or "",
                    metadata={"fence": "```", "malformed": not closed},
                )
            )
            index += 1 if closed else 0
            continue

        heading_match = re.match(r"^(?P<marks>#{1,6})\s+(?P<title>.+?)\s*$", stripped)
        if heading_match:
            level = len(heading_match.group("marks"))
            title = heading_match.group("title").strip()
            section_stack = section_stack[: level - 1] + [title]
            blocks.append(
                _block(
                    request,
                    block_id=f"block_heading_{line_number}",
                    block_type="heading",
                    text=title,
                    source_span=SourceSpan(
                        line_range=[line_number, line_number],
                        section_path=list(section_stack),
                    ),
                    metadata={"level": level},
                )
            )
            index += 1
            continue

        if "|" in stripped and _looks_like_markdown_table(raw_lines, index):
            start_index = index
            table_lines: list[str] = []
            while index < len(raw_lines) and "|" in raw_lines[index]:
                table_lines.append(raw_lines[index].strip())
                index += 1
            rows = _markdown_table_rows(table_lines)
            if rows:
                table_index += 1
                headers = rows[0]
                source_span = SourceSpan(
                    line_range=[start_index + 1, index],
                    section_path=list(section_stack),
                    table_cell=f"table:{table_index}",
                )
                blocks.append(
                    _block(
                        request,
                        block_id=f"block_table_{table_index}",
                        block_type="table",
                        text="\n".join(table_lines),
                        source_span=source_span,
                        metadata={
                            "format": "markdown",
                            "headers": headers,
                            "row_count": max(len(rows) - 1, 0),
                            "column_count": len(headers),
                        },
                    )
                )
                tables.append(
                    DocumentTable(
                        table_id=f"table_{table_index}",
                        rows=rows,
                        source_span=source_span,
                    )
                )
            continue

        link_match = re.search(r"\[([^\]]+)\]\(([^)]+)\)", stripped)
        if link_match:
            label, href = link_match.groups()
            blocks.append(
                _block(
                    request,
                    block_id=f"block_link_{line_number}",
                    block_type="link",
                    text=stripped,
                    source_span=SourceSpan(
                        line_range=[line_number, line_number],
                        section_path=list(section_stack),
                    ),
                    metadata={"label": label, "href": href, "links": [{"label": label, "href": href}]},
                )
            )
        else:
            blocks.append(
                _block(
                    request,
                    block_id=f"block_paragraph_{line_number}",
                    block_type="paragraph",
                    text=stripped,
                    source_span=SourceSpan(
                        line_range=[line_number, line_number],
                        section_path=list(section_stack),
                    ),
                )
            )
        index += 1
    return _ensure_blocks(blocks, text, request), tables, [], warnings, 1.0


def _parse_csv(
    text: str,
    request: ParseDocumentRequest,
) -> tuple[list[DocumentBlock], list[DocumentTable], list[DocumentFigure], list[str], float]:
    warnings: list[str] = []
    delimiter = _detect_csv_delimiter(text)
    rows = list(csv.reader(StringIO(text), delimiter=delimiter))
    rows = [[cell.strip() for cell in row] for row in rows if any(cell.strip() for cell in row)]
    if not rows:
        return _ensure_blocks([], text, request), [], [], ["malformed_csv: no rows"], 0.6

    headers = rows[0]
    data_rows = rows[1:]
    malformed = any(len(row) != len(headers) for row in data_rows)
    if malformed:
        warnings.append("malformed_csv: row length does not match header length")
    line_count = max(len(text.splitlines()), 1)
    table_span = SourceSpan(line_range=[1, line_count], table_cell="table:1")
    blocks = [
        _block(
            request,
            block_id="block_csv_table_1",
            block_type="table",
            text=text.strip(),
            source_span=table_span,
            metadata={
                "format": "csv",
                "delimiter": delimiter,
                "headers": headers,
                "row_count": len(data_rows),
                "column_count": len(headers),
                "malformed": malformed,
            },
        )
    ]

    for row_index, row in enumerate(data_rows, start=1):
        for column_index, cell in enumerate(row, start=1):
            column_name = headers[column_index - 1] if column_index <= len(headers) else f"column_{column_index}"
            blocks.append(
                _block(
                    request,
                    block_id=f"block_csv_r{row_index}_c{column_index}",
                    block_type="table_cell",
                    text=cell,
                    source_span=SourceSpan(
                        line_range=[row_index + 1, row_index + 1],
                        table_cell=f"row:{row_index},col:{column_name}",
                    ),
                    metadata={
                        "row_index": row_index,
                        "column_index": column_index,
                        "column_name": column_name,
                        "malformed": malformed and len(row) != len(headers),
                    },
                )
            )
    return (
        _ensure_blocks(blocks, text, request),
        [DocumentTable(table_id="table_1", rows=rows, source_span=table_span)],
        [],
        warnings,
        0.85 if malformed else 1.0,
    )


def _parse_json(
    text: str,
    request: ParseDocumentRequest,
) -> tuple[list[DocumentBlock], list[DocumentTable], list[DocumentFigure], list[str], float]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        return (
            [
                _block(
                    request,
                    block_id="block_json_malformed",
                    block_type="paragraph",
                    text=text.strip(),
                    source_span=SourceSpan(line_range=[1, max(len(text.splitlines()), 1)]),
                    metadata={"format": "json", "malformed": True, "error": str(exc)},
                    confidence=0.5,
                )
            ],
            [],
            [],
            [f"malformed_json: {exc.msg} at line {exc.lineno} column {exc.colno}"],
            0.5,
        )

    blocks: list[DocumentBlock] = []
    _append_json_blocks(
        blocks=blocks,
        request=request,
        value=payload,
        pointer="",
        path=[],
        line_count=max(len(text.splitlines()), 1),
    )
    return _ensure_blocks(blocks, text, request), [], [], [], 1.0


def _parse_html(
    text: str,
    request: ParseDocumentRequest,
) -> tuple[list[DocumentBlock], list[DocumentTable], list[DocumentFigure], list[str], float]:
    parser = _NativeHTMLParser(request)
    parser.feed(text)
    parser.close()
    malformed = _looks_malformed_html(text)
    warnings = list(parser.warnings)
    if malformed:
        warnings.append("malformed_html: document has unclosed or incomplete html structure")
        if not parser.blocks:
            parser.blocks.append(
                _block(
                    request,
                    block_id="block_html_malformed",
                    block_type="paragraph",
                    text=_normalize_space(re.sub(r"<[^>]+>", " ", text)),
                    source_span=SourceSpan(line_range=[1, max(len(text.splitlines()), 1)]),
                    metadata={"format": "html", "malformed": True},
                    confidence=0.5,
                )
            )
        else:
            first = parser.blocks[0]
            parser.blocks[0] = first.model_copy(
                update={"metadata": {**first.metadata, "malformed": True}}
            )
    return _ensure_blocks(parser.blocks, text, request), parser.tables, [], warnings, 0.85 if malformed else 1.0


def _parse_image_ocr(
    text: str,
    request: ParseDocumentRequest,
) -> tuple[list[DocumentBlock], list[DocumentTable], list[DocumentFigure], list[str], float]:
    normalized = text.strip()
    if not normalized:
        raise ValueError("empty OCR/VLM source content")
    block = _block(
        request,
        block_id="block_ocr_1",
        block_type="ocr_text",
        text=normalized,
        source_span=SourceSpan(page=1, bbox=[0.0, 0.0, 1024.0, 768.0]),
        confidence=0.86,
        metadata={
            "adapter_mode": "local_deterministic_ocr_vlm",
            "requires_human_review": True,
            "failure_path": "typed_parser_failure_on_empty_or_unreadable_content",
        },
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
    lines = text.splitlines()
    language, detection = _detect_code_language(request.source_uri)
    imports = _extract_imports(lines, language)
    classes = [
        match.group(1)
        for line in lines
        if (match := re.match(r"^class\s+([A-Za-z_]\w*)\b", line.strip()))
    ]
    functions = [
        match.group(1)
        for line in lines
        if (match := re.match(r"^def\s+([A-Za-z_]\w*)\s*\(", line.strip()))
    ]
    return [
        _block(
            request,
            block_id="block_code_1",
            block_type="code_block",
            text=text.rstrip(),
            source_span=SourceSpan(line_range=[1, max(len(lines), 1)]),
            language=language,
            metadata={
                "language_detection": detection,
                "imports": imports,
                "classes": classes,
                "functions": functions,
                "symbol_parser": "regex",
            },
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
    language: str | None = None,
    code_fence: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> DocumentBlock:
    return DocumentBlock(
        block_id=block_id,
        type=block_type,
        text=text,
        source_span=source_span,
        language=language,
        code_fence=code_fence,
        metadata=metadata or {},
        acl_scope=request.acl_scope,
        sensitivity_tags=list(request.sensitivity_tags),
        confidence=confidence,
    )


def _looks_like_markdown_table(lines: list[str], index: int) -> bool:
    line = lines[index].strip()
    if "|" not in line:
        return False
    if index + 1 >= len(lines):
        return False
    return bool(re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", lines[index + 1]))


def _markdown_table_rows(table_lines: list[str]) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in table_lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and all(re.match(r"^:?-{3,}:?$", cell) for cell in cells):
            continue
        rows.append(cells)
    return rows


def _detect_csv_delimiter(text: str) -> str:
    try:
        return csv.Sniffer().sniff(text, delimiters=",;\t|").delimiter
    except csv.Error:
        return ","


def _append_json_blocks(
    *,
    blocks: list[DocumentBlock],
    request: ParseDocumentRequest,
    value: Any,
    pointer: str,
    path: list[str],
    line_count: int,
) -> None:
    block_id = "block_json_root" if not pointer else "block_json_" + re.sub(r"[^A-Za-z0-9]+", "_", pointer).strip("_")
    metadata = {"format": "json", "json_pointer": pointer or "/", "path": list(path)}
    source_span = SourceSpan(line_range=[1, line_count], section_path=list(path))
    if isinstance(value, dict):
        blocks.append(
            _block(
                request,
                block_id=block_id,
                block_type="json_object",
                text=", ".join(value.keys()),
                source_span=source_span,
                metadata={**metadata, "keys": list(value.keys()), "child_count": len(value)},
            )
        )
        for key, child in value.items():
            _append_json_blocks(
                blocks=blocks,
                request=request,
                value=child,
                pointer=_json_pointer_join(pointer, str(key)),
                path=[*path, str(key)],
                line_count=line_count,
            )
    elif isinstance(value, list):
        blocks.append(
            _block(
                request,
                block_id=block_id,
                block_type="json_array",
                text=f"{len(value)} items",
                source_span=source_span,
                metadata={**metadata, "item_count": len(value)},
            )
        )
        for index, child in enumerate(value):
            _append_json_blocks(
                blocks=blocks,
                request=request,
                value=child,
                pointer=_json_pointer_join(pointer, str(index)),
                path=[*path, str(index)],
                line_count=line_count,
            )
    else:
        blocks.append(
            _block(
                request,
                block_id=block_id,
                block_type="json_value",
                text=str(value),
                source_span=source_span,
                metadata={**metadata, "value_type": type(value).__name__},
            )
        )


def _json_pointer_join(pointer: str, part: str) -> str:
    escaped = part.replace("~", "~0").replace("/", "~1")
    return f"{pointer}/{escaped}" if pointer else f"/{escaped}"


class _NativeHTMLParser(HTMLParser):
    def __init__(self, request: ParseDocumentRequest) -> None:
        super().__init__(convert_charrefs=True)
        self.request = request
        self.blocks: list[DocumentBlock] = []
        self.tables: list[DocumentTable] = []
        self.warnings: list[str] = []
        self._section_stack: list[str] = []
        self._skip_tag: str | None = None
        self._text_stack: list[dict[str, Any]] = []
        self._link: dict[str, Any] | None = None
        self._table_rows: list[list[str]] | None = None
        self._current_row: list[str] | None = None
        self._current_cell: list[str] | None = None
        self._table_start_line = 1

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attr_map = {name.lower(): value or "" for name, value in attrs}
        line_number = self.getpos()[0]
        if tag in {"script", "style"}:
            self._skip_tag = tag
            return
        if self._skip_tag:
            return
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6", "p"}:
            self._text_stack.append(
                {
                    "tag": tag,
                    "line": line_number,
                    "data": [],
                    "attrs": attr_map,
                }
            )
        elif tag == "a":
            self._link = {"href": attr_map.get("href", ""), "line": line_number, "data": []}
        elif tag == "table":
            self._table_rows = []
            self._table_start_line = line_number
        elif tag == "tr" and self._table_rows is not None:
            self._current_row = []
        elif tag in {"td", "th"} and self._current_row is not None:
            self._current_cell = []

    def handle_data(self, data: str) -> None:
        if self._skip_tag:
            return
        if self._current_cell is not None:
            self._current_cell.append(data)
            return
        if self._link is not None:
            self._link["data"].append(data)
        if self._text_stack:
            self._text_stack[-1]["data"].append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        line_number = self.getpos()[0]
        if self._skip_tag == tag:
            self._skip_tag = None
            return
        if self._skip_tag:
            return
        if tag == "a" and self._link is not None:
            label = _normalize_space("".join(self._link["data"]))
            if label:
                href = self._link["href"]
                self.blocks.append(
                    _block(
                        self.request,
                        block_id=f"block_html_link_{len(self.blocks) + 1}",
                        block_type="link",
                        text=label,
                        source_span=SourceSpan(
                            line_range=[self._link["line"], line_number],
                            section_path=list(self._section_stack),
                        ),
                        metadata={"label": label, "href": href, "links": [{"label": label, "href": href}]},
                    )
                )
            self._link = None
        elif tag in {"td", "th"} and self._current_cell is not None and self._current_row is not None:
            self._current_row.append(_normalize_space("".join(self._current_cell)))
            self._current_cell = None
        elif tag == "tr" and self._table_rows is not None and self._current_row is not None:
            if any(cell for cell in self._current_row):
                self._table_rows.append(self._current_row)
            self._current_row = None
        elif tag == "table" and self._table_rows is not None:
            self._append_table(line_number)
            self._table_rows = None
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6", "p"}:
            self._close_text_block(tag, line_number)

    def _close_text_block(self, tag: str, line_number: int) -> None:
        if not self._text_stack:
            return
        entry = self._text_stack.pop()
        if entry["tag"] != tag:
            self.warnings.append(f"malformed_html: closing tag mismatch for {tag}")
        text = _normalize_space("".join(entry["data"]))
        if not text:
            return
        if tag.startswith("h") and tag[1:].isdigit():
            level = int(tag[1:])
            self._section_stack = self._section_stack[: level - 1] + [text]
            self.blocks.append(
                _block(
                    self.request,
                    block_id=f"block_html_heading_{len(self.blocks) + 1}",
                    block_type="heading",
                    text=text,
                    source_span=SourceSpan(
                        line_range=[entry["line"], line_number],
                        section_path=list(self._section_stack),
                    ),
                    metadata={"level": level},
                )
            )
        else:
            self.blocks.append(
                _block(
                    self.request,
                    block_id=f"block_html_paragraph_{len(self.blocks) + 1}",
                    block_type="paragraph",
                    text=text,
                    source_span=SourceSpan(
                        line_range=[entry["line"], line_number],
                        section_path=list(self._section_stack),
                    ),
                )
            )

    def _append_table(self, line_number: int) -> None:
        rows = self._table_rows or []
        if not rows:
            return
        headers = rows[0]
        table_id = f"table_{len(self.tables) + 1}"
        source_span = SourceSpan(
            line_range=[self._table_start_line, line_number],
            section_path=list(self._section_stack),
            table_cell=table_id,
        )
        self.blocks.append(
            _block(
                self.request,
                block_id=f"block_html_table_{len(self.tables) + 1}",
                block_type="table",
                text="\n".join(" | ".join(row) for row in rows),
                source_span=source_span,
                metadata={
                    "format": "html",
                    "headers": headers,
                    "row_count": max(len(rows) - 1, 0),
                    "column_count": len(headers),
                },
            )
        )
        self.tables.append(DocumentTable(table_id=table_id, rows=rows, source_span=source_span))


def _looks_malformed_html(text: str) -> bool:
    lowered = text.lower()
    if "<html" in lowered and "</html>" not in lowered:
        return True
    if "<table" in lowered and "</table>" not in lowered:
        return True
    return False


def _normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _detect_code_language(source_uri: str) -> tuple[str | None, str]:
    parsed = urlparse(source_uri)
    path = unquote(parsed.path or source_uri).lower()
    suffix_map = {
        ".py": "python",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
        ".java": "java",
        ".go": "go",
    }
    for suffix, language in suffix_map.items():
        if path.endswith(suffix):
            return language, "extension"
    return None, "unknown"


def _extract_imports(lines: list[str], language: str | None) -> list[str]:
    if language != "python":
        return []
    imports: list[str] = []
    for line in lines:
        stripped = line.strip()
        if match := re.match(r"^import\s+([A-Za-z_][\w.]*)", stripped):
            imports.append(match.group(1))
        elif match := re.match(r"^from\s+([A-Za-z_][\w.]*)\s+import\s+(.+)$", stripped):
            module = match.group(1)
            names = [name.strip().split(" as ", 1)[0] for name in match.group(2).split(",")]
            imports.extend(f"{module}.{name}" for name in names if name)
    return imports


__all__ = ["PARSER_ADAPTER_REGISTRY", "ParserAdapter", "get_parser_adapter"]
