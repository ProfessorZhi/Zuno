from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from zuno.platform.database.schema_registry import SECURITY_TABLE_OWNERS

REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION_PATH = (
    REPO_ROOT
    / "infra"
    / "db"
    / "alembic"
    / "versions"
    / "20260719_16_security_control_plane.py"
)
EXPECTED_REVISION = "20260719_16"
EXPECTED_DOWN_REVISION = "20260718_15"
FORBIDDEN_SECRET_COLUMNS = {
    "secret",
    "secret_material",
    "plaintext",
    "plain_text",
    "token",
    "access_token",
    "refresh_token",
    "api_key",
    "password",
    "value",
    "material",
}
REQUIRED_COLUMNS = {
    "security_principal_contexts": {
        "principal_context_id",
        "tenant_id",
        "user_principal_id",
        "agent_principal_id",
        "task_principal_id",
        "session_principal_id",
        "epoch_ref",
        "context_hash",
        "status",
        "created_at",
    },
    "security_effective_epochs": {
        "epoch_ref",
        "tenant_id",
        "policy_bundle_ref",
        "policy_bundle_hash",
        "action_set_version",
        "principal_context_hash",
        "generation",
        "status",
        "created_at",
    },
    "security_authorization_decisions": {
        "decision_id",
        "tenant_id",
        "principal_context_id",
        "epoch_ref",
        "resource_ref",
        "action",
        "decision",
        "reason_code",
        "prepared_action_hash",
        "decision_hash",
        "created_at",
    },
    "security_approval_requests": {
        "approval_request_id",
        "tenant_id",
        "decision_id",
        "prepared_action_hash",
        "requested_by_principal_id",
        "required_approver_policy_ref",
        "status",
        "deadline_at",
        "created_at",
    },
    "security_approval_decisions": {
        "approval_decision_id",
        "tenant_id",
        "approval_request_id",
        "approver_principal_id",
        "decision",
        "decision_hash",
        "decided_at",
    },
    "security_secret_refs": {
        "secret_ref",
        "tenant_id",
        "credential_version_ref",
        "audience",
        "owner_principal_id",
        "scope_hash",
        "status",
        "created_at",
    },
    "security_secret_leases": {
        "lease_id",
        "tenant_id",
        "secret_ref",
        "workload_identity_ref",
        "on_behalf_of_binding_ref",
        "audience",
        "lease_generation",
        "lease_hash",
        "issued_at",
        "expires_at",
    },
    "security_redaction_decisions": {
        "redaction_id",
        "tenant_id",
        "source_ref",
        "sink_ref",
        "trust_label",
        "decision",
        "redaction_policy_ref",
        "redacted_payload_hash",
        "decision_hash",
        "created_at",
    },
    "security_audit_requirements": {
        "audit_requirement_id",
        "tenant_id",
        "decision_id",
        "audit_channel_id",
        "requirement_hash",
        "status",
        "created_at",
        "effect_observed_at",
    },
    "security_outbox_events": {
        "event_id",
        "tenant_id",
        "aggregate_id",
        "topic",
        "payload_hash",
        "payload",
        "idempotency_key",
        "status",
        "created_at",
    },
}


class OpRecorder:
    def __init__(self) -> None:
        self.tables: dict[str, set[str]] = {}
        self.indexes: set[str] = set()
        self.dropped_tables: list[str] = []

    def create_table(self, name: str, *objects: Any, **_: Any) -> None:
        columns = {
            str(item.name)
            for item in objects
            if item.__class__.__name__ == "Column" and getattr(item, "name", None)
        }
        self.tables[name] = columns

    def create_index(self, name: str, *_: Any, **__: Any) -> None:
        self.indexes.add(name)

    def drop_index(self, *_: Any, **__: Any) -> None:
        return None

    def drop_table(self, name: str) -> None:
        self.dropped_tables.append(name)


def _load_migration():
    spec = importlib.util.spec_from_file_location("phase05_security_migration", MIGRATION_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load PHASE05 security migration")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_with_recorder(function: Any) -> OpRecorder:
    module = _load_migration()
    recorder = OpRecorder()
    original_op = module.op
    module.op = recorder
    try:
        getattr(module, function)()
    finally:
        module.op = original_op
    return recorder


def verify_phase05_security_persistence() -> list[str]:
    errors: list[str] = []
    if not MIGRATION_PATH.exists():
        return ["missing PHASE05 security control plane migration"]

    module = _load_migration()
    if module.revision != EXPECTED_REVISION:
        errors.append(f"unexpected PHASE05 security revision: {module.revision!r}")
    if module.down_revision != EXPECTED_DOWN_REVISION:
        errors.append(
            f"PHASE05 security migration must follow {EXPECTED_DOWN_REVISION}, found {module.down_revision!r}"
        )

    if set(SECURITY_TABLE_OWNERS) != set(REQUIRED_COLUMNS):
        errors.append("SECURITY_TABLE_OWNERS does not match required security tables")

    upgrade = _run_with_recorder("upgrade")
    missing_tables = set(REQUIRED_COLUMNS) - set(upgrade.tables)
    if missing_tables:
        errors.append(f"security migration missing tables: {sorted(missing_tables)!r}")
    extra_tables = set(upgrade.tables) - set(REQUIRED_COLUMNS)
    if extra_tables:
        errors.append(f"security migration has unexpected tables: {sorted(extra_tables)!r}")

    for table, required_columns in REQUIRED_COLUMNS.items():
        actual_columns = upgrade.tables.get(table, set())
        missing_columns = required_columns - actual_columns
        if missing_columns:
            errors.append(f"{table} missing columns: {sorted(missing_columns)!r}")
        forbidden = FORBIDDEN_SECRET_COLUMNS & actual_columns
        if forbidden:
            errors.append(f"{table} stores forbidden secret material columns: {sorted(forbidden)!r}")
        if "tenant_id" not in actual_columns:
            errors.append(f"{table} missing tenant_id boundary column")

    source = MIGRATION_PATH.read_text(encoding="utf-8")
    for phrase in [
        "prepared_action_hash",
        "epoch_ref",
        "credential_version_ref",
        "workload_identity_ref",
        "on_behalf_of_binding_ref",
        "redacted_payload_hash",
        "audit_requirement_id",
    ]:
        if phrase not in source:
            errors.append(f"security migration missing target phrase: {phrase}")
    for forbidden in ["create_all(", "drop_all(", "access_token", "refresh_token", "api_key", "password"]:
        if forbidden in source:
            errors.append(f"security migration contains forbidden phrase: {forbidden}")

    repository = (
        REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "security" / "persistence.py"
    ).read_text(encoding="utf-8")
    for phrase in [
        "class PostgresSecurityApprovalFactSink",
        "class SecurityUnitOfWork",
        "class SecurityRepository",
        "record_tool_approval_fact",
        "record_effective_epoch",
        "ensure_effective_epoch",
        "record_principal_context",
        "record_authorization_decision",
        "request_approval",
        "decide_approval",
        "ensure_audit_requirement",
        "record_secret_ref",
        "issue_secret_lease",
        "validate_secret_lease",
        "record_redaction_decision",
        "validate_pre_effect_authorization",
        "enqueue_security_event",
        "SecurityPersistenceError",
    ]:
        if phrase not in repository:
            errors.append(f"security persistence repository missing phrase: {phrase}")
    for forbidden in ["access_token", "refresh_token", "api_key", "password"]:
        if forbidden in repository:
            errors.append(f"security persistence repository contains forbidden phrase: {forbidden}")

    product_actions = (
        REPO_ROOT
        / "src"
        / "backend"
        / "zuno"
        / "platform"
        / "security"
        / "product_actions.py"
    ).read_text(encoding="utf-8")
    for phrase in [
        "class SecurityProductActionRequest",
        "class SecurityProductActionGuard",
        "class PostgresSecurityProductActionGuard",
        "validate_pre_effect_authorization",
        "build_product_action_hash",
        "SecurityProductActionDenied",
    ]:
        if phrase not in product_actions:
            errors.append(f"security product action guard missing phrase: {phrase}")

    tool_runtime = (
        REPO_ROOT / "src" / "backend" / "zuno" / "capability" / "runtime.py"
    ).read_text(encoding="utf-8")
    for phrase in [
        "class SecurityApprovalFactSink",
        "security_approval_sink",
        "_record_security_approval_fact",
        "prepared_action_hash",
        "approved_before_effect",
        "failed_closed_before_effect",
    ]:
        if phrase not in tool_runtime:
            errors.append(f"tool runtime missing Security approval fact sink phrase: {phrase}")

    workspace_runtime = (
        REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "workspace_task_runtime.py"
    ).read_text(encoding="utf-8")
    for phrase in [
        "configure_security_approval_sink",
        "configure_security_product_action_guard",
        "_require_product_action_authorized",
        "_require_workspace_task_action_authorized",
        "artifact.read",
        "artifact.download",
        "task.resume.",
        "build_default_tool_control_plane_runtime(",
        "security_approval_sink=sink",
    ]:
        if phrase not in workspace_runtime:
            errors.append(f"workspace runtime missing Security approval sink wiring phrase: {phrase}")

    workspace_api = (
        REPO_ROOT / "src" / "backend" / "zuno" / "api" / "v1" / "workspace.py"
    ).read_text(encoding="utf-8")
    for phrase in [
        "principal_id=str(login_user.user_id or \"\")",
        "WorkspaceTaskRuntimeService.get_artifact(",
        "WorkspaceTaskRuntimeService.download_artifact(",
    ]:
        if phrase not in workspace_api:
            errors.append(f"workspace API missing product action reauthorization phrase: {phrase}")

    app_startup = (REPO_ROOT / "src" / "backend" / "zuno" / "main.py").read_text(encoding="utf-8")
    for phrase in [
        "PostgresSecurityProductActionGuard(engine)",
        "WorkspaceTaskRuntimeService.configure_security_product_action_guard(",
        "MCPService.configure_security_product_action_guard(",
        "MCPServerService.configure_security_product_action_guard(",
    ]:
        if phrase not in app_startup:
            errors.append(f"app startup missing product action security guard phrase: {phrase}")

    mcp_service = (
        REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "mcp_server.py"
    ).read_text(encoding="utf-8")
    for phrase in [
        "configure_security_product_action_guard",
        "_require_admin_action_authorized",
        "admin.mcp.create",
        "admin.mcp.update",
        "admin.mcp.delete",
        "admin.mcp.list",
        "SecurityProductActionRequest",
        "build_product_action_hash",
    ]:
        if phrase not in mcp_service:
            errors.append(f"MCP admin service missing Security product action phrase: {phrase}")

    mcp_stdio_service = (
        REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "mcp_stdio_server.py"
    ).read_text(encoding="utf-8")
    for phrase in [
        "configure_security_product_action_guard",
        "_require_admin_action_authorized",
        "admin.mcp_stdio.create",
        "admin.mcp_stdio.update",
        "admin.mcp_stdio.delete",
        "SecurityProductActionRequest",
        "build_product_action_hash",
    ]:
        if phrase not in mcp_stdio_service:
            errors.append(f"MCP stdio admin service missing Security product action phrase: {phrase}")

    fault_test = (
        REPO_ROOT
        / "tests"
        / "fault"
        / "security"
        / "test_phase05_security_sink_fail_closed.py"
    ).read_text(encoding="utf-8")
    for phrase in [
        "security sink unavailable",
        "approved_before_effect",
        "failed_closed_before_effect",
        "calls == []",
    ]:
        if phrase not in fault_test:
            errors.append(f"security sink fault test missing phrase: {phrase}")

    pre_effect_fault_test = (
        REPO_ROOT
        / "tests"
        / "fault"
        / "security"
        / "test_phase05_security_pre_effect_faults.py"
    ).read_text(encoding="utf-8")
    for phrase in [
        "prepared action hash changed",
        "approval deadline expired",
        "stale security epoch",
        "audience mismatch",
        "revoked secret",
        "redaction_succeeded=False",
    ]:
        if phrase not in pre_effect_fault_test:
            errors.append(f"security pre-effect fault test missing phrase: {phrase}")

    workspace_test = (
        REPO_ROOT
        / "tests"
        / "api"
        / "test_workspace_task_runtime.py"
    ).read_text(encoding="utf-8")
    for phrase in [
        "test_workspace_artifact_read_and_download_reauthorize_through_security_guard",
        "test_workspace_artifact_download_returns_403_when_security_reauthorization_denies",
        "test_workspace_task_approval_resume_reauthorizes_through_security_guard",
        "test_workspace_task_approval_resume_returns_403_when_security_guard_denies",
        "artifact.read",
        "artifact.download",
        "task.resume.approved",
        "product action denied by Security",
    ]:
        if phrase not in workspace_test:
            errors.append(f"workspace security reauthorization test missing phrase: {phrase}")

    mcp_admin_test = (REPO_ROOT / "tests" / "agent" / "test_mcp_server_service.py").read_text(
        encoding="utf-8"
    )
    for phrase in [
        "test_mcp_admin_override_reauthorizes_through_security_guard",
        "test_mcp_admin_override_denial_blocks_before_permission_success",
        "admin.mcp.delete",
        "admin.mcp.update",
    ]:
        if phrase not in mcp_admin_test:
            errors.append(f"MCP admin security reauthorization test missing phrase: {phrase}")

    mcp_stdio_admin_test = (
        REPO_ROOT / "tests" / "agent" / "test_mcp_stdio_server_security.py"
    ).read_text(encoding="utf-8")
    for phrase in [
        "test_mcp_stdio_admin_delete_reauthorizes_through_security_guard",
        "test_mcp_stdio_admin_update_denial_blocks_dao_write",
        "admin.mcp_stdio.delete",
        "admin.mcp_stdio.update",
    ]:
        if phrase not in mcp_stdio_admin_test:
            errors.append(f"MCP stdio admin security reauthorization test missing phrase: {phrase}")

    downgrade = _run_with_recorder("downgrade")
    if set(downgrade.dropped_tables) != set(REQUIRED_COLUMNS):
        errors.append(
            "security migration downgrade does not drop the same table set: "
            f"{sorted(downgrade.dropped_tables)!r}"
        )
    return errors


def main() -> int:
    errors = verify_phase05_security_persistence()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE05 security persistence verification failed.")
        return 1
    print("PHASE05 security persistence verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
