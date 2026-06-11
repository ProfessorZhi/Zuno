from typing import Dict, List, Optional

import chromadb
from loguru import logger

from agentchat.schema.search import SearchModel
from agentchat.services.rag.embedding import get_embedding
from agentchat.services.rag.vl_embedding import get_vl_image_embedding, get_vl_text_embedding


class ChromaClient:
    def __init__(self, **kwargs):
        self.collections: Dict[str, chromadb.Collection] = {}
        self.client = chromadb.PersistentClient(path="./vector_db")
        logger.info("Successfully connected to Chroma")

    @staticmethod
    def _image_collection_name(collection_name: str) -> str:
        return f"{collection_name}__vl"

    def _get_collection_safe(self, collection_name: str) -> Optional[chromadb.Collection]:
        try:
            if collection_name not in self.collections:
                self.collections[collection_name] = self.client.get_collection(collection_name)
            return self.collections[collection_name]
        except Exception:
            return None

    async def create_collection(self, collection_name: str):
        if self._get_collection_safe(collection_name):
            return
        self.collections[collection_name] = self.client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    async def _search_collection(self, *, collection_name: str, query_embedding: list[float], top_k: int, modality: str):
        collection = self._get_collection_safe(collection_name)
        if not collection:
            return []
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, 100),
            include=["metadatas", "documents", "distances"],
        )
        documents = []
        for i in range(len(results.get("ids", [[]])[0])):
            metadata = results["metadatas"][0][i] or {}
            documents.append(
                SearchModel(
                    content=results["documents"][0][i] or "",
                    chunk_id=metadata.get("chunk_id", ""),
                    file_id=metadata.get("file_id", ""),
                    file_name=metadata.get("file_name", ""),
                    knowledge_id=metadata.get("knowledge_id", ""),
                    update_time=metadata.get("update_time", ""),
                    summary=metadata.get("summary", ""),
                    score=1.0 - results["distances"][0][i],
                    modality=modality,
                    source_url=metadata.get("source_url", ""),
                )
            )
        return documents

    async def search(self, query: str, collection_name: str, top_k: int = 10, config_override=None) -> List[SearchModel]:
        query_embeddings = await get_embedding([query], config_override=config_override)
        if not query_embeddings:
            return []
        return await self._search_collection(
            collection_name=collection_name,
            query_embedding=query_embeddings[0],
            top_k=top_k,
            modality="text",
        )

    async def search_summary(self, query: str, collection_name: str, top_k: int = 10) -> List[SearchModel]:
        return []

    async def search_image(self, query: str, collection_name: str, top_k: int = 10, config_override=None) -> List[SearchModel]:
        query_embeddings = await get_vl_text_embedding([query], config_override=config_override)
        if not query_embeddings:
            return []
        return await self._search_collection(
            collection_name=self._image_collection_name(collection_name),
            query_embedding=query_embeddings[0],
            top_k=top_k,
            modality="image",
        )

    async def _delete_by_file_id_from_collection(self, file_id: str, collection_name: str) -> bool:
        collection = self._get_collection_safe(collection_name)
        if not collection:
            return True
        collection.delete(where={"file_id": file_id})
        return True

    async def delete_by_file_id(self, file_id: str, collection_name: str) -> bool:
        return await self._delete_by_file_id_from_collection(file_id, collection_name)

    async def delete_image_by_file_id(self, file_id: str, collection_name: str) -> bool:
        return await self._delete_by_file_id_from_collection(file_id, self._image_collection_name(collection_name))

    async def _insert_collection(self, collection_name: str, chunks, embeddings: list[list[float]]) -> bool:
        if not self._get_collection_safe(collection_name):
            await self.create_collection(collection_name)
        collection = self._get_collection_safe(collection_name)
        collection.add(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.content for chunk in chunks],
            embeddings=embeddings,
            metadatas=[
                {
                    "chunk_id": chunk.chunk_id,
                    "file_id": chunk.file_id,
                    "file_name": chunk.file_name or "",
                    "knowledge_id": chunk.knowledge_id or "",
                    "update_time": chunk.update_time or "",
                    "summary": chunk.summary or "",
                    "source_url": chunk.source_url or "",
                }
                for chunk in chunks
            ],
        )
        return True

    async def insert(self, collection_name: str, chunks, config_override=None) -> bool:
        text_chunks = [chunk for chunk in chunks if getattr(chunk, "modality", "text") == "text"]
        if not text_chunks:
            return True
        embeddings = await get_embedding([chunk.content for chunk in text_chunks], config_override=config_override)
        return await self._insert_collection(collection_name, text_chunks, embeddings)

    async def insert_image_chunks(self, collection_name: str, chunks, config_override=None) -> bool:
        image_chunks = [chunk for chunk in chunks if getattr(chunk, "modality", "text") == "image" and chunk.source_url]
        if not image_chunks:
            return True
        embeddings = await get_vl_image_embedding([chunk.source_url for chunk in image_chunks], config_override=config_override)
        if len(embeddings) != len(image_chunks):
            logger.error(f"VL embedding count mismatch for collection '{collection_name}'")
            return False
        return await self._insert_collection(self._image_collection_name(collection_name), image_chunks, embeddings)

    async def delete_collection(self, collection_name: str) -> bool:
        deleted = False
        for target in [collection_name, self._image_collection_name(collection_name)]:
            try:
                self.client.delete_collection(target)
                self.collections.pop(target, None)
                deleted = True
            except Exception:
                pass
        return deleted

    def unload_collection(self, collection_name: str) -> bool:
        self.collections.pop(collection_name, None)
        self.collections.pop(self._image_collection_name(collection_name), None)
        return True

    def get_loaded_collections(self) -> List[str]:
        return list(self.collections.keys())

    def get_all_collections(self) -> List[str]:
        return [col.name for col in self.client.list_collections()]

    def close(self):
        self.collections.clear()
        self.client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
