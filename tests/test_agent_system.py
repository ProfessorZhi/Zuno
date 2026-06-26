from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_agent_system_required_paths_exist() -> None:
    required_paths = [
        "apps/web/AGENTS.md",
        "src/backend/zuno/AGENTS.md",
        "tools/evals/zuno/AGENTS.md",
        ".agent/references/workflow-map.md",
        ".agent/references/skills-map.md",
        ".agent/references/local-state-map.md",
        ".agent/workflows/docs-maintenance.md",
        ".agent/workflows/repo-hygiene.md",
        ".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html",
        ".agent/architecture/near-term/18-context-memory-ideal-architecture.md",
        ".agent/architecture/near-term/19-repository-layout-and-module-boundaries.md",
        "docs/architecture/history/programs/zuno-target-architecture-migration-v1/README.md",
        "docs/architecture/history/programs/zuno-target-architecture-migration-v1/implementation-roadmap.md",
        "docs/architecture/history/programs/zuno-target-architecture-migration-v1/implementation-phases/README.md",
        "docs/architecture/history/programs/context-memory-agent-runtime-v1/README.md",
        ".agent/skills/zuno-docs-maintenance/SKILL.md",
        ".agent/skills/zuno-repo-hygiene/SKILL.md",
        ".agent/lessons/README.md",
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
        ".agent/lessons/",
        "Temporary discovery -> `.agent/local/notes/`",
        "Implemented, verified, human-facing facts -> `docs/`",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing promotion phrase: {phrase}"


def test_current_program_points_to_target_migration_and_archives_old_candidate() -> None:
    current = (REPO_ROOT / ".agent" / "programs" / "current.md").read_text(encoding="utf-8")
    programs_index = (REPO_ROOT / ".agent" / "programs" / "README.md").read_text(
        encoding="utf-8"
    )
    history_index = (
        REPO_ROOT / "docs" / "architecture" / "history" / "programs" / "README.md"
    ).read_text(encoding="utf-8")

    assert "There is no active executable Agent program" in current
    assert "zuno-target-architecture-migration-v1/README.md" not in programs_index
    assert "zuno-target-architecture-migration-v1/" in history_index
    assert "context-memory-agent-runtime-v1" not in programs_index
    assert "context-memory-agent-runtime-v1" in history_index


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
    current_validation = (
        REPO_ROOT / ".agent/references/current_architecture/validation.md"
    ).read_text(encoding="utf-8")

    assert ".agent/scripts/grep-domain-pack.ps1" in verification_map
    assert ".agent/scripts/grep-domain-pack.ps1" in current_validation
