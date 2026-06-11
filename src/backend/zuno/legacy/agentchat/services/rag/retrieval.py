from agentchat.services.rag.es_client import client as es_client
from agentchat.services.rag.vector_db import milvus_client


class MixRetrival:
    @classmethod
    async def retrival_milvus_documents(
        cls,
        query,
        knowledges_id,
        search_field,
        *,
        top_k: int = 10,
        text_embedding_config=None,
        vl_embedding_config=None,
        image_indexing_mode: str = "dual",
    ):
        documents = []
        queries = query if isinstance(query, list) else [query]

        for current_query in queries:
            for knowledge_id in knowledges_id:
                if search_field == "summary":
                    documents += await milvus_client.search_summary(current_query, knowledge_id, top_k=top_k)
                else:
                    documents += await milvus_client.search(
                        current_query,
                        knowledge_id,
                        top_k=top_k,
                        config_override=text_embedding_config,
                    )
                    if image_indexing_mode != "text_only":
                        documents += await milvus_client.search_image(
                            current_query,
                            knowledge_id,
                            top_k=top_k,
                            config_override=vl_embedding_config,
                        )

        return documents

    @classmethod
    async def retrival_es_documents(cls, query, knowledges_id, search_field):
        documents = []
        queries = query if isinstance(query, list) else [query]

        for current_query in queries:
            for knowledge_id in knowledges_id:
                if search_field == "summary":
                    documents += await es_client.search_documents_summary(current_query, knowledge_id)
                else:
                    documents += await es_client.search_documents(current_query, knowledge_id)

        return documents

    @classmethod
    async def mix_retrival_documents(cls, query_list, knowledges_id, search_field, **kwargs):
        es_documents = []
        milvus_documents = []
        for query in query_list:
            es_documents += await cls.retrival_es_documents(query, knowledges_id, search_field)
            milvus_documents += await cls.retrival_milvus_documents(query, knowledges_id, search_field, **kwargs)

        return es_documents, milvus_documents
