from typing import Optional

from loguru import logger

from agentchat.services.graphrag.models import normalize_retrieval_mode
from agentchat.services.graphrag.orchestrator import RetrievalOrchestrator
from agentchat.services.rag.es_client import client as es_client
from agentchat.services.rag.rerank import Reranker
from agentchat.services.rag.retrieval import MixRetrival
from agentchat.services.rag.vector_db import milvus_client
from agentchat.services.rewrite.query_write import query_rewriter
from agentchat.settings import app_settings


class RagHandler:
    @classmethod
    async def query_rewrite(cls, query):
        query_list = await query_rewriter.rewrite(query)
        return query_list

    @classmethod
    async def index_milvus_documents(cls, collection_name, chunks):
        await milvus_client.insert(collection_name, chunks)

    @classmethod
    async def index_es_documents(cls, index_name, chunks):
        await es_client.index_documents(index_name, chunks)

    @classmethod
    async def mix_retrival_documents(cls, query_list, knowledges_id, search_field="summary"):
        if app_settings.rag.enable_elasticsearch:
            es_documents, milvus_documents = await MixRetrival.mix_retrival_documents(
                query_list,
                knowledges_id,
                search_field,
            )
            es_documents.sort(key=lambda x: x.score, reverse=True)
            milvus_documents.sort(key=lambda x: x.score, reverse=True)
            all_documents = es_documents + milvus_documents
        else:
            all_documents = await MixRetrival.retrival_milvus_documents(query_list, knowledges_id, search_field)

        documents = []
        seen_chunk_ids = set()
        all_documents.sort(key=lambda x: x.score, reverse=True)
        for doc in all_documents:
            if doc.chunk_id not in seen_chunk_ids:
                seen_chunk_ids.add(doc.chunk_id)
                documents.append(doc)
                if len(documents) >= 10:
                    break
        return documents

    @classmethod
    async def rag_query_summary(
        cls,
        query,
        knowledges_id,
        min_score: Optional[float] = None,
        top_k: Optional[int] = None,
        needs_query_rewrite: bool = True,
    ):
        if min_score is None:
            min_score = app_settings.rag.retrival.get("min_score")
        if top_k is None:
            top_k = app_settings.rag.retrival.get("top_k")

        rewritten_queries = await cls.query_rewrite(query) if needs_query_rewrite else [query]
        retrieved_documents = await cls.mix_retrival_documents(rewritten_queries, knowledges_id, "summary")
        documents_to_rerank = [doc.content for doc in retrieved_documents]
        reranked_docs = await Reranker.rerank_documents(query, documents_to_rerank)

        filtered_results = []
        actual_top_k = top_k if top_k is not None else 0
        if len(reranked_docs) >= actual_top_k:
            for doc in reranked_docs[:actual_top_k]:
                if min_score is not None and doc.score >= min_score:
                    filtered_results.append(doc)
            return "\n".join(result.content for result in filtered_results)

        logger.info("Recall for summary Field numbers < top k, Start recall use content Field")
        return await cls._retrieve_ranked_documents_rag(query, knowledges_id, knowledges_id)

    @classmethod
    async def _retrieve_ranked_documents_rag(
        cls,
        query,
        collection_names,
        index_names=None,
        min_score: Optional[float] = None,
        top_k: Optional[int] = None,
        needs_query_rewrite: bool = True,
    ):
        if min_score is None:
            min_score = app_settings.rag.retrival.get("min_score")
        if top_k is None:
            top_k = app_settings.rag.retrival.get("top_k")

        rewritten_queries = await cls.query_rewrite(query) if needs_query_rewrite else [query]
        retrieved_documents = await cls.mix_retrival_documents(rewritten_queries, collection_names, "content")
        documents_to_rerank = [doc.content for doc in retrieved_documents]
        reranked_docs = await Reranker.rerank_documents(query, documents_to_rerank)

        filtered_results = []
        actual_top_k = top_k if top_k is not None else 0
        docs_to_process = reranked_docs if len(reranked_docs) <= actual_top_k else reranked_docs[:actual_top_k]
        for doc in docs_to_process:
            if min_score is not None and doc.score >= min_score:
                filtered_results.append(doc)

        if not filtered_results:
            return "No relevant documents found."

        return "\n".join(result.content for result in filtered_results)

    @classmethod
    async def retrieve_ranked_documents(
        cls,
        query,
        collection_names,
        index_names=None,
        min_score: Optional[float] = None,
        top_k: Optional[int] = None,
        needs_query_rewrite: bool = True,
        retrieval_mode: str = "rag",
    ):
        normalized_mode = normalize_retrieval_mode(retrieval_mode)
        if normalized_mode in {"default", "rag"}:
            return await cls._retrieve_ranked_documents_rag(
                query,
                collection_names,
                index_names,
                min_score=min_score,
                top_k=top_k,
                needs_query_rewrite=needs_query_rewrite,
            )

        orchestrator = RetrievalOrchestrator()
        result = await orchestrator.run(
            mode=normalized_mode,
            query=query,
            knowledge_ids=collection_names,
        )
        return result["content"]

    @classmethod
    async def delete_documents_es_milvus(cls, file_id, knowledge_id):
        if app_settings.rag.enable_elasticsearch:
            await es_client.delete_documents(file_id, knowledge_id)
        await milvus_client.delete_by_file_id(file_id, knowledge_id)
