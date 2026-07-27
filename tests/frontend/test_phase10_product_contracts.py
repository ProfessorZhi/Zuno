from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = REPO_ROOT / "apps/web/src/product/contracts.ts"
CLIENT = REPO_ROOT / "apps/web/src/product/client.ts"
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
