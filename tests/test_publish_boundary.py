from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_gitignore_matches_current_local_only_boundary() -> None:
    content = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")

    required_entries = [
        ".local/",
        "apps/web/AGENTS.md",
        "infra/docker/docker_config.local.yaml",
        ".local/config/zuno/",
        ".local/evals/zuno/rag_eval/corpus/",
        ".local/evals/zuno/rag_eval/runs/",
    ]

    for entry in required_entries:
        assert entry in content, f"missing local-only ignore: {entry}"


def test_readme_and_phase_index_share_current_phase_truth() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    phases = (
        REPO_ROOT / "docs" / "architecture" / "phases" / "README.md"
    ).read_text(encoding="utf-8")

    for phrase in [
        "Phase 3 已完成 Domain Pack Formalization",
        "Phase 4: Knowledge Config V2 + Local Eval Strengthening",
        "Phase 5: Docs And Public Explanation Sync",
        "Phase 6: Agent GraphRAG Pluginization / Future Platform Layer",
    ]:
        assert phrase in readme

    for phrase in [
        "Phase 3: Domain Pack Formalization",
        "Phase 4: Knowledge Config V2 + Local Eval Strengthening",
        "Phase 5: Docs And Public Explanation Sync",
        "Phase 6: Agent GraphRAG Pluginization / Future Platform Layer",
        "`Phase 3` is complete",
        "`Phase 4` is complete",
        "`Phase 5` is complete",
        "`Phase 6` is complete",
    ]:
        assert phrase in phases


def test_public_docs_keep_history_off_front_path_but_reachable() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    architecture_index = (
        REPO_ROOT / "docs" / "architecture" / "README.md"
    ).read_text(encoding="utf-8")
    development_index = (
        REPO_ROOT / "docs" / "development" / "README.md"
    ).read_text(encoding="utf-8")

    assert "./docs/architecture/phases/README.md" in readme
    assert "./history/README.md" in architecture_index
    assert "history/README.md" in development_index
    assert "`src/backend/zuno` 是当前唯一后端运行真相" in readme
    assert "./phases/README.md" in architecture_index


def test_launcher_docs_label_phase0_as_recovery_surface() -> None:
    launcher_docs = (
        REPO_ROOT / "tools" / "launchers" / "windows" / "README.md"
    ).read_text(encoding="utf-8")

    assert "Phase 0" in launcher_docs
    assert "recovery" in launcher_docs.lower()
    assert "Phase0-Backend-Start" in launcher_docs


def test_public_release_staging_plan_uses_clean_history_link() -> None:
    content = (
        REPO_ROOT / "docs" / "development" / "public-release-staging-plan.md"
    ).read_text(encoding="utf-8")

    assert "development/history/README.md" in content
    assert "05_TopDown_题库学习/项目/02_项目映射/Zuno/" not in content
