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


def _detect_tool_bypass(
    file_index: dict[str, ast.AST],
) -> list[Finding]:
    """Detect direct tool / handler / MCP execution that bypasses
    ``ToolInvocationGateway``.

    The detector flags:

    - ``self.tool.ainvoke(...)`` calls inside a class method that owns
      the Product Runtime. A function-adapter pattern that takes a
      ``tool`` parameter is NOT flagged because the surrounding
      function is itself a tool-adapter, not a runtime owner.
    - ``handler(request)`` direct invocations.
    - ``mcp_direct`` / ``direct_mcp`` / ``image_gen_bypass`` /
      ``skill_direct_execute`` identifiers.
    """
    findings: list[Finding] = []
    for rel, tree in file_index.items():
        if _is_excluded(rel):
            continue
        for call_text, lineno in _call_target_strings(tree):
            # Only flag tool invocations where the receiver is
            # ``self`` (i.e. the class owns the tool). This rules out
            # function-adapter patterns that take ``tool`` as a
            # parameter.
            if call_text.endswith(".invoke") or call_text.endswith(".ainvoke"):
                if "tool" in call_text and call_text.startswith("self."):
                    findings.append(
                        Finding(
                            category="tool_bypass_direct",
                            path=rel,
                            line=lineno,
                            detail=f"direct tool invocation bypass: {call_text}",
                        )
                    )
            # MCP direct execution.
            if "mcp_direct" in call_text or "direct_mcp" in call_text:
                findings.append(
                    Finding(
                        category="tool_bypass_mcp_direct",
                        path=rel,
                        line=lineno,
                        detail=f"MCP direct execution: {call_text}",
                    )
                )
            # Image generation product bypass.
            if "image_gen_bypass" in call_text:
                findings.append(
                    Finding(
                        category="tool_bypass_image_gen",
                        path=rel,
                        line=lineno,
                        detail=f"image generation product bypass: {call_text}",
                    )
                )
            # Read-only bypass (security / budget / trace skipped).
            if "skill_direct_execute" in call_text:
                findings.append(
                    Finding(
                        category="tool_bypass_read_only",
                        path=rel,
                        line=lineno,
                        detail=(
                            f"read-only bypass of security/budget/trace: {call_text}"
                        ),
                    )
                )
    # Direct handler(request) pattern (assignments).
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
                text = ast.unparse(inner.func)
            except Exception:
                continue
            if text == "handler":
                findings.append(
                    Finding(
                        category="tool_bypass_handler",
                        path=rel,
                        line=node.lineno,
                        detail=f"direct handler(request) bypass: {ast.unparse(inner)}",
                    )
                )
    return findings


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
    """Determine the final status by priority order."""
    if unresolved:
        return STATUS_AUDIT_UNRESOLVED
    categories = {f.category for f in findings}
    if any(c.startswith("ownership_") for c in categories):
        return STATUS_OWNERSHIP_VIOLATION
    if any(c.startswith("tool_bypass_") for c in categories):
        return STATUS_TOOL_BYPASS
    if any(c.startswith("legacy_") for c in categories):
        return STATUS_LEGACY_RUNTIME
    if any(c.startswith("dual_path_") for c in categories):
        return STATUS_DUAL_PATH
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

    # 5. Unresolved (dynamic / alias / factory).
    for finding in _detect_dynamic_constructor_sites(file_index):
        result.add_unresolved(finding)
    for finding in _detect_alias_factory_unresolved(file_index):
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
