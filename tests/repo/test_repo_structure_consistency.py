import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_required_current_paths_exist() -> None:
    required_paths = [
        "AGENTS.md",
        ".agent/README.md",
        ".agent/references/README.md",
        ".agent/references/task-routing.md",
        ".agent/references/workflow.md",
        ".agent/references/docs-map.md",
        ".agent/programs/current.md",
        ".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html",
        ".agent/architecture/near-term/01-target-runtime-architecture.md",
        ".agent/architecture/near-term/02-context-memory-architecture.md",
        ".agent/architecture/near-term/03-capability-tool-retrieval-architecture.md",
        ".agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md",
        ".agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md",
        "apps/desktop",
        "apps/web",
        "docs/README.md",
        "docs/architecture/current-architecture.md",
        "docs/architecture/target-architecture.md",
        "docs/architecture/roadmap.md",
        "docs/evidence/public-demo.md",
        "docs/reference/terminology.md",
        "docs/history/README.md",
        "docs/history/phases/README.md",
        "docs/history/plans/README.md",
        "docs/history/programs/README.md",
        "docs/history/development/README.md",
        "docs/history/reference/migration.md",
        "docs/history/audits",
        "docs/history/specs",
        "docs/history/domain-packs/root-contract-review/contract_review/pack.yaml",
        "src/backend/zuno/main.py",
        "tools/evals/zuno",
    ]

    for relative_path in required_paths:
        assert (REPO_ROOT / relative_path).exists(), f"missing required path: {relative_path}"


def test_repo_structure_verifier_pins_current_front_path() -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    required_paths = set(verifier.REQUIRED_PATHS)
    for relative_path in [
        "AGENTS.md",
        ".agent/references/task-routing.md",
        ".agent/references/workflow.md",
        "docs/README.md",
        "docs/architecture/current-architecture.md",
        "docs/architecture/target-architecture.md",
        "docs/architecture/roadmap.md",
        "docs/evidence/public-demo.md",
        "docs/reference/terminology.md",
        "docs/history/audits",
        "docs/history/specs",
        "docs/history/development/README.md",
    ]:
        assert relative_path in required_paths


def test_retired_front_path_directories_are_not_current_paths() -> None:
    retired_paths = [
        "docs/architecture/history",
        "docs/architecture/audits",
        "docs/architecture/specs",
        "docs/architecture/phases",
        "docs/architecture/plans",
        "docs/architecture/programs",
        "docs/development",
        "docs/prototypes",
        "docs/ui-review",
        "docs/ui-gallery",
        "docs/reference/api.md",
        "docs/reference/core.md",
        "docs/reference/database.md",
        "docs/reference/service.md",
        "docs/reference/zuno.md",
        ".agent/skills",
        ".agent/workflows",
        ".agent/programs/context-memory-agent-runtime-v1",
        ".agent/programs/official-graphrag-cleanup-v1",
        "docs/superpowers",
        "src/frontend",
        "domain-packs",
        "tests/compat",
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
    content = (REPO_ROOT / "docs" / "history" / "phases" / "README.md").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "Phase 0: Stable Runtime Recovery",
        "Phase 1: LangGraph Runtime Deepening",
        "Phase 2: GraphRAG Mainline Deepening",
        "Phase 3: Domain Pack Formalization",
        "Phase 4: Knowledge Config V2 + Local Eval Strengthening",
        "Phase 5: Docs And Public Explanation Sync",
        "Phase 6: Agent GraphRAG Pluginization / Future Platform Layer",
    ]:
        assert phrase in content


def test_readme_mentions_current_backend_start_and_focused_verification() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    for phrase in [
        "python tools/scripts/verify_docs_entrypoints.py",
        "python tools/scripts/verify_repo_structure.py",
        "pytest -q tests/repo/test_repo_structure_consistency.py",
        "pytest -q tests/repo/test_publish_boundary.py",
        "uvicorn --app-dir src/backend zuno.main:app --host 0.0.0.0 --port 7860",
        "受限历史兼容",
        "docs/history/domain-packs/root-contract-review/",
        "Phase 11A",
        "Phase 11B",
        "Phase 11C",
        "Phase 12",
    ]:
        assert phrase in readme


def test_reference_migration_doc_is_archived_out_of_front_path() -> None:
    assert not (REPO_ROOT / "docs" / "reference" / "migration.md").exists()
    assert (REPO_ROOT / "docs" / "history" / "reference" / "migration.md").exists()


def test_active_v2_program_is_slim_and_phase_details_are_archived() -> None:
    active_files = sorted(
        path.name
        for path in (REPO_ROOT / ".agent" / "programs" / "zuno-target-runtime-v2").iterdir()
        if path.is_file()
    )

    assert active_files == sorted(
        ["README.md", "implementation-roadmap.md", "current-phase.md", "closure-checklist.md"]
    )
    assert not (
        REPO_ROOT / ".agent/programs/zuno-target-runtime-v2/implementation-phases"
    ).exists()
    assert (
        REPO_ROOT
        / "docs/history/programs/zuno-target-runtime-v2/implementation-phases/README.md"
    ).exists()

    roadmap = (
        REPO_ROOT / ".agent/programs/zuno-target-runtime-v2/implementation-roadmap.md"
    ).read_text(encoding="utf-8")
    for phrase in [
        "Phase 05：记忆引擎",
        "Phase 06：能力与工具检索",
        "Phase 07：知识检索与融合",
        "Phase 08：GeneralAgent LangGraph 运行时",
        "Phase 09：产品边界、Trace 与 Eval 收口",
    ]:
        assert phrase in roadmap


def test_superseded_specs_are_archived_out_of_architecture_front_path() -> None:
    assert not (REPO_ROOT / "docs" / "architecture" / "specs").exists()
    for relative_path in [
        "deep-graphrag-v1-runtime.md",
        "domain-pack-langgraph-graphrag-architecture.md",
        "domain-pack-builder.md",
        "knowledge-product-boundary.md",
    ]:
        assert (REPO_ROOT / "docs" / "history" / "specs" / relative_path).exists()
