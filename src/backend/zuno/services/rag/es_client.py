import json
from typing import List

from elasticsearch import Elasticsearch
from loguru import logger

from zuno.config.es_index import ESIndex
from zuno.schema.chunk import ChunkModel
from zuno.schema.search import SearchModel
from zuno.settings import app_settings


class ESClient:
    def __init__(self):
        self.client = Elasticsearch(hosts=app_settings.rag.elasticsearch.get("hosts"))

    async def insert_documents(self, index_name, chunks: List[ChunkModel]):
        index_config = json.loads(ESIndex.index_config)

        if not self.client.indices.exists(index=index_name):
            try:
                self.client.indices.create(index=index_name, body=index_config)
                logger.info(f"index name: {index_name} 创建成功")
            except Exception as exc:
                logger.error(f"index name {index_name} error: {exc}")
                raise ValueError("index create error")
        try:
            for chunk in chunks:
                self.client.index(
                    index=index_name,
                    body=chunk.to_dict(),
                )
                logger.info(f"chunk id: {chunk.chunk_id} 已存到索引中")
        except Exception as exc:
            logger.error(f"索引增加数据失败: {exc}")
        finally:
            await self.close()

    async def index_documents(self, index_name, chunks):
        await self.insert_documents(index_name, chunks)

    async def search_documents(self, query, index_name):
        index_search = json.loads(ESIndex.index_search_content.format(query=query))

        documents = []
        try:
            response = self.client.search(index=index_name, body=index_search)
            hits = response["hits"]
            if not hits.get("max_score"):
                return documents
            for hit in hits.get("hits", []):
                documents.append(
                    SearchModel(
                        score=hit["_score"],
                        chunk_id=hit["_source"]["chunk_id"],
                        update_time=hit["_source"]["update_time"],
                        content=hit["_source"]["content"],
                        file_name=hit["_source"]["file_name"],
                        summary=hit["_source"]["summary"],
                        file_id=hit["_source"]["file_id"],
                        knowledge_id=hit["_source"]["knowledge_id"],
                        document_hash=hit["_source"].get("document_hash", ""),
                        chunk_hash=hit["_source"].get("chunk_hash", ""),
                    )
                )
        except Exception as exc:
            logger.error(f"Search documents error: {exc}")
        finally:
            await self.close()
            return documents

    async def search_documents_summary(self, query, index_name):
        index_search = json.loads(ESIndex.index_search_summary.format(query=query))

        documents = []
        try:
            response = self.client.search(index=index_name, body=index_search)
            hits = response["hits"]
            if not hits.get("max_score"):
                return documents

            for hit in hits.get("hits", []):
                documents.append(
                    SearchModel(
                        score=hit["_score"],
                        chunk_id=hit["_source"]["chunk_id"],
                        update_time=hit["_source"]["update_time"],
                        content=hit["_source"]["content"],
                        file_name=hit["_source"]["file_name"],
                        summary=hit["_source"]["summary"],
                        file_id=hit["_source"]["file_id"],
                        knowledge_id=hit["_source"]["knowledge_id"],
                        document_hash=hit["_source"].get("document_hash", ""),
                        chunk_hash=hit["_source"].get("chunk_hash", ""),
                    )
                )
        except Exception as exc:
            logger.error(f"Search documents summary error: {exc}")
        finally:
            await self.close()
            return documents

    async def delete_documents(self, file_id, index_name):
        try:
            delete_query = json.loads(ESIndex.index_delete.format(file_id=file_id))
            self.client.delete_by_query(index=index_name, body=delete_query)
            logger.info(f"Success delete documents in file id: {file_id}")
        except Exception as exc:
            logger.error(f"Delete documents Error: {exc}")

    async def close(self):
        pass


class LazyESClient:
    def __init__(self):
        self._client = None

    def _get_client(self) -> ESClient:
        if self._client is None:
            self._client = ESClient()
        return self._client

    def __getattr__(self, item):
        return getattr(self._get_client(), item)


client = LazyESClient()


__all__ = ["ESClient", "LazyESClient", "client"]
