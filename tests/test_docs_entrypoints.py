from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_readme_exposes_short_first_reader_path() -> None:
    content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    required_phrases = [
        "./docs/architecture/current-architecture.md",
        "./docs/architecture/target-architecture.md",
        "./docs/architecture/roadmap.md",
        "./docs/evidence/public-demo.md",
        "First-time readers start here:",
        "Blocked Legacy",
        "Phase 11A",
        "Phase 11B",
        "Completion API -> CompletionService -> GeneralAgent single loop",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing README first-reader phrase: {phrase}"


def test_docs_index_prioritizes_stable_public_path() -> None:
    content = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")

    required_phrases = [
        "./architecture/current-architecture.md",
        "./architecture/target-architecture.md",
        "./architecture/roadmap.md",
        "./evidence/public-demo.md",
        "./architecture/history/README.md",
        "## First-Read Path",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing docs index phrase: {phrase}"


def test_architecture_docs_use_current_target_roadmap_path() -> None:
    content = (REPO_ROOT / "docs" / "architecture" / "README.md").read_text(
        encoding="utf-8"
    )

    required_phrases = [
        "current-architecture.md",
        "target-architecture.md",
        "roadmap.md",
        "../evidence/public-demo.md",
        ".agent/programs/official-graphrag-cleanup-v1/",
        ".agent/programs/zuno-target-architecture-migration-v1/",
        "history/phases/",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing architecture index phrase: {phrase}"


def test_evidence_page_links_selected_public_demo_material() -> None:
    content = (REPO_ROOT / "docs" / "evidence" / "public-demo.md").read_text(
        encoding="utf-8"
    )

    required_phrases = [
        "../development/public-demo-evidence.md",
        "../development/public-demo-runbook.md",
        "../development/public-demo-acceptance.md",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing evidence link: {phrase}"


def test_verify_docs_entrypoints_script_tracks_current_public_entry_surface() -> None:
    content = (
        REPO_ROOT / "tools" / "scripts" / "verify_docs_entrypoints.py"
    ).read_text(encoding="utf-8")

    required_phrases = [
        "documentation entrypoint verification passed.",
        "./docs/architecture/current-architecture.md",
        "./docs/architecture/target-architecture.md",
        "./docs/architecture/roadmap.md",
        "./docs/evidence/public-demo.md",
        "Blocked Legacy",
        "Phase 11A",
        "Phase 11B",
        "Phase 11C",
        "Phase 12",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing docs entrypoint verifier phrase: {phrase}"


def test_active_entrypoints_do_not_restore_retired_front_path() -> None:
    files = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "docs" / "README.md",
        REPO_ROOT / "docs" / "architecture" / "README.md",
    ]
    forbidden = [
        "docs/architecture/plans/stable-baseline-recovery-and-runtime-deepening-plan.md",
        "./docs/architecture/phases/README.md",
        "./phases/README.md",
        "./plans/",
        "05_TopDown_题库学习/项目/02_项目映射/Zuno/",
    ]

    for path in files:
        content = path.read_text(encoding="utf-8")
        for phrase in forbidden:
            assert phrase not in content, f"{path} contains retired front-path text: {phrase}"


def test_current_target_and_roadmap_do_not_promote_target_runtime_to_current() -> None:
    current = (REPO_ROOT / "docs" / "architecture" / "current-architecture.md").read_text(
        encoding="utf-8"
    )
    roadmap = (REPO_ROOT / "docs" / "architecture" / "roadmap.md").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "GeneralAgent single loop",
        "GraphRAG Project Query Runtime",
        "Context Orchestrator and new Memory layering are Target, not Current",
        "Domain Pack route/service/frontend/eval/Docker surfaces",
    ]:
        assert phrase in current

    for phrase in [
        "Phase 11A: complete",
        "Phase 11B: complete",
        "Phase 11C: blocked",
        "Phase 12: partial / not closed",
        "11C active dependency removal",
        "full pytest",
        "eval baseline comparison",
    ]:
        assert phrase in roadmap


def test_repository_docs_do_not_keep_local_download_reference() -> None:
    for path in [*REPO_ROOT.glob("docs/**/*.md"), *REPO_ROOT.glob(".agent/**/*.md")]:
        content = path.read_text(encoding="utf-8")
        assert "C:\\Users\\Administrator\\Downloads" not in content
