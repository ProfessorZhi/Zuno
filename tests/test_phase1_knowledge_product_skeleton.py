from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_phase11c_frontend_routes_retire_domain_pack_entrypoints() -> None:
    router = _read("apps/web/src/router/index.ts")
    settings_shell = _read("apps/web/src/pages/workspace/components/WorkspaceSettingsShell.vue")
    knowledge_page = _read("apps/web/src/pages/knowledge/knowledge.vue")
    create_page = _read("apps/web/src/pages/knowledge/knowledge-create.vue")
    settings_page = _read("apps/web/src/pages/knowledge/knowledge-settings.vue")

    for phrase in [
        "workspaceSettingsKnowledgeCreate",
        "workspaceSettingsKnowledgeSettings",
        "knowledge-create",
        "knowledge-settings",
        "GraphRAG Project",
    ]:
        assert phrase in "\n".join([router, create_page, settings_page])

    retired_active_phrases = [
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
    ]
    active_surfaces = "\n".join([router, settings_shell, knowledge_page, create_page, settings_page])
    for phrase in retired_active_phrases:
        assert phrase not in active_surfaces, f"Domain Pack frontend surface still active: {phrase}"


def test_phase11c_domain_pack_frontend_files_are_retired_assets() -> None:
    for relative_path in [
        "apps/web/src/apis/domain-packs.ts",
        "apps/web/src/pages/knowledge/domain-pack-list.vue",
        "apps/web/src/pages/knowledge/domain-pack-create.vue",
        "apps/web/src/pages/knowledge/domain-pack-detail.vue",
    ]:
        assert not (REPO_ROOT / relative_path).exists(), f"retired frontend asset remains: {relative_path}"


def test_phase1_frontend_contract_keeps_only_two_product_modes() -> None:
    retrieval_utils = _read("apps/web/src/utils/retrieval.ts")
    create_page = _read("apps/web/src/pages/knowledge/knowledge-create.vue")
    settings_page = _read("apps/web/src/pages/knowledge/knowledge-settings.vue")

    assert "standard" in create_page
    assert "enhanced" in create_page
    assert "rag" in retrieval_utils
    assert "rag_graph" in retrieval_utils
    assert "rag_graph_deep" not in create_page
    assert "community_global" not in create_page
    assert "drift_like" not in create_page
    assert "rag_graph_deep" not in settings_page
