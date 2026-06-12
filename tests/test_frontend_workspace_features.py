from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_workspace_and_knowledge_pages_expose_retrieval_modes():
    knowledge_page = (REPO_ROOT / "apps/web/src/pages/knowledge/knowledge.vue").read_text(encoding="utf-8")
    workspace_page = (REPO_ROOT / "apps/web/src/pages/workspace/defaultPage/defaultPage.vue").read_text(encoding="utf-8")
    retrieval_utils = (REPO_ROOT / "apps/web/src/utils/retrieval.ts").read_text(encoding="utf-8")
    knowledge_config_utils = (REPO_ROOT / "apps/web/src/utils/knowledge-config.ts").read_text(encoding="utf-8")

    assert "normalizeKnowledgeConfig" in knowledge_page
    assert "describeKnowledgeConfig" in knowledge_page
    assert "标准检索" in retrieval_utils
    assert "图谱增强检索" in retrieval_utils
    assert "retrievalModeOptions" in knowledge_config_utils
    assert "autoAvailableMcpIds" in workspace_page
    assert "getValidAutoMcpIds()" in workspace_page
    assert "fetchMcpServers" in workspace_page


def test_knowledge_file_page_includes_task_status_and_retry_hooks():
    knowledge_file_page = (REPO_ROOT / "apps/web/src/pages/knowledge/knowledge-file.vue").read_text(encoding="utf-8")

    assert "retryKnowledgeTaskAPI" in knowledge_file_page
    assert "taskDrawerVisible" in knowledge_file_page
    assert "last_task_id" in knowledge_file_page


def test_workspace_initial_route_message_waits_for_success_before_consuming():
    workspace_page = (REPO_ROOT / "apps/web/src/pages/workspace/defaultPage/defaultPage.vue").read_text(encoding="utf-8")

    assert "initialRouteMessageInFlightKey" in workspace_page
    assert "ensureInitialRouteDependencies" in workspace_page
    assert "attempt < 4" in workspace_page
    assert "const submitted = await submitMessage()" in workspace_page
    assert "if (!submitted) return" in workspace_page
    assert "watch(selectedModelId" in workspace_page
    assert "if (mcpServers.value.length === 0)" in workspace_page
    assert "await fetchMcpServers()" in workspace_page
