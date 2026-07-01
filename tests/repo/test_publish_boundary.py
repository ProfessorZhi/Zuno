from pathlib import Path
import runpy
import shlex


REPO_ROOT = Path(__file__).resolve().parents[2]


def _current_phase_name(content: str) -> str | None:
    for line in content.splitlines():
        if line.startswith("current_phase:"):
            return line.split(":", 1)[1].strip().strip("`")
    return None


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
    architecture = (REPO_ROOT / "docs" / "architecture" / "architecture.md").read_text(
        encoding="utf-8"
    )
    current_program = (REPO_ROOT / ".agent" / "programs" / "current.md").read_text(
        encoding="utf-8"
    )

    for phrase in [
        ".agent/programs/",
        "zuno-production-architecture-and-deliverables-completion-v1",
        "docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/",
        "zuno-target-architecture-runtime-full-implementation-v1",
        "zuno-master-architecture-implementation-v1",
    ]:
        assert phrase in readme

    for phrase in [
        "Current",
        "Target",
        "Document Ingestion / Parse Gateway",
        "Tool Control Plane",
        "LangSmith-compatible Trace / Eval",
    ]:
        assert phrase in architecture
    assert _current_phase_name(current_program) == "PHASE05_memory-context-engine.md"
    assert "state: active" in current_program
    assert "active_program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1" in current_program
    assert "latest_completed_program: zuno-enterprise-document-ingestion-platform-v2" in current_program
    assert "zuno-enterprise-agentic-graphrag-production-suite-v1" in current_program
    assert "docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/" in current_program
    assert "zuno-production-architecture-and-deliverables-completion-v1" in readme
    assert "zuno-production-architecture-and-deliverables-completion-v1" in architecture
    assert "一次性交付型成熟化 program" in current_program
    assert "zuno-production-document-ingestion-and-thread-foundation-v1" in current_program
    assert "zuno-launchable-enterprise-agentic-graphrag-full-closure-v1" in current_program
    assert "zuno-enterprise-ingestion-async-infrastructure-v1" in current_program
    assert "zuno-target-architecture-runtime-full-implementation-v1" in current_program
    assert "docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/" in current_program


def test_public_docs_keep_history_off_front_path_but_reachable() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    architecture_index = (
        REPO_ROOT / "docs" / "architecture" / "README.md"
    ).read_text(encoding="utf-8")
    history_index = (REPO_ROOT / "docs" / "history" / "README.md").read_text(
        encoding="utf-8"
    )

    assert "./docs/architecture/architecture.md" in readme
    assert "docs/history/architecture-surface-cleanup-2026-06-30/" in architecture_index
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
        REPO_ROOT / "docs" / "history" / "development" / "public-release-staging-plan.md"
    ).read_text(encoding="utf-8")

    assert "README.md" in content
    assert "05_TopDown_题库学习/项目/02_项目映射/Zuno/" not in content


def test_public_release_guidance_does_not_keep_retired_runtime_group() -> None:
    staging_plan = (
        REPO_ROOT / "docs" / "history" / "development" / "public-release-staging-plan.md"
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


def test_public_release_stage_commands_do_not_cross_backend_group_boundaries() -> None:
    namespace = runpy.run_path(
        str(REPO_ROOT / "tools" / "scripts" / "print_public_release_stage_commands.py")
    )
    stage_groups = dict(namespace["STAGE_GROUPS"])
    commands = stage_groups["backend_public_entrypoints"]
    staged_paths = [
        token
        for command in commands
        for token in shlex.split(command, posix=False)
        if token not in {"git", "add"}
    ]

    assert "src/backend/zuno/" not in staged_paths, (
        "backend_public_entrypoints stage command must not include broad "
        "src/backend/zuno/ because it can stage backend_domain_runtime or "
        "backend_rag_graphrag_eval changes into the wrong commit"
    )


def test_public_release_audit_blocks_entire_superpowers_tree() -> None:
    audit_script = (
        REPO_ROOT / "tools" / "scripts" / "audit_public_release.py"
    ).read_text(encoding="utf-8")

    assert '"docs/superpowers/"' in audit_script
    assert '"docs/superpowers/specs/"' not in audit_script


def test_public_release_preview_ready_note_points_to_existing_history() -> None:
    namespace = runpy.run_path(
        str(REPO_ROOT / "tools" / "scripts" / "preview_public_release_group.py")
    )
    ready_note = namespace["DOCS_AND_README_READY_NOTE"]

    assert ready_note == "docs/history/development/docs-and-readme-ready.md"
    assert (REPO_ROOT / ready_note).exists()


def test_public_demo_docs_prefer_graphrag_project_id() -> None:
    runbook = (
        REPO_ROOT / "docs" / "history" / "development" / "public-demo-runbook.md"
    ).read_text(encoding="utf-8")

    assert "--graphrag-project-id contract_review" in runbook
    assert "--domain-pack-id contract_review" not in runbook


def test_architecture_maintenance_workflow_tracks_project_contracts() -> None:
    workflow = (
        REPO_ROOT
        / "docs"
        / "history"
        / "development"
        / "architecture-doc-maintenance-workflow.md"
    ).read_text(encoding="utf-8")

    assert "GraphRAG Project / migration compatibility contracts" in workflow
    assert "GraphRAG / Domain Pack contracts" not in workflow
