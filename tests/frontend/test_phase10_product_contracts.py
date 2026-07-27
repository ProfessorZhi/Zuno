from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = REPO_ROOT / "apps/web/src/product/contracts.ts"
CLIENT = REPO_ROOT / "apps/web/src/product/client.ts"
STORE = REPO_ROOT / "apps/web/src/product/store.ts"
RUNTIME = REPO_ROOT / "apps/web/src/product/runtime.ts"
INDEX = REPO_ROOT / "apps/web/src/product/index.ts"
DEFAULT_PAGE = REPO_ROOT / "apps/web/src/pages/workspace/defaultPage/defaultPage.vue"


def test_phase10_product_contract_surface_exists() -> None:
    assert CONTRACTS.exists()
    assert INDEX.exists()
    text = CONTRACTS.read_text(encoding="utf-8")

    for phrase in [
        "PRODUCT_CONTRACT_BUNDLE_VERSION",
        "AgentDefinition",
        "AgentDraft",
        "AgentVersion",
        "AgentPublication",
        "AgentInstallation",
        "AgentCatalogEntry",
        "status: 'DRAFTING' | 'DRAFT' | 'ACTIVE' | 'ARCHIVED' | 'RETIRED' | 'REVOKED'",
        "status: 'OPEN' | 'DRAFT' | 'VALIDATING' | 'READY_TO_PUBLISH' | 'LOCKED' | 'DISCARDED'",
        "status: 'PUBLISHED' | 'WITHDRAWN' | 'REVOKED' | 'SUPERSEDED'",
        "ProductCommand",
        "RuntimeRequest",
        "CommandReceipt",
        "ProductProjection",
        "AvailableAction",
        "ChannelDelivery",
        "ProductProblemDetail",
        "ProductDisplayStatus",
        "ProjectionFreshness",
        "ConnectionStatus",
        "ProductStreamEvent",
        "PRODUCT_CONTRACT_SCHEMA_SENTINEL",
        "unknown_enum_policy: 'fail_closed'",
        "frontend_fact_source: false",
        "product_actions_from_server_only: true",
    ]:
        assert phrase in text


def test_phase10_product_contract_does_not_import_backend_or_workspace_state() -> None:
    text = CONTRACTS.read_text(encoding="utf-8")

    forbidden = [
        "from 'zuno",
        'from "zuno',
        "WorkspaceTaskStatus",
        "WorkspaceTaskLifecycleState",
        "approval_required",
        "recoverable_failed",
        "domain_success_ref: string",
    ]
    for phrase in forbidden:
        assert phrase not in text


def test_phase10_product_api_client_exposes_command_problem_and_stream_boundary() -> None:
    assert CLIENT.exists()
    text = CLIENT.read_text(encoding="utf-8")

    for phrase in [
        "submitProductRuntimeRequest",
        "consumeProductAction",
        "listProductStreamEvents",
        "openProductProjectionStream",
        "getProductArtifact",
        "downloadProductArtifact",
        "submitProductFeedback",
        "createProductAgentDraft",
        "publishProductAgentVersion",
        "installProductAgentVersion",
        "revokeProductAgentInstallation",
        "revokeProductAgentPublication",
        "listProductAgentCatalog",
        "normalizeProductProblem",
        "shouldRetryProductTransportFailure",
        "createProductClientRequestId",
        "ProductProblemDetail",
        "ProductRuntimeRequestCommand",
        "ProductActionConsumeCommand",
        "ProductRuntimeRequestReceipt",
        "'/api/v1/product/runtime-requests'",
        "'/api/v1/product/actions/consume'",
        "/api/v1/product/artifacts/${artifactId}",
        "/api/v1/product/artifacts/${artifactId}/download",
        "'/api/v1/product/feedback'",
        "'/api/v1/product/agent-drafts'",
        "'/api/v1/product/agent-publications'",
        "'/api/v1/product/agent-installations'",
        "'/api/v1/product/agent-catalog'",
        "'/api/v1/product/stream-events'",
        "/api/v1/product/stream?tenant_id=",
        "client_request_id: command.client_request_id || createProductClientRequestId",
        "COMMAND_RETRY_BLOCKED",
        "return false",
        "'Last-Event-ID'",
        "fetchEventSource",
    ]:
        assert phrase in text


def test_phase10_product_api_client_does_not_replay_side_effect_commands() -> None:
    text = CLIENT.read_text(encoding="utf-8")

    assert "post:/api/v1/product/runtime-requests" in text
    assert "post:/api/v1/product/actions/consume" in text
    assert "problem.retryable && problem.status >= 500" in text
    assert "COMMAND_RETRY_BLOCKED.has(key)" in text
    assert "domain_success_ref" not in text


def test_phase10_product_projection_store_tracks_server_projection_not_runtime_facts() -> None:
    assert STORE.exists()
    text = STORE.read_text(encoding="utf-8")
    index_text = INDEX.read_text(encoding="utf-8")

    for phrase in [
        "useProductProjectionStore",
        "ProductProjection",
        "AvailableAction",
        "ProjectionFreshness",
        "ConnectionStatus",
        "lastEventId",
        "lastSequenceNo",
        "sourceWatermark",
        "projectionVersion",
        "gapDetected",
        "resyncRequired",
        "agentDefinitions",
        "catalogEntries",
        "agentVersions",
        "agentDrafts",
        "publications",
        "installations",
        "interrupts",
        "artifacts",
        "deliveries",
        "quality",
        "citation_count",
        "citation_authorized",
        "download_policy",
        "metrics?: Record<string, number | string | boolean | null>",
        "disclosure?: string",
        "sortedAvailableActions",
        "pendingInterrupts",
        "needsResync",
        "applyProjection",
        "applyStreamEvent",
        "replaceAvailableActions",
        "upsertAgentDefinition",
        "upsertCatalogEntry",
        "upsertAgentDraft",
        "upsertAgentVersion",
        "upsertPublication",
        "upsertInstallation",
        "upsertInterrupt",
        "upsertArtifact",
        "upsertDelivery",
        "upsertQuality",
        "markResyncRequired",
        "completeResync",
        "purgeAuthorizedView",
        "paths: ['lastEventId', 'lastSequenceNo', 'sourceWatermark', 'projectionVersion']",
    ]:
        assert phrase in text

    for phrase in [
        "applyProjection",
        "projection.projection_version < projectionVersion.value",
        "projection.source_watermark",
        "projection.freshness === 'GAP'",
        "projection.freshness === 'RESYNC_REQUIRED'",
        "event.event_type === 'REVOKED'",
        "purgeAuthorizedView()",
        "event.sequence_no <= lastSequenceNo.value",
        "event.event_id === lastEventId.value",
        "INGESTION_COMPLETION",
    ]:
        assert phrase in text

    assert "export * from './store'" in index_text


def test_phase10_product_projection_store_keeps_frontend_out_of_agent_core_ownership() -> None:
    text = STORE.read_text(encoding="utf-8")

    forbidden = [
        "AgentRun",
        "ApprovalDecision",
        "EffectReceipt",
        "RunOutcome",
        "WorkspaceTaskStatus",
        "WorkspaceTaskLifecycleState",
        "approval_required",
        "pendingToolApproval",
        "domain_success_ref",
        "status === 'completed'",
        "status === 'COMPLETED'",
    ]
    for phrase in forbidden:
        assert phrase not in text


def test_phase10_product_runtime_adapter_connects_command_stream_and_action_tokens() -> None:
    assert RUNTIME.exists()
    text = RUNTIME.read_text(encoding="utf-8")
    index_text = INDEX.read_text(encoding="utf-8")

    for phrase in [
        "submitWorkspacePayloadToProductRuntime",
        "connectProductRuntimeProjectionStream",
        "consumeProductStoreAction",
        "buildProductRuntimeRequestCommand",
        "productProjectionFromRuntimeReceipt",
        "normalizeAvailableActionsFailClosed",
        "submitProductRuntimeRequest(command)",
        "openProductProjectionStream",
        "last_event_id: store.lastEventId || undefined",
        "store.applyStreamEvent(event)",
        "store.applyProjection(projection, acceptedActions)",
        "consumeProductAction",
        "store.replaceAvailableActions",
        "command_kind: 'SUBMIT_USER_GOAL'",
        "runtime_request_ref: `runtime:${requestId}`",
        "raw_intent_ref: `intent:${context.conversation_id}:${requestId}`",
        "client_request_id: requestId",
        "redaction_decision_ref: receipt.projection.redaction_decision_ref",
    ]:
        assert phrase in text

    for phrase in [
        "Boolean(action.effective_security_epoch_ref)",
        "Number(action.projection_version) === projectionVersion",
        "return 'RESYNC_REQUIRED'",
        "problem.type === 'AUTHENTICATION_REQUIRED'",
        "store.purgeAuthorizedView()",
        "problem.type === 'PROJECTION_GAP'",
        "store.markResyncRequired()",
    ]:
        assert phrase in text

    assert "export * from './runtime'" in index_text


def test_phase10_default_workspace_page_uses_product_projection_path_without_legacy_task_fallback() -> None:
    assert DEFAULT_PAGE.exists()
    text = DEFAULT_PAGE.read_text(encoding="utf-8")

    for phrase in [
        "useProductProjectionStore",
        "const productProjectionStore = useProductProjectionStore()",
        "submitWorkspacePayloadToProductRuntime",
        "connectProductRuntimeProjectionStream",
        "consumeProductStoreAction",
        "await submitWorkspacePayloadToProductRuntime(payload as Record<string, unknown>",
        "const productSubmission = await submitWorkspacePayloadToProductRuntime(payload as Record<string, unknown>",
        "activeRuntimeTaskId.value = productSubmission.receipt.command_id",
        "void connectProductRuntimeProjectionStream({ workspace_id: workspaceId }, productProjectionStore",
        "Object.values(productProjectionStore.availableActions).find",
        "action.action === (decision === 'approved' ? 'APPROVE' : 'DENY')",
        "if (!availableAction) throw new Error('Product AvailableAction token is required before approval can be consumed.')",
        "await submitProductAvailableAction(availableAction",
        "await consumeProductStoreAction(action",
        "productProjectionStore.sortedAvailableActions.length > 0",
        "submitProductAvailableAction(action)",
        "Product Actions",
        "title: 'Product Command 已接收'",
        "title: 'Product 投影已同步'",
        "title: 'Product 投影同步受阻'",
        "getProductArtifact",
        "downloadProductArtifact",
        "submitProductFeedback",
        "productProjectionStore.upsertArtifact(productArtifact)",
        "productProjectionStore.upsertQuality(productQuality)",
        "Quality {{ activeRuntimeArtifact.qualityDisclosure.status }}",
        "activeRuntimeArtifact.citationRefs.length > 0",
    ]:
        assert phrase in text

    assert "createWorkspaceTaskAPI" not in text
    assert "workspaceTaskEventsStreamAPI" not in text
    assert "streamWorkspaceTaskEvents" not in text
    assert "approveWorkspaceTaskAPI" not in text


def test_phase10_desktop_bridge_is_versioned_product_surface() -> None:
    preload = (REPO_ROOT / "apps/desktop/preload.cjs").read_text(encoding="utf-8")
    web_api = (REPO_ROOT / "apps/web/src/utils/api.ts").read_text(encoding="utf-8")

    for phrase in [
        "productBridgeVersion: 'product-desktop-bridge-v1.phase10'",
        "productBridgeCapabilities",
        "streamLastEventId: true",
        "streamDedup: true",
        "streamReauthorization: true",
        "artifactReadTemplate: '/api/v1/product/artifacts/:artifactId'",
        "artifactDownloadTemplate: '/api/v1/product/artifacts/:artifactId/download'",
        "feedback: '/api/v1/product/feedback'",
        "productBridgeVersion?: string",
        "getDesktopProductBridge",
    ]:
        assert phrase in preload or phrase in web_api
