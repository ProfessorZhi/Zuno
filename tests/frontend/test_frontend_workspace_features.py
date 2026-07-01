from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


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


def test_workspace_page_exposes_tool_approval_runtime_surface():
    workspace_page = (REPO_ROOT / "apps/web/src/pages/workspace/defaultPage/defaultPage.vue").read_text(encoding="utf-8")
    workspace_api = (REPO_ROOT / "apps/web/src/apis/workspace.ts").read_text(encoding="utf-8")

    for phrase in [
        "approveWorkspaceTaskAPI",
        "pendingToolApproval",
        "capturePendingToolApproval",
        "submitToolApproval",
        "tool-approval-card",
        "required_approval",
        "audit_ref",
    ]:
        assert phrase in workspace_page or phrase in workspace_api


def test_workspace_agent_mode_uses_task_runtime_product_loop():
    workspace_page = (REPO_ROOT / "apps/web/src/pages/workspace/defaultPage/defaultPage.vue").read_text(encoding="utf-8")

    for phrase in [
        "createWorkspaceFileAPI",
        "createWorkspaceIngestAPI",
        "createWorkspaceTaskAPI",
        "workspaceTaskEventsStreamAPI",
        "getWorkspaceTaskAPI",
        "getWorkspaceArtifactAPI",
        "downloadWorkspaceArtifactAPI",
        "getWorkspaceTaskLifecycleAPI",
        "createWorkspaceFeedbackAPI",
        "submitAgentRuntimeTask",
        "registerRuntimeAttachments",
        "streamWorkspaceTaskEvents",
        "loadWorkspaceArtifact",
        "downloadActiveWorkspaceArtifact",
        "submitWorkspaceFeedback",
        "buildRuntimeAssistantMessage",
        "runtime-artifact-panel",
        "runtime-download-button",
        "runtime-observability-panel",
        "runtime-feedback-panel",
        "runtime-failure-panel",
        "recoverable_failed",
        "recovery_actions",
        "release-eval",
        "security_gate",
        "eval_diagnostic",
        "artifact_created",
        "if (isAgentMode.value) return await submitAgentRuntimeTask",
    ]:
        assert phrase in workspace_page


def test_desktop_shell_exposes_same_workspace_task_lifecycle_contract():
    preload = (REPO_ROOT / "apps/desktop/preload.cjs").read_text(encoding="utf-8")
    desktop_readme = (REPO_ROOT / "apps/desktop/README.md").read_text(encoding="utf-8")
    web_api = (REPO_ROOT / "apps/web/src/utils/api.ts").read_text(encoding="utf-8")

    for phrase in [
        "taskLifecycleEndpoint",
        "/api/v1/workspace/task-lifecycle",
        "artifactDownloadEndpointTemplate",
        "/api/v1/workspace/artifact/:artifactId/download",
        "workspaceTaskLifecycleStates",
        "recoverable_failed",
    ]:
        assert phrase in preload or phrase in desktop_readme or phrase in web_api
