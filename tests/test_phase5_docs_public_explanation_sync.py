from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_phase5_docs_sync_current_public_story() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    phase_index = (
        REPO_ROOT / "docs" / "architecture" / "history" / "phases" / "README.md"
    ).read_text(encoding="utf-8")
    phase5_doc = (
        REPO_ROOT / "docs" / "architecture" / "history" / "phases" / "phase-05-docs-and-public-explanation-sync.md"
    ).read_text(encoding="utf-8")

    for phrase in [
        "local-first Agent Workspace",
        "`src/backend/zuno` is the only active Python backend runtime boundary.",
        "Phase 0-6 architecture closure remains complete historical truth.",
        "architecture/             # current, target, roadmap, decisions, history",
    ]:
        assert phrase in readme

    for phrase in [
        "README, architecture index, development index, launcher docs, and maintainer workflow all agree on the same runtime truth",
        "Zuno = local-first Agent Workspace + LangGraph Runtime + RetrievalOrchestrator + Local GraphRAG + Domain Pack + Eval",
    ]:
        assert phrase in phase5_doc

    assert "`Phase 5` is complete" in phase_index
    assert "src/backend/zuno/            # current backend runtime truth" in readme


def test_phase5_maintainer_docs_use_clean_paths_and_current_truth() -> None:
    staging_plan = (
        REPO_ROOT / "docs" / "development" / "public-release-staging-plan.md"
    ).read_text(encoding="utf-8")
    launcher_docs = (
        REPO_ROOT / "tools" / "launchers" / "windows" / "README.md"
    ).read_text(encoding="utf-8")

    assert "../history/development/README.md" in staging_plan
    assert "05_TopDown_棰樺簱瀛︿範/椤圭洰/02_椤圭洰鏄犲皠/Zuno/" not in staging_plan
    assert "Phase 0" in launcher_docs
    assert "recovery" in launcher_docs.lower()
