from __future__ import annotations

from datetime import datetime, timezone
from mimetypes import guess_type
from pathlib import Path

from zuno.schema.chunk import ChunkModel

from .contracts import CanonicalDocumentIR, ParseDocumentRequest
from .gateway import ParseGateway


LEGACY_ADAPTER_ID = "temporary.adapter.phase11.legacy_chunk_projection"
LEGACY_ADAPTER_OWNER = "Input Parser Adapter Owner"
LEGACY_ADAPTER_REMOVAL_PHASE = "PHASE16"


def parse_file_to_canonical_ir(
    *,
    file_id: str,
    file_path: str,
    knowledge_id: str,
    source_url: str | None = None,
    knowledge_config: dict | None = None,
) -> CanonicalDocumentIR:
    path = Path(file_path)
    source_uri = source_url or path.resolve().as_uri()
    mime_type = guess_type(path.name)[0] or "text/plain"
    source_bytes = path.read_bytes()
    result = ParseGateway.parse_document(
        ParseDocumentRequest(
            document_id=file_id,
            source_id=file_id,
            workspace_id=f"knowledge:{knowledge_id}",
            source_uri=source_uri,
            mime_type=mime_type,
            source_bytes=source_bytes,
            parser_config={
                "legacy_adapter": LEGACY_ADAPTER_ID,
                "knowledge_config": knowledge_config or {},
                "owner": LEGACY_ADAPTER_OWNER,
                "removal_phase": LEGACY_ADAPTER_REMOVAL_PHASE,
            },
        )
    )
    if result.status != "succeeded" or result.document is None:
        reason = result.failure.reason if result.failure else result.status
        raise ValueError(f"legacy parser adapter failed through ParseGateway: {reason}")
    return result.document


async def parse_file_into_legacy_chunks(
    *,
    file_id: str,
    file_path: str,
    knowledge_id: str,
    source_url: str | None = None,
    knowledge_config: dict | None = None,
) -> list[ChunkModel]:
    document = parse_file_to_canonical_ir(
        file_id=file_id,
        file_path=file_path,
        knowledge_id=knowledge_id,
        source_url=source_url,
        knowledge_config=knowledge_config,
    )
    return canonical_ir_to_legacy_chunks(
        document=document,
        file_id=file_id,
        file_name=Path(file_path).name,
        knowledge_id=knowledge_id,
        source_url=source_url or document.metadata.source_uri,
    )


def canonical_ir_to_legacy_chunks(
    *,
    document: CanonicalDocumentIR,
    file_id: str,
    file_name: str,
    knowledge_id: str,
    source_url: str = "",
) -> list[ChunkModel]:
    update_time = datetime.now(timezone.utc).isoformat()
    chunks: list[ChunkModel] = []
    for index, block in enumerate(document.blocks, start=1):
        content = (block.text or "").strip()
        if not content:
            continue
        chunks.append(
            ChunkModel(
                chunk_id=f"{file_id}_{block.block_id}_{index}"[:128],
                content=content,
                file_id=file_id,
                file_name=file_name,
                update_time=update_time,
                knowledge_id=knowledge_id,
                modality="image" if block.type in {"image", "ocr_text"} else "text",
                source_url=source_url,
                document_hash=document.metadata.source_sha256 or document.metadata.hash,
                source_chunk_id=f"{document.metadata.document_version_id}:{block.block_id}"[:128],
            )
        )
    return chunks


__all__ = [
    "LEGACY_ADAPTER_ID",
    "LEGACY_ADAPTER_OWNER",
    "LEGACY_ADAPTER_REMOVAL_PHASE",
    "canonical_ir_to_legacy_chunks",
    "parse_file_into_legacy_chunks",
    "parse_file_to_canonical_ir",
]
