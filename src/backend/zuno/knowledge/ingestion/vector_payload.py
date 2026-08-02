from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone
from urllib.parse import urlparse

from .contracts import CanonicalDocumentIR
from .router import build_index_handoff_payload


def canonical_ir_to_vector_payloads(
    document: CanonicalDocumentIR,
    *,
    knowledge_id: str,
    update_time: str | None = None,
) -> list[dict]:
    handoff = build_index_handoff_payload(document)
    source_path = urlparse(document.metadata.source_uri or "").path
    file_name = os.path.basename(source_path) or document.metadata.document_id
    resolved_update_time = update_time or datetime.now(timezone.utc).isoformat()
    document_hash = document.metadata.source_sha256 or document.metadata.hash
    chunks = []
    for item in handoff.vector_documents:
        chunk_id = str(item["id"])
        content = str(item["text"])
        metadata = dict(item.get("metadata") or {})
        chunk_hash = hashlib.sha1(f"{document_hash}|{chunk_id}|{content}".encode("utf-8")).hexdigest()
        chunks.append(
            {
                "chunk_id": chunk_id,
                "content": content,
                "file_id": document.metadata.document_id,
                "file_name": file_name,
                "knowledge_id": knowledge_id,
                "update_time": resolved_update_time,
                "summary": "",
                "modality": "text",
                "source_url": document.metadata.source_uri,
                "source_chunk_id": metadata.get("source_span", {}).get("chunk_id") or chunk_id,
                "document_hash": document_hash,
                "chunk_hash": chunk_hash,
                "metadata": metadata,
            }
        )
    return chunks


__all__ = ["canonical_ir_to_vector_payloads"]
