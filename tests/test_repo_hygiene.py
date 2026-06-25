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


def test_multi_agent_supervisor_source_stays_retired_from_current_backend() -> None:
    assert not (
        REPO_ROOT / "src/backend/zuno/core/graphs/multi_agent_supervisor_graph.py"
    ).exists(), "MultiAgentSupervisorGraph should not remain as current backend source"

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "MultiAgentSupervisorGraph source must not remain as current backend source" in verifier


def test_domain_pack_frontend_files_stay_retired() -> None:
    for path in [
        "apps/web/src/apis/domain-packs.ts",
        "apps/web/src/pages/knowledge/domain-pack-list.vue",
        "apps/web/src/pages/knowledge/domain-pack-create.vue",
        "apps/web/src/pages/knowledge/domain-pack-detail.vue",
    ]:
        assert not (REPO_ROOT / path).exists(), f"retired Domain Pack frontend file remains: {path}"

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "Retired Domain Pack frontend file must not remain" in verifier


def test_domain_pack_api_wrapper_files_stay_retired() -> None:
    for path in [
        "src/backend/zuno/api/v1/domain_packs.py",
        "src/backend/zuno/api/services/domain_pack.py",
    ]:
        assert not (REPO_ROOT / path).exists(), f"retired Domain Pack API wrapper remains: {path}"

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "Retired Domain Pack API wrapper must not remain" in verifier


def test_knowledge_service_stays_off_domain_pack_loader_runtime_defaults() -> None:
    knowledge_service = (
        REPO_ROOT / "src/backend/zuno/api/services/knowledge.py"
    ).read_text(encoding="utf-8")
    assert "from zuno.services.domain_pack.loader import DomainPackLoader" not in knowledge_service
    assert "DomainPackLoader().load" not in knowledge_service

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "KnowledgeService runtime settings must not load DomainPackLoader" in verifier


def test_retired_backend_domain_pack_asset_copy_is_removed() -> None:
    assert not (
        REPO_ROOT / "src/backend/zuno/domain_packs"
    ).exists(), "backend package Domain Pack asset copy should not remain a current path"


def test_active_repo_tools_do_not_reference_retired_backend_domain_pack_copy() -> None:
    for path in [
        "tools/scripts/preview_public_release_group.py",
        "tools/scripts/preview_public_release_stage_dry_run.py",
        "tools/scripts/print_public_release_stage_commands.py",
        "tools/scripts/summarize_public_release_scope.py",
    ]:
        content = (REPO_ROOT / path).read_text(encoding="utf-8")
        assert "src/backend/zuno/domain_packs" not in content, path

    roadmap = (
        REPO_ROOT
        / ".agent/programs/official-graphrag-cleanup-v1/implementation-roadmap.md"
    ).read_text(encoding="utf-8")
    assert "`src/backend/zuno/domain_packs/` still exist" not in roadmap


def test_workspace_knowledge_path_stays_off_legacy_agent_runtime() -> None:
    workspace_agent = (
        REPO_ROOT / "src/backend/zuno/services/workspace/simple_agent.py"
    ).read_text(encoding="utf-8")
    assert "from zuno.core.runtime.agent_runtime import AgentRuntime" not in workspace_agent
    assert "domain_qa_runtime" not in workspace_agent
    assert "_run_domain_pack_query" not in workspace_agent
    assert "KnowledgeQueryService" in workspace_agent

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "Workspace knowledge path must not import AgentRuntime" in verifier


def test_agent_runtime_facade_stays_retired() -> None:
    assert not (REPO_ROOT / "src/backend/zuno/core/runtime/agent_runtime.py").exists()

    core_init = (REPO_ROOT / "src/backend/zuno/core/__init__.py").read_text(
        encoding="utf-8"
    )
    runtime_init = (
        REPO_ROOT / "src/backend/zuno/core/runtime/__init__.py"
    ).read_text(encoding="utf-8")
    assert '"AgentRuntime"' not in core_init
    assert "AgentRuntime" not in runtime_init

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "AgentRuntime facade must not remain as current backend source" in verifier


def test_legacy_graphs_are_not_current_public_package_exports() -> None:
    core_init = (REPO_ROOT / "src/backend/zuno/core/__init__.py").read_text(
        encoding="utf-8"
    )
    graphs_init = (
        REPO_ROOT / "src/backend/zuno/core/graphs/__init__.py"
    ).read_text(encoding="utf-8")

    for legacy_name in ["DomainQAGraph", "MultiAgentSupervisorGraph"]:
        assert legacy_name not in core_init
        assert legacy_name not in graphs_init

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "Legacy graph facades must not be exported" in verifier


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
