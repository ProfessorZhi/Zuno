"""Tests for `tools.scripts.verify_phase22_nonbackend_legacy_surface`.

These tests pin the PHASE22 nonbackend legacy/cutover surface invariants so that
future worker branches cannot regress the audit-classified touchpoints. Every
test asserts a single invariant; failures should be treated as evidence that the
audit classification has drifted and the manifest under
`docs/evidence/goal05-phase22-nonbackend-legacy-cleanup/` needs updating.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.scripts.verify_phase22_nonbackend_legacy_surface import (
    WEB_LEGACY_REDIRECT_PATHS,
    verify_desktop,
    verify_governance,
    verify_tools_infra_workflows,
    verify_web,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Web surface tests
# ---------------------------------------------------------------------------


WEB_LEGACY_COMPAT_FILES = [
    "apps/web/src/utils/retrieval.ts",
    "apps/web/src/utils/knowledge-config.ts",
    "apps/web/src/utils/user-avatars.ts",
]


@pytest.mark.parametrize("relpath", WEB_LEGACY_COMPAT_FILES)
def test_web_legacy_compat_file_exists(relpath: str) -> None:
    """Allow-listed compat shims must remain on disk."""

    path = REPO_ROOT / relpath
    assert path.exists(), f"missing web compat shim file {relpath}"


def test_web_retrieval_compat_defines_legacy_mode_map() -> None:
    text = (REPO_ROOT / "apps/web/src/utils/retrieval.ts").read_text(encoding="utf-8")
    assert "legacyModeMap" in text
    for old_mode in ("auto", "default", "hybrid", "graphrag"):
        assert old_mode in text, f"retrieval.ts lost legacy mapping for {old_mode}"


def test_web_knowledge_config_compat_keeps_legacy_aliases() -> None:
    text = (REPO_ROOT / "apps/web/src/utils/knowledge-config.ts").read_text(encoding="utf-8")
    assert "LegacyKnowledgeProductMode" in text
    assert "LegacyKnowledgeConfigInput" in text
    assert "domain_pack_id" in text, "knowledge-config.ts lost legacy domain_pack_id field"
    assert "enhanced" in text, "knowledge-config.ts lost legacy 'enhanced' product mode"


def test_web_user_avatars_keeps_legacy_remote_pattern() -> None:
    text = (REPO_ROOT / "apps/web/src/utils/user-avatars.ts").read_text(encoding="utf-8")
    assert "isLegacyRemoteUserAvatar" in text
    assert "zuno.oss-cn-beijing.aliyuncs.com" in text
    assert "/zuno/icons/user/" in text
    assert "/icons/user/" in text


def test_web_router_keeps_legacy_redirects() -> None:
    text = (REPO_ROOT / "apps/web/src/router/index.ts").read_text(encoding="utf-8")
    for path, name, target in WEB_LEGACY_REDIRECT_PATHS:
        assert f"path: '{path}'" in text, f"router lost historical alias {path!r}"
        assert f"name: '{name}'" in text, f"router lost historical route name {name!r}"
        assert f"name: '{target}'" in text, f"alias {name!r} no longer targets {target!r}"


def test_web_apis_do_not_reference_retired_endpoints() -> None:
    forbidden = (
        "/api/v1/dialog",
        "/api/v1/completion/legacy",
        "/api/v1/agent/legacy",
        "/api/v1/chat/legacy",
        "/api/v1/llm/legacy",
        "/api/v1/message_events/legacy",
    )
    apis_dir = REPO_ROOT / "apps/web/src/apis"
    for path in apis_dir.rglob("*.ts"):
        body = path.read_text(encoding="utf-8")
        for needle in forbidden:
            assert needle not in body, (
                f"{path}: front-end client still references retired endpoint {needle!r}"
            )


def test_web_runtime_keeps_fail_closed_product_cutover() -> None:
    text = (REPO_ROOT / "apps/web/src/product/runtime.ts").read_text(encoding="utf-8")
    assert "ProductRuntimeRollbackError" in text
    for mode in ("shadow", "canary", "new_default", "rollback"):
        assert f"'{mode}'" in text or f'"{mode}"' in text
    for kind in (
        "SHADOW_SUBMIT_USER_GOAL",
        "CANARY_SUBMIT_USER_GOAL",
        "SUBMIT_USER_GOAL",
    ):
        assert kind in text


def test_web_no_legacy_state_in_workspace_settings_shell() -> None:
    """WorkspaceSettingsShell + defaultPage must keep importing the page folders
    that act as historical re-export layers."""

    shell = (REPO_ROOT / "apps/web/src/pages/workspace/components/WorkspaceSettingsShell.vue").read_text(
        encoding="utf-8"
    )
    for import_path in (
        "../../agent",
        "../../agent-skill",
        "../../knowledge",
        "../../mcp-server",
        "../../model",
        "../../profile",
        "../../tool",
        "../../dashboard",
    ):
        assert import_path in shell, (
            f"WorkspaceSettingsShell.vue lost historical re-export import {import_path}"
        )


def test_verify_web_suite_clean() -> None:
    assert verify_web() == []


# ---------------------------------------------------------------------------
# Desktop surface tests
# ---------------------------------------------------------------------------


def test_desktop_main_and_preload_pin_product_bridge_version() -> None:
    main = (REPO_ROOT / "apps/desktop/main.cjs").read_text(encoding="utf-8")
    preload = (REPO_ROOT / "apps/desktop/preload.cjs").read_text(encoding="utf-8")
    assert "product-desktop-bridge-v1.phase10" in main or "product-desktop-bridge-v1.phase10" in preload


def test_desktop_preload_exposes_all_product_capabilities() -> None:
    preload = (REPO_ROOT / "apps/desktop/preload.cjs").read_text(encoding="utf-8")
    for capability in (
        "runtimeRequest",
        "actionConsume",
        "projectionStream",
        "streamLastEventId",
        "streamDedup",
        "streamReauthorization",
        "artifactRead",
        "artifactDownload",
        "feedback",
    ):
        assert capability in preload


def test_desktop_main_smoke_does_not_ship_legacy_capabilities() -> None:
    main = (REPO_ROOT / "apps/desktop/main.cjs").read_text(encoding="utf-8")
    forbidden = (
        "legacyProductStreamV0",
        "phase0StreamBridge",
        "legacyProductBridgeV0",
        "electronLegacyBridge",
        "streamReauthorizeV0",
        "chunkStreamV0",
    )
    for needle in forbidden:
        assert needle not in main, f"main.cjs re-introduced legacy capability {needle!r}"


def test_legacy_bat_forwarders_point_to_current_launchers() -> None:
    forwarders = {
        "tools/scripts/zuno-start.bat": "Zuno-Desktop-Start.cmd",
        "tools/scripts/zuno-stop.bat": "Zuno-Desktop-Stop.cmd",
        "tools/scripts/zuno-rebuild-start.bat": "Zuno-Desktop-Rebuild.cmd",
        "tools/scripts/zuno-clean-rebuild-start.bat": "Zuno-Desktop-Full-Rebuild.cmd",
    }
    for relpath, target in forwarders.items():
        text = (REPO_ROOT / relpath).read_text(encoding="utf-8")
        assert target in text, f"{relpath} no longer forwards to {target!r}"


def test_verify_desktop_suite_clean() -> None:
    assert verify_desktop() == []


# ---------------------------------------------------------------------------
# Tools / Infra / Workflow surface tests
# ---------------------------------------------------------------------------


def test_workflows_only_reference_existing_scripts() -> None:
    """Re-runs the verifier slice for workflows without spawning Python."""

    import re

    workflow_dir = REPO_ROOT / ".github" / "workflows"
    script_patterns = (
        r"tools/scripts/verify_[A-Za-z0-9_]+\.py",
        r"tools/scripts/generate_phase22_[A-Za-z0-9_]+\.py",
        r"\.agent/scripts/verify_[A-Za-z0-9_]+\.py",
    )
    for workflow in sorted(workflow_dir.glob("*.yml")):
        text = workflow.read_text(encoding="utf-8")
        for pattern in script_patterns:
            for match in re.finditer(pattern, text):
                script = match.group(0).strip()
                assert (REPO_ROOT / script).exists(), (
                    f"workflow {workflow.name} references missing script {script!r}"
                )


def test_compose_services_match_audit() -> None:
    compose = (REPO_ROOT / "infra/docker/docker-compose.yml").read_text(encoding="utf-8")
    for service_header in (
        "\n  postgres:\n",
        "\n  redis:\n",
        "\n  rabbitmq:\n",
        "\n  neo4j:\n",
        "\n  elasticsearch:\n",
        "\n  minio:\n",
        "\n  etcd:\n",
        "\n  milvus:\n",
        "\n  backend:\n",
        "\n  worker:\n",
        "\n  frontend:\n",
    ):
        assert service_header in compose, f"compose missing service {service_header!r}"


def test_elasticsearch_stays_behind_opt_in_profile() -> None:
    compose = (REPO_ROOT / "infra/docker/docker-compose.yml").read_text(encoding="utf-8")
    assert "profiles:\n      - elasticsearch" in compose


def test_dockerfile_keeps_configurable_build_args() -> None:
    dockerfile = (REPO_ROOT / "infra/docker/Dockerfile").read_text(encoding="utf-8")
    for arg in (
        "ARG PYTHON_BASE_IMAGE=",
        "ARG DEBIAN_MIRROR=",
        "ARG DEBIAN_SECURITY_MIRROR=",
        "ARG PIP_TRUSTED_HOST=",
        "ARG PIP_DEFAULT_TIMEOUT=",
        "ARG PIP_RETRIES=",
    ):
        assert arg in dockerfile, f"Dockerfile missing build arg {arg!r}"
    assert "chromium-driver" in dockerfile, "Dockerfile dropped chromium-driver install"


def test_phase0_backend_launcher_pins_canonical_module() -> None:
    text = (
        REPO_ROOT / "tools/launchers/windows/Zuno-Phase0-Backend-Start.cmd"
    ).read_text(encoding="utf-8")
    assert "uvicorn --app-dir src/backend zuno.main:app" in text
    assert "127.0.0.1" in text and "7860" in text


def test_powershell_smoke_scripts_resolve_repo_root() -> None:
    for relpath, snippet in (
        (
            "tools/scripts/run-full-e2e-smoke.ps1",
            "Split-Path -Parent (Split-Path -Parent $PSScriptRoot)",
        ),
        (
            "tools/scripts/run-desktop-smoke.ps1",
            "Split-Path -Parent (Split-Path -Parent $PSScriptRoot)",
        ),
    ):
        text = (REPO_ROOT / relpath).read_text(encoding="utf-8")
        assert snippet in text, f"{relpath} no longer resolves repo root"


def test_verify_tools_infra_workflows_suite_clean() -> None:
    assert verify_tools_infra_workflows() == []


# ---------------------------------------------------------------------------
# Governance tests
# ---------------------------------------------------------------------------


FEATURE_FLAG_REGISTRY = REPO_ROOT / ".agent/programs/work-products/feature-flag-registry.yaml"
TEMPORARY_ALLOWLIST = REPO_ROOT / ".agent/programs/work-products/temporary-allowlist.yaml"
LEGACY_BYPASS_INVENTORY = REPO_ROOT / ".agent/programs/work-products/legacy-bypass-inventory.yaml"


def _flag_block(text: str, flag: str) -> str:
    needle = f'  - flag: "{flag}"'
    assert needle in text, f"flag {flag!r} not in registry"
    after = text.split(needle, 1)[1]
    return after.split("\n  - flag:", 1)[0]


def test_history_reference_flag_keeps_retired_default() -> None:
    text = FEATURE_FLAG_REGISTRY.read_text(encoding="utf-8")
    block = _flag_block(text, "legacy_general_agent_completion_rollback")
    assert 'default: "RETIRED"' in block
    assert "ZUNO_AGENT_RUNTIME=legacy_general_agent" not in block


@pytest.mark.parametrize(
    "flag", ["product_api_v1_adapter", "workspace_projection_stream_v1"]
)
def test_versioned_public_api_flag_present(flag: str) -> None:
    text = FEATURE_FLAG_REGISTRY.read_text(encoding="utf-8")
    assert f'flag: "{flag}"' in text


@pytest.mark.parametrize(
    "flag",
    [
        "tool_runtime_readonly_gateway",
        "postgres_domain_uow_shadow",
    ],
)
def test_out_of_scope_expired_flag_kept_for_deepseek(flag: str) -> None:
    text = FEATURE_FLAG_REGISTRY.read_text(encoding="utf-8")
    assert f'flag: "{flag}"' in text, (
        f"out-of-scope flag {flag!r} collapsed; that decision is reserved for a DeepSeek branch"
    )


@pytest.mark.parametrize(
    "entry",
    [
        {
            "path": "apps/web/src/utils/retrieval.ts",
            "symbol": "legacyModeMap",
            "owner": "01 Product Surface",
        },
        {
            "path": "apps/web/src/utils/knowledge-config.ts",
            "symbol": "LegacyKnowledgeProductMode",
            "owner": "01 Product Surface",
        },
        {
            "path": "apps/web/src/utils/user-avatars.ts",
            "symbol": "isLegacyRemoteUserAvatar",
            "owner": "01 Product Surface",
        },
    ],
)
def test_web_allowlist_entry_is_preserved_in_both_registries(entry: dict[str, str]) -> None:
    for source in (TEMPORARY_ALLOWLIST, LEGACY_BYPASS_INVENTORY):
        text = source.read_text(encoding="utf-8")
        assert entry["path"] in text, f"{source.name}: missing {entry['path']!r}"
        block = text.split(f'path: "{entry["path"]}"', 1)[1].split("\n  - path:", 1)[0]
        assert entry["symbol"] in block, (
            f"{source.name}: entry {entry['path']!r} lost symbol {entry['symbol']!r}"
        )
        assert entry["owner"] in block, (
            f"{source.name}: entry {entry['path']!r} lost owner {entry['owner']!r}"
        )


def test_dynamic_command_documented_in_evidence() -> None:
    candidates = (
        REPO_ROOT / "docs/evidence/goal05-phase22-cleanup-start.md",
        REPO_ROOT
        / "docs/evidence/goal05-phase22-nonbackend-legacy-cleanup/escalations.md",
    )
    assert any(
        "ZUNO_COMPLETION_CUTOVER_MODE=rollback" in path.read_text(encoding="utf-8")
        for path in candidates
    ), "dynamic command cutover evidence must be retained"


def test_verify_governance_suite_clean() -> None:
    assert verify_governance() == []
