from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_graphrag_specs_define_local_community_and_hybrid_layers():
    domain_spec = (
        REPO_ROOT / "docs" / "architecture" / "specs" / "domain-pack-langgraph-graphrag-architecture.md"
    ).read_text(encoding="utf-8")
    orchestrator_spec = (
        REPO_ROOT / "docs" / "architecture" / "specs" / "retrieval-orchestrator.md"
    ).read_text(encoding="utf-8")
    phase_doc = (
        REPO_ROOT / "docs" / "architecture" / "phases" / "phase-02-graphrag-mainline-deepening.md"
    ).read_text(encoding="utf-8")

    assert "Local GraphRAG" in domain_spec
    assert "Community GraphRAG" in domain_spec
    assert "DRIFT-like" in domain_spec
    assert "共用同一张实体关系图" in domain_spec

    assert "Local GraphRAG" in orchestrator_spec
    assert "Community GraphRAG" in orchestrator_spec
    assert "global overview + local deep dive" in orchestrator_spec

    assert "先把 Local GraphRAG 主线做扎实" in phase_doc
    assert "Community GraphRAG" in phase_doc
