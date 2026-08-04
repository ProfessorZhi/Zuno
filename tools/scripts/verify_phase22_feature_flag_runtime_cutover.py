"""PHASE22 Feature Flag and Residual Runtime Cutover Verifier.

Fail-closed audit gate for the PHASE22 closure of the expired rollout flags
and the residual AgentControlRuntime / product_baseline ownership.

Retired flags (PHASE22-FEATURE-FLAG-AND-RESIDUAL-RUNTIME-CUTOVER):

- product_api_v1_adapter      -> RETIRED; the v1 routes remain the stable
                                 Public API bound to ProductService through
                                 ProductUnitOfWork/ProductRepository.
- workspace_projection_stream_v1 -> RETIRED; a single projection stream owner
                                 (WorkspaceTaskRuntimeService.stream_task_events
                                 / v1 SSE route); v1 is a protocol version, not
                                 a dual runtime.
- tool_runtime_readonly_gateway -> RETIRED; ToolInvocationGateway is the only
                                 tool execution entry; READ_ONLY exempt from
                                 human approval but never from Security/Budget/
                                 Trace; unknown side-effect level fails closed.
- postgres_domain_uow_shadow    -> RETIRED; ProductUnitOfWork is the single
                                 PostgreSQL persistence path; current state +
                                 outbox commit in one transaction; no shadow
                                 write, no dual write, no second fact owner.

Residual runtime:

- AgentControlRuntime (zuno.agent.control_runtime) is INTERNAL_TEST_HARNESS:
  zero production callers, removed from the zuno.agent production facade,
  still importable for the eval harness (product_baseline,
  test_react_reflection_replan_runtime).
- product_baseline.py is INTERNAL_TEST_HARNESS: only tests/evals reference it.

Status values:
- FEATURE_FLAG_RUNTIME_CUTOVER_CONFIRMED
- ACTIVE_RUNTIME_READER_FOUND
- DUAL_PATH_FOUND
- PUBLIC_ADAPTER_OWNERSHIP_VIOLATION
- RESIDUAL_PRODUCT_RUNTIME_FOUND
- UNRESOLVED
- TOOL_ERROR

Default mode is fail-closed: any finding exits non-zero; unknown dynamic
readers resolve to UNRESOLVED.

Usage:
    python tools/scripts/verify_phase22_feature_flag_runtime_cutover.py
    python tools/scripts/verify_phase22_feature_flag_runtime_cutover.py --report
    python tools/scripts/verify_phase22_feature_flag_runtime_cutover.py --json
"""

from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"
EVIDENCE_DIR = (
    REPO_ROOT / "docs" / "evidence" / "goal05-phase22-feature-flag-runtime-cutover"
)
REGISTRY = (
    REPO_ROOT / ".agent" / "programs" / "work-products" / "feature-flag-registry.yaml"
)

STATUS_CONFIRMED = "FEATURE_FLAG_RUNTIME_CUTOVER_CONFIRMED"
STATUS_ACTIVE_READER = "ACTIVE_RUNTIME_READER_FOUND"
STATUS_DUAL_PATH = "DUAL_PATH_FOUND"
STATUS_ADAPTER_VIOLATION = "PUBLIC_ADAPTER_OWNERSHIP_VIOLATION"
STATUS_RESIDUAL_RUNTIME = "RESIDUAL_PRODUCT_RUNTIME_FOUND"
STATUS_UNRESOLVED = "UNRESOLVED"
STATUS_TOOL_ERROR = "TOOL_ERROR"

RETIRED_FLAGS = [
    "product_api_v1_adapter",
    "workspace_projection_stream_v1",
    "tool_runtime_readonly_gateway",
    "postgres_domain_uow_shadow",
]

# Known out-of-work-package direct-execution surface. Any bypass outside this
# pinned set is a DUAL_PATH finding (fail-closed on growth).
#
# - workspace simple/wechat agents: workspace cutover wave, pinned by the tool
#   side-effect gate tests, owned by another worker.
# - legacy GeneralAgent-family modules: semantic legacy runtimes whose
#   retirement is PR #127 (candidate dependency, not assumed accepted). They
#   still exist on origin/main and call tools directly; this verifier pins
#   them so the surface cannot grow beyond these two modules.
KNOWN_OUT_OF_SCOPE_TOOL_SURFACE = (
    "src/backend/zuno/platform/services/workspace/simple_agent.py",
    "src/backend/zuno/platform/services/workspace/wechat_agent.py",
    "src/backend/zuno/agent/core/agents/react_agent.py",
    "src/backend/zuno/agent/core/agents/plan_execute_agent.py",
)

PRODUCTION_ENTRY_POINTS = (
    "src/backend/zuno/main.py",
    "src/backend/zuno/api/services/completion.py",
    "src/backend/zuno/api/services/workspace_task_runtime.py",
    "src/backend/zuno/api/v1/product.py",
    "src/backend/zuno/api/v1/workspace.py",
    "src/backend/zuno/platform/services/queue/workers.py",
    "src/backend/zuno/platform/services/cli_tool_discovery.py",
    "src/backend/zuno/platform/services/simple_api_tool.py",
    "tools/scripts/start.py",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _findings() -> dict[str, list[str]]:
    findings: dict[str, list[str]] = {
        "flag_not_retired": [],
        "flag_reader_found": [],
        "dynamic_selector_found": [],
        "dual_path_found": [],
        "adapter_ownership_violation": [],
        "residual_runtime_found": [],
        "unresolved": [],
    }

    # --- 1. Registry: every retired flag is RETIRED fail-closed -------------
    registry_text = _read(REGISTRY)
    for flag_name in RETIRED_FLAGS:
        block_match = re.search(
            rf'(?ms)^  - flag: "{re.escape(flag_name)}"(.*?)^  - flag: |^  - flag: "{re.escape(flag_name)}"(.*?)\Z',
            registry_text,
        )
        if block_match is None:
            findings["flag_not_retired"].append(f"{flag_name}: missing from registry")
            continue
        block = (block_match.group(1) or block_match.group(2) or "").strip()
        if 'default: "RETIRED"' not in block:
            findings["flag_not_retired"].append(f"{flag_name}: default is not RETIRED")
        if "retired and fail-closed" not in block.lower():
            findings["flag_not_retired"].append(f"{flag_name}: rollback_command is not fail-closed")

    # --- 2. No production reader of any retired flag name -------------------
    for path in sorted((BACKEND_ROOT / "zuno").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        text = _read(path)
        for flag_name in RETIRED_FLAGS:
            if flag_name in text:
                findings["flag_reader_found"].append(f"{rel}: references {flag_name}")
        # dynamic selectors for the retired flags must not exist
        for marker in ("ZUNO_PRODUCT_ADAPTER", "ZUNO_PROJECTION_STREAM", "ZUNO_TOOL_GATEWAY", "ZUNO_UOW"):
            if marker in text:
                findings["dynamic_selector_found"].append(f"{rel}: dynamic selector marker {marker}")

    # --- 3. Public v1 API contract preserved, no adapter ownership violation -
    v1_product = BACKEND_ROOT / "zuno" / "api" / "v1" / "product.py"
    v1_workspace = BACKEND_ROOT / "zuno" / "api" / "v1" / "workspace.py"
    for path, label in ((v1_product, "v1 product route"), (v1_workspace, "v1 workspace route")):
        if not path.exists():
            findings["adapter_ownership_violation"].append(f"{label} missing: {path.relative_to(REPO_ROOT)}")

    # Public adapter (api/services/product/*) must not import DAO classes
    # directly; persistence goes through ProductUnitOfWork/ProductRepository.
    for path in sorted((BACKEND_ROOT / "zuno" / "api" / "services" / "product").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        text = _read(path)
        if re.search(r"(?m)^\s*(from zuno\.platform\.database\.dao|import zuno\.platform\.database\.dao)", text):
            findings["adapter_ownership_violation"].append(
                f"{path.relative_to(REPO_ROOT)}: direct DAO import in public adapter"
            )

    # --- 4. Single projection stream owner ----------------------------------
    workspace_route = _read(v1_workspace) if v1_workspace.exists() else ""
    stream_route_count = len(re.findall(r"events/stream", workspace_route))
    if stream_route_count != 1:
        findings["dual_path_found"].append(
            f"v1 workspace SSE stream route count != 1 ({stream_route_count})"
        )
    if "text/event-stream" not in workspace_route:
        findings["dual_path_found"].append("v1 workspace SSE contract missing text/event-stream")

    # --- 5. ToolInvocationGateway is the only execution entry (allowed
    #        surface; known out-of-scope workspace agents pinned) ------------
    gateway_path = BACKEND_ROOT / "zuno" / "capability" / "tool_runtime" / "invocation_gateway.py"
    if not gateway_path.exists():
        findings["dual_path_found"].append("ToolInvocationGateway missing")
    for root_rel in (
        "src/backend/zuno/agent",
        "src/backend/zuno/api/services",
        "src/backend/zuno/capability",
    ):
        root = BACKEND_ROOT / root_rel.removeprefix("src/backend/")
        for path in sorted(root.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            rel = path.relative_to(REPO_ROOT).as_posix()
            if rel in KNOWN_OUT_OF_SCOPE_TOOL_SURFACE:
                continue
            text = _read(path)
            # direct tool dispatch that bypasses the gateway (classic dual path)
            if re.search(r"(?m)\.ainvoke\(\s*tool|execute_tool\s*\(", text) and "invocation_gateway" not in text:
                findings["dual_path_found"].append(f"{rel}: direct tool dispatch candidate")

    # --- 6. PostgreSQL UoW: single transaction, no shadow write -------------
    product_domain = BACKEND_ROOT / "zuno" / "platform" / "database" / "product" / "domain.py"
    if not product_domain.exists():
        findings["adapter_ownership_violation"].append("product/domain.py missing (UoW owner)")
    else:
        text = _read(product_domain)
        if "self._transaction.commit()" not in text or "self._transaction.rollback()" not in text:
            findings["adapter_ownership_violation"].append("ProductUnitOfWork lacks commit/rollback transaction")
        if re.search(r"(?i)shadow", text):
            findings["dual_path_found"].append("shadow marker inside product/domain.py")
    for path in sorted((BACKEND_ROOT / "zuno" / "platform" / "database").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        if "cutover" in rel:
            continue  # Phase08CutoverController domain owned by parallel session
        if re.search(r"(?i)\bshadow\s+(write|table|insert|update)", _read(path)):
            findings["dual_path_found"].append(f"{rel}: shadow write pattern")

    # --- 7. Residual AgentControlRuntime / product_baseline -----------------
    try:
        if str(BACKEND_ROOT) not in sys.path:
            sys.path.insert(0, str(BACKEND_ROOT))
        import zuno.agent as agent
        if "AgentControlRuntime" in getattr(agent, "__all__", []):
            findings["residual_runtime_found"].append("zuno.agent facade still exports AgentControlRuntime")
        if hasattr(agent, "AgentControlRuntime"):
            findings["residual_runtime_found"].append("zuno.agent facade exposes AgentControlRuntime attribute")
        importlib.import_module("zuno.agent.control_runtime")  # harness module must stay importable
    except Exception as exc:  # pragma: no cover - defensive
        findings["unresolved"].append(f"facade import check failed: {exc}")

    for entry in PRODUCTION_ENTRY_POINTS:
        path = REPO_ROOT / entry
        if not path.exists():
            continue
        text = _read(path)
        if "control_runtime" in text or "AgentControlRuntime" in text:
            findings["residual_runtime_found"].append(f"{entry}: imports residual control runtime")
        if "product_baseline" in text:
            findings["residual_runtime_found"].append(f"{entry}: imports product baseline")

    # product_baseline may only be referenced by tests/evals and the verifier.
    baseline_refs = []
    for path in sorted((REPO_ROOT / "src" / "backend").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        if "product_baseline" in _read(path):
            baseline_refs.append(path.relative_to(REPO_ROOT).as_posix())
    non_harness = [ref for ref in baseline_refs if "product_baseline.py" not in ref]
    if non_harness:
        findings["residual_runtime_found"].append(
            f"product_baseline referenced outside its own module: {non_harness}"
        )

    return findings


def verify() -> tuple[str, dict]:
    report: dict = {
        "verifier": "verify_phase22_feature_flag_runtime_cutover.py",
        "phase": "PHASE22-FEATURE-FLAG-AND-RESIDUAL-RUNTIME-CUTOVER",
        "repo_root": str(REPO_ROOT),
        "retired_flags": list(RETIRED_FLAGS),
        "status": STATUS_UNRESOLVED,
        "findings": {},
    }
    try:
        findings = _findings()
    except Exception as exc:  # pragma: no cover - defensive
        report["status"] = STATUS_TOOL_ERROR
        report["error"] = str(exc)
        return STATUS_TOOL_ERROR, report

    report["findings"] = findings
    total = sum(len(items) for items in findings.values())
    if total == 0:
        status = STATUS_CONFIRMED
    elif findings["flag_not_retired"] or findings["flag_reader_found"] or findings["dynamic_selector_found"]:
        status = STATUS_ACTIVE_READER
    elif findings["dual_path_found"]:
        status = STATUS_DUAL_PATH
    elif findings["adapter_ownership_violation"]:
        status = STATUS_ADAPTER_VIOLATION
    elif findings["residual_runtime_found"]:
        status = STATUS_RESIDUAL_RUNTIME
    else:
        status = STATUS_UNRESOLVED
    report["status"] = status
    report["finding_count"] = total
    return status, report


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    status, report = verify()
    if "--report" in argv:
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        report_path = EVIDENCE_DIR / "verifier_report.json"
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(f"wrote {report_path.relative_to(REPO_ROOT)}")
    if "--json" in argv:
        print(json.dumps({"status": status, "findings": report["findings"]}, indent=2, sort_keys=True))
    if status != STATUS_CONFIRMED:
        for category, items in report["findings"].items():
            for item in items:
                print(f"FINDING [{category}]: {item}")
        print(f"PHASE22 feature flag runtime cutover verification failed: {status}")
        return 1
    print(f"PHASE22 feature flag runtime cutover verification passed: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
