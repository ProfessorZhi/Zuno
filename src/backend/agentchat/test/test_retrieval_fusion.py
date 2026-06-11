from agentchat.services.retrieval.fusion import RetrievalFusion
from agentchat.services.retrieval.models import RetrievedDocument


def _doc(chunk_id: str, source_type: str, score: float, content: str):
    return RetrievedDocument(
        chunk_id=chunk_id,
        knowledge_id="kb_1",
        file_id="f_1",
        file_name="doc.md",
        content=content,
        summary="",
        score=score,
        normalized_score=None,
        source_type=source_type,
        source_backend=source_type,
        retrieval_reason=source_type,
        metadata={},
    )


def test_fusion_merges_same_chunk_and_tracks_matched_sources():
    fusion = RetrievalFusion()

    result = fusion.merge(
        query="redis persistence",
        documents_by_source={
            "vector": [_doc("c1", "vector", 0.8, "redis content")],
            "keyword": [_doc("c1", "keyword", 12.0, "redis content")],
        },
        top_k=5,
    )

    assert len(result.documents) == 1
    assert result.documents[0].metadata["matched_by"] == ["vector", "keyword"]


def test_fusion_demotes_graph_only_documents_with_weak_seed_signal():
    fusion = RetrievalFusion()

    strong_vector = _doc("c_vector", "vector", 0.7, "Python variable binding and namespace mapping.")
    weak_graph = _doc("c_graph", "graph", 0.0, "Python -> Agent")
    weak_graph.metadata.update({"graph_seed_hit_count": 1, "graph_support_count": 1})

    result = fusion.merge(
        query="Python 鍙橀噺 鍛藉悕绌洪棿 缁戝畾",
        documents_by_source={
            "vector": [strong_vector],
            "graph": [weak_graph],
        },
        top_k=5,
    )

    assert result.documents[0].chunk_id == "c_vector"
