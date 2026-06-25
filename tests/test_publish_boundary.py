from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_gitignore_matches_current_local_only_boundary() -> None:
    content = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")

    required_entries = [
        ".local/",
        "infra/docker/docker_config.local.yaml",
        ".local/config/zuno/",
        ".local/evals/zuno/rag_eval/corpus/",
        ".local/evals/zuno/rag_eval/runs/",
    ]

    for entry in required_entries:
        assert entry in content, f"missing local-only ignore: {entry}"


def test_readme_and_roadmap_share_current_program_truth() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    roadmap = (REPO_ROOT / "docs" / "architecture" / "roadmap.md").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "Phase 0-6 architecture closure remains complete historical truth.",
        "official GraphRAG alignment program",
        "Blocked Legacy",
    ]:
        assert phrase in readme

    for phrase in [
        "Phase 11A: complete",
        "Phase 11B: complete",
        "Phase 11C: blocked",
        "Phase 12: partial / not closed",
        "Phase 01 through Phase 10 are complete.",
        "Blocked Legacy",
    ]:
        assert phrase in roadmap


def test_public_docs_keep_history_off_front_path_but_reachable() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    architecture_index = (
        REPO_ROOT / "docs" / "architecture" / "README.md"
    ).read_text(encoding="utf-8")
    history_index = (
        REPO_ROOT / "docs" / "architecture" / "history" / "README.md"
    ).read_text(encoding="utf-8")

    assert "./docs/architecture/roadmap.md" in readme
    assert "history/phases/" in architecture_index
    assert "phases/" in history_index
    assert "plans/" in history_index
    assert "src/backend/zuno" in readme


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


def test_public_release_guidance_does_not_keep_retired_runtime_group() -> None:
    staging_plan = (
        REPO_ROOT / "docs" / "development" / "public-release-staging-plan.md"
    ).read_text(encoding="utf-8")
    commit_order = (
        REPO_ROOT / "tools" / "scripts" / "print_public_release_commit_order.py"
    ).read_text(encoding="utf-8")

    assert "retired_runtime_legacy" not in staging_plan
    assert "retired_runtime_legacy" not in commit_order
    assert "backend_domain_runtime" in staging_plan
    assert "backend_domain_runtime" in commit_order


def test_public_release_stage_commands_cover_release_guard_helpers() -> None:
    stage_commands = (
        REPO_ROOT / "tools" / "scripts" / "print_public_release_stage_commands.py"
    ).read_text(encoding="utf-8")

    for path in [
        "tools/scripts/preview_public_release_group.py",
        "tools/scripts/preview_public_release_stage_dry_run.py",
        "tools/scripts/verify_docs_and_readme_ready.py",
    ]:
        assert path in stage_commands


def test_public_demo_docs_prefer_graphrag_project_id() -> None:
    runbook = (
        REPO_ROOT / "docs" / "development" / "public-demo-runbook.md"
    ).read_text(encoding="utf-8")

    assert "--graphrag-project-id contract_review" in runbook
    assert "--domain-pack-id contract_review" not in runbook


def test_architecture_maintenance_workflow_tracks_project_contracts() -> None:
    workflow = (
        REPO_ROOT / "docs" / "development" / "architecture-doc-maintenance-workflow.md"
    ).read_text(encoding="utf-8")

    assert "GraphRAG Project / migration compatibility contracts" in workflow
    assert "GraphRAG / Domain Pack contracts" not in workflow
