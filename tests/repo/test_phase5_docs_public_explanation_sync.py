from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_phase5_docs_sync_current_public_story() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    phase_index = (
        REPO_ROOT / "docs" / "history" / "phases" / "README.md"
    ).read_text(encoding="utf-8")
    phase5_doc = (
        REPO_ROOT / "docs" / "history" / "phases" / "phase-05-docs-and-public-explanation-sync.md"
    ).read_text(encoding="utf-8")

    for phrase in [
        "本地优先、短小精悍但工程完整的",
        "后端主路径位于 `src/backend/zuno`",
        "当前 program 前台：`.agent/programs/`",
    ]:
        assert phrase in readme

    for phrase in [
        "README, architecture index, development index, launcher docs, and maintainer workflow all agree on the same runtime truth",
        "Zuno = local-first Agent Workspace + LangGraph Runtime + RetrievalOrchestrator + Local GraphRAG + Domain Pack + Eval",
    ]:
        assert phrase in phase5_doc

    assert "Phase 0-6" in phase_index
    assert "Phase 5: Docs And Public Explanation Sync" in phase5_doc


def test_phase5_maintainer_docs_use_clean_paths_and_current_truth() -> None:
    staging_plan = (
        REPO_ROOT / "docs" / "history" / "development" / "public-release-staging-plan.md"
    ).read_text(encoding="utf-8")
    launcher_docs = (
        REPO_ROOT / "tools" / "launchers" / "windows" / "README.md"
    ).read_text(encoding="utf-8")

    assert "../history/development/README.md" in staging_plan
    assert "05_TopDown_棰樺簱瀛︿範/椤圭洰/02_椤圭洰鏄犲皠/Zuno/" not in staging_plan
    assert "Phase 0" in launcher_docs
    assert "recovery" in launcher_docs.lower()
