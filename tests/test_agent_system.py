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
        ".agent/skills/zuno-docs-maintenance/SKILL.md",
        ".agent/skills/zuno-repo-hygiene/SKILL.md",
        ".agent/lessons/README.md",
    ]

    for relative_path in required_paths:
        assert (REPO_ROOT / relative_path).exists(), f"missing Agent path: {relative_path}"


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


def test_gitignore_allows_module_agents() -> None:
    content = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "apps/web/AGENTS.md" not in content
    assert ".agent/local/*" in content
