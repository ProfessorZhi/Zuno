import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
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
        },
    )


BRIDGE_QUERY = (
    "Kaiser Ventures corporation was founded by an American industrialist "
    "who became known as the father of modern American shipbuilding?"
)


def test_bridge_relation_noisy_graph_doc_cannot_displace_top2_evidence():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", "Henry J. Kaiser", "vector", 0.92),
        _doc("v2", "Kaiser Ventures", "vector", 0.87),
        _doc("v3", "Kaiser Shipyards", "vector", 0.84),
    ]
    graph_docs = [
        _doc(
            "g1",
            "Cho Kyuhyun",
            "graph",
            0.0,
            content="Cho Kyuhyun is a South Korean singer.",
            graph_seed_hit_count=4,
            graph_support_count=12,
            graph_path_count=10,
        )
    ]

    result = fusion.merge(
        query=BRIDGE_QUERY,
        documents_by_source={"vector": vector_docs, "graph": graph_docs},
        top_k=5,
    )

    top2 = [doc.file_name for doc in result.documents[:2]]
    noisy = next(doc for doc in result.documents if doc.file_name == "Cho Kyuhyun")

    assert result.fusion_metadata["bridge_relation_question"] is True
    assert "Kaiser Ventures" in top2
    assert noisy.metadata["bridge_promotion_blocked_reason"] == "bridge_chain_protection"
    assert noisy.metadata["noisy_bridge_graph_only"] is True


def test_bridge_graph_doc_can_promote_when_it_restores_missing_bridge_evidence():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", "Henry J. Kaiser", "vector", 0.92),
        _doc("v2", "Kaiser Shipyards", "vector", 0.87),
        _doc("v3", "Edgar Kaiser Sr.", "vector", 0.84),
    ]
    graph_docs = [
        _doc(
            "g1",
            "Kaiser Ventures",
            "graph",
            0.0,
            content="Kaiser Ventures was founded by Henry J. Kaiser.",
            graph_seed_hit_count=3,
            graph_support_count=5,
            graph_path_count=4,
        )
    ]

    result = fusion.merge(
        query=BRIDGE_QUERY,
        documents_by_source={"vector": vector_docs, "graph": graph_docs},
        top_k=5,
    )

    top2 = [doc.file_name for doc in result.documents[:2]]
    promoted = next(doc for doc in result.documents if doc.file_name == "Kaiser Ventures")

    assert "Kaiser Ventures" in top2
    assert promoted.metadata["bridge_chain_score"] >= 2
    assert promoted.metadata["bridge_promotion_blocked_reason"] is None


def test_bridge_guardrail_does_not_penalize_fused_baseline_candidate():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", "Henry J. Kaiser", "vector", 0.92),
        _doc("v2", "Kaiser Ventures", "vector", 0.87),
        _doc("v3", "Kaiser Shipyards", "vector", 0.84),
    ]
    graph_docs = [
        _doc(
            "v2",
            "Kaiser Ventures",
            "graph",
            0.0,
            content="Kaiser Ventures was founded by Henry J. Kaiser.",
            matched_by=["graph"],
            graph_seed_hit_count=3,
            graph_support_count=5,
            graph_path_count=4,
        )
    ]

    result = fusion.merge(
        query=BRIDGE_QUERY,
        documents_by_source={"vector": vector_docs, "graph": graph_docs},
        top_k=5,
    )

    fused = next(doc for doc in result.documents if doc.file_name == "Kaiser Ventures")

    assert "graph" in fused.metadata["matched_by"]
    assert fused.metadata["bridge_promotion_blocked_reason"] is None


def test_standard_top2_bridge_coverage_is_preserved_when_graph_noise_appears():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", "Henry J. Kaiser", "vector", 0.92),
        _doc("v2", "Kaiser Ventures", "vector", 0.87),
        _doc("v3", "Kaiser Shipyards", "vector", 0.84),
    ]
    graph_docs = [
        _doc(
            "g1",
            "Cho Kyuhyun",
            "graph",
            0.0,
            content="Cho Kyuhyun is a South Korean singer.",
            graph_seed_hit_count=4,
            graph_support_count=12,
            graph_path_count=10,
        ),
        _doc(
            "g2",
            "Method Man",
            "graph",
            0.0,
            content="Method Man is an American rapper.",
            graph_seed_hit_count=3,
            graph_support_count=8,
            graph_path_count=6,
        ),
    ]

    result = fusion.merge(
        query=BRIDGE_QUERY,
        documents_by_source={"vector": vector_docs, "graph": graph_docs},
        top_k=5,
    )

    top2 = result.documents[:2]
    combined_coverage = set()
    for doc in top2:
        combined_coverage.update(doc.metadata.get("bridge_seed_coverage") or [])

    assert {"henry j kaiser", "kaiser ventures"} <= combined_coverage


def test_non_bridge_query_does_not_receive_bridge_guardrail_penalty():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", "Big Stone Gap (film)", "vector", 0.91),
        _doc("v2", "Kingston", "vector", 0.86),
        _doc("v3", "Adriana Trigiani", "vector", 0.83),
    ]
    graph_docs = [
        _doc(
            "g1",
            "Kingston",
            "graph",
            0.0,
            content="Kingston is a city in New York.",
            graph_seed_hit_count=3,
            graph_support_count=3,
            graph_path_count=3,
        )
    ]

    result = fusion.merge(
        query="Where is Kingston located?",
        documents_by_source={"vector": vector_docs, "graph": graph_docs},
        top_k=5,
    )

    promoted = next(doc for doc in result.documents if doc.file_name == "Kingston")

    assert result.fusion_metadata["bridge_relation_question"] is False
    assert promoted.metadata.get("bridge_promotion_blocked_reason") is None
