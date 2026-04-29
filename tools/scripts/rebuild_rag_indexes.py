import asyncio
import os
from collections import defaultdict
from urllib.parse import urlparse

from sqlmodel import select

from agentchat.database.models.knowledge_file import KnowledgeFileTable
from agentchat.database.session import session_getter
from agentchat.services.rag.handler import RagHandler
from agentchat.services.rag.vector_db import milvus_client
from agentchat.services.storage import storage_client
from agentchat.settings import initialize_app_settings
from agentchat.utils.file_utils import get_object_key_from_public_url, get_save_tempfile


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
    await initialize_app_settings("/app/agentchat/config.yaml")
    from agentchat.services.rag.parser import DocParser

    parser = DocParser()
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
                chunks = await parser.parse_doc_into_chunks(
                    knowledge_file.id,
                    local_path,
                    knowledge_id,
                )
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
