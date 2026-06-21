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
        metadata={"matched_by": list(matched_by or [source_type])},
    )


def test_low_confidence_requery_cannot_displace_standard_top5():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", 'I&quot;s', "vector", 0.95, content="I's follows Ichitaka Seto."),
        _doc("v2", "Haven't You Heard? I'm Sakamoto", "vector", 0.90),
        _doc("v3", "Clear Skies!", "vector", 0.88),
        _doc("v4", "Silver Spoon (manga)", "vector", 0.86),
        _doc("v5", "Masakazu Katsura", "vector", 0.84, content="Masakazu Katsura was born in 1962."),
    ]
    requery_docs = [
        _doc(
            "r1",
            "My Bride is a Mermaid",
            "vector",
            0.0,
            matched_by=["requery"],
            content="A manga and anime work by a related creator.",
        )
    ]

    result = fusion.merge(
        query="A Japanese manga series based on a 16 year old high school student Ichitaka Seto, is written and illustrated by someone born in what year?",
        documents_by_source={"vector": vector_docs, "requery": requery_docs},
        top_k=6,
    )

    top5 = [doc.file_name for doc in result.documents[:5]]
    requery_doc = next(doc for doc in result.documents if doc.file_name == "My Bride is a Mermaid")

    assert "Masakazu Katsura" in top5
    assert requery_doc.metadata["requery_promotion_allowed"] is False
    assert requery_doc.metadata["requery_promotion_blocked_reason"] == "low_confidence_requery"
    assert requery_doc.metadata["requery_noise_reason"] is not None


def test_requery_can_promote_when_it_recovers_missing_evidence_side():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", "Buck-Tick", "vector", 0.95, content="Buck-Tick is a Japanese rock band."),
        _doc("v2", "Atsushi Sakurai", "vector", 0.90),
        _doc("v3", "Masami Tsuchiya", "vector", 0.88),
        _doc("v4", "Kyo (musician)", "vector", 0.86),
        _doc("v5", "Gus Williams (musician)", "vector", 0.84),
    ]
    requery_docs = [
        _doc(
            "r1",
            "Hayden (musician)",
            "vector",
            0.0,
            matched_by=["requery"],
            content="Hayden is a Canadian singer-songwriter from Canada.",
        )
    ]

    result = fusion.merge(
        query="Hayden is a singer-songwriter from Canada, but where does Buck-Tick hail from?",
        documents_by_source={"vector": vector_docs, "requery": requery_docs},
        top_k=6,
    )

    top3 = [doc.file_name for doc in result.documents[:3]]
    requery_doc = next(doc for doc in result.documents if doc.file_name == "Hayden (musician)")

    assert "Hayden (musician)" in top3
    assert requery_doc.metadata["requery_promotion_allowed"] is True
    assert requery_doc.metadata["requery_confidence_score"] >= 2
    assert requery_doc.metadata["requery_help_reason"] is not None


def test_unrelated_noisy_requery_candidate_is_downgraded():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", "Ralph Hefferline", "vector", 0.95, content="Ralph Hefferline taught at Columbia University."),
        _doc("v2", "Columbia University", "vector", 0.90, content="Columbia University is in New York City."),
        _doc("v3", "Virginia Commonwealth University", "vector", 0.88),
        _doc("v4", "University of Kansas", "vector", 0.86),
        _doc("v5", "Amherst, Massachusetts", "vector", 0.84),
    ]
    requery_docs = [
        _doc(
            "r1",
            "My Chemical Romance",
            "vector",
            0.0,
            matched_by=["requery"],
            content="An unrelated band article with no city relation.",
        )
    ]

    result = fusion.merge(
        query="Ralph Hefferline was a psychology professor at a university that is located in what city?",
        documents_by_source={"vector": vector_docs, "requery": requery_docs},
        top_k=6,
    )

    top5 = [doc.file_name for doc in result.documents[:5]]
    requery_doc = next(doc for doc in result.documents if doc.file_name == "My Chemical Romance")

    assert "My Chemical Romance" not in top5
    assert requery_doc.metadata["requery_promotion_allowed"] is False
    assert requery_doc.metadata["requery_noise_reason"] is not None


def test_requery_metadata_records_confidence_and_block_reason():
    fusion = RetrievalFusion()
    vector_docs = [
        _doc("v1", "Buck-Tick", "vector", 0.95, content="Buck-Tick is a Japanese rock band."),
        _doc("v2", "Atsushi Sakurai", "vector", 0.90),
    ]
    requery_docs = [
        _doc(
            "r1",
            "Hayden (musician)",
            "vector",
            0.0,
            matched_by=["requery"],
            content="Hayden is a Canadian singer-songwriter from Canada.",
        ),
        _doc(
            "r2",
            "My Bride is a Mermaid",
            "vector",
            0.0,
            matched_by=["requery"],
            content="A manga and anime work by a related creator.",
        ),
    ]

    result = fusion.merge(
        query="Hayden is a singer-songwriter from Canada, but where does Buck-Tick hail from?",
        documents_by_source={"vector": vector_docs, "requery": requery_docs},
        top_k=6,
    )

    promoted = next(doc for doc in result.documents if doc.file_name == "Hayden (musician)")
    blocked = next(doc for doc in result.documents if doc.file_name == "My Bride is a Mermaid")

    assert promoted.metadata["requery_confidence_score"] >= 2
    assert promoted.metadata["requery_promotion_allowed"] is True
    assert blocked.metadata["requery_confidence_score"] < promoted.metadata["requery_confidence_score"]
    assert blocked.metadata["requery_promotion_blocked_reason"] == "low_confidence_requery"
