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
    content: str | None = None,
    matched_by: list[str] | None = None,
    graph_seed_hit_count: int = 0,
    graph_support_count: int = 0,
    graph_path_count: int = 0,
    graph_connects_two_seeds: bool = False,
):
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
        metadata={
            "matched_by": list(matched_by or [source_type]),
            "graph_seed_hit_count": graph_seed_hit_count,
            "graph_support_count": graph_support_count,
            "graph_path_count": graph_path_count,
            "graph_connects_two_seeds": graph_connects_two_seeds,
        },
    )


def test_dual_seed_graph_candidate_scores_above_single_seed_graph_candidate():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", "Scott Derrickson", "vector", 0.9),
        _doc("v2", "Doctor Strange (2016 film)", "vector", 0.8),
        _doc("v3", "Conrad Brooks", "vector", 0.79),
    ]
    graph_docs = [
        _doc(
            "g1",
            "Ed Wood",
            "graph",
            0.0,
            content="Ed Wood was an American filmmaker.",
            graph_seed_hit_count=3,
            graph_support_count=4,
            graph_path_count=3,
        ),
        _doc(
            "g2",
            "Scott Derrickson and Ed Wood",
            "graph",
            0.0,
            content="Scott Derrickson and Ed Wood were both American directors.",
            graph_seed_hit_count=3,
            graph_support_count=4,
            graph_path_count=3,
            graph_connects_two_seeds=True,
        ),
    ]

    result = fusion.merge(
        query="Were Scott Derrickson and Ed Wood of the same nationality?",
        documents_by_source={"vector": vector_docs, "graph": graph_docs},
        top_k=5,
    )

    ranked_names = [doc.file_name for doc in result.documents]
    dual_seed = next(doc for doc in result.documents if doc.file_name == "Scott Derrickson and Ed Wood")
    single_seed = next(doc for doc in result.documents if doc.file_name == "Ed Wood")

    assert ranked_names.index("Scott Derrickson and Ed Wood") < ranked_names.index("Ed Wood")
    assert dual_seed.metadata["chain_completeness_score"] > single_seed.metadata["chain_completeness_score"]
    assert dual_seed.metadata["fusion_score"] > single_seed.metadata["fusion_score"]


def test_comparison_fusion_metadata_records_seed_entities():
    fusion = RetrievalFusion()
    result = fusion.merge(
        query="Were Scott Derrickson and Ed Wood of the same nationality?",
        documents_by_source={
            "vector": [
                _doc("v1", "Scott Derrickson", "vector", 0.9),
                _doc("v2", "Ed Wood", "vector", 0.8),
            ]
        },
        top_k=5,
    )

    assert result.fusion_metadata["comparison_question"] is True
    assert result.fusion_metadata["comparison_seed_entities"] == ["scott derrickson", "ed wood"]


def test_non_comparison_query_keeps_chain_metadata_inactive():
    fusion = RetrievalFusion()
    result = fusion.merge(
        query='The director of the romantic comedy "Big Stone Gap" is based in what New York city?',
        documents_by_source={
            "vector": [
                _doc("v1", "Big Stone Gap (film)", "vector", 0.9),
                _doc("v2", "Adriana Trigiani", "vector", 0.8),
            ]
        },
        top_k=5,
    )

    assert result.fusion_metadata["comparison_question"] is False
    assert result.fusion_metadata["comparison_seed_entities"] == []
    for doc in result.documents:
        assert doc.metadata["comparison_question"] is False
        assert doc.metadata["chain_completeness_score"] == 0

