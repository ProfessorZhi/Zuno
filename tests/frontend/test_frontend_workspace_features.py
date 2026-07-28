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

    for phrase in [
        "submitProductAvailableAction",
        "consumeProductStoreAction",
        "productProjectionStore.sortedAvailableActions.length > 0",
        "tool-approval-card",
        "Product Available Actions",
        "action.action_token_id",
        "action.disabled_reason",
        "productActionLabel(action)",
    ]:
        assert phrase in workspace_page

    assert "pendingToolApproval" not in workspace_page
    assert "capturePendingToolApproval" not in workspace_page
    assert "submitToolApproval" not in workspace_page
    assert "approveWorkspaceTaskAPI" not in workspace_page


def test_workspace_agent_mode_uses_product_runtime_projection_loop():
    workspace_page = (REPO_ROOT / "apps/web/src/pages/workspace/defaultPage/defaultPage.vue").read_text(encoding="utf-8")

    for phrase in [
        "createWorkspaceFileAPI",
        "createWorkspaceIngestAPI",
        "getProductArtifact",
        "downloadProductArtifact",
        "submitProductFeedback",
        "submitAgentRuntimeTask",
        "registerRuntimeAttachments",
        "submitWorkspacePayloadToProductRuntime",
        "connectProductRuntimeProjectionStream",
        "Product Command 已接收",
        "Product Actions",
        "submitProductAvailableAction",
        "loadWorkspaceArtifact",
        "downloadActiveWorkspaceArtifact",
        "submitWorkspaceFeedback",
        "buildRuntimeAssistantMessage",
        "runtime-artifact-panel",
        "runtime-download-button",
        "qualityDisclosure",
        "productProjectionStore.upsertArtifact(productArtifact)",
        "productProjectionStore.upsertQuality(productQuality)",
        "activeRuntimeArtifact.citationRefs.length > 0",
        "runtime-observability-panel",
        "runtime-feedback-panel",
        "runtime-failure-panel",
        "release-eval",
        "productSubmission.projection.display_status === 'BLOCKED'",
        "productSubmission.projection.display_status === 'REFUSED'",
        "if (isAgentMode.value) return await submitAgentRuntimeTask",
    ]:
        assert phrase in workspace_page

    assert "createWorkspaceTaskAPI" not in workspace_page
    assert "workspaceTaskEventsStreamAPI" not in workspace_page
    assert "streamWorkspaceTaskEvents" not in workspace_page
    assert "approveWorkspaceTaskAPI" not in workspace_page
    assert "getWorkspaceTaskLifecycleAPI" not in workspace_page


def test_workspace_default_chat_uses_product_runtime_not_simple_chat_stream():
    workspace_page = (REPO_ROOT / "apps/web/src/pages/workspace/defaultPage/defaultPage.vue").read_text(encoding="utf-8")

    assert "submitWorkspacePayloadToProductRuntime" in workspace_page
    assert "connectProductRuntimeProjectionStream" in workspace_page
    assert "Product Command 已接收" in workspace_page
    assert "workspaceSimpleChatStreamAPI" not in workspace_page
    assert "/api/v1/workspace/simple/chat" not in workspace_page


def test_desktop_shell_removes_legacy_workspace_task_lifecycle_contract():
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
        assert phrase not in preload
        assert phrase not in desktop_readme
        assert phrase not in web_api


def test_desktop_shell_exposes_versioned_product_bridge_contract():
    preload = (REPO_ROOT / "apps/desktop/preload.cjs").read_text(encoding="utf-8")
    desktop_readme = (REPO_ROOT / "apps/desktop/README.md").read_text(encoding="utf-8")
    web_api = (REPO_ROOT / "apps/web/src/utils/api.ts").read_text(encoding="utf-8")

    for phrase in [
        "productBridgeVersion",
        "product-desktop-bridge-v1.phase10",
        "productBridgeCapabilities",
        "runtimeRequest: true",
        "actionConsume: true",
        "projectionStream: true",
        "streamLastEventId: true",
        "streamDedup: true",
        "streamReauthorization: true",
        "artifactRead: true",
        "artifactDownload: true",
        "feedback: true",
        "productEndpoints",
        "runtimeRequests: '/api/v1/product/runtime-requests'",
        "actionConsume: '/api/v1/product/actions/consume'",
        "streamEvents: '/api/v1/product/stream-events'",
        "stream: '/api/v1/product/stream'",
        "artifactReadTemplate: '/api/v1/product/artifacts/:artifactId'",
        "artifactDownloadTemplate: '/api/v1/product/artifacts/:artifactId/download'",
        "feedback: '/api/v1/product/feedback'",
        "productBridgeHealth",
        "getDesktopProductBridge",
    ]:
        assert phrase in preload or phrase in desktop_readme or phrase in web_api
