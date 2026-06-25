from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_required_current_paths_exist() -> None:
    required_paths = [
        "AGENTS.md",
        ".agent/README.md",
        ".agent/programs/current.md",
        ".agent/programs/official-graphrag-cleanup-v1",
        "apps/desktop",
        "apps/web",
        "docs/architecture/current-architecture.md",
        "docs/architecture/target-architecture.md",
        "docs/architecture/roadmap.md",
        "docs/architecture/history/phases/README.md",
        "docs/architecture/history/plans/README.md",
        "docs/evidence/public-demo.md",
        "domain-packs",
        "src/backend/zuno/main.py",
        "tests/compat",
        "tools/evals/zuno",
    ]

    for relative_path in required_paths:
        assert (REPO_ROOT / relative_path).exists(), f"missing required path: {relative_path}"


def test_retired_front_path_directories_are_not_current_paths() -> None:
    retired_paths = [
        "docs/architecture/phases",
        "docs/architecture/plans",
        "docs/architecture/programs",
        "docs/superpowers",
        "docs/prototypes/superpowers-legacy",
        "docs/ui-gallery/knowledge-product-refactor-deep-graphrag-v1",
        "src/frontend",
    ]

    for relative_path in retired_paths:
        assert not (REPO_ROOT / relative_path).exists(), f"retired path still current: {relative_path}"


def test_front_path_docs_link_current_entrypoints() -> None:
    architecture_index = (
        REPO_ROOT / "docs" / "architecture" / "README.md"
    ).read_text(encoding="utf-8")
    docs_index = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "current-architecture.md" in architecture_index
    assert "target-architecture.md" in architecture_index
    assert "roadmap.md" in architecture_index
    assert "../evidence/public-demo.md" in architecture_index
    assert "./architecture/roadmap.md" in docs_index
    assert "./docs/architecture/roadmap.md" in readme


def test_phase_completion_truth_is_historical() -> None:
    content = (
        REPO_ROOT / "docs" / "architecture" / "history" / "phases" / "README.md"
    ).read_text(encoding="utf-8")

    required_phrases = [
        "Phase 0: Stable Runtime Recovery",
        "Phase 1: LangGraph Runtime Deepening",
        "Phase 2: GraphRAG Mainline Deepening",
        "Phase 3: Domain Pack Formalization",
        "Phase 4: Knowledge Config V2 + Local Eval Strengthening",
        "Phase 5: Docs And Public Explanation Sync",
        "Phase 6: Agent GraphRAG Pluginization / Future Platform Layer",
        "the user has personally tried the recovered runtime",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing historical phase phrase: {phrase}"


def test_readme_mentions_current_backend_start_and_focused_verification() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    required_phrases = [
        "python tools/scripts/verify_docs_entrypoints.py",
        "python tools/scripts/verify_repo_structure.py",
        "pytest -q tests/test_repo_structure_consistency.py",
        "pytest -q tests/test_publish_boundary.py",
        "uvicorn --app-dir src/backend zuno.main:app --host 0.0.0.0 --port 7860",
        "domain-packs/",
        "Blocked Legacy",
    ]

    for phrase in required_phrases:
        assert phrase in readme, f"missing README phrase: {phrase}"


def test_reference_migration_doc_is_archived_out_of_front_path() -> None:
    assert not (REPO_ROOT / "docs" / "reference" / "migration.md").exists()
    assert (REPO_ROOT / "docs" / "reference" / "history" / "migration.md").exists()
