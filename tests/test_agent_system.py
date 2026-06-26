from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_agent_system_required_paths_exist() -> None:
    required_paths = [
        "apps/web/AGENTS.md",
        "src/backend/zuno/AGENTS.md",
        "tools/evals/zuno/AGENTS.md",
        ".agent/references/code-map.md",
        ".agent/references/verification-map.md",
        ".agent/workflows/docs-maintenance.md",
        ".agent/workflows/repo-hygiene.md",
        ".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html",
        ".agent/architecture/near-term/01-target-runtime-architecture.md",
        ".agent/architecture/near-term/02-context-memory-architecture.md",
        ".agent/architecture/near-term/03-capability-tool-retrieval-architecture.md",
        ".agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md",
        ".agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md",
        ".agent/scripts/verify_module_boundaries.py",
        ".agent/programs/zuno-target-runtime-v2/README.md",
        ".agent/programs/zuno-target-runtime-v2/implementation-roadmap.md",
        ".agent/programs/zuno-target-runtime-v2/current-phase.md",
        ".agent/programs/zuno-target-runtime-v2/closure-checklist.md",
        "docs/architecture/history/programs/zuno-target-runtime-v2/README.md",
        "docs/architecture/history/programs/zuno-target-architecture-migration-v1/README.md",
        "docs/architecture/history/programs/zuno-target-architecture-migration-v1/implementation-roadmap.md",
        "docs/architecture/history/programs/zuno-target-architecture-migration-v1/implementation-phases/README.md",
        "docs/architecture/history/programs/context-memory-agent-runtime-v1/README.md",
        ".agent/skills/zuno-docs-maintenance/SKILL.md",
        ".agent/skills/zuno-repo-hygiene/SKILL.md",
    ]

    for relative_path in required_paths:
        assert (REPO_ROOT / relative_path).exists(), f"missing Agent path: {relative_path}"


def test_target_architecture_html_is_canonical_and_referenced() -> None:
    html_path = (
        REPO_ROOT
        / ".agent"
        / "architecture"
        / "near-term"
        / "zuno-ideal-architecture-and-repo-layout.html"
    )
    html = html_path.read_text(encoding="utf-8")
    assert "<html" in html.lower()
    assert "Zuno" in html
    assert "Target" in html or "Proposed" in html or "目标" in html
    for phrase in ["Native BM25", "RRF", "Summary Compression", "Structured Extraction", "ToolCard"]:
        assert phrase in html

    tracked_html = [
        path.replace("\\", "/")
        for path in __import__("subprocess")
        .run(
            ["git", "ls-files", "*.html"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        .stdout.splitlines()
        if "zuno-ideal-architecture" in path
    ]
    assert tracked_html == [
        ".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html"
    ]

    required_files = [
        "AGENTS.md",
        ".agent/architecture/near-term/README.md",
        ".agent/workflows/architecture-refactor.md",
        ".agent/workflows/repo-hygiene.md",
        ".agent/skills/zuno-architecture-refactor/SKILL.md",
        ".agent/skills/zuno-repo-hygiene/SKILL.md",
    ]
    for relative_path in required_files:
        content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        assert "zuno-ideal-architecture-and-repo-layout.html" in content


def test_root_agents_routes_to_module_agents_and_skills() -> None:
    content = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

    required_phrases = [
        "## Task Routing",
        "apps/web/AGENTS.md",
        "src/backend/zuno/AGENTS.md",
        "tools/evals/zuno/AGENTS.md",
        ".agent/skills/zuno-frontend-change/SKILL.md",
        ".agent/skills/zuno-backend-change/SKILL.md",
        ".agent/skills/zuno-eval-change/SKILL.md",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing root routing phrase: {phrase}"


def test_agent_readme_documents_knowledge_promotion() -> None:
    content = (REPO_ROOT / ".agent" / "README.md").read_text(encoding="utf-8")

    required_phrases = [
        ".agent/workflows/",
        ".agent/skills/",
        "Temporary discovery -> `.agent/local/notes/`",
        "Implemented, verified, human-facing facts -> `docs/`",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing promotion phrase: {phrase}"


def test_current_program_points_to_active_v2_and_archives_old_candidate() -> None:
    current = (REPO_ROOT / ".agent" / "programs" / "current.md").read_text(encoding="utf-8")
    programs_index = (REPO_ROOT / ".agent" / "programs" / "README.md").read_text(
        encoding="utf-8"
    )
    history_index = (
        REPO_ROOT / "docs" / "architecture" / "history" / "programs" / "README.md"
    ).read_text(encoding="utf-8")

    assert "zuno-target-runtime-v2/" in current
    assert "controlled first implementation slice" in current
    assert "zuno-target-architecture-migration-v1/README.md" not in programs_index
    assert "zuno-target-architecture-migration-v1/" in history_index
    assert "context-memory-agent-runtime-v1" not in programs_index
    assert "context-memory-agent-runtime-v1" in history_index


def test_near_term_architecture_uses_canonical_five_doc_set() -> None:
    files = sorted(
        path.name
        for path in (REPO_ROOT / ".agent" / "architecture" / "near-term").iterdir()
        if path.is_file()
    )

    assert files == sorted(
        [
            "README.md",
            "zuno-ideal-architecture-and-repo-layout.html",
            "01-target-runtime-architecture.md",
            "02-context-memory-architecture.md",
            "03-capability-tool-retrieval-architecture.md",
            "04-knowledge-graphrag-retrieval-fusion.md",
            "05-repository-boundaries-and-acceptance-gates.md",
        ]
    )


def test_agent_references_are_slim_navigation_set() -> None:
    files = sorted(
        path.name
        for path in (REPO_ROOT / ".agent" / "references").iterdir()
        if path.is_file()
    )

    assert files == sorted(
        [
            "README.md",
            "current-program.md",
            "docs-map.md",
            "code-map.md",
            "runtime-call-chain.md",
            "verification-map.md",
            "command-catalog.md",
            "known-pitfalls.md",
        ]
    )


def test_gitignore_allows_module_agents() -> None:
    content = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "apps/web/AGENTS.md" not in content
    assert ".agent/local/*" in content


def test_domain_pack_grep_helper_tracks_all_phase11c_legacy_patterns() -> None:
    content = (REPO_ROOT / ".agent/scripts/grep-domain-pack.ps1").read_text(
        encoding="utf-8"
    )

    for pattern in [
        "Domain Pack",
        "domain_pack",
        "DomainQAGraph",
        "MultiAgentSupervisorGraph",
        "domain-packs",
    ]:
        assert pattern in content

    assert "rg" in content
    assert "docs/architecture/history/**" in content

    verification_map = (
        REPO_ROOT / ".agent/references/verification-map.md"
    ).read_text(encoding="utf-8")

    assert ".agent/scripts/grep-domain-pack.ps1" in verification_map
