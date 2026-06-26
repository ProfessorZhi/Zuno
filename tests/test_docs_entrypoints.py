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
        "docs/architecture/history/programs/official-graphrag-cleanup-v1/",
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
        "verify_active_spec_domain_pack_boundaries",
        "verify_near_term_retired_runtime_boundaries",
        "verify_architecture_decision_boundaries",
        "verify_active_docs_do_not_link_retired_architecture_current_paths",
        "docs/architecture/plans/",
        "Domain Pack retrieval policy inputs",
        "Current Evidence: `DomainQAGraph`",
        "0001-domain-pack-binding.md",
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


def test_active_docs_do_not_link_retired_architecture_current_paths() -> None:
    active_docs = [
        path
        for path in REPO_ROOT.glob("docs/**/*.md")
        if "docs/architecture/history" not in path.as_posix()
    ]
    forbidden = [
        "docs/architecture/plans/",
        "docs/architecture/phases/",
        "docs/architecture/programs/",
    ]

    for path in active_docs:
        content = path.read_text(encoding="utf-8")
        for phrase in forbidden:
            assert phrase not in content, f"{path} links retired architecture current path: {phrase}"


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
        "Root `domain-packs/` assets are archived",
        "Docker no longer copies or mounts `/app/domain-packs`",
        "`src/backend/zuno/services/domain_pack/` runtime service package",
        "not mounted on the current FastAPI router",
        "not active knowledge routes or settings-shell pages",
    ]:
        assert phrase in current

    for phrase in [
        "Phase 11A: complete",
        "Phase 11B: complete",
        "Phase 11C: active runtime cleanup complete",
        "Phase 12: partial / not closed",
        "Bounded migration compatibility evidence remains",
        "full pytest",
        "eval baseline comparison",
    ]:
        assert phrase in roadmap


def test_repository_docs_do_not_keep_local_download_reference() -> None:
    for path in [*REPO_ROOT.glob("docs/**/*.md"), *REPO_ROOT.glob(".agent/**/*.md")]:
        content = path.read_text(encoding="utf-8")
        assert "C:\\Users\\Administrator\\Downloads" not in content


def test_stable_architecture_specs_do_not_make_domain_pack_the_target_driver() -> None:
    allowed_migration_specs = {
        REPO_ROOT / "docs/architecture/specs/README.md",
    }
    stable_specs = sorted(
        path
        for path in (REPO_ROOT / "docs/architecture/specs").glob("*.md")
        if path not in allowed_migration_specs
    )
    forbidden_phrases = [
        "Domain Pack\n  ->",
        "Domain Pack ->",
        "Domain Pack retrieval policy inputs",
        "Domain-specific graph cues belong in `Domain Pack retrieval_policy`",
        "GraphRAG 不是孤立能力，而是受 Domain Pack 驱动",
        "Domain Pack 成为领域扩展机制",
        "GraphRAG 受 `Domain Pack` 控制",
        "LangGraph runtime 必须能感知 Domain Pack",
        "它验证 Domain Pack 是否有价值",
        "Domain Pack schema",
        "Phase 3: Domain Pack Formalization",
        "deeper LangGraph, GraphRAG, Domain Pack",
        "business orchestration, retrieval, GraphRAG, Domain Pack, provider adapters",
    ]

    for path in stable_specs:
        content = path.read_text(encoding="utf-8")
        for phrase in forbidden_phrases:
            assert phrase not in content, f"{path} still promotes Domain Pack target wording: {phrase}"


def test_near_term_architecture_docs_do_not_mark_retired_runtime_as_current() -> None:
    near_term_docs = sorted((REPO_ROOT / ".agent/architecture/near-term").glob("*.md"))
    forbidden_phrases = [
        "Current Evidence: `DomainQAGraph`",
        "current Domain Pack state",
        "`DomainQAGraph` carries runtime settings",
        "`DomainQAGraph` collects trace and cost metadata",
        "including legacy-facing `domain_packs`",
        "Current storage and query filters still use `domain_pack_id`",
        "remaining Domain Pack pages are migration/runtime surfaces",
    ]

    for path in near_term_docs:
        content = path.read_text(encoding="utf-8")
        for phrase in forbidden_phrases:
            assert phrase not in content, (
                f"{path} marks retired Domain Pack runtime evidence as current: {phrase}"
            )


def test_architecture_decisions_do_not_keep_domain_pack_binding_as_active_mainline() -> None:
    active_decision = (
        REPO_ROOT / "docs/architecture/decisions/0001-domain-pack-binding.md"
    )
    history_decision = (
        REPO_ROOT
        / "docs/architecture/history/decisions/0001-domain-pack-binding.md"
    )
    decisions_index = (
        REPO_ROOT / "docs/architecture/decisions/README.md"
    ).read_text(encoding="utf-8")

    assert not active_decision.exists()
    assert history_decision.exists()
    assert "0001-domain-pack-binding.md" not in decisions_index
    assert "ADR 0002: Retire Compat Namespace" in decisions_index


def test_active_architecture_audits_are_not_history_documents() -> None:
    active_audits = sorted((REPO_ROOT / "docs/architecture/audits").glob("*.md"))
    assert active_audits

    for path in active_audits:
        content = path.read_text(encoding="utf-8")
        assert "Status: History" not in content, (
            f"{path} is marked History but remains in active architecture audits"
        )


def test_doc_boundary_verifier_rejects_history_status_in_active_audits() -> None:
    content = (
        REPO_ROOT / ".agent/scripts/verify_doc_boundaries.py"
    ).read_text(encoding="utf-8")

    assert "verify_active_audits_are_not_history_documents" in content
    assert "active architecture audit is marked History" in content
