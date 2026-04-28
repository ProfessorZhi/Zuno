from typing import Dict, List, Optional

from loguru import logger
from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility

from agentchat.schema.search import SearchModel
from agentchat.services.rag.embedding import get_embedding
from agentchat.services.rag.vl_embedding import get_vl_image_embedding, get_vl_text_embedding
from agentchat.settings import app_settings


class MilvusLiteClient:
    def __init__(self, **kwargs):
        self.milvus_host = app_settings.rag.vector_db.get("host")
        self.milvus_port = app_settings.rag.vector_db.get("port")
        self.collections: Dict[str, Collection] = {}
        self.loaded_collections: set = set()
        self._connect()

    @staticmethod
    def _image_collection_name(collection_name: str) -> str:
        return f"{collection_name}__vl"

    def _connect(self):
        connections.connect("default", host=self.milvus_host, port=self.milvus_port)
        logger.info(f"Successfully connected to Milvus at {self.milvus_host}:{self.milvus_port}")

    def _collection_exists(self, collection_name: str) -> bool:
        return utility.has_collection(collection_name)

    def _ensure_collection_loaded(self, collection: Collection) -> bool:
        if collection.name in self.loaded_collections:
            return True
        try:
            collection.load()
            self.loaded_collections.add(collection.name)
            return True
        except Exception as err:
            logger.error(f"Failed to load collection '{collection.name}': {err}")
            return False

    def _get_collection_safe(self, collection_name: str) -> Optional[Collection]:
        if collection_name not in self.collections:
            if not self._collection_exists(collection_name):
                return None
            self.collections[collection_name] = Collection(collection_name)
        collection = self.collections[collection_name]
        self._ensure_collection_loaded(collection)
        return collection

    async def create_collection(self, collection_name: str):
        if self._collection_exists(collection_name):
            self.collections[collection_name] = Collection(collection_name)
            return

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="chunk_id", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=4096),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024),
            FieldSchema(name="summary", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="file_id", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="file_name", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="knowledge_id", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="update_time", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="source_url", dtype=DataType.VARCHAR, max_length=1024),
        ]
        collection = Collection(collection_name, CollectionSchema(fields, description=f"RAG Collection: {collection_name}"))
        collection.create_index("embedding", {"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 128}})
        collection.load()
        self.collections[collection_name] = collection
        self.loaded_collections.add(collection_name)

    async def _search_collection(
        self,
        *,
        collection_name: str,
        query_embedding: list[float],
        top_k: int,
        modality: str,
    ) -> List[SearchModel]:
        collection = self._get_collection_safe(collection_name)
        if not collection:
            return []

        try:
            results = collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param={"metric_type": "L2", "params": {"nprobe": 16}},
                limit=top_k,
                output_fields=["content", "chunk_id", "summary", "file_id", "file_name", "knowledge_id", "update_time", "source_url"],
            )
            documents = []
            for hit in results[0]:
                documents.append(
                    SearchModel(
                        content=hit.entity.content,
                        chunk_id=hit.entity.chunk_id,
                        file_id=hit.entity.file_id,
                        file_name=hit.entity.file_name,
                        knowledge_id=hit.entity.knowledge_id,
                        update_time=hit.entity.update_time,
                        summary=hit.entity.summary,
                        score=hit.distance,
                        modality=modality,
                        source_url=getattr(hit.entity, "source_url", ""),
                    )
                )
            return documents
        except Exception as err:
            logger.error(f"Search failed in collection '{collection_name}': {err}")
            return []

    async def search(self, query: str, collection_name: str, top_k: int = 10, config_override=None) -> List[SearchModel]:
        query_embedding = await get_embedding(query, config_override=config_override)
        return await self._search_collection(
            collection_name=collection_name,
            query_embedding=query_embedding,
            top_k=top_k,
            modality="text",
        )

    async def search_summary(self, query: str, collection_name: str, top_k: int = 10):
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

        results = collection.query(f'file_id == "{file_id}"', output_fields=["id"])
        delete_ids = [result["id"] for result in results]
        if not delete_ids:
            return True
        collection.delete(f"id in {delete_ids}")
        collection.flush()
        return True

    async def delete_by_file_id(self, file_id: str, collection_name: str) -> bool:
        return await self._delete_by_file_id_from_collection(file_id, collection_name)

    async def delete_image_by_file_id(self, file_id: str, collection_name: str) -> bool:
        return await self._delete_by_file_id_from_collection(file_id, self._image_collection_name(collection_name))

    async def _insert_collection(self, collection_name: str, chunks, embeddings: list[list[float]]) -> bool:
        if collection_name not in self.collections:
            await self.create_collection(collection_name)
        collection = self._get_collection_safe(collection_name)
        if not collection:
            return False

        data = [
            [chunk.chunk_id for chunk in chunks],
            [chunk.content for chunk in chunks],
            embeddings,
            [chunk.summary for chunk in chunks],
            [chunk.file_id for chunk in chunks],
            [chunk.file_name for chunk in chunks],
            [chunk.knowledge_id for chunk in chunks],
            [chunk.update_time for chunk in chunks],
            [chunk.source_url for chunk in chunks],
        ]
        collection.insert(data)
        collection.flush()
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
            if self._collection_exists(target):
                Collection(target).drop()
                self.collections.pop(target, None)
                self.loaded_collections.discard(target)
                deleted = True
        return deleted

    def unload_collection(self, collection_name: str) -> bool:
        try:
            for target in [collection_name, self._image_collection_name(collection_name)]:
                if target in self.collections:
                    self.collections[target].release()
                    self.loaded_collections.discard(target)
            return True
        except Exception as err:
            logger.error(f"Failed to unload collection '{collection_name}': {err}")
            return False

    def get_loaded_collections(self) -> List[str]:
        return list(self.loaded_collections)

    def get_all_collections(self) -> List[str]:
        try:
            return utility.list_collections()
        except Exception as err:
            logger.error(f"Failed to get collection list: {err}")
            return []

    def close(self):
        try:
            for collection_name in list(self.loaded_collections):
                self.unload_collection(collection_name)
            connections.disconnect("default")
        except Exception as err:
            logger.error(f"Error closing Milvus connection: {err}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
