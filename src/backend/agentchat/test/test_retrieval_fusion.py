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
