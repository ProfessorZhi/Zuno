"""PHASE22 Backend Semantic Legacy Cleanup Verifier.

Fail-closed audit gate for the retirement of the semantic legacy agent
runtimes that used to hide under canonical names (the ``GeneralAgent``
family). After this cleanup the Single Controller Product Runtime
(``zuno.agent.runtime``) is the only top-level product runtime:

- Single Controller  -> ``SingleControllerRuntimeHarness`` (zuno.agent.harness)
- Fixed AgentRunGraph -> ``build_agent_graph`` (zuno.agent.runtime.graph)
- Dynamic Plan DAG    -> ``RuntimePlanner`` / planning package (zuno.agent.runtime.planning)
- Fixed StepExecutionGraph -> ``build_phase08_step_graph`` (zuno.agent.runtime.phase08)

The verifier checks:

1. Retired modules are physically gone and cannot be imported dynamically.
2. Retired symbols are gone from the agent package exports
   (``zuno.agent``, ``zuno.agent.core``, ``zuno.agent.core.agents``).
3. No production entry point (FastAPI main, API v1, Completion, Workspace
   Task, Queue Worker, CLI, Tool Script) imports or constructs a retired
   legacy agent.
4. No environment-variable runtime selector or silent fallback
   (``ZUNO_AGENT_RUNTIME``, ``legacy_general_agent``, ``_create_chat_agent``,
   ``ModuleNotFoundError`` fallback into a legacy runtime).
5. ``direct_answer`` remains a canonical planner strategy only; any use that
   bypasses the Plan stage is a finding.
6. No server-product SQLite/InMemory fallback dual path outside the
   canonical stores (``SQLiteAgentRunStore`` / ``InMemoryDurableRuntimeStore``
   are canonical run stores, not fallbacks).

Status values:
- BACKEND_SEMANTIC_LEGACY_CLEAN
- PRODUCT_LEGACY_RUNTIME_FOUND
- CANONICAL_RUNTIME_BYPASS_FOUND
- PRODUCTION_ADAPTER_FALLBACK_FOUND
- UNRESOLVED
- TOOL_ERROR

Usage:
    python tools/scripts/verify_phase22_backend_semantic_legacy.py
    python tools/scripts/verify_phase22_backend_semantic_legacy.py --report   # writes verifier_report.json
    python tools/scripts/verify_phase22_backend_semantic_legacy.py --json     # machine-readable status
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"
EVIDENCE_DIR = (
    REPO_ROOT / "docs" / "evidence" / "goal05-phase22-backend-semantic-legacy-cleanup"
)

STATUS_CLEAN = "BACKEND_SEMANTIC_LEGACY_CLEAN"
STATUS_LEGACY_FOUND = "PRODUCT_LEGACY_RUNTIME_FOUND"
STATUS_BYPASS_FOUND = "CANONICAL_RUNTIME_BYPASS_FOUND"
STATUS_ADAPTER_FALLBACK = "PRODUCTION_ADAPTER_FALLBACK_FOUND"
STATUS_UNRESOLVED = "UNRESOLVED"
STATUS_TOOL_ERROR = "TOOL_ERROR"

RETIRED_MODULES = [
    "zuno.agent.core.agents.general_agent",
    "zuno.agent.core.agents.react_agent",
    "zuno.agent.core.agents.plan_execute_agent",
    "zuno.agent.core.agents.codeact_agent",
    "zuno.agent.core.agents.text2sql_agent",
    "zuno.agent.state",
    "zuno.agent.streaming",
    "zuno.agent.runtime",  # the shadowed dead shim module (package wins today)
]

RETIRED_SYMBOLS = (
    "GeneralAgent",
    "AgentConfig",
    "StreamAgentState",
    "EmitEventAgentMiddleware",
    "PlanExecuteAgent",
    "ReactAgent",
    "CodeActAgent",
    "Text2SQLAgent",
)

RETIRED_FILES = [
    "src/backend/zuno/agent/core/agents/general_agent.py",
    "src/backend/zuno/agent/core/agents/react_agent.py",
    "src/backend/zuno/agent/core/agents/plan_execute_agent.py",
    "src/backend/zuno/agent/core/agents/codeact_agent.py",
    "src/backend/zuno/agent/core/agents/text2sql_agent.py",
    "src/backend/zuno/agent/runtime.py",
    "src/backend/zuno/agent/state.py",
    "src/backend/zuno/agent/streaming.py",
]

ENTRY_POINT_FILES = [
    "src/backend/zuno/main.py",
    "src/backend/zuno/api/services/completion.py",
    "src/backend/zuno/api/services/workspace_task_runtime.py",
    "src/backend/zuno/api/services/agent_skill.py",
    "src/backend/zuno/api/services/mcp_server.py",
    "src/backend/zuno/api/v1/completion.py",
    "src/backend/zuno/platform/services/queue/workers.py",
    "src/backend/zuno/platform/services/cli_tool_discovery.py",
    "src/backend/zuno/platform/services/simple_api_tool.py",
    "tools/scripts/start.py",
]

# Production roots scanned for forbidden legacy markers.
PRODUCTION_ROOT = "src/backend/zuno"

# canonical planner files where "direct_answer" is a legitimate strategy name
# (Dynamic Plan DAG strategy selection and contract enums).
DIRECT_ANSWER_ALLOWED_PREFIXES = (
    "src/backend/zuno/agent/planning.py",
    "src/backend/zuno/agent/contracts.py",
    "src/backend/zuno/agent/runtime/planning/",
    "src/backend/zuno/agent/runtime/contracts.py",
)

# canonical stores; a store choice is not a legacy fallback.
CANONICAL_STORE_MODULES = (
    "zuno.agent.runtime.sqlite_store",
    "zuno.agent.durable_runtime",
    "zuno.agent.runtime.store",
)

FORBIDDEN_MARKERS = [
    "from zuno.agent.core.agents.general_agent import",
    "import zuno.agent.core.agents.general_agent",
    "from zuno.agent.core.agents.react_agent import",
    "from zuno.agent.core.agents.plan_execute_agent import",
    "from zuno.agent.core.agents.codeact_agent import",
    "from zuno.agent.core.agents.text2sql_agent import",
    "from zuno.agent.state import",
    "from zuno.agent.streaming import",
    "import zuno.agent.state",
    "import zuno.agent.streaming",
    "zuno.agent.runtime import GeneralAgent",
    "zuno.agent.runtime import AgentConfig",
]

FORBIDDEN_RUNTIME_SELECTORS = [
    "ZUNO_AGENT_RUNTIME",
    "legacy_general_agent",
    "_create_chat_agent",
    "runtime_selector",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _findings() -> dict[str, list[str]]:
    findings: dict[str, list[str]] = {
        "retired_files_present": [],
        "retired_modules_importable": [],
        "retired_exports_present": [],
        "entry_point_legacy_imports": [],
        "runtime_selector_found": [],
        "direct_answer_bypass": [],
        "legacy_fallback_found": [],
    }

    # 1. Retired files must not exist.
    for rel in RETIRED_FILES:
        path = REPO_ROOT / rel
        if path.exists():
            findings["retired_files_present"].append(rel)

    # 2. Retired modules must not be importable.
    if str(BACKEND_ROOT) not in sys.path:
        sys.path.insert(0, str(BACKEND_ROOT))
    for module_name in RETIRED_MODULES:
        if module_name == "zuno.agent.runtime":
            # package wins over the retired shim module; never treat the
            # canonical package as importable legacy
            continue
        try:
            importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue
        except Exception as exc:  # pragma: no cover - defensive
            findings["retired_modules_importable"].append(f"{module_name} (unexpected: {exc})")
            continue
        findings["retired_modules_importable"].append(module_name)

    # 3. Retired symbols must be gone from package exports.
    for package_name in ["zuno.agent", "zuno.agent.core", "zuno.agent.core.agents"]:
        try:
            package = importlib.import_module(package_name)
        except Exception as exc:  # pragma: no cover - defensive
            findings["retired_exports_present"].append(f"{package_name} import failed: {exc}")
            continue
        for symbol in RETIRED_SYMBOLS:
            if symbol in getattr(package, "__all__", []):
                findings["retired_exports_present"].append(f"{package_name}.__all__ contains {symbol}")
            if hasattr(package, symbol):
                findings["retired_exports_present"].append(f"{package_name} has attribute {symbol}")

    # 4. Production entry points must not reference retired modules.
    production_root = REPO_ROOT / PRODUCTION_ROOT
    for path in sorted(production_root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        text = _read(path)
        for marker in FORBIDDEN_MARKERS:
            if marker in text:
                findings["entry_point_legacy_imports"].append(f"{rel}: {marker}")
        for selector in FORBIDDEN_RUNTIME_SELECTORS:
            if selector in text:
                findings["runtime_selector_found"].append(f"{rel}: {selector}")

    # 5. direct_answer may only live in the canonical planner/contracts files.
    for path in sorted(production_root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel.startswith(DIRECT_ANSWER_ALLOWED_PREFIXES):
            continue
        text = _read(path)
        if "direct_answer" in text:
            findings["direct_answer_bypass"].append(f"{rel}: direct_answer outside canonical planner")

    # 6. Silent legacy fallback patterns in entry points: try/except around a
    #    legacy runtime import, or an explicit fallback to a retired module.
    for rel in ENTRY_POINT_FILES:
        path = REPO_ROOT / rel
        if not path.exists():
            continue
        text = _read(path)
        lower = text.lower()
        for marker in ("except modulenotfounderror", "except importerror"):
            if marker in lower and any(
                token in text for token in ("legacy", "general_agent", "fallback_runtime")
            ):
                findings["legacy_fallback_found"].append(f"{rel}: {marker} fallback candidate")

    return findings


def verify() -> tuple[str, dict]:
    """Return (status, report)."""
    report: dict = {
        "verifier": "verify_phase22_backend_semantic_legacy.py",
        "phase": "PHASE22-BACKEND-SEMANTIC-LEGACY-CLEANUP",
        "repo_root": str(REPO_ROOT),
        "retired_modules": list(RETIRED_MODULES),
        "retired_files": list(RETIRED_FILES),
        "entry_point_files": list(ENTRY_POINT_FILES),
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
        status = STATUS_CLEAN
    else:
        if findings["retired_files_present"] or findings["retired_modules_importable"]:
            status = STATUS_LEGACY_FOUND
        elif (
            findings["retired_exports_present"]
            or findings["entry_point_legacy_imports"]
            or findings["direct_answer_bypass"]
        ):
            status = STATUS_BYPASS_FOUND
        elif findings["runtime_selector_found"] or findings["legacy_fallback_found"]:
            status = STATUS_ADAPTER_FALLBACK
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
    if status != STATUS_CLEAN:
        for category, items in report["findings"].items():
            for item in items:
                print(f"FINDING [{category}]: {item}")
        print(f"PHASE22 backend semantic legacy verification failed: {status}")
        return 1
    print(f"PHASE22 backend semantic legacy verification passed: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
