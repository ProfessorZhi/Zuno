from agentchat.services.graphrag.models import normalize_retrieval_mode
from agentchat.services.graphrag.retriever import GraphRetriever


class RagRetrieverAdapter:
    async def retrieve(self, query: str, knowledge_ids: list[str]):
        from agentchat.services.rag.handler import RagHandler

        content = await RagHandler._retrieve_ranked_documents_rag(
            query,
            knowledge_ids,
            knowledge_ids,
        )
        return {
            "content": content,
            "documents": [content] if content else [],
        }


class RetrievalOrchestrator:
    def __init__(self, rag_retriever=None, graph_retriever=None):
        self.rag_retriever = rag_retriever or RagRetrieverAdapter()
        self.graph_retriever = graph_retriever or GraphRetriever()

    async def run(self, mode: str, query: str, knowledge_ids: list[str]) -> dict:
        normalized_mode = normalize_retrieval_mode(mode)
        actual_mode = normalized_mode
        if normalized_mode == "default":
            actual_mode = "rag"
        elif normalized_mode == "auto":
            actual_mode = "graphrag" if any(word in query.lower() for word in ["relation", "graph", "relationship"]) or "关系" in query else "hybrid"

        rag_result = {"content": "", "documents": []}
        graph_result = {"content": "", "entities": [], "paths": []}

        if actual_mode in {"rag", "hybrid"}:
            rag_result = await self.rag_retriever.retrieve(query, knowledge_ids)

        if actual_mode in {"graphrag", "hybrid"} and knowledge_ids:
            graph_result = await self.graph_retriever.retrieve(query, knowledge_ids[0])

        if actual_mode == "graphrag":
            content = graph_result.get("content", "")
        elif actual_mode == "hybrid":
            content = "\n".join(filter(None, [rag_result.get("content", ""), graph_result.get("content", "")]))
        else:
            content = rag_result.get("content", "")

        return {
            "actual_mode": actual_mode,
            "content": content or "No relevant documents found.",
            "rag_result": rag_result,
            "graph_result": graph_result,
        }
