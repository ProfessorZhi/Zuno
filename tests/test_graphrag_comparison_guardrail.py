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


def test_low_confidence_graph_doc_cannot_evict_second_seed_evidence_on_comparison_query():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", "Scott Derrickson", "vector", 0.9),
        _doc("v2", "Ed Wood (film)", "vector", 0.8),
        _doc("v3", "Ed Wood", "vector", 0.79),
    ]
    graph_docs = [
        _doc(
            "g1",
            "Sinister (film)",
            "graph",
            0.0,
            content="Scott Derrickson directed Sinister.",
            graph_seed_hit_count=4,
            graph_support_count=12,
            graph_path_count=10,
        )
    ]

    result = fusion.merge(
        query="Were Scott Derrickson and Ed Wood of the same nationality?",
        documents_by_source={"vector": vector_docs, "graph": graph_docs},
        top_k=5,
    )

    top3 = [doc.file_name for doc in result.documents[:3]]

    assert "Ed Wood" in top3
    sinister = next(doc for doc in result.documents if doc.file_name == "Sinister (film)")
    assert sinister.metadata["promotion_blocked_reason"] == "comparison_chain_protection"


def test_graph_doc_can_enter_top3_when_it_covers_missing_seed_entity():
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
            graph_seed_hit_count=2,
            graph_support_count=3,
            graph_path_count=2,
        )
    ]

    result = fusion.merge(
        query="Were Scott Derrickson and Ed Wood of the same nationality?",
        documents_by_source={"vector": vector_docs, "graph": graph_docs},
        top_k=5,
    )

    top3 = [doc.file_name for doc in result.documents[:3]]
    promoted = next(doc for doc in result.documents if doc.file_name == "Ed Wood")

    assert "Ed Wood" in top3
    assert promoted.metadata["covers_missing_seed"] is True


def test_graph_doc_can_promote_when_it_connects_two_comparison_seeds():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", "Scott Derrickson", "vector", 0.9),
        _doc("v2", "Doctor Strange (2016 film)", "vector", 0.8),
        _doc("v3", "Conrad Brooks", "vector", 0.79),
    ]
    graph_docs = [
        _doc(
            "g1",
            "Scott Derrickson and Ed Wood",
            "graph",
            0.0,
            content="Scott Derrickson and Ed Wood were both American directors.",
            graph_seed_hit_count=4,
            graph_support_count=4,
            graph_path_count=3,
            graph_connects_two_seeds=True,
        )
    ]

    result = fusion.merge(
        query="Were Scott Derrickson and Ed Wood of the same nationality?",
        documents_by_source={"vector": vector_docs, "graph": graph_docs},
        top_k=5,
    )

    top3 = [doc.file_name for doc in result.documents[:3]]
    promoted = next(doc for doc in result.documents if doc.file_name == "Scott Derrickson and Ed Wood")

    assert "Scott Derrickson and Ed Wood" in top3
    assert promoted.metadata["connects_two_seeds"] is True


def test_standard_top3_dual_seed_coverage_is_preserved_for_comparison_query():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", "Scott Derrickson", "vector", 0.9),
        _doc("v2", "Ed Wood (film)", "vector", 0.8),
        _doc("v3", "Ed Wood", "vector", 0.79),
        _doc("v4", "Conrad Brooks", "vector", 0.7),
    ]
    graph_docs = [
        _doc("g1", "Sinister (film)", "graph", 0.0, content="Scott Derrickson directed Sinister.", graph_seed_hit_count=4, graph_support_count=12, graph_path_count=10),
        _doc("g2", "Adam Collis", "graph", 0.0, content="Adam Collis worked with Scott Derrickson.", graph_seed_hit_count=3, graph_support_count=3, graph_path_count=3),
    ]

    result = fusion.merge(
        query="Were Scott Derrickson and Ed Wood of the same nationality?",
        documents_by_source={"vector": vector_docs, "graph": graph_docs},
        top_k=5,
    )

    top3 = result.documents[:3]
    combined_coverage = set()
    for doc in top3:
        combined_coverage.update(doc.metadata.get("candidate_seed_coverage") or [])

    assert combined_coverage >= {"scott derrickson", "ed wood"}


def test_non_comparison_query_does_not_receive_comparison_guardrail_penalty():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", "Big Stone Gap (film)", "vector", 0.9),
        _doc("v2", "Scott Derrickson", "vector", 0.8),
        _doc("v3", "Kingston", "vector", 0.7),
    ]
    graph_docs = [
        _doc(
            "g1",
            "Adriana Trigiani",
            "graph",
            0.0,
            content="Adriana Trigiani is based in Big Stone Gap and New York.",
            graph_seed_hit_count=3,
            graph_support_count=3,
            graph_path_count=3,
        )
    ]

    result = fusion.merge(
        query='The director of the romantic comedy "Big Stone Gap" is based in what New York city?',
        documents_by_source={"vector": vector_docs, "graph": graph_docs},
        top_k=5,
    )

    top3 = [doc.file_name for doc in result.documents[:3]]
    promoted = next(doc for doc in result.documents if doc.file_name == "Adriana Trigiani")

    assert "Adriana Trigiani" in top3
    assert promoted.metadata.get("promotion_blocked_reason") is None
