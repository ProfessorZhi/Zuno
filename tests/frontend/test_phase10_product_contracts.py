from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = REPO_ROOT / "apps/web/src/product/contracts.ts"
CLIENT = REPO_ROOT / "apps/web/src/product/client.ts"
STORE = REPO_ROOT / "apps/web/src/product/store.ts"
INDEX = REPO_ROOT / "apps/web/src/product/index.ts"


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
        "normalizeProductProblem",
        "shouldRetryProductTransportFailure",
        "createProductClientRequestId",
        "ProductProblemDetail",
        "ProductRuntimeRequestCommand",
        "ProductActionConsumeCommand",
        "ProductRuntimeRequestReceipt",
        "'/api/v1/product/runtime-requests'",
        "'/api/v1/product/actions/consume'",
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
