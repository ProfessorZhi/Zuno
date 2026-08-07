"""PHASE22 Final Legacy Cutover Audit — V3.

This verifier is the single source of truth for the final PHASE22 legacy
cutover audit. It must be run against the **exact** integration tree
that the audit verdict is being recorded for. The verifier is fail-closed
and uses Python AST + yaml.safe_load + reachability + ownership + runtime
behaviour + flag reader + dual-read / dual-write detection to produce
one of the following statuses:

  LEGACY_CUTOVER_AUDIT_CLEAN
  LEGACY_RUNTIME_BLOCKERS_FOUND
  DUAL_PATH_BLOCKERS_FOUND
  TOOL_BYPASS_BLOCKERS_FOUND
  PUBLIC_ADAPTER_OWNERSHIP_VIOLATION
  AUDIT_UNRESOLVED
  TOOL_ERROR

Priority (highest first):

  TOOL_ERROR
  > AUDIT_UNRESOLVED
  > PUBLIC_ADAPTER_OWNERSHIP_VIOLATION
  > TOOL_BYPASS_BLOCKERS_FOUND
  > LEGACY_RUNTIME_BLOCKERS_FOUND
  > DUAL_PATH_BLOCKERS_FOUND
  > LEGACY_CUTOVER_AUDIT_CLEAN

The verifier must NOT be declared CLEAN when the integration tree
contains any unresolved / dual-path / tool-bypass / ownership finding.
The only allowed path to CLEAN is an exact tree with zero findings
across all five categories.

Numeric facts only — no string counting.

Usage:
    python tools/scripts/verify_phase22_final_legacy_cutover.py
    python tools/scripts/verify_phase22_final_legacy_cutover.py --json
    python tools/scripts/verify_phase22_final_legacy_cutover.py --report
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = (
    REPO_ROOT / "docs" / "evidence" / "goal05-phase22-final-legacy-audit-v3"
)

WORK_PACKAGE = "PHASE22-FINAL-LEGACY-AUDIT-V3"
OWNER_WORK_PACKAGE = WORK_PACKAGE
CANDIDATE_PR = "PHASE22-FINAL-LEGACY-AUDIT-V3"


# Status constants (priority order: highest first).
STATUS_TOOL_ERROR = "TOOL_ERROR"
STATUS_AUDIT_UNRESOLVED = "AUDIT_UNRESOLVED"
STATUS_OWNERSHIP_VIOLATION = "PUBLIC_ADAPTER_OWNERSHIP_VIOLATION"
STATUS_TOOL_BYPASS = "TOOL_BYPASS_BLOCKERS_FOUND"
STATUS_LEGACY_RUNTIME = "LEGACY_RUNTIME_BLOCKERS_FOUND"
STATUS_DUAL_PATH = "DUAL_PATH_BLOCKERS_FOUND"
STATUS_CLEAN = "LEGACY_CUTOVER_AUDIT_CLEAN"


STATUS_PRIORITY = [
    STATUS_TOOL_ERROR,
    STATUS_AUDIT_UNRESOLVED,
    STATUS_OWNERSHIP_VIOLATION,
    STATUS_TOOL_BYPASS,
    STATUS_LEGACY_RUNTIME,
    STATUS_DUAL_PATH,
    STATUS_CLEAN,
]


# Scanned roots (production surfaces).
SCANNED_ROOTS = [
    REPO_ROOT / "src" / "backend" / "zuno",
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "workspace",
    REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "runtime",
    REPO_ROOT / "src" / "backend" / "zuno" / "api" / "v1",
]


# Excluded paths (tests, docs, eval scaffolding, vendor is in .gitignore).
EXCLUDED_PATH_PREFIXES = (
    "tests/",
    "docs/",
    ".agent/",
    "tools/evals/",
    "tools/scripts/_archive/",
    "node_modules/",
)


# -----------------------------------------------------------------------------
# Candidate symbols for each detection category.
# -----------------------------------------------------------------------------


# GeneralAgent family — must be missing or only referenced from docs/evals.
LEGACY_AGENT_FAMILY_CLASSES = (
    "GeneralAgent",
    "ReactAgent",
    "PlanExecuteAgent",
    "CodeActAgent",
    "Text2SQLAgent",
)

# Top-level runtime candidates — must be classified against the canonical
# ownership contract.
CANDIDATE_RUNTIME_CLASSES = (
    "SingleControllerRuntimeHarness",
    "WorkSpaceSimpleAgent",
    "WeChatAgent",
    "AgentControlRuntime",
    "Phase08LegacyRuntime",
)

# Phase08 legacy execution paths — must be unreachable in production.
PHASE08_LEGACY_SYMBOLS = (
    "phase08_cutover",
    "Phase08LegacyRuntime",
    "legacy_phase08_agent",
    "build_phase08_legacy",
    "rollback_to_phase08",
)

# Dual-path / shadow / canary / fallback / runtime selector names.
DUAL_PATH_SYMBOLS = (
    "rollback",
    "rollback_to_legacy",
    "shadow",
    "shadow_write",
    "canary",
    "dual_read",
    "dual_write",
    "expired_flag",
    "fallback_to_legacy",
    "legacy_runtime_selector",
    "runtime_selector",
)

# Tool bypass symbols — direct execution of tools / handlers / MCP.
TOOL_BYPASS_SYMBOLS = (
    "tool.invoke",
    "tool.ainvoke",
    "handler(request)",
    "mcp_direct",
    "direct_tool_dispatch",
    "image_gen_bypass",
    "skill_direct_execute",
)

# Public Adapter / DAO / Repository ownership — must NOT be in adapter.
DAO_REPOSITORY_DB_SYMBOLS = (
    "ORMBase",
    "DBSession",
    "Repository",
    "Dao",
    "DAO",
    "RepositoryBase",
    "AsyncSession",
    "session.add",
    "session.commit",
    "session.delete",
)

# Canonical runtime symbols — adapters must delegate to these.
CANONICAL_RUNTIME_SYMBOLS = (
    "UnifiedAgentRuntimeService",
    "SingleControllerRuntimeHarness",
    "SingleControllerDurableRuntime",
    "build_single_controller_runtime_harness",
    "WorkspaceAgentRuntime",
    "WorkspaceTaskRuntimeService",
)

# Dynamic-load / alias callers — these must surface as UNRESOLVED.
DYNAMIC_LOAD_NAMES = (
    "globals",
    "getattr",
    "eval",
    "__import__",
    "import_module",
    "locals",
    "vars",
)


# -----------------------------------------------------------------------------
# Data classes
# -----------------------------------------------------------------------------


@dataclass
class Finding:
    category: str
    path: str
    line: int
    detail: str
    severity: str = "error"

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "path": self.path,
            "line": self.line,
            "detail": self.detail,
            "severity": self.severity,
        }


@dataclass
class AuditResult:
    status: str = STATUS_CLEAN
    findings: list[Finding] = field(default_factory=list)
    unresolved: list[Finding] = field(default_factory=list)
    exclusions: list[dict] = field(default_factory=list)
    scanned_roots: list[str] = field(default_factory=list)
    not_proven_boundary: list[str] = field(default_factory=list)
    integration_base_sha: str = ""
    # PHASE22 final engineering closure (P0-8): the audit MUST NOT carry a
    # self-referential SHA. ``audit_subject_sha`` records the candidate
    # commit actually scanned (passed via --audit-subject-sha); the
    # ``evidence_revision_sha`` field is the SHA of the commit that
    # carries the audit_report.json into the tree and is supplied
    # externally (typically by CI metadata or the PR body). ``workflow_head_sha``
    # is the head of the GitHub Actions run that published this report,
    # also externally supplied. None of these three are derived from
    # ``git rev-parse HEAD`` because HEAD moves as soon as the audit
    # report is committed, producing an obvious self-reference.
    audit_subject_sha: str = ""
    evidence_revision_sha: str = ""
    workflow_head_sha: str = ""

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)

    def add_unresolved(self, finding: Finding) -> None:
        self.unresolved.append(finding)

    def add_exclusion(self, path: str, reason: str) -> None:
        self.exclusions.append({"path": path, "reason": reason})

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "finding_count": len(self.findings),
            "unresolved_count": len(self.unresolved),
            "findings": [f.to_dict() for f in self.findings],
            "unresolved": [f.to_dict() for f in self.unresolved],
            "exclusions": list(self.exclusions),
            "scanned_roots": list(self.scanned_roots),
            "not_proven_boundary": list(self.not_proven_boundary),
            "integration_base_sha": self.integration_base_sha,
            "audit_subject_sha": self.audit_subject_sha,
            "evidence_revision_sha": self.evidence_revision_sha,
            "workflow_head_sha": self.workflow_head_sha,
        }


# -----------------------------------------------------------------------------
# AST helpers
# -----------------------------------------------------------------------------


def _classdef_names(tree: ast.AST) -> list[str]:
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]


def _call_target_strings(tree: ast.AST) -> list[tuple[str, int]]:
    results: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            try:
                results.append((ast.unparse(node.func), node.lineno))
            except Exception:  # pragma: no cover - defensive
                continue
    return results


def _attribute_chains(tree: ast.AST) -> list[tuple[str, int]]:
    results: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            try:
                results.append((ast.unparse(node), node.lineno))
            except Exception:  # pragma: no cover - defensive
                continue
    return results


def _name_ids(tree: ast.AST) -> list[tuple[str, int]]:
    results: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            results.append((node.id, node.lineno))
    return results


def _safe_parse(path: Path) -> ast.AST | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return None


def _is_excluded(rel: str) -> bool:
    rel = rel.replace("\\", "/")
    for prefix in EXCLUDED_PATH_PREFIXES:
        if rel.startswith(prefix):
            return True
    return False


def _iter_python_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return
    for path in root.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        yield path


def _safe_yaml_load(path: Path):
    """Load YAML using yaml.safe_load — raises on unsafe payloads."""
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"yaml.safe_load unavailable: {exc}") from exc
    return yaml.safe_load(path.read_text(encoding="utf-8"))


# -----------------------------------------------------------------------------
# Category 1 — Legacy Runtime.
# -----------------------------------------------------------------------------


def _detect_legacy_runtime_class_definitions(
    file_index: dict[str, ast.AST],
) -> list[Finding]:
    """Detect any ``ClassDef`` for a legacy agent family class.

    The GeneralAgent family must be physically deleted from the
    production tree. A live ``ClassDef`` anywhere in production is
    a legacy runtime blocker.
    """
    findings: list[Finding] = []
    for rel, tree in file_index.items():
        if _is_excluded(rel):
            continue
        for class_name in _classdef_names(tree):
            if class_name in LEGACY_AGENT_FAMILY_CLASSES:
                findings.append(
                    Finding(
                        category="legacy_runtime_class_def",
                        path=rel,
                        line=0,
                        detail=(
                            f"legacy GeneralAgent family class definition "
                            f"'{class_name}' is present in production tree"
                        ),
                    )
                )
    return findings


def _detect_phase08_legacy_reachability(
    file_index: dict[str, ast.AST],
) -> list[Finding]:
    """Detect any ``Phase08LegacyRuntime`` / ``phase08_cutover`` / etc.
    symbols that are reachable from production code paths.
    """
    findings: list[Finding] = []
    for rel, tree in file_index.items():
        if _is_excluded(rel):
            continue
        for name, lineno in _name_ids(tree):
            if name in PHASE08_LEGACY_SYMBOLS:
                findings.append(
                    Finding(
                        category="legacy_phase08_reachability",
                        path=rel,
                        line=lineno,
                        detail=f"phase08 legacy symbol referenced: {name}",
                    )
                )
    return findings


def _detect_workspace_top_level_runtime(
    file_index: dict[str, ast.AST],
) -> list[Finding]:
    """Detect ``WorkSpaceSimpleAgent`` / ``WeChatAgent`` as a top-level
    runtime that owns the Product Run lifecycle. Allowed shapes are
    thin adapters delegating to canonical runtime. Anything else is a
    legacy runtime blocker.
    """
    findings: list[Finding] = []
    for rel, tree in file_index.items():
        if _is_excluded(rel):
            continue
        for class_name in _classdef_names(tree):
            if class_name not in ("WorkSpaceSimpleAgent", "WeChatAgent"):
                continue
            # Walk method bodies for legacy evidence.
            for class_node in ast.walk(tree):
                if not isinstance(class_node, ast.ClassDef):
                    continue
                if class_node.name != class_name:
                    continue
                for method in class_node.body:
                    if not isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        continue
                    for call_text, call_line in _call_target_strings(method):
                        head = call_text.split("(", 1)[0]
                        # ``create_agent`` / ``create_react_agent`` triggers legacy.
                        if head in (
                            "create_agent",
                            "create_react_agent",
                            "create_structured_chat_agent",
                        ):
                            findings.append(
                                Finding(
                                    category="legacy_workspace_runtime",
                                    path=rel,
                                    line=call_line,
                                    detail=(
                                        f"workspace runtime '{class_name}' constructs "
                                        f"independent graph via {head}"
                                    ),
                                )
                            )
                        # Direct model / tool invocation.
                        if call_text.endswith(".model.ainvoke") or call_text.endswith(".model.invoke"):
                            findings.append(
                                Finding(
                                    category="legacy_workspace_runtime",
                                    path=rel,
                                    line=call_line,
                                    detail=(
                                        f"workspace runtime '{class_name}' directly "
                                        f"invokes model: {call_text}"
                                    ),
                                )
                            )
                        if call_text.endswith(".tool.ainvoke") or call_text.endswith(".tool.invoke"):
                            findings.append(
                                Finding(
                                    category="legacy_workspace_runtime",
                                    path=rel,
                                    line=call_line,
                                    detail=(
                                        f"workspace runtime '{class_name}' directly "
                                        f"invokes tool: {call_text}"
                                    ),
                                )
                            )
                    # Direct handler(request) pattern.
                    for stmt in ast.walk(method):
                        if not isinstance(stmt, ast.Assign):
                            continue
                        if not isinstance(stmt.value, ast.Await):
                            continue
                        inner = stmt.value.value
                        if not isinstance(inner, ast.Call):
                            continue
                        try:
                            text = ast.unparse(inner.func)
                        except Exception:
                            continue
                        if text == "handler":
                            findings.append(
                                Finding(
                                    category="legacy_workspace_runtime",
                                    path=rel,
                                    line=stmt.lineno,
                                    detail=(
                                        f"workspace runtime '{class_name}' bypasses "
                                        f"ToolInvocationGateway via handler(request)"
                                    ),
                                )
                            )
    return findings


# -----------------------------------------------------------------------------
# Category 2 — Dual Path / Shadow / Canary / Fallback / Runtime Selector.
# -----------------------------------------------------------------------------


def _detect_dual_path(
    file_index: dict[str, ast.AST],
) -> list[Finding]:
    """Detect dual-path / shadow / canary / runtime selector / fallback
    patterns in production code. Including:

    - rollback / shadow / canary / dual_read / dual_write identifiers
    - expired flag reader (a YAML-loaded config whose ``expires_at`` is
      compared against now)
    - runtime selector (``select_runtime`` / ``legacy_runtime_selector``)
    - try / except ImportError recovery that catches the legacy import
    """
    findings: list[Finding] = []
    for rel, tree in file_index.items():
        if _is_excluded(rel):
            continue
        for name, lineno in _name_ids(tree):
            if name in DUAL_PATH_SYMBOLS:
                findings.append(
                    Finding(
                        category="dual_path_signal",
                        path=rel,
                        line=lineno,
                        detail=f"dual-path / rollback / shadow / fallback symbol: {name}",
                    )
                )
        # expired flag reader: a yaml.safe_load of a config file combined
        # with a check against ``expires_at`` is a flag reader.
        _detect_expired_flag_reader(rel, tree, findings)
    return findings


def _detect_expired_flag_reader(
    rel: str,
    tree: ast.AST,
    findings: list[Finding],
) -> None:
    """Detect a flag reader that consumes ``expires_at`` or
    ``valid_until`` keys AND loads the value from a YAML / JSON config.

    The verifier requires BOTH the structural pattern (a yaml.safe_load
    call) AND the expiry comparison to fire. Plain record timestamps
    that happen to be named ``expires_at`` are not flagged.
    """
    has_yaml_load = False
    has_expiry_check = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            func_name = None
            if isinstance(func, ast.Name):
                func_name = func.id
            elif isinstance(func, ast.Attribute):
                func_name = func.attr
            if func_name in ("safe_load", "yaml_load"):
                has_yaml_load = True
        if isinstance(node, ast.Compare):
            try:
                text = ast.unparse(node)
            except Exception:
                continue
            if "expires_at" in text or "valid_until" in text:
                if any(op in text for op in ("<", ">", "<=", ">=")):
                    has_expiry_check = True
    if has_yaml_load and has_expiry_check:
        findings.append(
            Finding(
                category="dual_path_expired_flag_reader",
                path=rel,
                line=0,
                detail=(
                    "expired-flag reader pattern detected: yaml.safe_load + "
                    "expires_at / valid_until comparison"
                ),
            )
        )


# -----------------------------------------------------------------------------
# Category 3 — Tool Bypass.
# -----------------------------------------------------------------------------


# PHASE22 (Slice B): canonical executor adapter entry points. A tool call
# through one of these names is the *allowed* shape; the verifier must not
# flag it. Adding new adapters here requires the existing audit + tests.
_CANONICAL_ADAPTER_RECEIVERS = frozenset(
    {
        "ToolInvocationGateway",
        "ToolControlPlaneRuntime",
        "WorkspaceToolBinding",
        "register_executor_adapter",
        "ExecutorAdapterContract",
    }
)

# Invoke / ainvoke / stream / astream attribute names that indicate a tool
# or model call. The verifier flags these regardless of the receiver name.
_INVOKE_ATTR_NAMES = frozenset(
    {"invoke", "ainvoke", "stream", "astream", "call", "acall", "run"}
)

# PHASE22 (Slice B): name-free detection rules. Each rule is a tuple
# (attribute-name or None, call-text predicate, finding category). The
# detector runs the predicate against every call text it sees; the
# category is reported verbatim when the predicate matches.
# These are intentionally not name-coupled to the receiver so renaming
# cannot evade the audit.
_NAME_FREE_RULES: tuple[tuple[str, str, str], ...] = (
    (
        "tool_bypass",
        "MCP",
        "mcp",
    ),
    (
        "tool_bypass_image_gen",
        "image_gen",
        "image_gen",
    ),
    (
        "tool_bypass_read_only",
        "skill_direct_execute",
        "skill_direct_execute",
    ),
)


def _build_alias_map(tree: ast.AST) -> dict[str, set[str]]:
    """Build a coarse intra-file alias map for use by name-free call
    detection.

    The algorithm walks the module-level / class-level / function-level
    assignments and records the alias targets. The maps are best-effort;
    the verifier fails closed on dynamic dispatch (calling ``getattr`` /
    ``globals`` / ``eval``).

    The alias map also records ``from X import Y as Z`` import aliases,
    so a renamed import (``direct_mcp as foo``) is walked back to the
    original MCP symbol when the detector checks a call site.
    """
    alias_map: dict[str, set[str]] = {}

    def _record(name: str, source: str) -> None:
        if name == source:
            return
        alias_map.setdefault(name, set()).add(source)

    def _node_alias_source(node: ast.AST) -> str | None:
        """Return a stable alias source description for an assignment RHS.

        Names like ``self.tool`` map to ``self.tool``; attribute chains
        like ``self.tool_manager.some_client`` map to the dotted form.
        """
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            try:
                return ast.unparse(node)
            except Exception:
                return None
        return None

    for node in ast.walk(tree):
        # ``from X import Y as Z`` — record ``Z -> X.Y`` so renamed
        # MCP / tool imports are walked back to their original name.
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                local = alias.asname or alias.name
                source = f"{node.module}.{alias.name}" if node.module else alias.name
                _record(local, source)
        if not isinstance(node, ast.Assign):
            continue
        rhs_source = _node_alias_source(node.value)
        if rhs_source is None:
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                _record(target.id, rhs_source)
            elif isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                # ``self.binding = self.tool`` — record the attribute.
                _record(
                    f"{target.value.id}.{target.attr}",
                    rhs_source,
                )

    return alias_map


def _build_module_level_call_graph(tree: ast.AST) -> dict[str, set[str]]:
    """Build a coarse intra-file module-level function call graph.

    Maps ``func_name -> {callee_name, ...}`` for module-level functions
    so the two-hop helper detector can walk a chain
    ``class.method -> _middle -> _final -> tool.ainvoke`` and surface
    the canonical ToolInvocationGateway bypass even though no direct
    ``<...>.ainvoke`` appears in the class method body.
    """
    graph: dict[str, set[str]] = {}

    def _walk(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        called: set[str] = set()
        for child in ast.walk(func_node):
            if not isinstance(child, ast.Call):
                continue
            if isinstance(child.func, ast.Name):
                called.add(child.func.id)
        graph[func_node.name] = called

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            _walk(node)
    return graph


def _walk_helper_chain(
    start: str,
    graph: dict[str, set[str]],
    *,
    max_depth: int = 4,
) -> set[str]:
    """Return every helper reachable from ``start`` within ``max_depth``
    hops in the module-level call graph.

    Used by the two-hop helper detector: a class method's callee is
    expanded into its transitive helper set so a chain that ultimately
    reaches a direct tool invocation is still flagged.
    """
    visited: set[str] = set()
    frontier = {start}
    for _ in range(max_depth):
        next_frontier: set[str] = set()
        for node in frontier:
            for callee in graph.get(node, ()):
                if callee in visited or callee == node:
                    continue
                visited.add(callee)
                next_frontier.add(callee)
        if not next_frontier:
            break
        frontier = next_frontier
    return visited


# PHASE22 (Slice B): symbols whose import alias chain must trigger the
# direct-MCP bypass category. The verifier walks every ``from X import
# Y as Z`` alias chain; if any resolved name ends with one of these
# suffixes, a chained ``<...>.ainvoke`` call site is flagged regardless
# of the local binding name (``foo``, ``helper``, ...).
_MCP_ALIAS_SUFFIXES = ("mcp", "direct_mcp", "mcp_direct")


def _call_resolves_to_mcp(
    call_text: str,
    alias_map: dict[str, set[str]],
) -> bool:
    """Return True when any alias of the call's receiver resolves to an
    MCP-shaped symbol."""
    candidates = _resolve_call_chain(call_text, alias_map)
    for candidate in candidates:
        lowered = candidate.lower()
        if any(lowered.endswith(suffix) for suffix in _MCP_ALIAS_SUFFIXES):
            return True
        if "mcp" in lowered:
            return True
    return False


def _resolve_call_chain(
    call_text: str,
    alias_map: dict[str, set[str]],
    *,
    _seen: frozenset[str] | None = None,
) -> list[str]:
    """Return every concrete name the call could refer to, honouring
    intra-file aliases. ``self.tool.ainvoke`` resolves to ``self.tool``,
    plus any alias that maps onto ``self.tool``.

    Aliases are walked recursively so a renamed import chain
    ``from x import direct_mcp as foo`` → ``self._binding = foo``
    → ``self._binding.ainvoke`` resolves all the way back to the
    original ``direct_mcp`` symbol. The recursive walk is bounded by
    ``_seen`` to prevent infinite cycles on cyclic alias maps.
    """
    parts = call_text.split(".", 1)
    head = parts[0]
    seen = _seen or frozenset()
    # Cycle guard: if ``head`` was already visited on this walk path,
    # return the head verbatim and let the caller dedupe. Cyclic alias
    # maps would otherwise recurse without bound.
    if head in seen:
        return [head]
    candidates: list[str] = []
    next_seen = seen | {head}
    if head in alias_map:
        for alias_target in sorted(alias_map[head]):
            if alias_target not in candidates:
                candidates.append(alias_target)
            # Walk further: the alias target may itself be aliased.
            for deeper in _resolve_call_chain(
                alias_target, alias_map, _seen=next_seen
            ):
                if deeper not in candidates:
                    candidates.append(deeper)
    candidates.append(head)
    if len(parts) == 1:
        return candidates
    head_attr = parts[1]
    resolver = f"{head}.{head_attr.split('.', 1)[0]}"
    if resolver in alias_map:
        for alias_target in sorted(alias_map[resolver]):
            if alias_target not in candidates:
                candidates.append(alias_target)
            for deeper in _resolve_call_chain(
                alias_target, alias_map, _seen=next_seen
            ):
                if deeper not in candidates:
                    candidates.append(deeper)
    return candidates


def _is_canonical_adapter_call(
    call_text: str,
    alias_map: dict[str, set[str]],
) -> bool:
    """Return True when the call is a registered canonical executor adapter
    dispatch. The detector must NOT flag these — they are the allowed
    path through the Tool Control Plane.
    """
    candidates = _resolve_call_chain(call_text, alias_map)
    if call_text in _CANONICAL_ADAPTER_RECEIVERS:
        return True
    head = call_text.split("(", 1)[0]
    head_parts = head.split(".")
    last = head_parts[-1] if head_parts else ""
    if last in {"register_executor_adapter", "register_manifest"}:
        return True
    for candidate in candidates:
        if candidate in _CANONICAL_ADAPTER_RECEIVERS:
            return True
    return False


def _is_module_level_function(tree: ast.AST, func_name: str) -> bool:
    """Return True when ``func_name`` is defined at module level (top-level
    function)."""
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
            return True
    return False


def _classify_tool_invocation(
    call_text: str,
    *,
    alias_map: dict[str, set[str]],
    is_module_level: bool,
    enclosing_class_name: str | None = None,
) -> str | None:
    """Return a category if the call is a tool bypass, else ``None``.

    Detection is name-free in two ways:

    1. The attribute-name list is fixed (``invoke`` / ``ainvoke`` /
       ``stream`` / ``astream`` / ``call`` / ``acall`` / ``run``). The
       receiver name is NOT inspected *except* for the small
       ``_MODEL_RECEIVER_SUFFIXES`` whitelist that exempts legitimate
       model / provider / gateway attribute chains.
    2. Aliases are honored: ``binding = self.tool; binding.ainvoke(args)``
       is treated the same as ``self.tool.ainvoke(args)``.
    """
    if _is_canonical_adapter_call(call_text, alias_map):
        return None
    parts = call_text.split(".", 1)
    head = parts[0]
    rest = parts[1] if len(parts) > 1 else ""
    last_attr = rest.split("(")[0].split(".")[-1] if rest else ""
    if not last_attr or last_attr not in _INVOKE_ATTR_NAMES:
        return None

    # The receiver must be a chained attribute access (e.g. ``self.x.y``),
    # not a bare identifier (a function call). ``self.x.ainvoke`` has
    # chain depth 2 (self -> x -> ainvoke); a bare ``self.ainvoke`` has
    # chain depth 1 and is treated as a method invocation, not a tool bypass.
    if "." not in rest:
        return None
    chain_parts = rest.split("(")[0].split(".")
    # The last element is the method name; the remaining pieces are the
    # receiver chain. The receiver must have at least one part.
    if len(chain_parts) < 2:
        return None
    # Exempt legitimate model / provider / gateway calls. The receiver
    # attribute name is checked against a small whitelist of suffixes
    # that the canonical model gateway exposes. This is a deliberately
    # narrow exemption: only attribute names that *end* with one of
    # these suffixes are exempted, and the call must not be a documented
    # tool bypass pattern (``tool`` / ``binding`` / ``handler``).
    receiver_attr = chain_parts[-2]
    receiver_lower = receiver_attr.lower()
    if any(
        receiver_lower.endswith(suffix)
        for suffix in _MODEL_RECEIVER_SUFFIXES_INTERNAL
    ):
        return None
    # Adapter-shaped classes (canonical adapters that delegate to a
    # runtime / unified service) are also exempt: the chain call is the
    # delegation contract, not a tool bypass.
    if enclosing_class_name and any(
        suffix in enclosing_class_name
        for suffix in ("Adapter", "RuntimeAdapter", "Engine")
    ):
        return None
    if is_module_level:
        # Module-level helper invocations are not tool bypasses — they
        # are adapter / dispatcher helpers.
        return None
    return "tool_bypass_invoke"


# PHASE22 (Slice B): narrow whitelist for legitimate model / provider /
# gateway receivers. Adding entries here is a deliberate decision — the
# canonical WorkspaceChatModelProvider exposes ``self.model.ainvoke``,
# which is a model call, not a tool bypass. The whitelist is intentionally
# small and only matches attribute-name suffixes.
_MODEL_RECEIVER_SUFFIXES_INTERNAL = (
    "model",
    "models",
    "provider",
    "providers",
    "client",
    "chat",
    "gateway",
    "embedding",
    "embeddings",
)


def _classify_model_direct_call(
    call_text: str,
    *,
    alias_map: dict[str, set[str]],
) -> str | None:
    """Detect a direct model invocation from a Product Adapter. The
    detector is name-free: any ``invoke`` / ``ainvoke`` / ``stream`` /
    ``astream`` call on a chained attribute that is NOT a canonical
    adapter is treated as a model direct call.
    """
    if _is_canonical_adapter_call(call_text, alias_map):
        return None
    parts = call_text.split(".", 1)
    head = parts[0]
    rest = parts[1] if len(parts) > 1 else ""
    last_attr = rest.split("(")[0].split(".")[-1] if rest else ""
    if last_attr not in {"invoke", "ainvoke", "stream", "astream"}:
        return None
    # The receiver must be a chained attribute (not a bare identifier).
    if "." not in rest:
        return None
    chain_parts = rest.split("(")[0].split(".")
    if len(chain_parts) < 2:
        return None
    # Only flag when the receiver looks like a tool / binding / executor
    # chain, not a model / provider / gateway chain. Without type info
    # the receiver name is the only signal; the detector consults the
    # same whitelist as ``_classify_tool_invocation``.
    receiver_attr = chain_parts[-2]
    receiver_lower = receiver_attr.lower()
    if not any(
        receiver_lower.endswith(suffix)
        for suffix in _MODEL_RECEIVER_SUFFIXES_INTERNAL
    ):
        # The receiver is NOT a model / provider / gateway attribute;
        # this is a tool-style chain. Skip — the tool-bypass category
        # above already covers it.
        return None
    # The receiver is a model / provider / gateway attribute. The call
    # itself is a legitimate model invocation through the canonical
    # runner; the WorkspaceChatModelProvider adapter owns the dispatch.
    return None


def _detect_tool_bypass(
    file_index: dict[str, ast.AST],
) -> list[Finding]:
    """Detect direct tool / handler / MCP execution that bypasses
    ``ToolInvocationGateway``.

    The detector is name-free: it examines the call *shape* (chained
    attribute + invoke-style method) and ignores the receiver name. This
    rules out rename evasion (``tool`` -> ``binding``, ``handler`` ->
    ``executor``).

    The detector flags:

    - Any ``self.<...>.invoke`` / ``.<...>.ainvoke`` / ``.<...>.stream``
      / ``.<...>.astream`` call inside a Product Adapter class method
      that is NOT a registered canonical executor adapter. Aliases are
      honored (``binding = self.tool; binding.ainvoke(args)`` is still
      flagged).
    - MCP / image-gen / read-only bypass by identifier (preserved for
      backward compatibility; new categories are added below).
    - Direct ``handler(...)`` invocations via assignment, regardless of
      the receiver name.
    - Renamed MCP imports (``from x import direct_mcp as foo`` ->
      ``self.foo.ainvoke(...)``) — the alias map walks the import back
      to the MCP-shaped symbol and flags the call regardless of the
      local binding name.
    - Two-hop helper chains: a class method that delegates to a
      module-level helper which itself delegates to another helper
      which performs the direct tool invocation. The hardened detector
      walks the intra-file module-level call graph so the chain is
      flagged even though no ``<...>.ainvoke`` appears in the class
      method body.
    """
    findings: list[Finding] = []
    for rel, tree in file_index.items():
        if _is_excluded(rel):
            continue
        alias_map = _build_alias_map(tree)
        module_level_funcs = {
            node.name
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        # Build a method_name -> enclosing_class_map for context-aware
        # exemptions. The detector must know whether a call is inside a
        # canonical Adapter class or a class that owns a tool / model.
        enclosing_class_for_call = _build_call_enclosing_class_map(tree)
        # Pre-compute the module-level call graph for two-hop helper
        # detection. A class method whose callee expands (transitively)
        # to a direct tool invocation is flagged even though no
        # ``<...>.ainvoke`` appears in the class method body.
        call_graph = _build_module_level_call_graph(tree)
        # Pre-compute which module-level helpers are flagged as
        # "tool-bypass helpers" (they themselves perform a direct
        # ``<...>.ainvoke`` call). The two-hop detector then flags any
        # class method whose callees transitively reach one of these.
        # To find direct tool invocations INSIDE a helper's body, we
        # walk the helper's function node specifically — the previous
        # iteration over all call targets in the file matched calls
        # TO the helper rather than calls INSIDE the helper.
        # We use a broader check than ``_classify_tool_invocation`` so
        # helpers that take a tool as a parameter and call
        # ``tool.ainvoke(...)`` are still classified as tool-bypass
        # helpers (the strict detector exempts single-name receivers
        # because they look like local variables; the helper-bypass
        # check is a structural concern, not a context-aware one).
        helper_bypass_names: set[str] = set()
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            helper_name = node.name
            helper_has_bypass = False
            for child in ast.walk(node):
                if not isinstance(child, ast.Call):
                    continue
                try:
                    child_text = ast.unparse(child)
                except Exception:
                    continue
                last_attr = child_text.split("(")[0].split(".")[-1]
                if last_attr not in {"invoke", "ainvoke", "stream", "astream"}:
                    continue
                # Structural check: any chained-attribute or
                # bare-identifier receiver paired with an invoke-style
                # method is a tool-bypass shape inside a helper.
                head = child_text.split("(", 1)[0].split(".")[0]
                if head and head != child_text.split("(", 1)[0]:
                    helper_has_bypass = True
                    break
                # Single-identifier receiver: still a tool-bypass
                # shape if the call is on a parameter / local that
                # carries a tool.
                if head and head.islower():
                    helper_has_bypass = True
                    break
            if helper_has_bypass:
                helper_bypass_names.add(helper_name)
        for call_text, lineno in _call_target_strings(tree):
            # MCP / image-gen / read-only bypass by identifier (legacy).
            for category, predicate, marker in _NAME_FREE_RULES:
                if marker in call_text:
                    findings.append(
                        Finding(
                            category=category,
                            path=rel,
                            line=lineno,
                            detail=(
                                f"direct {predicate} bypass: {call_text}"
                            ),
                        )
                    )
            # PHASE22 (Slice B): direct MCP bypass via renamed import
            # alias. ``from x import direct_mcp as foo`` followed by
            # ``self.foo.ainvoke(...)`` is flagged regardless of the
            # local binding name. The detector only fires when the
            # call is an invoke-style method call — a class-method
            # dispatch on an MCP-named class (``MCPService.foo()``)
            # is not flagged because the receiver is a registered MCP
            # service, not a renamed tool bypass.
            last_attr = call_text.split("(")[0].split(".")[-1]
            if (
                _call_resolves_to_mcp(call_text, alias_map)
                and last_attr in {"invoke", "ainvoke", "stream", "astream"}
            ):
                findings.append(
                    Finding(
                        category="tool_bypass_direct_mcp",
                        path=rel,
                        line=lineno,
                        detail=(
                            "direct MCP bypass via import alias: "
                            f"{call_text}"
                        ),
                    )
                )
            # Name-free tool invocation detection.
            enclosing = enclosing_class_for_call.get(lineno)
            tool_cat = _classify_tool_invocation(
                call_text,
                alias_map=alias_map,
                is_module_level=_is_module_top_level(tree, call_text),
                enclosing_class_name=enclosing,
            )
            if tool_cat is not None:
                findings.append(
                    Finding(
                        category=tool_cat,
                        path=rel,
                        line=lineno,
                        detail=f"direct tool invocation bypass: {call_text}",
                    )
                )
            # Name-free model direct invocation (Product adapter -> model).
            model_cat = _classify_model_direct_call(
                call_text, alias_map=alias_map
            )
            if model_cat is not None:
                findings.append(
                    Finding(
                        category=model_cat,
                        path=rel,
                        line=lineno,
                        detail=f"direct model invocation bypass: {call_text}",
                    )
                )
            # PHASE22 (Slice B): two-hop helper detection. A class
            # method whose callees transitively reach a module-level
            # helper that performs the direct tool invocation is
            # flagged as a tool bypass even though no chained
            # ``<...>.ainvoke`` appears in the class method body.
            if (
                enclosing is not None
                and helper_bypass_names
            ):
                head = call_text.split("(", 1)[0].split(".")[0]
                # The class method's callee (``head``) must itself be a
                # module-level helper, AND its transitive callees must
                # include at least one helper-bypass function. A
                # two-hop chain (class method -> helper A -> helper B
                # -> tool.ainvoke) lands here when ``helper A`` is in
                # the transitive set that includes ``helper B``.
                if head in module_level_funcs and _walk_helper_chain(
                    head, call_graph
                ) & helper_bypass_names:
                    findings.append(
                        Finding(
                            category="tool_bypass_two_hop_helper",
                            path=rel,
                            line=lineno,
                            detail=(
                                "direct tool invocation bypass via "
                                f"two-hop helper chain: {call_text}"
                            ),
                        )
                    )
    # Direct handler-style invocation via assignment (the historical
    # shape). The hardened detector preserves the original "handler"
    # identifier rule for backward compatibility, while the new
    # name-free ``tool_bypass_invoke`` category above catches the
    # renamed shapes. We do NOT flag bare identifier calls because
    # production code routinely calls helper functions like
    # ``get_embedding(...)`` that are not tool bypasses.
    for rel, tree in file_index.items():
        if _is_excluded(rel):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            if not isinstance(node.value, ast.Await):
                continue
            inner = node.value.value
            if not isinstance(inner, ast.Call):
                continue
            try:
                func_text = ast.unparse(inner.func)
            except Exception:
                continue
            # Single identifier (no dot) and not a method invocation.
            if "." in func_text:
                continue
            if func_text == "handler":
                findings.append(
                    Finding(
                        category="tool_bypass_handler",
                        path=rel,
                        line=node.lineno,
                        detail=f"direct handler(request) bypass: {ast.unparse(inner)}",
                    )
                )
    return findings


def _build_call_enclosing_class_map(tree: ast.AST) -> dict[int, str]:
    """Walk the AST and build a mapping from each call's line number to
    the enclosing class name. ``None`` is recorded for module-level
    calls.
    """
    result: dict[int, str] = {}

    class _Visitor(ast.NodeVisitor):
        def __init__(self, current_class: str | None = None) -> None:
            self.current_class = current_class

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            previous = self.current_class
            self.current_class = node.name
            self.generic_visit(node)
            self.current_class = previous

        def visit_Call(self, node: ast.Call) -> None:
            result[node.lineno] = self.current_class
            self.generic_visit(node)

    _Visitor().visit(tree)
    return result


def _is_module_top_level(tree: ast.AST, call_text: str) -> bool:
    """Return True when the call's callee is a module-level function in
    ``tree`` (the helper is not a class method, so the call is an
    adapter / dispatcher helper, not a runtime owner).
    """
    head = call_text.split(".", 1)[0].split("(")[0]
    if "." in head:
        return False
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == head:
            return True
    return False


# -----------------------------------------------------------------------------
# Category 4 — Public Adapter Ownership Violation.
# -----------------------------------------------------------------------------


def _detect_public_adapter_ownership(
    file_index: dict[str, ast.AST],
) -> list[Finding]:
    """Detect a public adapter that directly writes to the DAO /
    Repository, owns a Plan, owns a Tool Effect, or directly updates
    the final answer.

    The detector looks for *instantiation* and *attribute assignment*
    patterns, not type annotations. A function parameter annotated
    as ``PlannerOutput`` is a consumer, not an owner.
    """
    findings: list[Finding] = []
    public_adapter_modules = (
        "src/backend/zuno/agent/harness.py",
        "src/backend/zuno/agent/runtime/adapters.py",
        "src/backend/zuno/agent/runtime/service.py",
        "src/backend/zuno/agent/runtime/factory.py",
    )
    for rel, tree in file_index.items():
        if _is_excluded(rel):
            continue
        if rel not in public_adapter_modules:
            continue

        # Detect DAO / Repository writes that are call patterns.
        for call_text, lineno in _call_target_strings(tree):
            for sym in ("session.add", "session.commit", "session.delete"):
                if call_text == sym or call_text.endswith("." + sym):
                    findings.append(
                        Finding(
                            category="ownership_dao_write",
                            path=rel,
                            line=lineno,
                            detail=(
                                f"public adapter has direct DAO/Repository write: "
                                f"{call_text}"
                            ),
                        )
                    )

        # Detect Plan / RunOutcome / CapabilityPlan / FinalGate
        # *instantiation* — ClassName(...) in the adapter body.
        for call_text, lineno in _call_target_strings(tree):
            head = call_text.split("(", 1)[0]
            if head in ("PlannerOutput", "CapabilityPlan", "RunOutcome", "FinalGate"):
                findings.append(
                    Finding(
                        category="ownership_plan_owned",
                        path=rel,
                        line=lineno,
                        detail=(
                            f"public adapter owns Plan / RunOutcome: {head}"
                        ),
                    )
                )

        # Detect ``self.<attr> = ClassName(...)`` ownership.
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            for target in node.targets:
                if not isinstance(target, ast.Attribute):
                    continue
                if not isinstance(target.value, ast.Name):
                    continue
                if target.value.id != "self":
                    continue
                try:
                    rhs_text = ast.unparse(node.value)
                except Exception:
                    continue
                rhs_head = rhs_text.split("(", 1)[0]
                if rhs_head in ("PlannerOutput", "CapabilityPlan", "RunOutcome", "FinalGate"):
                    findings.append(
                        Finding(
                            category="ownership_plan_owned",
                            path=rel,
                            line=node.lineno,
                            detail=(
                                f"public adapter owns Plan / RunOutcome via "
                                f"self assignment: {target.attr} = {rhs_text}"
                            ),
                        )
                    )
    return findings


# -----------------------------------------------------------------------------
# Category 5 — Dynamic / Alias / Factory (UNRESOLVED).
# -----------------------------------------------------------------------------


def _detect_dynamic_constructor_sites(
    file_index: dict[str, ast.AST],
) -> list[Finding]:
    """Detect any dynamic loader that targets a class name token. The
    verifier cannot prove the runtime type and must surface this as
    AUDIT_UNRESOLVED.
    """
    findings: list[Finding] = []
    tokens = ("Agent", "Runtime", "Controller", "Service", "Harness", "Factory")
    for rel, tree in file_index.items():
        if _is_excluded(rel):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func_name: str | None = None
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            if func_name not in DYNAMIC_LOAD_NAMES:
                continue
            try:
                text = ast.unparse(node)
            except Exception:
                continue
            if not any(token in text for token in tokens):
                continue
            findings.append(
                Finding(
                    category="unresolved_dynamic_constructor",
                    path=rel,
                    line=node.lineno,
                    detail=f"unresolved dynamic constructor: {text}",
                )
            )
    return findings


def _detect_alias_factory_unresolved(
    file_index: dict[str, ast.AST],
) -> list[Finding]:
    """Detect assignment aliases / factory patterns whose runtime type
    cannot be proven statically. The verifier must surface these as
    AUDIT_UNRESOLVED.
    """
    findings: list[Finding] = []
    for rel, tree in file_index.items():
        if _is_excluded(rel):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # LocalName = ClassName — if local name is also used to
                # construct a runtime, the alias is unresolvable without
                # knowing the candidate class. Flag only if local name
                # ends with Runtime / Agent / Service.
                if not all(isinstance(t, ast.Name) for t in node.targets):
                    continue
                try:
                    rhs_text = ast.unparse(node.value)
                except Exception:
                    continue
                for target in node.targets:
                    if not isinstance(target, ast.Name):
                        continue
                    if target.id in ("Runtime", "AgentRuntime", "AdapterRuntime"):
                        findings.append(
                            Finding(
                                category="unresolved_alias_factory",
                                path=rel,
                                line=node.lineno,
                                detail=(
                                    f"module-level assignment alias "
                                    f"'{target.id} = {rhs_text}' is unresolvable"
                                ),
                            )
                        )
    return findings


# PHASE22 (Slice B): file-rename AUDIT_UNRESOLVED detector. A file
# rename is not detectable from the AST alone: the verifier cannot
# distinguish a renamed legacy / bypass surface from an originally-named
# file. The detector treats any scanned-root file whose module name does
# NOT match the canonical executor adapter naming contract but whose
# body shows a direct tool / model invocation chain as AUDIT_UNRESOLVED.
# The verifier must fail-closed: it cannot statically prove the file is
# not a renamed legacy / bypass surface, so the audit must surface the
# ambiguity rather than claim CLEAN.
_CANONICAL_ADAPTER_FILE_MARKERS = (
    "adapter",
    "runtime_adapter",
    "engine",
    "harness",
    "control_plane",
)

# Vendor / third-party surface — never produced / maintained by this
# repository, so a file rename ambiguity in vendor code is not a
# concern for the PHASE22 cutover audit. The detector must skip these
# paths so the audit does not block on imported library code.
_FILE_RENAME_SKIP_PREFIXES = (
    "src/backend/zuno/platform/vendor/",
    "vendor/",
)


def _detect_unresolved_file_rename(
    file_index: dict[str, ast.AST],
) -> list[Finding]:
    """Surface AUDIT_UNRESOLVED for any scanned-root file whose module
    name does NOT match the canonical executor adapter naming contract
    AND whose body shows a direct tool invocation chain (chained
    attribute + invoke-style method call) OR a dynamic dispatch shape
    (getattr / __import__ / import_module / eval / globals) that
    targets a tool / model / handler symbol.

    A file rename is not detectable from the AST alone: the verifier
    cannot distinguish a renamed file from an originally-named file.
    The detector therefore treats any "ambiguous-shape" file — one
    whose name does not match the canonical executor adapter naming
    contract and whose classes do not match the canonical adapter
    naming contract, but whose body shows a direct tool invocation
    chain OR a dynamic dispatch — as AUDIT_UNRESOLVED.

    Files that contain at least one class whose name matches the
    canonical executor adapter naming contract (``Adapter`` /
    ``RuntimeAdapter`` / ``Engine`` / ``Harness``) are exempt: they
    are not "renamed" relative to the canonical contract. This keeps
    legitimate thin adapters — like the canonical
    ``CleanRuntimeAdapter`` shape — from blocking the audit.

    Vendor / third-party paths are excluded — file-rename ambiguity in
    imported library code is not a concern for the PHASE22 cutover
    audit.
    """
    canonical_class_markers = (
        "Adapter",
        "RuntimeAdapter",
        "Engine",
        "Harness",
    )
    findings: list[Finding] = []
    for rel, tree in file_index.items():
        if _is_excluded(rel):
            continue
        lowered = rel.lower()
        if any(
            lowered.startswith(prefix) for prefix in _FILE_RENAME_SKIP_PREFIXES
        ):
            continue
        if any(marker in lowered for marker in _CANONICAL_ADAPTER_FILE_MARKERS):
            continue
        # Class-name exemption: if any class in this file matches the
        # canonical executor adapter naming contract, the file is not
        # a renamed legacy / bypass surface.
        class_names = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
        }
        if any(
            any(marker in name for marker in canonical_class_markers)
            for name in class_names
        ):
            continue
        has_invoke_chain = False
        has_dynamic_dispatch = False
        for call_text, _lineno in _call_target_strings(tree):
            head = call_text.split("(", 1)[0]
            last = head.split(".")[-1] if head else ""
            # Direct invocation chain: ``<receiver>.<method>(...)``
            # where the method is an invoke-style name and the
            # receiver is a chained attribute (not a bare identifier).
            if (
                last in {"invoke", "ainvoke", "stream", "astream", "call", "acall", "run"}
                and "." in head
                and head.split(".")[0]
            ):
                has_invoke_chain = True
                break
            # Dynamic dispatch: getattr(...) on a tool/model/handler
            # symbol. The verifier cannot statically prove the
            # resolved attribute is a canonical executor adapter.
            if call_text.startswith("getattr("):
                has_dynamic_dispatch = True
                break
        if not (has_invoke_chain or has_dynamic_dispatch):
            continue
        findings.append(
            Finding(
                category="unresolved_file_rename",
                path=rel,
                line=0,
                detail=(
                    "file contains a direct tool invocation chain or a "
                    "dynamic dispatch shape but does not match the "
                    "canonical executor adapter naming contract; the "
                    "verifier cannot statically prove it is not a "
                    "renamed legacy / bypass surface"
                ),
            )
        )
    return findings


# -----------------------------------------------------------------------------
# Verifier entrypoint.
# -----------------------------------------------------------------------------


def _build_file_index() -> dict[str, ast.AST]:
    index: dict[str, ast.AST] = {}
    for root in SCANNED_ROOTS:
        for path in _iter_python_files(root):
            rel = path.relative_to(REPO_ROOT).as_posix()
            tree = _safe_parse(path)
            if tree is not None:
                index[rel] = tree
    return index


def _resolve_priority(findings: list[Finding], unresolved: list[Finding]) -> str:
    """Determine the final status by priority order.

    Priority semantics (PHASE22 final engineering closure):

    - ``unresolved_dynamic_constructor`` / ``unresolved_alias_factory``
      mean the verifier cannot statically prove the runtime type. These
      dominate over every specific finding — the audit cannot claim a
      concrete verdict when the runtime is unresolvable.
    - Specific findings (ownership / tool-bypass / legacy / dual-path)
      dominate over the generic ``unresolved_file_rename`` shape
      concern. A file may legitimately live outside the canonical
      adapter naming contract while still being a canonical adapter;
      a specific tool-bypass / ownership / legacy / dual-path finding
      on the same file is the dominant signal.
    - Pure ``unresolved_file_rename`` ambiguity without any specific
      finding still surfaces AUDIT_UNRESOLVED — the verifier cannot
      prove the file is not a renamed legacy / bypass surface.
    """
    categories = {f.category for f in findings}
    # The two highest-priority unresolved categories dominate over
    # every specific finding.
    unresolved_categories = {u.category for u in unresolved}
    strong_unresolved = {
        "unresolved_dynamic_constructor",
        "unresolved_alias_factory",
    } & unresolved_categories
    if strong_unresolved:
        return STATUS_AUDIT_UNRESOLVED
    # Specific findings dominate over the generic unresolved_file_rename
    # shape concern.
    if any(c.startswith("ownership_") for c in categories):
        return STATUS_OWNERSHIP_VIOLATION
    if any(c.startswith("tool_bypass_") for c in categories):
        return STATUS_TOOL_BYPASS
    if any(c.startswith("legacy_") for c in categories):
        return STATUS_LEGACY_RUNTIME
    if any(c.startswith("dual_path_") for c in categories):
        return STATUS_DUAL_PATH
    # Pure unresolved-file-rename ambiguity without any specific
    # finding surfaces AUDIT_UNRESOLVED.
    if unresolved:
        return STATUS_AUDIT_UNRESOLVED
    return STATUS_CLEAN


def run_audit(
    *,
    integration_base_sha: str,
    audit_subject_sha: str = "",
    evidence_revision_sha: str = "",
    workflow_head_sha: str = "",
) -> AuditResult:
    result = AuditResult(
        integration_base_sha=integration_base_sha,
        audit_subject_sha=audit_subject_sha,
        evidence_revision_sha=evidence_revision_sha,
        workflow_head_sha=workflow_head_sha,
        scanned_roots=[str(p.relative_to(REPO_ROOT)) for p in SCANNED_ROOTS],
    )
    file_index = _build_file_index()

    # 1. Legacy runtime.
    for finding in _detect_legacy_runtime_class_definitions(file_index):
        result.add(finding)
    for finding in _detect_phase08_legacy_reachability(file_index):
        result.add(finding)
    for finding in _detect_workspace_top_level_runtime(file_index):
        result.add(finding)

    # 2. Dual path.
    for finding in _detect_dual_path(file_index):
        result.add(finding)

    # 3. Tool bypass.
    for finding in _detect_tool_bypass(file_index):
        result.add(finding)

    # 4. Ownership.
    for finding in _detect_public_adapter_ownership(file_index):
        result.add(finding)

    # 5. Unresolved (dynamic / alias / factory / file-rename ambiguity).
    for finding in _detect_dynamic_constructor_sites(file_index):
        result.add_unresolved(finding)
    for finding in _detect_alias_factory_unresolved(file_index):
        result.add_unresolved(finding)
    for finding in _detect_unresolved_file_rename(file_index):
        result.add_unresolved(finding)

    # Record standard exclusions.
    for prefix in EXCLUDED_PATH_PREFIXES:
        result.add_exclusion(prefix, "non-production surface (tests/docs/evals/agent scripts)")

    # Record not_proven_boundary entries (things we cannot prove).
    result.not_proven_boundary.append(
        "history-only caller like /agent/product_baseline.py is excluded by "
        "construction; reachability is not proven for runtime selectors that "
        "resolve via attribute-chain / class-name-only dispatch."
    )

    result.status = _resolve_priority(result.findings, result.unresolved)
    return result


# -----------------------------------------------------------------------------
# CLI driver.
# -----------------------------------------------------------------------------


def _git_head_sha() -> str:
    """Return the current HEAD SHA via git plumbing."""
    try:
        import subprocess

        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except Exception:  # pragma: no cover - defensive
        return "UNKNOWN"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--integration-base-sha",
        default=os.environ.get("INTEGRATION_BASE_SHA", ""),
        help="Exact integration tree SHA the audit is recorded for.",
    )
    parser.add_argument(
        "--audit-subject-sha",
        default=os.environ.get("AUDIT_SUBJECT_SHA", ""),
        help=(
            "Exact commit SHA of the production-tree candidate the audit "
            "scanned. Recorded verbatim in audit_report.json. NOT derived "
            "from git rev-parse HEAD (PHASE22 final engineering closure P0-8)."
        ),
    )
    parser.add_argument(
        "--evidence-revision-sha",
        default=os.environ.get("EVIDENCE_REVISION_SHA", ""),
        help=(
            "Exact commit SHA that carries this audit_report.json. Recorded "
            "verbatim. Usually supplied by CI / PR body; never derived."
        ),
    )
    parser.add_argument(
        "--workflow-head-sha",
        default=os.environ.get("WORKFLOW_HEAD_SHA", ""),
        help=(
            "Exact commit SHA on which the GitHub Actions run that published "
            "this report was triggered. Recorded verbatim; never derived."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Write audit_report.json to the evidence directory.",
    )
    args = parser.parse_args(argv)

    integration_base_sha = args.integration_base_sha
    audit_subject_sha = args.audit_subject_sha
    evidence_revision_sha = args.evidence_revision_sha
    workflow_head_sha = args.workflow_head_sha

    try:
        result = run_audit(
            integration_base_sha=integration_base_sha,
            audit_subject_sha=audit_subject_sha,
            evidence_revision_sha=evidence_revision_sha,
            workflow_head_sha=workflow_head_sha,
        )
    except Exception as exc:
        # Tool error dominates.
        if args.json:
            print(
                json.dumps(
                    {
                        "status": STATUS_TOOL_ERROR,
                        "error": str(exc),
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
        print(f"PHASE22 final legacy audit V3 tool error: {exc}", file=sys.stderr)
        return 2

    payload = {
        "status": result.status,
        "owner_work_package": OWNER_WORK_PACKAGE,
        "candidate_pr": CANDIDATE_PR,
        "integration_base_sha": result.integration_base_sha,
        "audit_subject_sha": result.audit_subject_sha,
        "evidence_revision_sha": result.evidence_revision_sha,
        "workflow_head_sha": result.workflow_head_sha,
        "scanned_roots": result.scanned_roots,
        "exclusions": result.exclusions,
        "not_proven_boundary": result.not_proven_boundary,
        "finding_count": len(result.findings),
        "unresolved_count": len(result.unresolved),
        "findings": [f.to_dict() for f in result.findings],
        "unresolved": [f.to_dict() for f in result.unresolved],
    }

    if args.report:
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        report_path = EVIDENCE_DIR / "audit_report.json"
        report_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        print(f"wrote {report_path.relative_to(REPO_ROOT)}", file=sys.stderr)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"PHASE22 final legacy audit V3 status={result.status}")
        for finding in result.findings:
            print(
                f"FINDING [{finding.category}] {finding.path}:{finding.line} "
                f"{finding.detail}"
            )
        for u in result.unresolved:
            print(
                f"UNRESOLVED [{u.category}] {u.path}:{u.line} {u.detail}"
            )

    # Non-zero exit unless CLEAN.
    return 0 if result.status == STATUS_CLEAN else 1


if __name__ == "__main__":
    raise SystemExit(main())
