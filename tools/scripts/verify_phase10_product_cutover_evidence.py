from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

FILES = {
    "web_runtime": REPO_ROOT / "apps/web/src/product/runtime.ts",
    "product_api": REPO_ROOT / "src/backend/zuno/api/v1/product.py",
    "product_service": REPO_ROOT / "src/backend/zuno/api/services/product/command_service.py",
    "product_repo": REPO_ROOT / "src/backend/zuno/platform/database/product/domain.py",
    "workspace_runtime": REPO_ROOT / "src/backend/zuno/api/services/workspace_task_runtime.py",
    "frontend_contract_tests": REPO_ROOT / "tests/frontend/test_phase10_product_contracts.py",
    "product_route_tests": REPO_ROOT / "tests/api/test_goal03_product_route.py",
    "workspace_tests": REPO_ROOT / "tests/api/test_workspace_task_runtime.py",
    "full_e2e": REPO_ROOT / "tools/qa/full-e2e/full_e2e.py",
    "launcher_tests": REPO_ROOT / "tests/tools/test_launcher_scripts.py",
    "evidence": REPO_ROOT / "docs/evidence/goal04-phase10-startup-audit.md",
}


def _read(path: Path, errors: list[str]) -> str:
    if not path.exists():
        errors.append(f"missing file: {path.relative_to(REPO_ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")


def _require(text: str, phrase: str, label: str, errors: list[str]) -> None:
    if phrase not in text:
        errors.append(f"{label} missing phrase: {phrase}")


def verify_phase10_product_cutover_evidence() -> list[str]:
    errors: list[str] = []
    web_runtime = _read(FILES["web_runtime"], errors)
    product_api = _read(FILES["product_api"], errors)
    product_service = _read(FILES["product_service"], errors)
    product_repo = _read(FILES["product_repo"], errors)
    workspace_runtime = _read(FILES["workspace_runtime"], errors)
    frontend_tests = _read(FILES["frontend_contract_tests"], errors)
    route_tests = _read(FILES["product_route_tests"], errors)
    workspace_tests = _read(FILES["workspace_tests"], errors)
    full_e2e = _read(FILES["full_e2e"], errors)
    launcher_tests = _read(FILES["launcher_tests"], errors)
    evidence = _read(FILES["evidence"], errors)

    for phrase in (
        "export type ProductRuntimeCutoverMode = 'shadow' | 'canary' | 'new_default' | 'rollback'",
        "PRODUCT_RUNTIME_CUTOVER_STORAGE_KEY = 'zuno.productRuntimeCutoverMode'",
        "buildProductCommandKindForCutover",
        "'SHADOW_SUBMIT_USER_GOAL'",
        "'CANARY_SUBMIT_USER_GOAL'",
        "'SUBMIT_USER_GOAL'",
        "throw new ProductRuntimeRollbackError",
        "cutover_mode: cutoverMode",
    ):
        _require(web_runtime, phrase, "web runtime cutover guard", errors)

    for phrase in (
        "ProductService.validate_runtime_cutover_contract(command_kind=body.command_kind, payload=body.payload)",
        "submit_runtime_request(",
    ):
        _require(product_api, phrase, "Product API cutover boundary", errors)

    for phrase in (
        "PRODUCT_RUNTIME_CUTOVER_COMMANDS",
        '"shadow": "SHADOW_SUBMIT_USER_GOAL"',
        '"canary": "CANARY_SUBMIT_USER_GOAL"',
        '"new_default": "SUBMIT_USER_GOAL"',
        "def validate_runtime_cutover_contract",
        "Product runtime rollback mode is active",
        "Product runtime cutover command mismatch",
        "def build_runtime_cutover_owner_context",
        '"cutover_mode": cutover_mode',
        '"constraints_hash": canonical_sha256(context)',
        'constraints_hash=cutover_context["constraints_hash"]',
        '"command_kind": cutover_context["command_kind"]',
        '"cutover_mode": cutover_context["cutover_mode"]',
    ):
        _require(product_service, phrase, "ProductService cutover contract", errors)

    for phrase in (
        '"command_kind": command.command_kind',
        '"cutover_mode": str(command.payload_json.get("cutover_mode") or "new_default")',
        'topic="product.runtime_request.dispatch"',
    ):
        _require(product_repo, phrase, "Product repository outbox cutover context", errors)

    for phrase in (
        '"cutover_mode": "new_default"',
        'command_kind="SUBMIT_USER_GOAL"',
    ):
        _require(workspace_runtime, phrase, "workspace bridge Product runtime cutover", errors)

    for phrase in (
        "test_phase10_product_runtime_cutover_modes_are_explicit_and_rollback_fail_closed",
        "command_kind: buildProductCommandKindForCutover(cutoverMode)",
    ):
        _require(frontend_tests, phrase, "frontend cutover tests", errors)

    for phrase in (
        "test_goal03_product_runtime_request_route_rejects_rollback_before_service",
        "test_goal03_product_service_rejects_rollback_before_database_write",
        "test_goal03_product_runtime_request_route_rejects_cutover_command_mismatch_before_service",
        "test_goal03_product_service_rejects_cutover_mismatch_and_unknown_mode_before_database_write",
        "test_goal03_product_service_builds_cutover_owner_context_for_agent_core_handoff",
    ):
        _require(route_tests, phrase, "Product route cutover tests", errors)

    for phrase in (
        "_PRODUCT_RUNTIME_SUBMISSIONS",
        '["command_kind"] == "SUBMIT_USER_GOAL"',
        '["payload"]["cutover_mode"] == "new_default"',
    ):
        _require(workspace_tests, phrase, "workspace bridge cutover tests", errors)

    for phrase in (
        "PRODUCT_CUTOVER_COMMANDS",
        '"shadow": "SHADOW_SUBMIT_USER_GOAL"',
        '"canary": "CANARY_SUBMIT_USER_GOAL"',
        '"new_default": "SUBMIT_USER_GOAL"',
        "'/api/v1/product/runtime-requests'",
        '"cutover_mode": mode',
        '_runtime_request_body("rollback", "SUBMIT_USER_GOAL")',
        "receipt/projection evidence",
        "Product runtime rollback mode is active",
    ):
        _require(full_e2e, phrase, "full E2E cutover smoke", errors)

    for phrase in (
        "test_full_e2e_smoke_covers_product_runtime_cutover_modes",
        "PRODUCT_CUTOVER_COMMANDS",
        "receipt/projection evidence",
    ):
        _require(launcher_tests, phrase, "launcher cutover smoke tests", errors)

    for phrase in (
        "P10-T22 Web Product Runtime Cutover Guard",
        "P10-T23 Product API Rollback Fail-Closed Boundary",
        "P10-T24 Product API Cutover Command Contract",
        "P10-T25 Product Runtime Cutover Handoff Context",
        "P10-T27 Browser Product Runtime Cutover Smoke Gate",
        "P10-T28 Branch-Scoped Alembic Upgrade Gate",
        "PHASE10 仍为 `in_progress`",
        "20260727_43 (head)",
        "temporary PostgreSQL database",
        "shadow/canary/default-new/rollback 仍缺完整闭环",
    ):
        _require(evidence, phrase, "PHASE10 cutover evidence", errors)

    return errors


if __name__ == "__main__":
    findings = verify_phase10_product_cutover_evidence()
    if findings:
        for finding in findings:
            print(finding)
        raise SystemExit(1)
    print("PHASE10 Product cutover evidence verifier passed.")
