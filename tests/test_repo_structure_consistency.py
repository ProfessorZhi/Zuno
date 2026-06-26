import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_required_current_paths_exist() -> None:
    required_paths = [
        "AGENTS.md",
        ".agent/README.md",
        ".agent/programs/current.md",
        "docs/architecture/history/programs/zuno-target-architecture-migration-v1",
        ".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html",
        ".agent/architecture/near-term/19-repository-layout-and-module-boundaries.md",
        "apps/desktop",
        "apps/web",
        "docs/architecture/current-architecture.md",
        "docs/architecture/target-architecture.md",
        "docs/architecture/roadmap.md",
        "docs/architecture/history/phases/README.md",
        "docs/architecture/history/plans/README.md",
        "docs/architecture/history/programs/README.md",
        "docs/architecture/history/programs/context-memory-agent-runtime-v1/README.md",
        "docs/architecture/history/programs/official-graphrag-cleanup-v1/README.md",
        "docs/architecture/history/development/README.md",
        "docs/architecture/history/reference/migration.md",
        "docs/evidence/public-demo.md",
        "examples/graphrag-projects/contract_review/settings.yaml",
        "docs/architecture/history/domain-packs/root-contract-review/contract_review/pack.yaml",
        "src/backend/zuno/main.py",
        "tools/evals/zuno",
    ]

    for relative_path in required_paths:
        assert (REPO_ROOT / relative_path).exists(), f"missing required path: {relative_path}"


def test_repo_structure_verifier_pins_full_contract_review_asset_migration() -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    required_paths = set(verifier.REQUIRED_PATHS)
    for relative_path in [
        "examples/graphrag-projects/contract_review/settings.yaml",
        "examples/graphrag-projects/contract_review/schema.json",
        "examples/graphrag-projects/contract_review/retrieval_policy.yaml",
        "examples/graphrag-projects/contract_review/prompts/extract_graph.md",
        "examples/graphrag-projects/contract_review/prompts/local_query.md",
        "examples/graphrag-projects/contract_review/prompts/report_template.md",
        "examples/graphrag-projects/contract_review/eval/eval_dataset.jsonl",
        "docs/architecture/history/domain-packs/root-contract-review/contract_review/pack.yaml",
        "docs/architecture/history/domain-packs/root-contract-review/contract_review/schema.json",
        "docs/architecture/history/domain-packs/root-contract-review/contract_review/retrieval_policy.yaml",
        "docs/architecture/history/domain-packs/root-contract-review/contract_review/extraction_prompt.md",
        "docs/architecture/history/domain-packs/root-contract-review/contract_review/answer_template.md",
        "docs/architecture/history/domain-packs/root-contract-review/contract_review/report_template.md",
        "docs/architecture/history/domain-packs/root-contract-review/contract_review/eval_dataset.jsonl",
        "docs/architecture/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/capture_knowledge_product_ui_gallery.py",
        "docs/architecture/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/check_knowledge_product_responsive.py",
        "docs/architecture/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/check_settings_navigation_interaction.py",
        "docs/architecture/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/preview_phase6_bundle_scope.py",
        "docs/architecture/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/verify_phase6_bundle_ready.py",
    ]:
        assert relative_path in required_paths


def test_retired_front_path_directories_are_not_current_paths() -> None:
    retired_paths = [
        "docs/architecture/phases",
        "docs/architecture/plans",
        "docs/architecture/programs",
        ".agent/programs/context-memory-agent-runtime-v1",
        ".agent/programs/official-graphrag-cleanup-v1",
        "docs/superpowers",
        "docs/prototypes/superpowers-legacy",
        "docs/ui-gallery/knowledge-product-refactor-deep-graphrag-v1",
        "src/frontend",
        "domain-packs",
        "tests/compat",
        "docs/development/history",
        "docs/reference/history",
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
        "Bounded Legacy Compatibility",
        "docs/architecture/history/domain-packs/root-contract-review/",
        "Phase 11A",
        "Phase 11B",
        "Phase 11C",
        "Phase 12",
    ]

    for phrase in required_phrases:
        assert phrase in readme, f"missing README phrase: {phrase}"


def test_reference_migration_doc_is_archived_out_of_front_path() -> None:
    assert not (REPO_ROOT / "docs" / "reference" / "migration.md").exists()
    assert (
        REPO_ROOT / "docs" / "architecture" / "history" / "reference" / "migration.md"
    ).exists()


def test_official_graphrag_cleanup_program_is_archived_out_of_active_programs() -> None:
    assert not (REPO_ROOT / ".agent/programs/official-graphrag-cleanup-v1").exists()
    assert not (REPO_ROOT / ".agent/programs/zuno-target-architecture-migration-v1").exists()
    assert (
        REPO_ROOT
        / "docs/architecture/history/programs/official-graphrag-cleanup-v1/README.md"
    ).exists()
    assert (
        REPO_ROOT
        / "docs/architecture/history/programs/zuno-target-architecture-migration-v1/README.md"
    ).exists()

    programs_index = (REPO_ROOT / ".agent/programs/README.md").read_text(
        encoding="utf-8"
    )
    history_index = (
        REPO_ROOT / "docs/architecture/history/programs/README.md"
    ).read_text(encoding="utf-8")

    assert "official-graphrag-cleanup-v1/" not in programs_index
    assert "zuno-target-architecture-migration-v1/README.md" not in programs_index
    assert "official-graphrag-cleanup-v1/" in history_index
    assert "zuno-target-architecture-migration-v1/" in history_index


def test_superseded_migration_specs_are_archived_out_of_active_specs() -> None:
    for relative_path in [
        "deep-graphrag-v1-runtime.md",
        "domain-pack-langgraph-graphrag-architecture.md",
        "domain-pack-builder.md",
        "knowledge-product-boundary.md",
    ]:
        assert not (REPO_ROOT / "docs" / "architecture" / "specs" / relative_path).exists()
        assert (REPO_ROOT / "docs" / "architecture" / "history" / "specs" / relative_path).exists()

    specs_index = (
        REPO_ROOT / "docs" / "architecture" / "specs" / "README.md"
    ).read_text(encoding="utf-8")
    history_index = (
        REPO_ROOT / "docs" / "architecture" / "history" / "README.md"
    ).read_text(encoding="utf-8")

    assert "../history/specs/domain-pack-builder.md" in specs_index
    assert "../history/specs/domain-pack-langgraph-graphrag-architecture.md" in specs_index
    assert "../history/specs/knowledge-product-boundary.md" in specs_index
    assert "../history/specs/deep-graphrag-v1-runtime.md" in specs_index
    assert "`specs/`: superseded architecture specs" in history_index
