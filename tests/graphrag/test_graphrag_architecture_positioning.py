from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_graphrag_specs_define_local_community_and_hybrid_layers():
    domain_spec = (
        REPO_ROOT
        / "docs"
        / "history"
        / "specs"
        / "domain-pack-langgraph-graphrag-architecture.md"
    ).read_text(encoding="utf-8")
    orchestrator_spec = (
        REPO_ROOT / "docs" / "history" / "specs" / "retrieval-orchestrator.md"
    ).read_text(encoding="utf-8")
    phase_doc = (
        REPO_ROOT / "docs" / "history" / "phases" / "phase-02-graphrag-mainline-deepening.md"
    ).read_text(encoding="utf-8")

    assert "Local GraphRAG" in domain_spec
    assert "Community GraphRAG" in domain_spec
    assert "DRIFT-like" in domain_spec
    assert "共用同一张实体关系图" in domain_spec
    assert "Community GraphRAG 不是当前默认检索主线" in domain_spec
    assert "Status: superseded migration context" in domain_spec
    assert "GraphRAG Project, Prompt Registry, Query Method, and Enhanced Mode" in domain_spec
    assert "src/backend/zuno/" in domain_spec

    assert "Local GraphRAG" in orchestrator_spec
    assert "Community GraphRAG" in orchestrator_spec
    assert "global overview + local deep dive" in orchestrator_spec

    assert "先把 Local GraphRAG 主线做扎实" in phase_doc
    assert "Community GraphRAG" in phase_doc


def test_phase_index_positions_knowledge_config_and_pluginization_tracks():
    phases_index = (
        REPO_ROOT / "docs" / "history" / "phases" / "README.md"
    ).read_text(encoding="utf-8")

    assert "Knowledge Config V2" in phases_index
    assert "Agent GraphRAG Pluginization" in phases_index
