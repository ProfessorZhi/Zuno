import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src" / "backend"))

from zuno.services.retrieval.fusion import RetrievalFusion
from zuno.services.retrieval.models import RetrievedDocument


def _doc(
    chunk_id: str,
    file_name: str,
    source_type: str,
    score: float,
    *,
    graph_seed_hit_count: int = 0,
    graph_support_count: int = 0,
    graph_path_count: int = 0,
    content: str | None = None,
):
    metadata = {
        "graph_seed_hit_count": graph_seed_hit_count,
        "graph_support_count": graph_support_count,
        "graph_path_count": graph_path_count,
    }
    return RetrievedDocument(
        chunk_id=chunk_id,
        knowledge_id="kb_1",
        file_id=file_name,
        file_name=file_name,
        content=content or file_name,
        summary="",
        score=score,
        normalized_score=None,
        source_type=source_type,
        source_backend=source_type,
        retrieval_reason=source_type,
        metadata=metadata,
    )


def test_graph_empty_does_not_return_fewer_candidates_than_baseline():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", "Scott Derrickson", "vector", 0.9),
        _doc("v2", "Ed Wood", "vector", 0.8),
        _doc("v3", "Conrad Brooks", "vector", 0.7),
    ]

    result = fusion.merge(
        query="Were Scott Derrickson and Ed Wood of the same nationality?",
        documents_by_source={"vector": vector_docs, "graph": []},
        top_k=5,
    )

    assert [doc.chunk_id for doc in result.documents] == ["v1", "v2", "v3"]


def test_noisy_graph_candidates_do_not_evict_baseline_top_gold_like_candidate():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", "Scott Derrickson", "vector", 0.9),
        _doc("v2", "Ed Wood", "vector", 0.85),
        _doc("v3", "Tyler Bates", "vector", 0.8),
        _doc("v4", "Conrad Brooks", "vector", 0.75),
        _doc("v5", "Ed Wood (film)", "vector", 0.7),
    ]
    graph_docs = [
        _doc("g1", "Sinister (film)", "graph", 0.99, graph_seed_hit_count=1, graph_support_count=1, graph_path_count=1),
        _doc("g2", "Adam Collis", "graph", 0.98, graph_seed_hit_count=1, graph_support_count=0, graph_path_count=1),
    ]

    result = fusion.merge(
        query="Were Scott Derrickson and Ed Wood of the same nationality?",
        documents_by_source={"vector": vector_docs, "graph": graph_docs},
        top_k=5,
    )

    top5 = [doc.file_name for doc in result.documents[:5]]

    assert "Ed Wood" in top5
    assert "Sinister (film)" not in top5


def test_high_confidence_graph_candidate_can_be_promoted():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", "Big Stone Gap (film)", "vector", 0.9),
        _doc("v2", "Scott Derrickson", "vector", 0.8),
        _doc("v3", "Kingston Morning", "vector", 0.7),
    ]
    graph_docs = [
        _doc(
            "g1",
            "Adriana Trigiani",
            "graph",
            0.5,
            graph_seed_hit_count=3,
            graph_support_count=3,
            graph_path_count=3,
            content="Adriana Trigiani is based in Big Stone Gap and lives in New York.",
        )
    ]

    result = fusion.merge(
        query='The director of the romantic comedy "Big Stone Gap" is based in what New York city?',
        documents_by_source={"vector": vector_docs, "graph": graph_docs},
        top_k=5,
    )

    top3 = [doc.file_name for doc in result.documents[:3]]

    assert "Adriana Trigiani" in top3


def test_fusion_deduplicates_and_keeps_debug_metadata():
    fusion = RetrievalFusion()
    vector_doc = _doc("shared", "Shirley Temple", "vector", 0.85)
    graph_doc = _doc("shared", "Shirley Temple", "graph", 0.5, graph_seed_hit_count=2, graph_support_count=2, graph_path_count=2)

    result = fusion.merge(
        query="What government position was held by Shirley Temple?",
        documents_by_source={"vector": [vector_doc], "graph": [graph_doc]},
        top_k=5,
    )

    assert len(result.documents) == 1
    metadata = result.documents[0].metadata
    assert metadata["matched_by"] == ["vector", "graph"]
    assert metadata["vector_rank"] == 1
    assert metadata["graph_rank"] == 1
    assert metadata["fusion_score"] is not None
