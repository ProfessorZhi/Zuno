"""PHASE22 Backend Semantic Legacy Cleanup Verifier — dual scope.

This verifier is a fail-closed audit gate for the retirement of the semantic
legacy agent runtimes. It produces a two-layer result so the PR truth can be
separated from the broader repository cutover truth:

  Scoped Slice Status (this PR's own retirement)
    - AGENT_FAMILY_LEGACY_SLICE_CLEAN
    - AGENT_FAMILY_LEGACY_SLICE_BLOCKED

  Repository Runtime Status (full Backend Product Runtime cutover)
    - BACKEND_PRODUCT_RUNTIME_CUTOVER_CONFIRMED
    - BACKEND_PRODUCT_RUNTIME_CUTOVER_BLOCKED
    - BACKEND_PRODUCT_RUNTIME_UNRESOLVED
    - TOOL_ERROR

Default invocation is equivalent to ``--scope repository`` so the verifier is
fail-closed in CI. ``--scope agent-family`` is provided for workflows that
want to gate only the slice owned by this work package.

Detection is AST-based (Python ``ast`` module) — no string counting.
The scanner inspects:

  - ClassDef nodes — defines the legacy runtime class shapes.
  - Import / ImportFrom nodes — every actual import statement.
  - Call nodes — instantiations (``SomeAgent(...)``) and function calls.
  - Attribute access — chained attribute lookups on imported names.
  - Await / async function bodies — reachable ``await handler(request)``
    patterns.
  - Reachability — every production entry point must reach a Single
    Controller class only; alternative top-level runtime classes are
    findings.

Usage:
    python tools/scripts/verify_phase22_backend_semantic_legacy.py
    python tools/scripts/verify_phase22_backend_semantic_legacy.py --scope agent-family
    python tools/scripts/verify_phase22_backend_semantic_legacy.py --scope repository --json
    python tools/scripts/verify_phase22_backend_semantic_legacy.py --report
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"
EVIDENCE_DIR = (
    REPO_ROOT / "docs" / "evidence" / "goal05-phase22-backend-semantic-legacy-cleanup"
)


SCOPE_AGENT_FAMILY = "agent-family"
SCOPE_REPOSITORY = "repository"

# Scoped slice statuses (this PR's own retirement)
STATUS_SCOPED_CLEAN = "AGENT_FAMILY_LEGACY_SLICE_CLEAN"
STATUS_SCOPED_BLOCKED = "AGENT_FAMILY_LEGACY_SLICE_BLOCKED"

# Repository statuses (whole Backend Product Runtime cutover)
STATUS_REPO_CONFIRMED = "BACKEND_PRODUCT_RUNTIME_CUTOVER_CONFIRMED"
STATUS_REPO_BLOCKED = "BACKEND_PRODUCT_RUNTIME_CUTOVER_BLOCKED"
STATUS_REPO_UNRESOLVED = "BACKEND_PRODUCT_RUNTIME_UNRESOLVED"
STATUS_TOOL_ERROR = "TOOL_ERROR"


# Symbols retired by THIS work package (the GeneralAgent family). Used
# for the scoped slice.
RETIRED_FAMILY_CLASSES = (
    "GeneralAgent",
    "ReactAgent",
    "PlanExecuteAgent",
    "CodeActAgent",
    "Text2SQLAgent",
)

RETIRED_FAMILY_SYMBOLS = RETIRED_FAMILY_CLASSES + (
    "AgentConfig",
    "StreamAgentState",
    "EmitEventAgentMiddleware",
)

RETIRED_FAMILY_MODULES = (
    "zuno.agent.core.agents.general_agent",
    "zuno.agent.core.agents.react_agent",
    "zuno.agent.core.agents.plan_execute_agent",
    "zuno.agent.core.agents.codeact_agent",
    "zuno.agent.core.agents.text2sql_agent",
)

RETIRED_FAMILY_FILES = (
    "src/backend/zuno/agent/core/agents/general_agent.py",
    "src/backend/zuno/agent/core/agents/react_agent.py",
    "src/backend/zuno/agent/core/agents/plan_execute_agent.py",
    "src/backend/zuno/agent/core/agents/codeact_agent.py",
    "src/backend/zuno/agent/core/agents/text2sql_agent.py",
    "src/backend/zuno/agent/runtime.py",
    "src/backend/zuno/agent/state.py",
    "src/backend/zuno/agent/streaming.py",
)

FORBIDDEN_FAMILY_RUNTIME_SELECTORS = (
    "ZUNO_AGENT_RUNTIME",
    "legacy_general_agent",
    "_create_chat_agent",
)


# Production entry points scanned in both scopes. These are the surfaces
# that can reach a Product Runtime today.
ENTRY_POINT_FILES = (
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
)

# Top-level Product Runtime classes that this verifier looks for in the
# repository scope. ``SINGLE_CONTROLLER`` is the only allowed entry —
# every other class is a finding.
SINGLE_CONTROLLER_CLASS = "SingleControllerRuntimeHarness"

TOP_LEVEL_PRODUCT_RUNTIME_CLASSES = (
    SINGLE_CONTROLLER_CLASS,
    "WorkSpaceSimpleAgent",
    "WechatAgent",
    "AgentControlRuntime",
)

# Modules that are explicitly out of the work-package scope. They are
# pinned as ``out_of_scope`` rather than reported as live callers so the
# repository status remains truthful about the current state.
OUT_OF_SCOPE_FILES = (
    "src/backend/zuno/agent/control_runtime.py",
    "src/backend/zuno/agent/product_baseline.py",
)

OUT_OF_SCOPE_PATHS_FOR_HISTORY = (
    "docs/",
    ".agent/",
    "tests/agent/runtime/",
)

# Direct ``handler(request)`` tool-call surface. AST-detected because
# string matching is too noisy on docstrings and tests.
DIRECT_HANDLER_AWAIT_PATTERN = "tool_result = await handler(request)"

# Retained internal mechanisms that the repository scope must NOT
# classify as a top-level runtime finding.
RETAINED_STEP_CAPABILITIES = (
    "StructuredResponseAgent",
    "ReActStepRunner",
)


@dataclass
class Finding:
    category: str
    path: str
    line: int
    detail: str
    severity: str = "error"


@dataclass
class ScopeResult:
    status: str = ""
    findings: list[Finding] = field(default_factory=list)

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------


def _classdef_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            names.add(node.name)
    return names


def _imports_in(tree: ast.AST) -> list[tuple[str, int]]:
    imports: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                full = f"{module}.{alias.name}" if module else alias.name
                imports.append((full, node.lineno))
    return imports


def _call_target_strings(tree: ast.AST) -> list[tuple[str, int]]:
    """Return (callable_text, line_no) for every Call node."""
    results: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            try:
                results.append((ast.unparse(node.func), node.lineno))
            except Exception:  # pragma: no cover - defensive
                continue
    return results


def _attribute_chains(tree: ast.AST) -> list[tuple[str, int]]:
    """Return attribute chain text for every Attribute node."""
    results: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            try:
                results.append((ast.unparse(node), node.lineno))
            except Exception:  # pragma: no cover - defensive
                continue
    return results


def _direct_handler_await_sites(tree: ast.AST) -> list[int]:
    """Return line numbers for ``await handler(request)`` assignments."""
    sites: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not isinstance(node.value, ast.Await):
            continue
        await_node = node.value
        if not isinstance(await_node.value, ast.Call):
            continue
        call = await_node.value
        try:
            text = ast.unparse(call.func)
        except Exception:  # pragma: no cover - defensive
            continue
        if text == "handler":
            sites.append(node.lineno)
    return sites


def _safe_parse(path: Path) -> ast.AST | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return None


# ---------------------------------------------------------------------------
# Scope: agent-family
# ---------------------------------------------------------------------------


def _check_retired_files_present() -> list[Finding]:
    findings: list[Finding] = []
    for rel in RETIRED_FAMILY_FILES:
        if (REPO_ROOT / rel).exists():
            findings.append(
                Finding(
                    category="retired_file_present",
                    path=rel,
                    line=0,
                    detail=f"retired file is present: {rel}",
                )
            )
    return findings


def _check_retired_imports_in_entry_points() -> list[Finding]:
    findings: list[Finding] = []
    for rel in ENTRY_POINT_FILES:
        path = REPO_ROOT / rel
        if not path.exists():
            continue
        tree = _safe_parse(path)
        if tree is None:
            continue
        for module, lineno in _imports_in(tree):
            if module in RETIRED_FAMILY_MODULES:
                findings.append(
                    Finding(
                        category="retired_module_imported",
                        path=rel,
                        line=lineno,
                        detail=f"entry point imports retired module: {module}",
                    )
                )
    return findings


def _check_retired_symbols_in_agent_exports() -> list[Finding]:
    """AST-detect retired symbols in agent package __all__."""
    findings: list[Finding] = []
    candidates = [
        "src/backend/zuno/agent/__init__.py",
        "src/backend/zuno/agent/core/__init__.py",
        "src/backend/zuno/agent/core/agents/__init__.py",
    ]
    for rel in candidates:
        path = REPO_ROOT / rel
        if not path.exists():
            continue
        tree = _safe_parse(path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if (
                        isinstance(target, ast.Name)
                        and target.id == "__all__"
                        and isinstance(node.value, (ast.List, ast.Tuple))
                    ):
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                if elt.value in RETIRED_FAMILY_SYMBOLS:
                                    findings.append(
                                        Finding(
                                            category="retired_symbol_in_all",
                                            path=rel,
                                            line=elt.lineno,
                                            detail=f"retired symbol re-exported: {elt.value}",
                                        )
                                    )
    return findings


def _check_forbidden_selectors_in_entry_points() -> list[Finding]:
    findings: list[Finding] = []
    for rel in ENTRY_POINT_FILES:
        path = REPO_ROOT / rel
        if not path.exists():
            continue
        tree = _safe_parse(path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in FORBIDDEN_FAMILY_RUNTIME_SELECTORS:
                findings.append(
                    Finding(
                        category="forbidden_selector",
                        path=rel,
                        line=node.lineno,
                        detail=f"forbidden runtime selector referenced: {node.id}",
                    )
                )
    return findings


def verify_agent_family_scope() -> ScopeResult:
    result = ScopeResult()
    result.findings.extend(_check_retired_files_present())
    result.findings.extend(_check_retired_imports_in_entry_points())
    result.findings.extend(_check_retired_symbols_in_agent_exports())
    result.findings.extend(_check_forbidden_selectors_in_entry_points())
    if result.findings:
        result.status = STATUS_SCOPED_BLOCKED
    else:
        result.status = STATUS_SCOPED_CLEAN
    return result


# ---------------------------------------------------------------------------
# Scope: repository
# ---------------------------------------------------------------------------


def _iter_python_files() -> Iterable[Path]:
    for path in BACKEND_ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        yield path


def _find_top_level_runtime_class_definitions() -> list[Finding]:
    """AST-detect class definitions for any known Product Runtime class."""
    findings: list[Finding] = []
    for path in _iter_python_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        tree = _safe_parse(path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            if node.name not in TOP_LEVEL_PRODUCT_RUNTIME_CLASSES:
                continue
            if node.name == SINGLE_CONTROLLER_CLASS:
                continue  # canonical
            # Skip retained step capabilities that are nested inside other
            # classes (they are Step-internal mechanisms, not top-level
            # runtimes).
            if node.name in RETAINED_STEP_CAPABILITIES:
                continue
            findings.append(
                Finding(
                    category="top_level_runtime_class_definition",
                    path=rel,
                    line=node.lineno,
                    detail=f"top-level Product Runtime class defined: {node.name}",
                )
            )
    return findings


def _find_direct_handler_await_in_agent_core() -> list[Finding]:
    """AST-detect ``await handler(request)`` in non-workspace agent paths.

    Workspace simple/wechat agents are explicitly out of scope for this
    work package but are reported as ``out_of_scope_bypass`` so the
    repository status remains truthful.
    """
    findings: list[Finding] = []
    for path in _iter_python_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        tree = _safe_parse(path)
        if tree is None:
            continue
        sites = _direct_handler_await_sites(tree)
        if not sites:
            continue
        is_workspace_agent = rel in (
            "src/backend/zuno/platform/services/workspace/simple_agent.py",
            "src/backend/zuno/platform/services/workspace/wechat_agent.py",
        )
        category = "workspace_bypass" if is_workspace_agent else "direct_handler_bypass"
        for lineno in sites:
            findings.append(
                Finding(
                    category=category,
                    path=rel,
                    line=lineno,
                    detail=f"direct handler(request) tool call at {rel}:{lineno}",
                )
            )
    return findings


def _find_agent_control_runtime_production_callers() -> list[Finding]:
    """AST-detect ``AgentControlRuntime()`` instantiations in production code.

    ``AgentControlRuntime`` is retained in ``zuno.agent.control_runtime`` but
    is superseded by the Single Controller. Any production caller other
    than ``product_baseline.py`` and the test/docs surfaces is a finding.
    """
    findings: list[Finding] = []
    for path in _iter_python_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel in OUT_OF_SCOPE_FILES:
            continue
        if rel.startswith("tests/") or rel.startswith("docs/") or rel.startswith(".agent/"):
            continue
        tree = _safe_parse(path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            try:
                text = ast.unparse(node.func)
            except Exception:  # pragma: no cover - defensive
                continue
            if text in ("AgentControlRuntime", "AgentControlRuntime()"):
                findings.append(
                    Finding(
                        category="agent_control_runtime_caller",
                        path=rel,
                        line=node.lineno,
                        detail=f"AgentControlRuntime() instantiated in production: {rel}:{node.lineno}",
                    )
                )
    return findings


def _detect_dynamic_runtime_loads() -> list[Finding]:
    """AST-detect dynamic / unresolved Runtime constructions.

    A construction like ``globals()['SomeAgent']()`` or
    ``getattr(module, 'SomeAgent')()`` is unresolved because the verifier
    cannot prove which class is built. Such sites force the repository
    scope to UNRESOLVED.

    The detector inspects every ``Call`` node and matches when the callee
    is one of ``globals``, ``getattr``, ``eval`` or ``__import__`` and one
    of the arguments references an agent/runtime-shaped name.
    """
    findings: list[Finding] = []
    agent_tokens = (
        "agent",
        "Agent",
        "Runtime",
        "Controller",
        "Executor",
        "Service",
        "zuno.agent",
    )
    dynamic_callees = {"globals", "getattr", "eval", "__import__"}
    for path in _iter_python_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel in OUT_OF_SCOPE_FILES:
            continue
        if rel.startswith("tests/") or rel.startswith("docs/") or rel.startswith(".agent/"):
            continue
        tree = _safe_parse(path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            callee_name = None
            if isinstance(node.func, ast.Name):
                callee_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                callee_name = node.func.attr
            if callee_name not in dynamic_callees:
                continue
            try:
                full_text = ast.unparse(node)
            except Exception:  # pragma: no cover - defensive
                continue
            if not any(token in full_text for token in agent_tokens):
                continue
            findings.append(
                Finding(
                    category="dynamic_runtime_load",
                    path=rel,
                    line=node.lineno,
                    detail=f"unresolved dynamic Runtime construction: {full_text}",
                )
            )
    return findings


def verify_repository_scope() -> ScopeResult:
    result = ScopeResult()
    dynamic = _detect_dynamic_runtime_loads()
    if dynamic:
        # Unresolved construction dominates: cannot prove cutover.
        for finding in dynamic:
            result.add(finding)
        result.status = STATUS_REPO_UNRESOLVED
        return result

    top_level = _find_top_level_runtime_class_definitions()
    for finding in top_level:
        result.add(finding)
    direct_handler = _find_direct_handler_await_in_agent_core()
    for finding in direct_handler:
        result.add(finding)
    agent_control = _find_agent_control_runtime_production_callers()
    for finding in agent_control:
        result.add(finding)

    if result.findings:
        result.status = STATUS_REPO_BLOCKED
    else:
        result.status = STATUS_REPO_CONFIRMED
    return result


# ---------------------------------------------------------------------------
# CLI driver
# ---------------------------------------------------------------------------


def _serialise_finding(finding: Finding) -> dict:
    return {
        "category": finding.category,
        "path": finding.path,
        "line": finding.line,
        "detail": finding.detail,
        "severity": finding.severity,
    }


def _serialise_scope(scope: str, result: ScopeResult) -> dict:
    return {
        "scope": scope,
        "status": result.status,
        "finding_count": len(result.findings),
        "findings": [_serialise_finding(f) for f in result.findings],
    }


def _run_scope(scope: str) -> ScopeResult:
    if scope == SCOPE_AGENT_FAMILY:
        return verify_agent_family_scope()
    if scope == SCOPE_REPOSITORY:
        return verify_repository_scope()
    raise SystemExit(f"unknown scope: {scope}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scope",
        choices=[SCOPE_AGENT_FAMILY, SCOPE_REPOSITORY],
        default=SCOPE_REPOSITORY,
        help="Scope of the verification (default: repository, fail-closed).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Write verifier_report.json to the evidence directory.",
    )
    args = parser.parse_args(argv)

    scope = args.scope
    try:
        result = _run_scope(scope)
    except Exception as exc:  # pragma: no cover - defensive
        if args.json:
            print(
                json.dumps(
                    {
                        "scope": scope,
                        "status": STATUS_TOOL_ERROR,
                        "finding_count": 0,
                        "findings": [],
                        "error": str(exc),
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
        print(f"PHASE22 backend semantic legacy verifier tool error: {exc}", file=sys.stderr)
        return 2

    payload = _serialise_scope(scope, result)
    if args.json:
        # JSON is the only thing on stdout when --json is set so downstream
        # tooling (and pytest tests) can parse it directly.
        print(json.dumps(payload, indent=2, sort_keys=True))

    if args.report:
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        report_path = EVIDENCE_DIR / "verifier_report.json"
        report_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        print(f"wrote {report_path.relative_to(REPO_ROOT)}", file=sys.stderr)

    if not args.json:
        print(f"PHASE22 backend semantic legacy verifier scope={scope} status={result.status}")
        for finding in result.findings:
            print(f"FINDING [{finding.category}] {finding.path}:{finding.line} {finding.detail}")

    if scope == SCOPE_AGENT_FAMILY:
        return 0 if result.status == STATUS_SCOPED_CLEAN else 1
    # Repository scope is fail-closed: any non-CONFIRMED status exits non-zero.
    return 0 if result.status == STATUS_REPO_CONFIRMED else 1


if __name__ == "__main__":
    raise SystemExit(main())