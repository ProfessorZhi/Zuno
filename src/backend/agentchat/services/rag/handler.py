from typing import Optional

from loguru import logger

from agentchat.api.services.knowledge import KnowledgeService
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
    async def index_milvus_documents(cls, collection_name, chunks, *, text_embedding_config=None, vl_embedding_config=None):
        await milvus_client.insert(collection_name, chunks, config_override=text_embedding_config)
        await milvus_client.insert_image_chunks(collection_name, chunks, config_override=vl_embedding_config)

    @classmethod
    async def index_es_documents(cls, index_name, chunks):
        await es_client.index_documents(index_name, chunks)

    @classmethod
    async def _resolve_runtime_settings(cls, knowledge_ids: list[str]):
        if not knowledge_ids:
            return {
                "knowledge_config": {
                    "index_settings": {"image_indexing_mode": "dual"},
                    "retrieval_settings": {
                        "top_k": app_settings.rag.retrival.get("top_k"),
                        "rerank_enabled": True,
                        "rerank_top_k": app_settings.rag.retrival.get("top_k"),
                        "score_threshold": app_settings.rag.retrival.get("min_score"),
                        "default_mode": "rag",
                    },
                },
                "text_embedding_config": None,
                "vl_embedding_config": None,
                "rerank_config": None,
            }
        return await KnowledgeService.get_runtime_settings(knowledge_ids[0])

    @classmethod
    async def mix_retrival_documents(cls, query_list, knowledges_id, search_field="summary", runtime_settings=None, top_k=None):
        runtime_settings = runtime_settings or await cls._resolve_runtime_settings(knowledges_id)
        knowledge_config = runtime_settings["knowledge_config"]
        retrieval_settings = knowledge_config.get("retrieval_settings", {})
        index_settings = knowledge_config.get("index_settings", {})
        actual_top_k = top_k or retrieval_settings.get("top_k") or app_settings.rag.retrival.get("top_k") or 5

        if app_settings.rag.enable_elasticsearch:
            es_documents, milvus_documents = await MixRetrival.mix_retrival_documents(
                query_list,
                knowledges_id,
                search_field,
                top_k=actual_top_k,
                text_embedding_config=runtime_settings.get("text_embedding_config"),
                vl_embedding_config=runtime_settings.get("vl_embedding_config"),
                image_indexing_mode=index_settings.get("image_indexing_mode", "dual"),
            )
            es_documents.sort(key=lambda x: x.score, reverse=True)
            milvus_documents.sort(key=lambda x: x.score, reverse=True)
            all_documents = es_documents + milvus_documents
        else:
            all_documents = await MixRetrival.retrival_milvus_documents(
                query_list,
                knowledges_id,
                search_field,
                top_k=actual_top_k,
                text_embedding_config=runtime_settings.get("text_embedding_config"),
                vl_embedding_config=runtime_settings.get("vl_embedding_config"),
                image_indexing_mode=index_settings.get("image_indexing_mode", "dual"),
            )

        documents = []
        seen_chunk_ids = set()
        all_documents.sort(key=lambda x: x.score, reverse=True)
        for doc in all_documents:
            if doc.chunk_id not in seen_chunk_ids:
                seen_chunk_ids.add(doc.chunk_id)
                documents.append(doc)
                if len(documents) >= actual_top_k * 2:
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
        runtime_settings = await cls._resolve_runtime_settings(knowledges_id)
        retrieval_settings = runtime_settings["knowledge_config"].get("retrieval_settings", {})
        if min_score is None:
            min_score = retrieval_settings.get("score_threshold")
        if top_k is None:
            top_k = retrieval_settings.get("top_k") or app_settings.rag.retrival.get("top_k")

        rewritten_queries = await cls.query_rewrite(query) if needs_query_rewrite else [query]
        retrieved_documents = await cls.mix_retrival_documents(
            rewritten_queries,
            knowledges_id,
            "summary",
            runtime_settings=runtime_settings,
            top_k=top_k,
        )
        documents_to_rerank = [doc.content for doc in retrieved_documents]
        reranked_docs = await Reranker.rerank_documents(
            query,
            documents_to_rerank,
            config_override=runtime_settings.get("rerank_config"),
            top_n=retrieval_settings.get("rerank_top_k") or top_k,
        )

        filtered_results = []
        actual_top_k = top_k if top_k is not None else 0
        if len(reranked_docs) >= actual_top_k:
            for doc in reranked_docs[:actual_top_k]:
                if min_score is None or doc.score >= min_score:
                    filtered_results.append(doc)
            return "\n".join(result.content for result in filtered_results)

        logger.info("Recall for summary field numbers < top k, fallback to content field")
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
        runtime_settings = await cls._resolve_runtime_settings(collection_names)
        retrieval_settings = runtime_settings["knowledge_config"].get("retrieval_settings", {})
        if min_score is None:
            min_score = retrieval_settings.get("score_threshold")
        if top_k is None:
            top_k = retrieval_settings.get("top_k") or app_settings.rag.retrival.get("top_k")

        rewritten_queries = await cls.query_rewrite(query) if needs_query_rewrite else [query]
        retrieved_documents = await cls.mix_retrival_documents(
          rewritten_queries,
          collection_names,
          "content",
          runtime_settings=runtime_settings,
          top_k=top_k,
        )
        documents_to_rerank = [doc.content for doc in retrieved_documents]

        rerank_enabled = retrieval_settings.get("rerank_enabled", False)
        if rerank_enabled:
            reranked_docs = await Reranker.rerank_documents(
                query,
                documents_to_rerank,
                config_override=runtime_settings.get("rerank_config"),
                top_n=retrieval_settings.get("rerank_top_k") or top_k,
            )
        else:
            reranked_docs = Reranker._fallback_documents(query, documents_to_rerank)

        filtered_results = []
        actual_top_k = top_k if top_k is not None else 0
        docs_to_process = reranked_docs if len(reranked_docs) <= actual_top_k else reranked_docs[:actual_top_k]
        for doc in docs_to_process:
            if min_score is None or doc.score >= min_score:
                filtered_results.append(doc)

        if not filtered_results:
            return "No relevant documents found."

        return "\n".join(result.content for result in filtered_results)

    @classmethod
    async def _retrieve_ranked_documents_rag_detail(
        cls,
        query,
        collection_names,
        index_names=None,
        min_score: Optional[float] = None,
        top_k: Optional[int] = None,
        needs_query_rewrite: bool = True,
    ):
        runtime_settings = await cls._resolve_runtime_settings(collection_names)
        retrieval_settings = runtime_settings["knowledge_config"].get("retrieval_settings", {})
        if min_score is None:
            min_score = retrieval_settings.get("score_threshold")
        if top_k is None:
            top_k = retrieval_settings.get("top_k") or app_settings.rag.retrival.get("top_k")

        rewritten_queries = await cls.query_rewrite(query) if needs_query_rewrite else [query]
        retrieved_documents = await cls.mix_retrival_documents(
          rewritten_queries,
          collection_names,
          "content",
          runtime_settings=runtime_settings,
          top_k=top_k,
        )
        documents_to_rerank = [doc.content for doc in retrieved_documents]

        rerank_enabled = retrieval_settings.get("rerank_enabled", False)
        if rerank_enabled:
            reranked_docs = await Reranker.rerank_documents(
                query,
                documents_to_rerank,
                config_override=runtime_settings.get("rerank_config"),
                top_n=retrieval_settings.get("rerank_top_k") or top_k,
            )
        else:
            reranked_docs = Reranker._fallback_documents(query, documents_to_rerank)

        filtered_results = []
        actual_top_k = top_k if top_k is not None else 0
        docs_to_process = reranked_docs if len(reranked_docs) <= actual_top_k else reranked_docs[:actual_top_k]
        for doc in docs_to_process:
            if min_score is None or doc.score >= min_score:
                filtered_results.append(doc)

        raw_content = "\n".join(result.content for result in filtered_results)
        return {
            "content": raw_content or "No relevant documents found.",
            "raw_content": raw_content,
            "documents": [result.to_dict() for result in filtered_results],
            "document_count": len(filtered_results),
            "requested_top_k": actual_top_k,
            "top_score": max((result.score for result in filtered_results), default=None),
            "score_threshold": min_score,
            "rerank_enabled": rerank_enabled,
        }

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
        result = await cls.retrieve_ranked_documents_with_metadata(
            query,
            collection_names,
            index_names,
            min_score=min_score,
            top_k=top_k,
            needs_query_rewrite=needs_query_rewrite,
            retrieval_mode=retrieval_mode,
        )
        return result["content"]

    @classmethod
    async def retrieve_ranked_documents_with_metadata(
        cls,
        query,
        collection_names,
        index_names=None,
        min_score: Optional[float] = None,
        top_k: Optional[int] = None,
        needs_query_rewrite: bool = True,
        retrieval_mode: str = "rag",
    ):
        runtime_settings = await cls._resolve_runtime_settings(collection_names)
        default_mode = runtime_settings["knowledge_config"].get("retrieval_settings", {}).get("default_mode", "rag")
        normalized_mode = normalize_retrieval_mode(retrieval_mode or default_mode)

        orchestrator = RetrievalOrchestrator()
        return await orchestrator.run(
            mode=normalized_mode,
            query=query,
            knowledge_ids=collection_names,
        )

    @classmethod
    async def delete_documents_es_milvus(cls, file_id, knowledge_id):
        if app_settings.rag.enable_elasticsearch:
            await es_client.delete_documents(file_id, knowledge_id)
        await milvus_client.delete_by_file_id(file_id, knowledge_id)
        await milvus_client.delete_image_by_file_id(file_id, knowledge_id)
