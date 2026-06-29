from zuno.services.graphrag.models import GraphRAGProjectContract, normalize_retrieval_mode


def __getattr__(name: str):
    if name == "Neo4jClient":
        from zuno.services.graphrag.client import Neo4jClient

        return Neo4jClient
    if name == "CommunityGraphService":
        from zuno.services.graphrag.community.service import CommunityGraphService

        return CommunityGraphService
    if name == "GraphWriter":
        from zuno.services.graphrag.graph_store.graph_writer import GraphWriter

        return GraphWriter
    if name == "GraphRetriever":
        from zuno.services.graphrag.retriever import GraphRetriever

        return GraphRetriever
    raise AttributeError(name)

__all__ = [
    "CommunityGraphService",
    "GraphRAGProjectContract",
    "GraphRetriever",
    "GraphWriter",
    "Neo4jClient",
    "normalize_retrieval_mode",
]
