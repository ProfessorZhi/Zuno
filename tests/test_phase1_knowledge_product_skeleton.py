from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_phase1_router_exposes_domain_pack_create_and_settings_routes() -> None:
    router = _read("apps/web/src/router/index.ts")
    settings_shell = _read("apps/web/src/pages/workspace/components/WorkspaceSettingsShell.vue")

    required_router_phrases = [
        "workspaceSettingsKnowledgeCreate",
        "workspaceSettingsKnowledgeSettings",
        "workspaceSettingsKnowledgeDomainPacks",
        "workspaceSettingsKnowledgeDomainPackCreate",
        "workspaceSettingsKnowledgeDomainPackDetail",
        "knowledge-create",
        "knowledge-settings",
        "knowledge-domain-packs",
    ]

    for phrase in required_router_phrases:
        assert phrase in router, f"missing Phase 1 knowledge route: {phrase}"

    required_shell_phrases = [
        "KnowledgeCreate",
        "KnowledgeSettings",
        "KnowledgeDomainPacks",
        "KnowledgeDomainPackCreate",
        "KnowledgeDomainPackDetail",
    ]

    for phrase in required_shell_phrases:
        assert phrase in settings_shell, f"settings shell is missing Phase 1 knowledge component: {phrase}"


def test_phase1_frontend_pages_split_builder_wizard_and_maintenance() -> None:
    create_page = _read("apps/web/src/pages/knowledge/knowledge-create.vue")
    settings_page = _read("apps/web/src/pages/knowledge/knowledge-settings.vue")
    domain_pack_page = _read("apps/web/src/pages/knowledge/domain-pack-list.vue")
    domain_pack_create_page = _read("apps/web/src/pages/knowledge/domain-pack-create.vue")

    for phrase in ["标准检索", "增强检索", "Embedding", "Rerank", "Domain Pack", "构建计划"]:
        assert phrase in create_page, f"knowledge create wizard missing phrase: {phrase}"

    for phrase in ["文本索引", "BM25", "图谱索引", "社区发现", "社区报告", "重新发现社区", "重新生成社区报告"]:
        assert phrase in settings_page, f"knowledge maintenance page missing phrase: {phrase}"

    for phrase in ["领域包", "创建新的领域包", "代表性文件", "发布领域包"]:
        assert phrase in domain_pack_page + domain_pack_create_page, f"domain pack pages missing phrase: {phrase}"


def test_phase1_frontend_contract_keeps_only_two_product_modes() -> None:
    retrieval_utils = _read("apps/web/src/utils/retrieval.ts")
    create_page = _read("apps/web/src/pages/knowledge/knowledge-create.vue")
    settings_page = _read("apps/web/src/pages/knowledge/knowledge-settings.vue")

    assert "标准检索" in retrieval_utils
    assert "增强检索" in retrieval_utils
    assert "rag_graph_deep" not in create_page
    assert "community_global" not in create_page
    assert "drift_like" not in create_page
    assert "rag_graph_deep" not in settings_page

