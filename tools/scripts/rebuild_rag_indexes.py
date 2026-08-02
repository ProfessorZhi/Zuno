import asyncio
import os
from collections import defaultdict
from mimetypes import guess_type
from urllib.parse import urlparse

from sqlmodel import select

from zuno.platform.database.models.knowledge_file import KnowledgeFileTable
from zuno.platform.database.session import session_getter
from zuno.platform.services.rag.handler import RagHandler
from zuno.platform.services.rag.vector_db import milvus_client
from zuno.platform.services.storage import storage_client
from zuno.platform.settings import initialize_app_settings
from zuno.platform.common.file_utils import get_object_key_from_public_url, get_save_tempfile
from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway
from zuno.knowledge.ingestion.vector_payload import canonical_ir_to_vector_payloads


def iter_successful_knowledge_files():
    with session_getter() as session:
        rows = session.exec(
            select(KnowledgeFileTable).where(KnowledgeFileTable.rag_index_status == "success")
        ).all()
    return rows


def download_to_local_path(oss_url: str, file_name: str) -> tuple[str, bool]:
    parsed = urlparse(oss_url)
    bucket_name = parsed.path.lstrip("/").split("/", 1)[0] if parsed.path else ""
    object_key = get_object_key_from_public_url(oss_url, bucket_name=bucket_name)
    local_file_path = get_save_tempfile(file_name)
    storage_client.download_file(object_key, local_file_path)
    return local_file_path, True


async def rebuild_indexes():
    await initialize_app_settings(os.getenv("ZUNO_CONFIG") or os.getenv("AGENTCHAT_CONFIG") or "/app/zuno/config.yaml")
    parser = ParseGateway(
        adapter_boundary={
            "adapter": "tools.scripts.rebuild_rag_indexes.canonical_handoff",
            "consumer": "rag_rebuild_index_script",
            "projection": "canonical_index_handoff_vector_documents",
        }
    )
    files = iter_successful_knowledge_files()
    if not files:
        print("No successful knowledge files found.")
        return

    grouped_files = defaultdict(list)
    for item in files:
        grouped_files[item.knowledge_id].append(item)

    client = milvus_client._get_client()
    for knowledge_id in grouped_files:
        if hasattr(client, "delete_collection"):
            try:
                await client.delete_collection(knowledge_id)
            except Exception as err:
                print(f"Skip clearing collection {knowledge_id}: {err}")

    total_chunks = 0
    rebuilt_files = 0

    for knowledge_id, knowledge_files in grouped_files.items():
        for knowledge_file in knowledge_files:
            cleanup = False
            local_path = ""
            try:
                local_path, cleanup = download_to_local_path(knowledge_file.oss_url, knowledge_file.file_name)
                result = await parser.parse(
                    ParseDocumentRequest(
                        document_id=knowledge_file.id,
                        workspace_id=str(getattr(knowledge_file, "workspace_id", None) or knowledge_id),
                        source_uri=f"file://{local_path}",
                        mime_type=getattr(knowledge_file, "mime_type", None) or guess_type(local_path)[0] or "",
                        source_object_ref=getattr(knowledge_file, "object_key", None) or knowledge_file.oss_url or "",
                        parser_config={},
                    )
                )
                if result.status != "succeeded" or result.document is None:
                    reason = result.failure.reason if result.failure else result.status
                    raise RuntimeError(f"canonical parse failed for {knowledge_file.file_name}: {reason}")
                chunks = canonical_ir_to_vector_payloads(result.document, knowledge_id=knowledge_id)
                await RagHandler.index_milvus_documents(knowledge_id, chunks)
                rebuilt_files += 1
                total_chunks += len(chunks)
                print(
                    f"Rebuilt knowledge_id={knowledge_id} file={knowledge_file.file_name} "
                    f"chunks={len(chunks)}"
                )
            finally:
                if cleanup and local_path and os.path.exists(local_path):
                    os.remove(local_path)

    print(f"Done. rebuilt_files={rebuilt_files}, total_chunks={total_chunks}")


if __name__ == "__main__":
    asyncio.run(rebuild_indexes())
