from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = REPO_ROOT / "apps/web/src/product/contracts.ts"
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
