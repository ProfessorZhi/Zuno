from __future__ import annotations

from typing import Iterable

from .contracts import CanonicalDocumentIR, DocumentBlock, DocumentMetadata, DocumentProvenance, SourceSpan


def normalize_legacy_chunks_to_ir(
    *,
    chunks: Iterable[object],
    document_id: str,
    workspace_id: str,
    source_uri: str,
    mime_type: str,
    parser_id: str,
    parser_version: str,
    acl_scope: str = "workspace",
    sensitivity_tags: list[str] | None = None,
) -> CanonicalDocumentIR:
    normalized_tags = list(sensitivity_tags or [])
    chunk_list = list(chunks)
    document_hash = _first_attr(chunk_list, "document_hash") or _first_attr(chunk_list, "chunk_hash") or ""
    blocks = [
        DocumentBlock(
            block_id=str(_attr(chunk, "chunk_id", f"chunk_{index}")),
            type=_block_type(chunk),
            text=str(_attr(chunk, "content", "")),
            source_span=SourceSpan(line_range=[index, index]),
            acl_scope=acl_scope,
            sensitivity_tags=list(normalized_tags),
            confidence=1.0,
        )
        for index, chunk in enumerate(chunk_list, start=1)
    ]
    return CanonicalDocumentIR(
        metadata=DocumentMetadata(
            document_id=document_id,
            workspace_id=workspace_id,
            source_uri=source_uri,
            mime_type=mime_type,
            hash=str(document_hash),
            parser_id=parser_id,
            parser_version=parser_version,
            acl_scope=acl_scope,
            sensitivity_tags=normalized_tags,
        ),
        blocks=blocks,
        provenance=DocumentProvenance(
            parser_id=parser_id,
            parser_version=parser_version,
            source_uri=source_uri,
            confidence=1.0,
        ),
    )


def _attr(obj: object, name: str, default: object = None) -> object:
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _first_attr(chunks: list[object], name: str) -> object:
    for chunk in chunks:
        value = _attr(chunk, name)
        if value:
            return value
    return None


def _block_type(chunk: object) -> str:
    modality = str(_attr(chunk, "modality", "text") or "text")
    return "image" if modality == "image" else "paragraph"


__all__ = ["normalize_legacy_chunks_to_ir"]
