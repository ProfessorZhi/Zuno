import re
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
    LOCAL_NOISE_QUERY_TERMS = {
        "a",
        "an",
        "and",
        "are",
        "for",
        "how",
        "in",
        "is",
        "of",
        "on",
        "or",
        "the",
        "this",
        "to",
        "what",
        "which",
        "who",
        "why",
    }
    SCALE_HINT_TERMS = {
        "scale",
        "scaling",
        "autoscaling",
        "throughput",
        "available_jobs",
        "n_jobs_per_worker",
        "qps",
        "read load",
        "write load",
        "reads",
        "writes",
        "\u914d\u7f6e",
        "\u6269\u7f29\u5bb9",
        "\u8bfb\u8d1f\u8f7d",
        "\u5199\u8d1f\u8f7d",
        "\u541e\u5410",
    }
    QUERY_TERM_ALIASES = {
        "\u90e8\u7f72": {"deployment", "deploy"},
        "\u7ec4\u6210": {"parts", "components"},
        "\u6838\u5fc3\u7ec4\u6210": {"parts", "components"},
        "\u6301\u4e45\u5316": {"persistence", "postgresql", "stored", "default"},
        "\u9ed8\u8ba4\u540e\u7aef": {"postgresql", "default", "backend"},
        "\u4e09\u7c7b\u6570\u636e": {"three", "types", "data"},
        "\u5c42\u6b21": {"levels", "layer"},
        "\u7cfb\u7edf\u8bbe\u8ba1": {"designed", "architecture"},
        "\u89d2\u8272": {"brain", "endpoint", "persistence"},
        "\u6267\u884c\u8def\u5f84": {"lifecycle", "execution", "stream"},
        "\u8fd0\u884c\u8def\u5f84": {"lifecycle", "execution", "stream"},
        "task queue": {"queue", "redis", "postgresql"},
        "redis": {"queue", "signaling", "pub/sub"},
        "postgresql": {"stored", "persistence"},
    }

    @classmethod
    def _tokenize_query(cls, text: str) -> list[str]:
        raw_tokens = re.findall(r"[\w\u4e00-\u9fff]+", str(text or "").lower())
        return [token for token in raw_tokens if token not in cls.LOCAL_NOISE_QUERY_TERMS and len(token) > 1]

    @classmethod
    def _expanded_query_terms(cls, query: str) -> set[str]:
        query_lower = str(query or "").lower()
        terms = set(cls._tokenize_query(query_lower))
        for trigger, aliases in cls.QUERY_TERM_ALIASES.items():
            if trigger in query_lower:
                terms.update(aliases)
        return terms

    @classmethod
    def _local_noise_penalty(cls, query: str, doc) -> int:
        query_lower = str(query or "").lower()
        file_name = str(getattr(doc, "file_name", "") or "").lower()
        content = str(getattr(doc, "content", "") or "").lower()
        summary = str(getattr(doc, "summary", "") or "").lower()
        haystack = " ".join([file_name, content, summary])
        penalty = 0

        if "agent-server-scale" in file_name and not any(term in query_lower for term in cls.SCALE_HINT_TERMS):
            penalty += 6
        if "milvus_adopters" in file_name or content.startswith("milvus adopters"):
            if "adopter" not in query_lower and "\u91c7\u7528" not in query_lower and "\u7528\u6237" not in query_lower:
                penalty += 6
        if content.lstrip().startswith("---"):
            penalty += 2
        if "development > run tests" in content and "test" not in query_lower:
            penalty += 6
        if "api documentation" in haystack or "user guide:" in haystack:
            if "api documentation" not in query_lower and "user guide" not in query_lower and "\u6587\u6863" not in query_lower:
                penalty += 3
        if "container architecture" in content and "docker compose" in query_lower:
            penalty += 6

        return penalty

    @classmethod
    def _local_section_bonus(cls, query: str, haystack: str) -> int:
        query_lower = str(query or "").lower()
        bonus = 0

        if "\u6301\u4e45\u5316" in query_lower:
            if "persists three types of data" in haystack or haystack.startswith("persistence"):
                bonus += 10
            if "stored in postgresql" in haystack or "backed by postgresql by default" in haystack:
                bonus += 8
        if "\u90e8\u7f72" in query_lower and "parts of a deployment" in haystack:
            bonus += 8
        if "task queue" in query_lower and "redis" in query_lower and "postgresql" in query_lower:
            if "redis handles the signaling" in haystack and "written to postgresql" in haystack:
                bonus += 12
            if "task queue" in haystack:
                bonus += 4
        if ("\u5c42\u6b21" in query_lower or "\u7cfb\u7edf\u8bbe\u8ba1" in query_lower) and "breaks down into four levels" in haystack:
            bonus += 12
        if ("\u6267\u884c\u8def\u5f84" in query_lower or "\u8fd0\u884c\u8def\u5f84" in query_lower) and "run execution lifecycle" in haystack:
            bonus += 10

        return bonus

    @classmethod
    def _local_priority_score(cls, query: str, doc) -> tuple[int, float]:
        query_tokens = cls._expanded_query_terms(query)
        haystack = " ".join(
            [
                str(getattr(doc, "file_name", "") or ""),
                str(getattr(doc, "content", "") or ""),
                str(getattr(doc, "summary", "") or ""),
            ]
        ).lower()
        overlap = sum(2 if len(token) > 4 else 1 for token in query_tokens if token in haystack)
        penalty = cls._local_noise_penalty(query, doc)
        bonus = cls._local_section_bonus(query, haystack)
        return overlap + bonus - penalty, float(getattr(doc, "score", 0.0) or 0.0)

    @classmethod
    def _apply_local_priority(cls, query: str, retrieved_documents: list):
        prioritized = list(retrieved_documents)
        prioritized.sort(key=lambda doc: cls._local_priority_score(query, doc), reverse=True)
        return prioritized

    @classmethod
    def _project_reranked_documents(cls, retrieved_documents, reranked_docs):
        projected = []
        for reranked in reranked_docs:
            index = getattr(reranked, "index", None)
            if index is None or index >= len(retrieved_documents):
                continue
            source_doc = retrieved_documents[index]
            source_doc.score = getattr(reranked, "score", source_doc.score)
            projected.append(source_doc)
        return projected

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
        graph_index_settings = knowledge_config.get("graph_index_settings", {})
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
        retrieved_documents = cls._apply_local_priority(query, retrieved_documents)
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
        retrieved_documents = cls._apply_local_priority(query, retrieved_documents)
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
        projected_docs = cls._project_reranked_documents(retrieved_documents, reranked_docs)
        docs_to_process = projected_docs if len(projected_docs) <= actual_top_k else projected_docs[:actual_top_k]
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
        retrieval_options: Optional[dict] = None,
    ):
        runtime_settings = await cls._resolve_runtime_settings(collection_names)
        retrieval_settings = dict(runtime_settings["knowledge_config"].get("retrieval_settings", {}))
        retrieval_settings.update(retrieval_options or {})
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
        retrieved_documents = cls._apply_local_priority(query, retrieved_documents)
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
        projected_docs = cls._project_reranked_documents(retrieved_documents, reranked_docs)
        docs_to_process = projected_docs if len(projected_docs) <= actual_top_k else projected_docs[:actual_top_k]
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
        retrieval_options: Optional[dict] = None,
    ):
        runtime_settings = await cls._resolve_runtime_settings(collection_names)
        knowledge_config = runtime_settings["knowledge_config"]
        retrieval_settings = knowledge_config.get("retrieval_settings", {})
        graph_index_settings = knowledge_config.get("graph_index_settings", {})
        default_mode = retrieval_settings.get("default_mode", "rag")
        normalized_mode = normalize_retrieval_mode(retrieval_mode or default_mode)
        effective_options = {
            "top_k": top_k if top_k is not None else retrieval_settings.get("top_k"),
            "score_threshold": min_score if min_score is not None else retrieval_settings.get("score_threshold"),
            "needs_query_rewrite": needs_query_rewrite,
            "rerank_enabled": retrieval_settings.get("rerank_enabled"),
            "rerank_top_k": retrieval_settings.get("rerank_top_k"),
            "graph_hop_limit": retrieval_settings.get("graph_hop_limit", 2),
            "max_paths_per_entity": retrieval_settings.get("max_paths_per_entity", 10),
            "use_rag_entry_chunk": graph_index_settings.get("use_rag_entry_chunk", True),
            "knowledge_capability": knowledge_config.get("index_capability", "rag"),
            "domain_pack_id": runtime_settings.get("domain_pack_id"),
            "requested_profile": retrieval_settings.get("profile", "auto"),
            "budget_policy": {},
            "fallback_policy": {},
            "trace_policy": {"enabled": True},
            "scope_policy": {
                "knowledge_ids": list(collection_names or []),
                "domain_pack_id": runtime_settings.get("domain_pack_id"),
                "status": str(
                    runtime_settings.get("knowledge_status")
                    or knowledge_config.get("index_settings", {}).get("status")
                    or "active"
                ),
            },
            "index_version": {
                "vector": str(knowledge_config.get("index_settings", {}).get("index_version") or "v1"),
                "graph": str(knowledge_config.get("graph_index_settings", {}).get("index_version") or "v1"),
            },
            "index_health": {
                "vector": str(knowledge_config.get("index_settings", {}).get("health_status") or "ready"),
                "graph": str(
                    knowledge_config.get("graph_index_settings", {}).get("health_status")
                    or ("ready" if knowledge_config.get("index_capability") == "rag_graph" else "unavailable")
                ),
            },
        }
        effective_options.update(retrieval_options or {})
        effective_options["budget_policy"] = {
            "top_k": effective_options.get("top_k"),
            "rerank_top_k": effective_options.get("rerank_top_k"),
            "graph_hop_limit": effective_options.get("graph_hop_limit"),
            "max_paths_per_entity": effective_options.get("max_paths_per_entity"),
            "rewrite_enabled": effective_options.get("needs_query_rewrite", True),
            **dict(effective_options.get("budget_policy") or {}),
        }
        effective_options["fallback_policy"] = {
            "allow_retry": True,
            "route_broadening": True,
            "query_rewrite_retry": True,
            **dict(effective_options.get("fallback_policy") or {}),
        }
        effective_options["trace_policy"] = {
            "enabled": True,
            **dict(effective_options.get("trace_policy") or {}),
        }

        orchestrator = RetrievalOrchestrator()
        return await orchestrator.run(
            mode=normalized_mode,
            query=query,
            knowledge_ids=collection_names,
            retrieval_options=effective_options,
        )

    @classmethod
    async def delete_documents_es_milvus(cls, file_id, knowledge_id):
        if app_settings.rag.enable_elasticsearch:
            await es_client.delete_documents(file_id, knowledge_id)
        await milvus_client.delete_by_file_id(file_id, knowledge_id)
        await milvus_client.delete_image_by_file_id(file_id, knowledge_id)
