"""Verify the nonbackend legacy/cutover surface that this branch is responsible for.

Phase:    PHASE22
Worker:   minimax-legacy-surface (branch claude/minimax-phase22-nonbackend-legacy-cleanup)
Scope:    apps/web/**, apps/desktop/**, tools/**, infra/**,
          .github/workflows/**, tests/frontend/**, tests/repo/**,
          .agent/programs/work-products/{feature-flag-registry,temporary-allowlist,
          legacy-bypass-inventory,phase22-removal-candidates}.yaml,
          docs/evidence/goal05-phase22-nonbackend-legacy-cleanup/**

Out of scope: src/backend/zuno/** (Runtime), infra/db/alembic/** (Migration),
agent core, security, benchmark thresholds, formal datasets, PR #119 evidence.

The verifier asserts (positive) that the audit-classified surface is still in
its expected ALLOWED_* state and asserts (negative) that nothing from the
forbidden zones has silently drifted into one of the 1:1-replacement-eligible
positions. It is deliberately read-only; it must never mutate the repo.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _contains_any(text: str, needles: Iterable[str]) -> bool:
    return any(needle in text for needle in needles)


def _matches(text: str, patterns: Iterable[str]) -> bool:
    return any(re.search(p, text) for p in patterns)


def _flag_block(feature_flags: str, flag: str) -> str:
    needle = f'  - flag: "{flag}"'
    if needle not in feature_flags:
        return ""
    block = feature_flags.split(needle, 1)[1]
    block = block.split("\n  - flag:", 1)[0]
    return block


# ---------------------------------------------------------------------------
# Web surface
# ---------------------------------------------------------------------------


WEB_LEGACY_COMPAT_FILES = [
    REPO_ROOT / "apps" / "web" / "src" / "utils" / "retrieval.ts",
    REPO_ROOT / "apps" / "web" / "src" / "utils" / "knowledge-config.ts",
    REPO_ROOT / "apps" / "web" / "src" / "utils" / "user-avatars.ts",
]


WEB_LEGACY_REDIRECT_PATHS = (
    # The full set of (path, name, target) tuples for router redirects that
    # keep the historical URL space alive and forward to the workspace
    # consolidated routes. If you find yourself wanting to add a row here,
    # you are adding a new historical URL alias, not making a 1:1 cutover.
    ("/homepage", "homepage", "workspaceDefaultPage"),
    ("/conversation", "conversation", "workspaceAccountConversations"),
    ("/conversation/", "defaultPage", "workspaceAccountConversations"),
    ("/conversation/chatPage", "chatPage", "workspaceDefaultPage"),
    ("/construct", "construct", "workspaceSettingsAgent"),
    ("/configuration", "configuration", "workspaceSettingsTool"),
    ("/agent", "agent", "workspaceSettingsAgent"),
    ("/agent/editor", "agent-editor", "workspaceSettingsAgentEditor"),
    ("/mcp-server", "mcp-server", "workspaceSettingsMcp"),
    ("/knowledge", "knowledge", "workspaceSettingsKnowledge"),
    ("/knowledge/create", "knowledge-create", "workspaceSettingsKnowledgeCreate"),
    ("/knowledge/:knowledgeId/files", "knowledge-file", "workspaceSettingsKnowledgeFile"),
    ("/knowledge/:knowledgeId/settings", "knowledge-settings", "workspaceSettingsKnowledgeSettings"),
    ("/knowledge/:knowledgeId/config", "knowledge-config", "workspaceSettingsKnowledgeSettings"),
    ("/tool", "tool", "workspaceSettingsTool"),
    ("/agent-skill", "agent-skill", "workspaceSettingsSkill"),
    ("/model", "model", "workspaceSettingsModel"),
    ("/model/editor", "model-editor", "workspaceSettingsModel"),
    ("/profile", "profile", "workspaceAccountProfile"),
    ("/dashboard", "dashboard", "workspaceSettingsDashboard"),
)


WEB_REEXPORTED_PAGE_DIRS = [
    "apps/web/src/pages/agent",
    "apps/web/src/pages/agent-skill",
    "apps/web/src/pages/configuration",
    "apps/web/src/pages/dashboard",
    "apps/web/src/pages/knowledge",
    "apps/web/src/pages/mcp-server",
    "apps/web/src/pages/model",
    "apps/web/src/pages/profile",
    "apps/web/src/pages/tool",
]


def verify_web() -> list[str]:
    errors: list[str] = []

    # Allow-listed compat shims must still be present and reference the legacy
    # symbol names we promised not to break in the audit. Removing the symbol
    # silently is the regression we are guarding against.
    expected_shims = {
        "apps/web/src/utils/retrieval.ts": ["legacyModeMap"],
        "apps/web/src/utils/knowledge-config.ts": [
            "LegacyKnowledgeProductMode",
            "LegacyKnowledgeConfigInput",
            "legacyMap",
        ],
        "apps/web/src/utils/user-avatars.ts": ["isLegacyRemoteUserAvatar"],
    }
    for relpath, symbols in expected_shims.items():
        text = _read(REPO_ROOT / relpath)
        for symbol in symbols:
            if symbol not in text:
                errors.append(
                    f"web: missing ALLOWED_HISTORY_REFERENCE symbol {symbol!r} in {relpath}"
                )

    # Fail-closed Product Runtime cutover mode machine must remain.
    runtime_text = _read(REPO_ROOT / "apps" / "web" / "src" / "product" / "runtime.ts")
    if "ProductRuntimeRollbackError" not in runtime_text:
        errors.append("web: missing ALLOWED_FAIL_CLOSED_TEST type ProductRuntimeRollbackError")
    for mode in ("shadow", "canary", "new_default", "rollback"):
        if f"'{mode}'" not in runtime_text and f'"{mode}"' not in runtime_text:
            errors.append(f"web: missing ProductRuntimeCutoverMode value {mode!r}")
    for kind in (
        "SHADOW_SUBMIT_USER_GOAL",
        "CANARY_SUBMIT_USER_GOAL",
        "SUBMIT_USER_GOAL",
    ):
        if kind not in runtime_text:
            errors.append(
                f"web: missing ALLOWED_FAIL_CLOSED_TEST product command kind {kind!r}"
            )

    # Back-compat URL aliases must still redirect to consolidated routes.
    router = _read(REPO_ROOT / "apps" / "web" / "src" / "router" / "index.ts")
    for path, name, target in WEB_LEGACY_REDIRECT_PATHS:
        if f"path: '{path}'" not in router and f'path: "{path}"' not in router:
            errors.append(f"web: missing historical URL alias path={path!r}")
        if f"name: '{name}'" not in router and f'name: "{name}"' not in router:
            errors.append(f"web: missing historical route name {name!r}")
        if f"name: '{target}'" not in router and f'name: "{target}"' not in router:
            errors.append(
                f"web: alias {name!r} targets unknown route {target!r}"
            )

    # Old API client calls — we forbid retired endpoints in the front-end.
    forbidden_api_patterns = [
        r"/api/v1/dialog",
        r"/api/v1/completion/legacy",
        r"/api/v1/agent/legacy",
        r"/api/v1/chat/legacy",
        r"/api/v1/llm/legacy",
        r"/api/v1/message_events/legacy",
    ]
    apis_text = ""
    for path in (REPO_ROOT / "apps" / "web" / "src" / "apis").rglob("*.ts"):
        apis_text += _read(path)
    for pattern in forbidden_api_patterns:
        if re.search(pattern, apis_text):
            errors.append(
                f"web: retired API endpoint pattern matched in front-end apis/: {pattern!r}"
            )

    return errors


# ---------------------------------------------------------------------------
# Desktop surface
# ---------------------------------------------------------------------------


DESKTOP_BRIDGE_VERSION = "product-desktop-bridge-v1.phase10"
DESKTOP_PRODUCT_CAPABILITIES = (
    "runtimeRequest",
    "actionConsume",
    "projectionStream",
    "streamLastEventId",
    "streamDedup",
    "streamReauthorization",
    "artifactRead",
    "artifactDownload",
    "feedback",
)
DESKTOP_PRODUCT_ENDPOINTS = (
    "runtimeRequests",
    "actionConsume",
    "streamEvents",
    "stream",
    "artifactReadTemplate",
    "artifactDownloadTemplate",
    "feedback",
)


def verify_desktop() -> list[str]:
    errors: list[str] = []
    main = _read(REPO_ROOT / "apps" / "desktop" / "main.cjs")
    preload = _read(REPO_ROOT / "apps" / "desktop" / "preload.cjs")

    if DESKTOP_BRIDGE_VERSION not in main and DESKTOP_BRIDGE_VERSION not in preload:
        errors.append(
            f"desktop: expected bridge version {DESKTOP_BRIDGE_VERSION!r} in main.cjs or preload.cjs"
        )
    for capability in DESKTOP_PRODUCT_CAPABILITIES:
        if capability not in main and capability not in preload:
            errors.append(f"desktop: missing capability {capability!r}")
    for endpoint in DESKTOP_PRODUCT_ENDPOINTS:
        if endpoint not in main and endpoint not in preload:
            errors.append(f"desktop: missing endpoint key {endpoint!r}")

    # Forbidden legacy IPC channels: enforce absence so a regression is loud.
    forbidden_ipc = [
        "legacyProductStreamV0",
        "phase0StreamBridge",
        "legacyProductBridgeV0",
        "electronLegacyBridge",
        "streamReauthorizeV0",
        "chunkStreamV0",
    ]
    desktop_text = main + "\n" + preload
    for name in forbidden_ipc:
        if name in desktop_text:
            errors.append(f"desktop: forbidden legacy IPC channel {name!r} present")

    # The 4 legacy .bat forwarders must still forward to canonical launchers.
    forwarders = {
        "tools/scripts/zuno-start.bat": "Zuno-Desktop-Start.cmd",
        "tools/scripts/zuno-stop.bat": "Zuno-Desktop-Stop.cmd",
        "tools/scripts/zuno-rebuild-start.bat": "Zuno-Desktop-Rebuild.cmd",
        "tools/scripts/zuno-clean-rebuild-start.bat": "Zuno-Desktop-Full-Rebuild.cmd",
    }
    for relpath, target in forwarders.items():
        text = _read(REPO_ROOT / relpath)
        if not text:
            errors.append(f"desktop: legacy forwarder {relpath} missing")
            continue
        if target not in text:
            errors.append(
                f"desktop: legacy forwarder {relpath} no longer forwards to {target!r}"
            )

    return errors


# ---------------------------------------------------------------------------
# Tools / Infra / Workflow surface
# ---------------------------------------------------------------------------


WORKFLOW_PATHS = sorted((REPO_ROOT / ".github" / "workflows").glob("*.yml"))


def verify_tools_infra_workflows() -> list[str]:
    errors: list[str] = []

    # 1) Every script path referenced by a workflow must still exist on disk.
    script_patterns = (
        r"tools/scripts/verify_[A-Za-z0-9_]+\.py",
        r"tools/scripts/generate_[A-Za-z0-9_]+\.py",
        r"\btools/scripts/verify_[A-Za-z0-9_]+\.py\b",
        r"\btools/scripts/generate_phase22_[A-Za-z0-9_]+\.py\b",
        r"\b\.agent/scripts/verify_[A-Za-z0-9_]+\.py\b",
    )
    for workflow in WORKFLOW_PATHS:
        content = _read(workflow)
        for pattern in script_patterns:
            for match in re.finditer(pattern, content):
                script_rel = match.group(0).strip()
                if not (REPO_ROOT / script_rel).exists():
                    errors.append(
                        f"workflow {workflow.name}: missing script {script_rel!r}"
                    )

    # 2) Compose service surface should not silently drift. Pin the 9 expected
    #    services plus the optional elasticsearch profile.
    compose = _read(REPO_ROOT / "infra" / "docker" / "docker-compose.yml")
    expected_services = (
        "postgres:",
        "redis:",
        "rabbitmq:",
        "neo4j:",
        "elasticsearch:",
        "minio:",
        "etcd:",
        "milvus:",
        "backend:",
        "worker:",
        "frontend:",
    )
    for service in expected_services:
        if f"\n  {service}\n" not in compose:
            errors.append(
                f"infra: docker-compose.yml missing service header {service!r}"
            )
    # The elasticsearch service must remain behind an opt-in profile.
    if "profiles:\n      - elasticsearch" not in compose:
        errors.append(
            "infra: elasticsearch service lost its opt-in profile guard; treat as retired"
        )

    # 3) Dockerfile / dockerfile.frontend must still get the configuration they
    #    claim to. (Args and key apt instructions.)
    dockerfile = _read(REPO_ROOT / "infra" / "docker" / "Dockerfile")
    for arg in (
        "ARG PYTHON_BASE_IMAGE=",
        "ARG DEBIAN_MIRROR=",
        "ARG DEBIAN_SECURITY_MIRROR=",
        "ARG PIP_TRUSTED_HOST=",
        "ARG PIP_DEFAULT_TIMEOUT=",
        "ARG PIP_RETRIES=",
    ):
        if arg not in dockerfile:
            errors.append(f"infra: backend Dockerfile missing build arg {arg!r}")
    if "chromium-driver" not in dockerfile:
        errors.append("infra: backend Dockerfile dropped chromium-driver install")

    frontend_dockerfile = _read(
        REPO_ROOT / "infra" / "docker" / "Dockerfile.frontend"
    )
    if not frontend_dockerfile.strip():
        errors.append("infra: Dockerfile.frontend is empty")

    # 4) Phase0 backend launcher should still bind 7860 and start uvicorn via
    #    the canonical src/backend module path (no override).
    phase0_start = _read(
        REPO_ROOT / "tools" / "launchers" / "windows" / "Zuno-Phase0-Backend-Start.cmd"
    )
    if "uvicorn --app-dir src/backend zuno.main:app" not in phase0_start:
        errors.append("tools: Phase0 backend launcher no longer pins canonical module path")
    if "127.0.0.1" not in phase0_start or "7860" not in phase0_start:
        errors.append("tools: Phase0 backend launcher lost 127.0.0.1:7860 binding")

    # 5) PowerShell smoke scripts must resolve the repo root, not tools root.
    ps1_check = [
        ("tools/scripts/run-full-e2e-smoke.ps1", "Split-Path -Parent (Split-Path -Parent $PSScriptRoot)"),
        ("tools/scripts/run-desktop-smoke.ps1", "Split-Path -Parent (Split-Path -Parent $PSScriptRoot)"),
    ]
    for relpath, snippet in ps1_check:
        if snippet not in _read(REPO_ROOT / relpath):
            errors.append(
                f"tools: {relpath} no longer resolves the repository root"
            )

    return errors


# ---------------------------------------------------------------------------
# Governance: feature-flag registry + temporary allowlist + bypass inventory
# ---------------------------------------------------------------------------


RETIRED_GENERAL_AGENT_FLAG = "legacy_general_agent_completion_rollback"
ALLOWED_VERSIONED_V1_FLAGS = (
    "product_api_v1_adapter",
    "workspace_projection_stream_v1",
)
OUT_OF_SCOPE_FLAG_BLOCKERS = (
    "tool_runtime_readonly_gateway",
    "postgres_domain_uow_shadow",
)
PROTECTED_WEB_ALLOWLIST_ENTRIES = (
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
)


def verify_governance() -> list[str]:
    errors: list[str] = []

    feature_flags = _read(
        REPO_ROOT / ".agent" / "programs" / "work-products" / "feature-flag-registry.yaml"
    )

    # 1) ALLOWED_HISTORY_REFERENCE: the registry must keep the explicit
    #    retirement record and the cutover drill rollback_command.
    if f'flag: "{RETIRED_GENERAL_AGENT_FLAG}"' not in feature_flags:
        errors.append(
            "governance: feature-flag-registry missing ALLOWED_HISTORY_REFERENCE "
            f"flag record {RETIRED_GENERAL_AGENT_FLAG!r}"
        )
    else:
        block = _flag_block(feature_flags, RETIRED_GENERAL_AGENT_FLAG)
        if 'default: "RETIRED"' not in block:
            errors.append(
                "governance: history reference flag is no longer RETIRED"
            )
        if "ZUNO_AGENT_RUNTIME=legacy_general_agent" in block:
            errors.append(
                "governance: history reference flag re-exposes legacy general agent runtime rollback"
            )

    # 2) ALLOWED_VERSIONED_PUBLIC_API exemption: v1 adapter and v1 stream must
    #    still be present (per worker brief "对于 product_api_v1_adapter 不能因为名字含 v1 就删除").
    for flag in ALLOWED_VERSIONED_V1_FLAGS:
        if f'flag: "{flag}"' not in feature_flags:
            errors.append(
                f"governance: versioned public API flag {flag!r} missing from registry"
            )

    # 3) ACTIVE_NONBACKEND_BLOCKER: the two out-of-scope expired flags must
    #    still exist so that DeepSeek workers can retire them in a
    #    coordinated branch; collapsing them here would be out of scope.
    for flag in OUT_OF_SCOPE_FLAG_BLOCKERS:
        if f'flag: "{flag}"' not in feature_flags:
            errors.append(
                f"governance: out-of-scope expired flag {flag!r} collapsed too early"
            )

    # 4) UNRESOLVED: 3 protected web allowlist entries. They must keep their
    #    path, symbol and owner; deadlines (PHASE10) are intentionally
    #    expired but the entry is "Temporary Allowlist 永久例外" per worker
    #    brief. Removing any row silently is the regression we are guarding.
    temporary = _read(
        REPO_ROOT / ".agent" / "programs" / "work-products" / "temporary-allowlist.yaml"
    )
    bypass = _read(
        REPO_ROOT / ".agent" / "programs" / "work-products" / "legacy-bypass-inventory.yaml"
    )
    for entry in PROTECTED_WEB_ALLOWLIST_ENTRIES:
        path = entry["path"]
        symbol = entry["symbol"]
        owner = entry["owner"]
        # The temporary allowlist is the canonical source; bypass inventory
        # mirrors it. We require both to remain in lock-step.
        for source_name, source in (
            ("temporary-allowlist", temporary),
            ("legacy-bypass-inventory", bypass),
        ):
            if path not in source:
                errors.append(
                    f"governance: {source_name} dropped protected entry {path!r}"
                )
                continue
            # Slice the entry block to verify symbol + owner fields.
            block = source.split(f'path: "{path}"', 1)[1]
            block = block.split("\n  - path:", 1)[0]
            if symbol not in block:
                errors.append(
                    f"governance: {source_name} entry {path!r} lost symbol {symbol!r}"
                )
            if owner not in block:
                errors.append(
                    f"governance: {source_name} entry {path!r} lost owner {owner!r}"
                )

    # 5) UNRESOLVED: dynamic command. The verifier does NOT exercise the
    #    runtime path. It only asserts the audit artifact still names the
    #    dynamic command as a documented unresolved item so that the next
    #    worker does not regress it.
    if (
        "ZUNO_COMPLETION_CUTOVER_MODE=rollback" not in _read(REPO_ROOT / "docs" / "evidence" / "goal05-phase22-cleanup-start.md")
        and "ZUNO_COMPLETION_CUTOVER_MODE=rollback"
        not in _read(REPO_ROOT / "docs" / "evidence" / "goal05-phase22-nonbackend-legacy-cleanup" / "escalations.md")
    ):
        # Tolerate the wording as long as one of the documents explicitly
        # records the dynamic command as still-around in PHASE22.
        errors.append(
            "governance: dynamic command ZUNO_COMPLETION_CUTOVER_MODE=rollback no longer documented"
        )

    return errors


# ---------------------------------------------------------------------------
# Verifier entrypoint
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SuiteResult:
    name: str
    errors: tuple[str, ...]


def run_all() -> list[SuiteResult]:
    return [
        SuiteResult("web", tuple(verify_web())),
        SuiteResult("desktop", tuple(verify_desktop())),
        SuiteResult("tools_infra_workflows", tuple(verify_tools_infra_workflows())),
        SuiteResult("governance", tuple(verify_governance())),
    ]


def main() -> int:
    suites = run_all()
    failed = 0
    for suite in suites:
        if suite.errors:
            failed += 1
            print(f"[{suite.name}] {len(suite.errors)} error(s):", file=sys.stderr)
            for err in suite.errors:
                print(f"  - {err}", file=sys.stderr)
        else:
            print(f"[{suite.name}] ok")
    if failed:
        print(
            "PHASE22 nonbackend legacy surface verification FAILED.", file=sys.stderr
        )
        return 1
    print("PHASE22 nonbackend legacy surface verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
