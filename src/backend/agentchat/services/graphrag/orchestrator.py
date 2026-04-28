from agentchat.services.graphrag.models import normalize_retrieval_mode
from agentchat.services.graphrag.retriever import GraphRetriever


class RagRetrieverAdapter:
    async def retrieve(self, query: str, knowledge_ids: list[str]):
        from agentchat.services.rag.handler import RagHandler

        return await RagHandler._retrieve_ranked_documents_rag_detail(
            query,
            knowledge_ids,
            knowledge_ids,
        )


class QueryExpanderAdapter:
    async def expand(self, query: str) -> list[str]:
        from agentchat.services.rewrite.query_write import query_rewriter

        variations = await query_rewriter.rewrite(query)
        ordered = [query]
        seen = {query.strip().lower()}
        for item in variations:
            text = str(item or "").strip()
            if not text:
                continue
            normalized = text.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            ordered.append(text)
        return ordered


class RetrievalOrchestrator:
    def __init__(self, rag_retriever=None, graph_retriever=None, query_expander=None, max_rounds: int = 3):
        self.rag_retriever = rag_retriever or RagRetrieverAdapter()
        self.graph_retriever = graph_retriever or GraphRetriever()
        self.query_expander = query_expander or QueryExpanderAdapter()
        self.max_rounds = max(1, min(int(max_rounds or 1), 3))

    @staticmethod
    def _resolve_auto_mode(query: str) -> str:
        return (
            "graphrag"
            if any(word in query.lower() for word in ["relation", "graph", "relationship"]) or "关系" in query
            else "hybrid"
        )

    @staticmethod
    def _quality_reason(mode: str, result: dict) -> str | None:
        raw_content = (result.get("raw_content") or result.get("content") or "").strip()
        if not raw_content or raw_content == "No relevant documents found.":
            return "empty_result"

        if mode == "graphrag":
            if not result.get("paths") and not result.get("entities"):
                return "graph_result_empty"
            return None

        document_count = result.get("document_count")
        requested_top_k = result.get("requested_top_k") or 0
        min_document_count = min(2, requested_top_k) if requested_top_k else 2
        if document_count is not None and document_count < min_document_count:
            return "too_few_documents"

        top_score = result.get("top_score")
        score_threshold = result.get("score_threshold")
        if top_score is not None and score_threshold is not None and top_score < score_threshold:
            return "low_rerank_score"

        if document_count == 0:
            return "no_relevant_documents"

        return None

    @staticmethod
    def _build_round_summary(
        *,
        round_index: int,
        mode: str,
        query: str,
        trigger: str,
        quality_reason: str | None,
        result: dict,
    ) -> dict:
        return {
            "round": round_index,
            "mode": mode,
            "query": query,
            "trigger": trigger,
            "quality_reason": quality_reason,
            "document_count": result.get("document_count"),
            "top_score": result.get("top_score"),
            "score_threshold": result.get("score_threshold"),
            "path_count": len(result.get("paths") or []),
            "entity_count": len(result.get("entities") or []),
            "content_found": bool((result.get("raw_content") or result.get("content") or "").strip()),
        }

    def _build_retry_plan(
        self,
        *,
        first_mode: str,
        fallback_reason: str | None,
        candidate_queries: list[str],
    ) -> list[dict]:
        if not fallback_reason:
            return []

        attempts: list[dict] = []

        if first_mode in {"rag", "graphrag"}:
            attempts.append(
                {
                    "mode": "hybrid",
                    "query": candidate_queries[0],
                    "trigger": "route_broadening",
                }
            )

        alternate_query = next(
            (
                candidate
                for candidate in candidate_queries[1:]
                if candidate.strip().lower() != candidate_queries[0].strip().lower()
            ),
            None,
        )
        if alternate_query:
            retry_mode = "hybrid" if first_mode != "hybrid" else "hybrid"
            duplicate = any(
                attempt["mode"] == retry_mode
                and attempt["query"].strip().lower() == alternate_query.strip().lower()
                for attempt in attempts
            )
            if not duplicate:
                attempts.append(
                    {
                        "mode": retry_mode,
                        "query": alternate_query,
                        "trigger": "query_rewrite_retry",
                    }
                )

        return attempts[: max(self.max_rounds - 1, 0)]

    async def _run_single_pass(self, mode: str, query: str, knowledge_ids: list[str]) -> dict:
        rag_result = {"content": "", "raw_content": "", "documents": []}
        graph_result = {"content": "", "raw_content": "", "entities": [], "paths": []}

        if mode in {"rag", "hybrid"}:
            rag_result = await self.rag_retriever.retrieve(query, knowledge_ids)

        if mode in {"graphrag", "hybrid"} and knowledge_ids:
            graph_result = await self.graph_retriever.retrieve(query, knowledge_ids[0])

        graph_content = graph_result.get("content", "")
        rag_content = rag_result.get("content", "")

        if mode == "graphrag":
            content = graph_content or rag_content
        elif mode == "hybrid":
            content = "\n".join(filter(None, [rag_content, graph_content]))
        else:
            content = rag_content

        return {
            "mode": mode,
            "content": content or "No relevant documents found.",
            "raw_content": content or "",
            "rag_result": rag_result,
            "graph_result": graph_result,
            "document_count": rag_result.get("document_count"),
            "requested_top_k": rag_result.get("requested_top_k"),
            "top_score": rag_result.get("top_score"),
            "score_threshold": rag_result.get("score_threshold"),
            "paths": graph_result.get("paths", []),
            "entities": graph_result.get("entities", []),
        }

    async def run(self, mode: str, query: str, knowledge_ids: list[str]) -> dict:
        normalized_mode = normalize_retrieval_mode(mode)
        first_mode = self._resolve_auto_mode(query) if normalized_mode == "auto" else normalized_mode
        candidate_queries = await self.query_expander.expand(query)
        if not candidate_queries:
            candidate_queries = [query]

        attempts = [
            {
                "mode": first_mode,
                "query": candidate_queries[0],
                "trigger": "initial",
            }
        ]

        first_pass = await self._run_single_pass(first_mode, candidate_queries[0], knowledge_ids)
        first_quality = self._quality_reason(first_mode, first_pass)
        rounds = [
            self._build_round_summary(
                round_index=1,
                mode=first_mode,
                query=candidate_queries[0],
                trigger="initial",
                quality_reason=first_quality,
                result=first_pass,
            )
        ]

        attempts.extend(
            self._build_retry_plan(
                first_mode=first_mode,
                fallback_reason=first_quality,
                candidate_queries=candidate_queries,
            )
        )

        final_pass = first_pass
        final_quality = first_quality
        for index, attempt in enumerate(attempts[1:], start=2):
            if final_quality is None:
                break
            current_pass = await self._run_single_pass(attempt["mode"], attempt["query"], knowledge_ids)
            current_quality = self._quality_reason(attempt["mode"], current_pass)
            rounds.append(
                self._build_round_summary(
                    round_index=index,
                    mode=attempt["mode"],
                    query=attempt["query"],
                    trigger=attempt["trigger"],
                    quality_reason=current_quality,
                    result=current_pass,
                )
            )
            final_pass = current_pass
            final_quality = current_quality

        final_mode = final_pass["mode"]
        second_pass_used = len(rounds) >= 2
        metadata = {
            "first_mode": first_mode,
            "final_mode": final_mode,
            "second_pass_used": second_pass_used,
            "fallback_triggered": second_pass_used,
            "fallback_reason": first_quality if second_pass_used else None,
            "final_quality_reason": final_quality,
            "round_count": len(rounds),
            "rounds": rounds,
            "query_variants": candidate_queries,
            "rewritten_query_used": any(
                round_info["query"].strip().lower() != query.strip().lower()
                for round_info in rounds
            ),
            "first_pass_quality": {
                "document_count": first_pass.get("document_count"),
                "top_score": first_pass.get("top_score"),
                "score_threshold": first_pass.get("score_threshold"),
                "path_count": len(first_pass.get("paths") or []),
                "entity_count": len(first_pass.get("entities") or []),
            },
        }

        return {
            "actual_mode": final_mode,
            "first_mode": first_mode,
            "final_mode": final_mode,
            "second_pass_used": second_pass_used,
            "fallback_triggered": second_pass_used,
            "fallback_reason": metadata["fallback_reason"],
            "round_count": metadata["round_count"],
            "content": final_pass["content"],
            "metadata": metadata,
            "first_pass_result": first_pass,
            "final_pass_result": final_pass,
            "rag_result": final_pass["rag_result"],
            "graph_result": final_pass["graph_result"],
        }
