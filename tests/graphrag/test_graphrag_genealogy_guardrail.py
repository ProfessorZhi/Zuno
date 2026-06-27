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
    graph_path_relation_labels: list[str] | None = None,
    direct_relation_path: bool = False,
    indirect_family_noise_path: bool = False,
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
            "graph_path_relation_labels": list(graph_path_relation_labels or []),
            "direct_relation_path": direct_relation_path,
            "indirect_family_noise_path": indirect_family_noise_path,
        },
    )


GENEALOGY_QUERY = "Who is the maternal grandfather of Antiochus X Eusebes?"
DIRECTOR_BIRTH_QUERY = "Where was the director of film Ronnie Rocket born?"


def test_noisy_genealogy_graph_doc_cannot_displace_standard_top5_evidence():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", "Antiochus X Eusebes", "vector", 0.96),
        _doc("v2", "Laodice of the Sameans", "vector", 0.90),
        _doc("v3", "Albert III, Prince of Anhalt-Zerbst", "vector", 0.85),
        _doc("v4", "Fujiwara no Nagara", "vector", 0.83),
        _doc("v5", "Cleopatra IV of Egypt", "vector", 0.82, content="Cleopatra IV of Egypt was the mother of Antiochus X Eusebes."),
    ]
    graph_docs = [
        _doc(
            "g1",
            "North Marion High School (West Virginia)",
            "graph",
            0.0,
            content="A noisy family-nearby graph neighbor with no real maternal grandfather evidence.",
            graph_seed_hit_count=4,
            graph_support_count=12,
            graph_path_count=8,
            graph_path_relation_labels=["school", "nearby_family"],
            indirect_family_noise_path=True,
        )
    ]

    result = fusion.merge(
        query=GENEALOGY_QUERY,
        documents_by_source={"vector": vector_docs, "graph": graph_docs},
        top_k=6,
    )

    top5 = [doc.file_name for doc in result.documents[:5]]
    noisy = next(doc for doc in result.documents if doc.file_name == "North Marion High School (West Virginia)")

    assert "Cleopatra IV of Egypt" in top5
    assert noisy.metadata["genealogy_bridge_question"] is True
    assert noisy.metadata["genealogy_promotion_allowed"] is False
    assert noisy.metadata["genealogy_promotion_blocked_reason"] == "relation_label_mismatch"
    assert noisy.metadata["noisy_genealogy_graph_only"] is True


def test_direct_genealogy_relation_path_can_promote_missing_evidence():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", "Antiochus X Eusebes", "vector", 0.96),
        _doc("v2", "Laodice of the Sameans", "vector", 0.90),
        _doc("v3", "Albert III, Prince of Anhalt-Zerbst", "vector", 0.85),
        _doc("v4", "Fujiwara no Nagara", "vector", 0.83),
    ]
    graph_docs = [
        _doc(
            "g1",
            "Cleopatra IV of Egypt",
            "graph",
            0.0,
            content="Cleopatra IV of Egypt was the mother of Antiochus X Eusebes and daughter of Ptolemy VI Philometor.",
            graph_seed_hit_count=3,
            graph_support_count=5,
            graph_path_count=4,
            graph_path_relation_labels=["mother", "daughter", "maternal_grandfather"],
            direct_relation_path=True,
        )
    ]

    result = fusion.merge(
        query=GENEALOGY_QUERY,
        documents_by_source={"vector": vector_docs, "graph": graph_docs},
        top_k=6,
    )

    top5 = [doc.file_name for doc in result.documents[:5]]
    promoted = next(doc for doc in result.documents if doc.file_name == "Cleopatra IV of Egypt")

    assert "Cleopatra IV of Egypt" in top5
    assert promoted.metadata["genealogy_promotion_allowed"] is True
    assert promoted.metadata["genealogy_path_precision_score"] >= 2
    assert promoted.metadata["genealogy_promotion_blocked_reason"] is None


def test_genealogy_guardrail_does_not_penalize_non_genealogy_bridge_query():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", "Ronnie Rocket", "vector", 0.94),
        _doc("v2", "David Lynch", "vector", 0.90),
        _doc("v3", "Xawery Żuławski", "vector", 0.84),
    ]
    graph_docs = [
        _doc(
            "g1",
            "Jason Moore (director)",
            "graph",
            0.0,
            content="Jason Moore is a director born in Arkansas.",
            graph_seed_hit_count=2,
            graph_support_count=3,
            graph_path_count=3,
            graph_path_relation_labels=["director", "birthplace"],
            direct_relation_path=True,
        )
    ]

    result = fusion.merge(
        query=DIRECTOR_BIRTH_QUERY,
        documents_by_source={"vector": vector_docs, "graph": graph_docs},
        top_k=6,
    )

    promoted = next(doc for doc in result.documents if doc.file_name == "Jason Moore (director)")

    assert result.fusion_metadata["genealogy_bridge_question"] is False
    assert promoted.metadata.get("genealogy_promotion_blocked_reason") is None


def test_genealogy_metadata_records_relation_labels_and_precision_reason():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", "Antiochus X Eusebes", "vector", 0.96),
        _doc("v2", "Laodice of the Sameans", "vector", 0.90),
    ]
    graph_docs = [
        _doc(
            "g1",
            "North Marion High School (West Virginia)",
            "graph",
            0.0,
            content="A noisy family-nearby graph neighbor with no kinship answer.",
            graph_seed_hit_count=4,
            graph_support_count=9,
            graph_path_count=7,
            graph_path_relation_labels=["school", "nearby_family"],
            indirect_family_noise_path=True,
        )
    ]

    result = fusion.merge(
        query=GENEALOGY_QUERY,
        documents_by_source={"vector": vector_docs, "graph": graph_docs},
        top_k=5,
    )

    noisy = next(doc for doc in result.documents if doc.file_name == "North Marion High School (West Virginia)")

    assert noisy.metadata["genealogy_relation_cues"]
    assert noisy.metadata["graph_path_relation_labels"] == ["school", "nearby_family"]
    assert noisy.metadata["indirect_family_noise_path"] is True
    assert noisy.metadata["genealogy_path_precision_score"] <= 0
