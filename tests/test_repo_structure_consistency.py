from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_phase0_required_paths_exist() -> None:
    required_paths = [
        "apps/desktop",
        "apps/web",
        "docs/architecture",
        "docs/development",
        "domain-packs",
        "infra/db",
        "infra/docker",
        "services",
        "services/api",
        "src/backend",
        "src/backend/zuno",
        "src/backend/zuno/main.py",
        "tests",
        "tests/compat",
        "tools",
        "tools/evals/zuno",
        "tools/launchers/windows",
    ]

    for relative_path in required_paths:
        assert (REPO_ROOT / relative_path).exists(), f"missing required path: {relative_path}"


def test_front_path_docs_link_current_phase0_entrypoints() -> None:
    architecture_index = (
        REPO_ROOT / "docs" / "architecture" / "README.md"
    ).read_text(encoding="utf-8")
    plans_index = (
        REPO_ROOT / "docs" / "architecture" / "plans" / "README.md"
    ).read_text(encoding="utf-8")
    docs_index = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")

    assert "./current-architecture.md" in architecture_index
    assert "./target-architecture.md" in architecture_index
    assert "./phases/README.md" in architecture_index
    assert "./plans/stable-baseline-recovery-and-runtime-deepening-plan.md" in architecture_index
    assert "../phases/README.md" in plans_index
    assert "./architecture/README.md" in docs_index
    assert "./development/README.md" in docs_index
    assert "./development/architecture-doc-maintenance-workflow.md" in docs_index


def test_phase_index_matches_phase0_to_phase5_program() -> None:
    content = (
        REPO_ROOT / "docs" / "architecture" / "phases" / "README.md"
    ).read_text(encoding="utf-8")

    required_phrases = [
        "Phase 0: Stable Runtime Recovery",
        "Phase 1: LangGraph Runtime Deepening",
        "Phase 2: GraphRAG Mainline Deepening",
        "Phase 3: Domain Pack Formalization",
        "Phase 4: Local Eval Strengthening",
        "Phase 5: Docs And Public Explanation Sync",
        "the user has personally tried the recovered runtime",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing phase phrase: {phrase}"


def test_readme_mentions_phase0_backend_start_and_focused_verification() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    required_phrases = [
        "python tools/scripts/verify_docs_entrypoints.py",
        "pytest tests/test_phase0_runtime_recovery.py",
        "python tools/scripts/verify_repo_structure.py",
        "pytest tests/test_repo_structure_consistency.py",
        "pytest tests/test_publish_boundary.py",
        "uvicorn --app-dir src/backend zuno.main:app --host 0.0.0.0 --port 7860",
        "services/",
        "domain-packs/",
    ]

    for phrase in required_phrases:
        assert phrase in readme, f"missing Phase 0 phrase: {phrase}"


def test_backend_layering_guidelines_use_src_backend_as_default() -> None:
    content = (
        REPO_ROOT / "docs" / "development" / "backend-layering-guidelines.md"
    ).read_text(encoding="utf-8")

    required_phrases = [
        "src/backend/zuno/api/*",
        "src/backend/zuno/core/*",
        "src/backend/zuno/services/*",
        "src/backend/zuno/database/dao/*",
        "do not treat `services/api/src/zuno/*` as the default placement rule while Phase 0 is still open",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing backend-layering Phase 0 phrase: {phrase}"


def test_reference_migration_doc_is_archived_out_of_front_path() -> None:
    assert not (REPO_ROOT / "docs" / "reference" / "migration.md").exists()
    assert (REPO_ROOT / "docs" / "reference" / "history" / "migration.md").exists()


def test_tools_scripts_readme_describes_recovery_period_start_surface() -> None:
    content = (REPO_ROOT / "tools" / "scripts" / "README.md").read_text(encoding="utf-8")

    required_phrases = [
        "local recovery-period starter",
        "`apps/web`",
        "mixed-runtime recovery period",
        "python tools/scripts/start.py",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing tools/scripts Phase 0 phrase: {phrase}"
