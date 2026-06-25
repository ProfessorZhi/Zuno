import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_ignore_files_match_current_structure() -> None:
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    dockerignore = (REPO_ROOT / ".dockerignore").read_text(encoding="utf-8")

    for entry in [
        ".codex/",
        ".local/",
        "apps/web/node_modules/",
        "apps/web/dist/",
        ".agent/local/*",
    ]:
        assert entry in gitignore

    for forbidden in ["apps/web/AGENTS.md", "$null", "&1"]:
        assert forbidden not in gitignore

    assert "apps/web/node_modules" in dockerignore
    assert "apps/web/dist" in dockerignore
    assert "src/frontend" not in dockerignore


def test_package_license_matches_root_license() -> None:
    package_json = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
    license_text = (REPO_ROOT / "LICENSE").read_text(encoding="utf-8")

    assert package_json["license"] == "MIT"
    assert license_text.startswith("MIT License")


def test_blocked_legacy_paths_are_present_and_classified() -> None:
    for path in [
        "domain-packs",
        "tests/compat",
        "src/backend/zuno/services/domain_pack",
        "src/backend/zuno/core/graphs/domain_qa_graph.py",
    ]:
        assert (REPO_ROOT / path).exists(), f"Blocked Legacy path missing: {path}"

    map_content = (
        REPO_ROOT / ".agent" / "references" / "repo-hygiene-map.md"
    ).read_text(encoding="utf-8")
    assert "`domain-packs/`: Blocked Legacy" in map_content
    assert "`tests/compat/`: Current / Blocked Legacy" in map_content
    assert "must not be treated as target repository layout" in map_content


def test_domain_pack_is_not_current_api_or_frontend_entrypoint() -> None:
    router = (REPO_ROOT / "src/backend/zuno/api/router.py").read_text(encoding="utf-8")
    api_v1_init = (REPO_ROOT / "src/backend/zuno/api/v1/__init__.py").read_text(encoding="utf-8")
    assert "domain_packs" not in router
    assert "router.include_router(domain_packs.router)" not in router
    assert "domain_packs" not in api_v1_init

    active_frontend_paths = [
        "apps/web/src/router/index.ts",
        "apps/web/src/pages/workspace/components/WorkspaceSettingsShell.vue",
        "apps/web/src/pages/knowledge/knowledge.vue",
        "apps/web/src/pages/knowledge/knowledge-create.vue",
        "apps/web/src/pages/knowledge/knowledge-settings.vue",
    ]
    active_frontend = "\n".join(
        (REPO_ROOT / path).read_text(encoding="utf-8")
        for path in active_frontend_paths
    )
    for phrase in [
        "workspaceSettingsKnowledgeDomainPacks",
        "workspaceSettingsKnowledgeDomainPackCreate",
        "workspaceSettingsKnowledgeDomainPackDetail",
        "knowledge-domain-packs",
        "settings/knowledge/domain-packs",
        "/knowledge/domain-packs",
        "KnowledgeDomainPacks",
        "KnowledgeDomainPackCreate",
        "KnowledgeDomainPackDetail",
        "getDomainPacksAPI",
        "openDomainPacks",
        "openDomainPackBuilder",
    ]:
        assert phrase not in active_frontend


def test_repo_hygiene_verifiers_are_registered() -> None:
    for path in [
        ".agent/scripts/verify_doc_boundaries.py",
        ".agent/scripts/verify_repo_hygiene.py",
        ".agent/workflows/repo-hygiene.md",
        ".agent/skills/zuno-repo-hygiene/SKILL.md",
    ]:
        assert (REPO_ROOT / path).exists()
