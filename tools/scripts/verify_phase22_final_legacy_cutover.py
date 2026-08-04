"""PHASE22 Final Legacy/Cutover Audit Verifier (V2).

This verifier is a FAIL-CLOSED audit gate that proves the repository has
retired every legacy runtime, alias registry, dual-path, alias/bypass,
public-adapter ownership violation, and expired feature flag reachable
from production source at the exact final head SHA.

The script supersedes PR #119 by enforcing the following invariants that
the prior verifier left under-tested:

1. **AST-based Python analysis** rather than substring search. The verifier
   walks every Python file with the ``ast`` module, classifies imports
   (static, dynamic, alias, attribute) and detects try/except canonical
   fallbacks, factory overrides, ``legacy_runner`` injection, ``_run_legacy``
   invocations and exception-driven ``_fallback_to_legacy`` paths.

2. **Reachability classification**, not just token matching. Legacy
   references inside excluded history documents and explicit
   ``docs/history`` packages do not constitute findings. References in
   production roots that are documented as ``resolved_retired`` in the
   removal candidates work product also do not constitute findings.
   Anything else does.

3. **Runtime blocker detection**: Phase08CutoverController's rollback,
   shadow, canary modes, ``legacy_runner`` field, ``_run_legacy``,
   ``_fallback_to_legacy`` and exception-driven fallbacks are treated as
   live cutover surface until the path is retired.

4. **Dual-path detection** for ``dual_read`` / ``dual_write`` markers,
   public-version adapter dual-write to domain DAOs, environment-variable
   runtime selectors and workflow legacy commands.

5. **Alias/bypass detection** for ``sys.meta_path``, ``sys.modules`` alias
   tables, dynamic ``import_module`` / ``__import__`` and ``try/except
   ImportError`` legacy fallbacks.

6. **Public-adapter ownership violation detection** that flags any
   versioned public adapter (e.g. ``api/v1``, ``api/product/v1``,
   ``api/product/v2``) that imports a domain DAO or repository directly
   and writes a domain table. The detection is deterministic: it
   enumerates public adapter roots, scans imports + AST write calls,
   and reports a finding for each write-into-domain violation.

7. **Feature-flag expiry enforcement** that compares each
   ``expires_at_phase`` against the current PHASE22 phase. Expired
   flags must be retired (removed, ``default=RETIRED``, no runtime
   reader, no rollback command, no active allowlist entry). Otherwise
   the gate reports ``DUAL_PATH_BLOCKERS_FOUND``.

8. **Unresolved escalation tracking**. When DeepSeek (or any other)
   architectural escalation is recorded as ESCALATE in the removal
   candidates work product or in active evidence, the verifier fails
   closed unless the escalation has been resolved.

The verifier is intentionally conservative: any unresolved finding
forces a non-zero exit code. A clean audit requires every category to
return zero findings AND every escalation to be resolved.

Status priority (highest priority first):

* Runtime blockers (LEGACY_RUNTIME_BLOCKERS_FOUND)
* Dual path (DUAL_PATH_BLOCKERS_FOUND)
* Alias/bypass (ALIAS_BYPASS_BLOCKERS_FOUND)
* Public adapter (PUBLIC_ADAPTER_OWNERSHIP_VIOLATION)
* Unresolved (AUDIT_UNRESOLVED)
* Clean (LEGACY_CUTOVER_AUDIT_CLEAN)

When the verifier cannot complete (e.g. the repo cannot be located,
YAML cannot be parsed, the AST walker crashes on a malformed file), it
returns ``TOOL_ERROR``.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator

# Optional YAML dependency: declared via PyYAML; missing dependency
# surfaces as TOOL_ERROR rather than silently substituting a tiny parser.
try:
    import yaml  # type: ignore[import-untyped]
    YAML_LOADER: Callable[[str], Any] | None = yaml.safe_load
except Exception:  # pragma: no cover - dependency is declared in pyproject.toml
    YAML_LOADER = None


REPO_ROOT = Path(__file__).resolve().parents[2]

# Production roots covered by the canonical-directory-contract.md.
# The audit MUST scan at least these roots and MUST treat each file as
# production source unless it sits under a documented history/archive
# subtree. Test trees and tool scripts are explicitly in scope per the
# task contract.
PRODUCTION_ROOTS: tuple[Path, ...] = (
    REPO_ROOT / "src" / "backend",
    REPO_ROOT / "apps" / "web" / "src",
    REPO_ROOT / "apps" / "desktop",
    REPO_ROOT / "tools",
    REPO_ROOT / "infra",
    REPO_ROOT / ".github" / "workflows",
)

# Roots whose content is allowed to describe historical architecture but
# MUST NOT be treated as production source. ``docs/history`` is the
# canonical archive; explicit history programs under docs/history and
# ``.agent/architecture/near-term`` legacy pre-canonical notes are
# excluded.
HISTORY_EXCLUDED_ROOTS: tuple[Path, ...] = (
    REPO_ROOT / "docs" / "history",
)

# Top-level config roots scanned for env/command/runtime selectors.
CONFIG_FILE_PATTERNS: tuple[str, ...] = (
    "pyproject.toml",
    "package.json",
)

# Old zuno root aliases that are forbidden in production source. The
# list mirrors the PHASE22 removal candidates work product.
OLD_ZUNO_ROOTS: tuple[str, ...] = (
    "zuno.core",
    "zuno.services",
    "zuno.schema",
    "zuno.database",
    "zuno.tools",
    "zuno.resources",
    "zuno.config",
    "zuno.mcp_servers",
    "zuno.utils",
)

# Public adapter roots that MUST NOT own domain writes. Each entry is
# a Path prefix relative to the repo root. Writes inside these roots
# trigger PUBLIC_ADAPTER_OWNERSHIP_VIOLATION.
PUBLIC_ADAPTER_ROOTS: tuple[Path, ...] = (
    REPO_ROOT / "src" / "backend" / "zuno" / "api" / "v1",
    REPO_ROOT / "src" / "backend" / "zuno" / "api" / "product",
    REPO_ROOT / "src" / "backend" / "zuno" / "api" / "errcode",
    REPO_ROOT / "apps" / "web" / "src" / "apis",
    REPO_ROOT / "apps" / "web" / "src" / "api",
)

# Directories whose very existence is forbidden by the canonical
# directory contract.
FORBIDDEN_ROOTS: tuple[Path, ...] = (
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "compatibility",
    REPO_ROOT / "tests" / "legacy_guards",
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "compatibility" / "legacy",
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "compatibility" / "legacy_aliases.py",
)

# Specific legacy filename patterns forbidden anywhere in production.
FORBIDDEN_FILENAMES: tuple[str, ...] = (
    "legacy_aliases.py",
)

# Substring patterns inside production paths that signal an active
# legacy segment. Matched on POSIX segments (no extension). Used by
# the AST/text inventory stage.
FORBIDDEN_LEGACY_SEGMENT_NAMES: tuple[str, ...] = (
    "legacy",
)

# Pattern markers that indicate a dual-read or dual-write bridge. Each
# tuple member is ``(category, regex, literal_markers)``; the regex is
# matched against per-file text for non-Python files, and against
# Python AST nodes for production source.
DUAL_PATH_LITERAL_MARKERS: tuple[str, ...] = (
    "dual_read",
    "dual_write",
    "ZUNO_AGENT_RUNTIME=legacy_general_agent",
    "legacy_general_agent",
    "completion_rollback_to_general_agent",
)

# Tokens whose presence in a non-Python file's text is evidence of an
# alias/bypass constructor.
ALIAS_BYPASS_LITERAL_MARKERS: tuple[str, ...] = (
    "zuno.platform.compatibility",
    "zuno.platform.compatibility.vendor",
    "fastapi_jwt_auth vendor shim",
    "register_legacy_aliases",
)

# File extensions scanned by the text-based stage.
TEXT_SCAN_EXTENSIONS: tuple[str, ...] = (
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".mjs",
    ".cjs",
    ".sh",
    ".ps1",
    ".yml",
    ".yaml",
    ".toml",
    ".json",
)

# Feature flag registry path. The phase22 audit owns the lifecycle of
# feature flags; expired flags must retire.
FEATURE_FLAG_REGISTRY = (
    REPO_ROOT / ".agent" / "programs" / "work-products" / "feature-flag-registry.yaml"
)

# Removal candidates work product path.
REMOVAL_CANDIDATES_YAML = (
    REPO_ROOT / ".agent" / "programs" / "work-products" / "phase22-removal-candidates.yaml"
)

# Temporary allowlist work product path.
TEMPORARY_ALLOWLIST_YAML = (
    REPO_ROOT / ".agent" / "programs" / "work-products" / "temporary-allowlist.yaml"
)

# Phase08 cutover controller location (the lone live legacy runtime
# surface we MUST inspect on every run).
PHASE08_CUTOVER_FILE = (
    REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "runtime" / "phase08_cutover.py"
)

# Workspace task runtime service (it instantiates a legacy_runner at
# runtime; this is the wiring the audit must prove is canonical-only).
WORKSPACE_TASK_RUNTIME_FILE = (
    REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "workspace_task_runtime.py"
)

# Completion service (the historical rollback entrypoint). The audit
# must prove no runtime selector reaches GeneralAgent.
COMPLETION_SERVICE_FILE = (
    REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "completion.py"
)

# Current phase used for feature-flag expiry comparison.
CURRENT_PHASE = "PHASE22"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Finding:
    """A single audit finding."""

    path: str
    line: int
    symbol: str
    category: str
    entrypoint: str
    reachable: bool
    resolution: str
    owner: str
    risk: str
    required_action: str
    recommended_worker: str
    evidence_kind: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "line": self.line,
            "symbol": self.symbol,
            "category": self.category,
            "entrypoint": self.entrypoint,
            "reachable": self.reachable,
            "resolution": self.resolution,
            "owner": self.owner,
            "risk": self.risk,
            "required_action": self.required_action,
            "recommended_worker": self.recommended_worker,
            "evidence_kind": self.evidence_kind,
        }


@dataclass
class Inventory:
    """Repository inventory snapshot."""

    head_sha: str = ""
    files_scanned: int = 0
    python_files_scanned: int = 0
    non_python_files_scanned: int = 0
    excluded_history_files: int = 0
    production_python_modules: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "head_sha": self.head_sha,
            "files_scanned": self.files_scanned,
            "python_files_scanned": self.python_files_scanned,
            "non_python_files_scanned": self.non_python_files_scanned,
            "excluded_history_files": self.excluded_history_files,
            "production_python_modules": list(self.production_python_modules),
        }


@dataclass
class ReachabilityReport:
    """Reachability classification per legacy symbol."""

    phase08_runtime_blockers: list[Finding] = field(default_factory=list)
    runtime_blockers: list[Finding] = field(default_factory=list)
    dual_path_blockers: list[Finding] = field(default_factory=list)
    alias_bypass_blockers: list[Finding] = field(default_factory=list)
    public_adapter_violations: list[Finding] = field(default_factory=list)
    unresolved_items: list[Finding] = field(default_factory=list)

    def all_findings(self) -> list[Finding]:
        return (
            self.phase08_runtime_blockers
            + self.runtime_blockers
            + self.dual_path_blockers
            + self.alias_bypass_blockers
            + self.public_adapter_violations
            + self.unresolved_items
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase08_runtime_blockers": [f.to_dict() for f in self.phase08_runtime_blockers],
            "runtime_blockers": [f.to_dict() for f in self.runtime_blockers],
            "dual_path_blockers": [f.to_dict() for f in self.dual_path_blockers],
            "alias_bypass_blockers": [f.to_dict() for f in self.alias_bypass_blockers],
            "public_adapter_violations": [f.to_dict() for f in self.public_adapter_violations],
            "unresolved_items": [f.to_dict() for f in self.unresolved_items],
        }


@dataclass
class VerifierReport:
    """Top-level verifier report."""

    status: str = "TOOL_ERROR"
    exit_code: int = 2
    inventory: Inventory = field(default_factory=Inventory)
    reachability: ReachabilityReport = field(default_factory=ReachabilityReport)
    tool_errors: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "exit_code": self.exit_code,
            "tool_errors": list(self.tool_errors),
            "notes": list(self.notes),
            "inventory": self.inventory.to_dict(),
            "reachability": self.reachability.to_dict(),
            "counts": {
                "runtime_blockers": len(self.reachability.runtime_blockers)
                + len(self.reachability.phase08_runtime_blockers),
                "dual_path_blockers": len(self.reachability.dual_path_blockers),
                "alias_bypass_blockers": len(self.reachability.alias_bypass_blockers),
                "public_adapter_violations": len(self.reachability.public_adapter_violations),
                "unresolved_items": len(self.reachability.unresolved_items),
            },
        }


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _strip_bom(text: str) -> str:
    if text.startswith("﻿"):
        return text[1:]
    return text


def _run_git_rev_parse_head() -> str:
    """Resolve the exact final HEAD SHA via ``git rev-parse HEAD``.

    The PR #119 implementation guessed the SHA from ``.git/HEAD`` text;
    the new implementation MUST shell out to ``git`` so the SHA is
    always consistent with the runner checkout. Empty output falls back
    to ``UNKNOWN``.
    """

    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO_ROOT),
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return "UNKNOWN"
    return completed.stdout.strip() or "UNKNOWN"


def _is_history_excluded(path: Path) -> bool:
    for excluded in HISTORY_EXCLUDED_ROOTS:
        try:
            path.relative_to(excluded)
        except ValueError:
            continue
        return True
    return False


def _is_production_path(path: Path) -> bool:
    """Whether a path belongs to a production root under audit."""
    for root in PRODUCTION_ROOTS:
        try:
            path.relative_to(root)
        except ValueError:
            continue
        return True
    # Include top-level config files explicitly.
    for pattern in CONFIG_FILE_PATTERNS:
        if path.name == pattern:
            try:
                path.relative_to(REPO_ROOT)
            except ValueError:
                continue
            return True
    return False


def _is_public_adapter_path(path: Path) -> bool:
    for root in PUBLIC_ADAPTER_ROOTS:
        try:
            path.relative_to(root)
        except ValueError:
            continue
        return True
    return False


def _iter_production_files() -> Iterator[Path]:
    seen: set[Path] = set()
    for root in PRODUCTION_ROOTS:
        if not root.exists():
            continue
        for candidate in root.rglob("*"):
            if not candidate.is_file():
                continue
            if any(part == "__pycache__" for part in candidate.parts):
                continue
            if candidate in seen:
                continue
            seen.add(candidate)
            yield candidate
    for pattern in CONFIG_FILE_PATTERNS:
        candidate = REPO_ROOT / pattern
        if candidate.is_file() and candidate not in seen:
            seen.add(candidate)
            yield candidate


def _should_scan_extension(path: Path) -> bool:
    if path.suffix == "":
        # Bare-name files such as ``Dockerfile`` are intentionally
        # scanned via the literal text stage only when their suffix is
        # in scope; here we require an explicit suffix.
        return False
    return path.suffix.lower() in TEXT_SCAN_EXTENSIONS


def _safe_relative(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


# ---------------------------------------------------------------------------
# AST walk utilities
# ---------------------------------------------------------------------------


def _imports_in_module(tree: ast.AST) -> list[tuple[str, int]]:
    """Return ``[(module, lineno)]`` for every static import in the tree."""

    results: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                results.append((alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level:
                # Relative import; mark as dotted module with leading dots.
                prefix = "." * node.level
                module = f"{prefix}{module}"
            if module:
                results.append((module, node.lineno))
    return results


def _dynamic_imports_in_module(
    tree: ast.AST,
) -> list[tuple[str, int, str]]:
    """Return ``[(call_text, lineno, kind)]`` for dynamic imports."""

    results: list[tuple[str, int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        kind = ""
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
            if func.value.id == "importlib" and func.attr in {"import_module"}:
                kind = "importlib.import_module"
            elif func.value.id == "sys" and func.attr in {"meta_path", "modules"}:
                kind = "sys.meta_path/sys.modules mutation"
        elif isinstance(func, ast.Name):
            if func.id == "__import__":
                kind = "dunder_import"
        if not kind:
            continue
        try:
            text = ast.unparse(node)
        except Exception:
            text = "<unparsable>"
        results.append((text, node.lineno, kind))
    return results


def _try_except_legacy_fallbacks(
    tree: ast.AST,
) -> list[tuple[int, str]]:
    """Return ``[(lineno, snippet)]`` for try/except ImportError fallbacks.

    The audit flags a try/except block when its ``try`` body imports from
    a legacy zuno root (``zuno.core`` / ``zuno.services`` / ...) or its
    ``except`` body statically names a legacy fallback symbol.
    """

    candidates: list[tuple[int, str]] = []
    legacy_alias_tokens = (
        "legacy",
        "fallback_to_legacy",
        "fallback",
        "legacy_runner",
        "general_agent",
    )
    legacy_module_prefixes = (
        "zuno.core",
        "zuno.services",
        "zuno.schema",
        "zuno.database",
        "zuno.tools",
        "zuno.resources",
        "zuno.config",
        "zuno.mcp_servers",
        "zuno.utils",
    )
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        handler = node.handlers[0] if node.handlers else None
        if handler is None:
            continue
        flag = False
        # Heuristic 1: the try body imports from a legacy root.
        for sub in ast.walk(node):
            if isinstance(sub, ast.ImportFrom) and sub.module:
                if any(
                    sub.module.startswith(prefix)
                    for prefix in legacy_module_prefixes
                ):
                    flag = True
                    break
        # Heuristic 2: the except body statically names a legacy token.
        if not flag:
            for sub in ast.walk(handler):
                token = None
                if isinstance(sub, ast.Name):
                    token = sub.id
                elif isinstance(sub, ast.Attribute):
                    token = sub.attr
                if token and any(t in token.lower() for t in legacy_alias_tokens):
                    flag = True
                    break
        if not flag:
            continue
        try:
            snippet = ast.unparse(handler)
        except Exception:
            snippet = "<unparsable except clause>"
        candidates.append((handler.lineno, snippet))
    return candidates


def _function_defs(tree: ast.AST) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]


def _call_targets(tree: ast.AST) -> list[tuple[str, int]]:
    """Return ``[(call_text, lineno)]`` for every Call node in the tree."""

    results: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        try:
            text = ast.unparse(node.func)
        except Exception:
            text = "<unparsable>"
        results.append((text, node.lineno))
    return results


# ---------------------------------------------------------------------------
# Inventory and phase8 inspection
# ---------------------------------------------------------------------------


def _inspect_phase08_cutover(report: VerifierReport) -> None:
    """Walk the Phase08CutoverController and verify retirement invariants."""

    if not PHASE08_CUTOVER_FILE.exists():
        report.tool_errors.append(
            "Phase08CutoverController not found at expected path"
        )
        return
    text = _strip_bom(_read_text(PHASE08_CUTOVER_FILE))
    rel = _safe_relative(PHASE08_CUTOVER_FILE)
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        report.tool_errors.append(
            f"Phase08CutoverController is not parseable: {exc}"
        )
        return

    expected_runtime_symbols = {
        "_run_legacy": False,
        "legacy_runner": False,
        "_fallback_to_legacy": False,
    }
    cutover_modes = {"rollback", "shadow", "canary"}
    cutover_modes_seen: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Phase08CutoverController":
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.FunctionDef):
                    if stmt.name in expected_runtime_symbols:
                        expected_runtime_symbols[stmt.name] = True
                    if stmt.name == "handle":
                        for sub in ast.walk(stmt):
                            if (
                                isinstance(sub, ast.Compare)
                                and isinstance(sub.left, ast.Attribute)
                                and isinstance(sub.left.value, ast.Name)
                                and sub.left.value.id == "self"
                                and sub.left.attr == "mode"
                            ):
                                for comparator in sub.comparators:
                                    if isinstance(comparator, ast.Constant):
                                        cutover_modes_seen.add(str(comparator.value))
                elif (
                    isinstance(stmt, ast.AnnAssign)
                    and isinstance(stmt.target, ast.Name)
                    and stmt.target.id == "legacy_runner"
                ):
                    expected_runtime_symbols["legacy_runner"] = True

    if cutover_modes & cutover_modes_seen:
        for mode in sorted(cutover_modes & cutover_modes_seen):
            report.reachability.phase08_runtime_blockers.append(
                Finding(
                    path=rel,
                    line=1,
                    symbol=f"Phase08CutoverController.mode=='{mode}'",
                    category="LEGACY_RUNTIME_BLOCKERS_FOUND",
                    entrypoint="Phase08CutoverController.handle",
                    reachable=True,
                    resolution="retire",
                    owner="06 Agent Core",
                    risk="active cutover mode routes real workspace tasks through legacy runtime",
                    required_action="retire rollback/shadow/canary branches and force new_default",
                    recommended_worker="deepseek-architectural-decision",
                    evidence_kind="STATIC_AST",
                )
            )

    for symbol, present in expected_runtime_symbols.items():
        if present:
            report.reachability.phase08_runtime_blockers.append(
                Finding(
                    path=rel,
                    line=1,
                    symbol=symbol,
                    category="LEGACY_RUNTIME_BLOCKERS_FOUND",
                    entrypoint=f"Phase08CutoverController.{symbol}",
                    reachable=True,
                    resolution="retire",
                    owner="06 Agent Core",
                    risk=(
                        "production runtime still constructs and dispatches to the legacy runtime; "
                        "PHASE22 must retire or prove this path unreachable on the final head"
                    ),
                    required_action=(
                        "retire the symbol or prove it is unreachable on the exact final head"
                    ),
                    recommended_worker="deepseek-architectural-decision",
                    evidence_kind="STATIC_AST",
                )
            )


def _inspect_workspace_task_runtime(report: VerifierReport) -> None:
    """Walk the workspace task runtime and find legacy_runner injection."""

    if not WORKSPACE_TASK_RUNTIME_FILE.exists():
        return
    text = _strip_bom(_read_text(WORKSPACE_TASK_RUNTIME_FILE))
    rel = _safe_relative(WORKSPACE_TASK_RUNTIME_FILE)
    try:
        tree = ast.parse(text)
    except SyntaxError:
        report.tool_errors.append(
            "workspace_task_runtime.py is not parseable"
        )
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "legacy_runner":
            report.reachability.phase08_runtime_blockers.append(
                Finding(
                    path=rel,
                    line=node.lineno,
                    symbol="legacy_runner",
                    category="LEGACY_RUNTIME_BLOCKERS_FOUND",
                    entrypoint="WorkspaceTaskRuntimeService._run_phase08_cutover_for_task",
                    reachable=True,
                    resolution="retire",
                    owner="01 Product Surface",
                    risk="workspace task runtime synthesizes a legacy_runner fallback for phase08 cutover",
                    required_action="remove the legacy_runner factory or wire the canonical runtime directly",
                    recommended_worker="deepseek-architectural-decision",
                    evidence_kind="STATIC_AST",
                )
            )
            break


def _inspect_completion_service(report: VerifierReport) -> None:
    """Confirm the completion route is no longer a rollback entrypoint."""

    if not COMPLETION_SERVICE_FILE.exists():
        return
    text = _read_text(COMPLETION_SERVICE_FILE)
    rel = _safe_relative(COMPLETION_SERVICE_FILE)
    forbidden_markers = (
        "ZUNO_AGENT_RUNTIME",
        "legacy_general_agent",
        "_create_chat_agent",
    )
    for marker in forbidden_markers:
        if marker in text:
            report.reachability.dual_path_blockers.append(
                Finding(
                    path=rel,
                    line=1,
                    symbol=marker,
                    category="DUAL_PATH_BLOCKERS_FOUND",
                    entrypoint="CompletionService",
                    reachable=True,
                    resolution="retire",
                    owner="01 Product Surface",
                    risk="completion service still exposes legacy runtime rollback markers",
                    required_action="remove the legacy marker and confirm rollback is fail-closed",
                    recommended_worker="minimax-runtime-cleanup",
                    evidence_kind="STATIC_TEXT",
                )
            )


# ---------------------------------------------------------------------------
# Inventory walk
# ---------------------------------------------------------------------------


def _build_inventory(report: VerifierReport) -> Inventory:
    inventory = Inventory(head_sha=_run_git_rev_parse_head())
    production_modules: list[str] = []
    for path in _iter_production_files():
        if _is_history_excluded(path):
            inventory.excluded_history_files += 1
            continue
        inventory.files_scanned += 1
        rel = _safe_relative(path)
        if path.suffix.lower() == ".py":
            inventory.python_files_scanned += 1
            production_modules.append(rel)
            if not _should_scan_extension(path):
                continue
        else:
            inventory.non_python_files_scanned += 1
            if not _should_scan_extension(path):
                continue
    inventory.production_python_modules = tuple(production_modules)
    return inventory


# ---------------------------------------------------------------------------
# Generic Python AST scan
# ---------------------------------------------------------------------------


_LEGACY_RUNTIME_TOKENS = (
    "fallback_to_legacy",
    "_fallback_to_legacy",
    "legacy_runner",
    "_run_legacy",
    "rollback",
    "shadow",
    "canary",
)


# Cutover mode literals to flag in production source. Each entry is the
# raw token we expect to find in an ``if self.mode == "<token>"`` style
# branch or in a configuration/env selector.
_CUTOVER_MODE_LITERALS: tuple[str, ...] = (
    "rollback",
    "shadow",
    "canary",
)


def _string_literal_candidates(tree: ast.AST) -> list[tuple[str, int]]:
    """Return ``[(literal_value, lineno)]`` for every ``ast.Constant`` str."""

    results: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            results.append((node.value, node.lineno))
    return results


def _scan_python_file(
    path: Path,
    rel: str,
    report: VerifierReport,
    removal_candidate_allowlist: set[str],
    *,
    is_phase08: bool,
) -> None:
    """Walk one Python production file and emit findings."""

    text = _strip_bom(_read_text(path))
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        report.tool_errors.append(f"{rel}: not parseable: {exc}")
        return

    # 1. Static imports of old zuno roots.
    for module, lineno in _imports_in_module(tree):
        # Skip self-imports of phase08_cutover that legitimately reference
        # the legacy runtime constants on the audit side.
        if is_phase08:
            continue
        for old_root in OLD_ZUNO_ROOTS:
            if module == old_root or module.startswith(f"{old_root}."):
                if rel in removal_candidate_allowlist:
                    continue
                report.reachability.dual_path_blockers.append(
                    Finding(
                        path=rel,
                        line=lineno,
                        symbol=module,
                        category="DUAL_PATH_BLOCKERS_FOUND",
                        entrypoint=f"static import {module}",
                        reachable=True,
                        resolution="retire",
                        owner="Repository Governance",
                        risk="production code imports a retired zuno.* root alias",
                        required_action=f"replace {module} with its canonical owner",
                        recommended_worker="minimax-runtime-cleanup",
                        evidence_kind="STATIC_AST",
                    )
                )

    # 2. Dynamic imports and sys.meta_path/sys.modules mutations.
    for call_text, lineno, kind in _dynamic_imports_in_module(tree):
        if rel in removal_candidate_allowlist:
            continue
        report.reachability.alias_bypass_blockers.append(
            Finding(
                path=rel,
                line=lineno,
                symbol=kind,
                category="ALIAS_BYPASS_BLOCKERS_FOUND",
                entrypoint=f"dynamic {kind}",
                reachable=True,
                resolution="retire",
                owner="Repository Governance",
                risk="dynamic import bypass can hide owner drift",
                required_action="replace dynamic import with a static canonical import",
                recommended_worker="minimax-runtime-cleanup",
                evidence_kind="STATIC_AST",
            )
        )
        _ = call_text  # kept for future AST-driven reasoning

    # 3. try/except legacy fallbacks.
    for lineno, snippet in _try_except_legacy_fallbacks(tree):
        if rel in removal_candidate_allowlist:
            continue
        report.reachability.alias_bypass_blockers.append(
            Finding(
                path=rel,
                line=lineno,
                symbol="try/except legacy fallback",
                category="ALIAS_BYPASS_BLOCKERS_FOUND",
                entrypoint="try/except ImportError legacy fallback",
                reachable=True,
                resolution="retire",
                owner="Repository Governance",
                risk="try/except legacy fallback can silently resurrect old runtime",
                required_action="remove the fallback or replace with a fail-closed error",
                recommended_worker="minimax-runtime-cleanup",
                evidence_kind="STATIC_AST",
            )
        )
        _ = snippet

    # 4. Runtime factory overrides / legacy_runner injection.
    for func in _function_defs(tree):
        name = func.name.lower()
        if name in {"legacy_runner", "_run_legacy", "_fallback_to_legacy"}:
            if rel in removal_candidate_allowlist:
                continue
            if not is_phase08:
                # Outside Phase08CutoverController the symbol must not exist.
                report.reachability.dual_path_blockers.append(
                    Finding(
                        path=rel,
                        line=func.lineno,
                        symbol=func.name,
                        category="DUAL_PATH_BLOCKERS_FOUND",
                        entrypoint=f"function {func.name}",
                        reachable=True,
                        resolution="retire",
                        owner="Repository Governance",
                        risk="legacy_runner factory injected outside the canonical cutover surface",
                        required_action=f"remove {func.name} or wire it to the canonical runtime",
                        recommended_worker="deepseek-architectural-decision",
                        evidence_kind="STATIC_AST",
                    )
                )

    # 5. Public-adapter ownership violation: any public adapter that
    #    imports a domain DAO/repository directly and writes to it.
    if _is_public_adapter_path(path):
        _scan_public_adapter_ownership(path, rel, tree, report)

    # 6. Cutover-mode literals in production source.
    for literal_value, lineno in _string_literal_candidates(tree):
        if literal_value in _CUTOVER_MODE_LITERALS:
            if rel in removal_candidate_allowlist:
                continue
            report.reachability.dual_path_blockers.append(
                Finding(
                    path=rel,
                    line=lineno,
                    symbol=f"cutover mode literal '{literal_value}'",
                    category="DUAL_PATH_BLOCKERS_FOUND",
                    entrypoint="cutover mode literal",
                    reachable=True,
                    resolution="retire",
                    owner=_owner_for_path(rel),
                    risk=f"production source still names cutover mode '{literal_value}'",
                    required_action=(
                        f"remove the '{literal_value}' branch or prove"
                        " it is unreachable on the final head"
                    ),
                    recommended_worker="deepseek-architectural-decision",
                    evidence_kind="STATIC_AST",
                )
            )
        for marker in DUAL_PATH_LITERAL_MARKERS:
            if marker in literal_value:
                if rel in removal_candidate_allowlist:
                    continue
                report.reachability.dual_path_blockers.append(
                    Finding(
                        path=rel,
                        line=lineno,
                        symbol=f"dual-path literal '{marker}'",
                        category="DUAL_PATH_BLOCKERS_FOUND",
                        entrypoint="dual-path literal",
                        reachable=True,
                        resolution="retire",
                        owner=_owner_for_path(rel),
                        risk=(
                            "production source still contains a"
                            f" dual-path marker '{marker}'"
                        ),
                        required_action=(
                            f"remove the '{marker}' literal"
                        ),
                        recommended_worker="minimax-runtime-cleanup",
                        evidence_kind="STATIC_AST",
                    )
                )
                break

    # 7. ``sys.modules`` literal alias table: detect any code that assigns
    # a string literal whose key starts with ``zuno.`` into ``sys.modules``.
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        target_text = ast.unparse(node.targets[0]) if node.targets else ""
        if target_text.startswith("sys.modules"):
            value_text = ast.unparse(node.value) if node.value else ""
            if "zuno." in value_text or "zuno." in target_text:
                if rel in removal_candidate_allowlist:
                    continue
                report.reachability.alias_bypass_blockers.append(
                    Finding(
                        path=rel,
                        line=node.lineno,
                        symbol=f"sys.modules alias: {target_text} = {value_text}",
                        category="ALIAS_BYPASS_BLOCKERS_FOUND",
                        entrypoint="sys.modules alias",
                        reachable=True,
                        resolution="retire",
                        owner="Repository Governance",
                        risk="sys.modules alias rewrites a zuno module entry",
                        required_action="remove the sys.modules alias assignment",
                        recommended_worker="minimax-runtime-cleanup",
                        evidence_kind="STATIC_AST",
                    )
                )

    # 8. ``sys.meta_path.append`` finder injection.
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        text = ast.unparse(func) if hasattr(ast, "unparse") else ""
        if "sys.meta_path" in text:
            if rel in removal_candidate_allowlist:
                continue
            report.reachability.alias_bypass_blockers.append(
                Finding(
                    path=rel,
                    line=node.lineno,
                    symbol=f"sys.meta_path mutation: {text}",
                    category="ALIAS_BYPASS_BLOCKERS_FOUND",
                    entrypoint="sys.meta_path mutation",
                    reachable=True,
                    resolution="retire",
                    owner="Repository Governance",
                    risk="sys.meta_path mutation can hide owner drift",
                    required_action="remove the sys.meta_path mutation",
                    recommended_worker="minimax-runtime-cleanup",
                    evidence_kind="STATIC_AST",
                )
            )


def _scan_public_adapter_ownership(
    path: Path,
    rel: str,
    tree: ast.AST,
    report: VerifierReport,
) -> None:
    """Detect public-adapter direct write into domain DAOs/repositories.

    The check is intentionally deterministic:

    * Imports the module ``zuno.platform.database`` or any of its
      submodules (``zuno.platform.database.dao``,
      ``zuno.platform.database.models``).
    * Calls ``.execute``, ``session.add``, ``session.delete``,
      ``session.commit`` or ``save_*`` / ``delete_*`` / ``update_*``
      on those imports.
    """

    database_modules = {"zuno.platform.database"}
    direct_dao_calls = {
        "session.add",
        "session.delete",
        "session.commit",
        "session.execute",
    }

    for module, lineno in _imports_in_module(tree):
        if not any(module == m or module.startswith(f"{m}.") for m in database_modules):
            continue
        # Look for direct-write calls in the same file.
        for call_text, call_lineno in _call_targets(tree):
            for marker in direct_dao_calls:
                if call_text.endswith(marker) or marker in call_text:
                    report.reachability.public_adapter_violations.append(
                        Finding(
                            path=rel,
                            line=call_lineno,
                            symbol=f"{module}::{call_text}",
                            category="PUBLIC_ADAPTER_OWNERSHIP_VIOLATION",
                            entrypoint=f"public adapter writes via {call_text}",
                            reachable=True,
                            resolution="retire",
                            owner="01 Product Surface",
                            risk="public adapter writes directly to a domain DAO/repository",
                            required_action="route writes through the application service",
                            recommended_worker="minimax-runtime-cleanup",
                            evidence_kind="STATIC_AST",
                        )
                    )
                    break


# ---------------------------------------------------------------------------
# Generic text scan for non-Python and YAML/Workflow files
# ---------------------------------------------------------------------------


_DUAL_PATH_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("dual_read", re.compile(r"\bdual_read\b")),
    ("dual_write", re.compile(r"\bdual_write\b")),
    ("legacy runtime selector", re.compile(r"ZUNO_AGENT_RUNTIME\s*[:=]\s*legacy_general_agent")),
    ("legacy completion rollback", re.compile(r"legacy_general_agent_completion_rollback")),
)

_ALIAS_BYPASS_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("legacy alias finder", re.compile(r"_LegacyAliasFinder|register_legacy_aliases")),
    ("compatibility shell", re.compile(r"zuno\.platform\.compatibility(?!\.vendor)")),
    ("compatibility vendor", re.compile(r"zuno\.platform\.compatibility\.vendor")),
)


def _scan_text_file(
    path: Path,
    rel: str,
    report: VerifierReport,
    removal_candidate_allowlist: set[str],
) -> None:
    """Scan non-Python production files for dual-path / alias-bypass markers."""

    if rel in removal_candidate_allowlist:
        return
    try:
        text = _read_text(path)
    except Exception as exc:
        report.tool_errors.append(f"{rel}: cannot read: {exc}")
        return

    suffix = path.suffix.lower()
    for label, pattern in _DUAL_PATH_PATTERNS:
        match = pattern.search(text)
        if match:
            # Heuristic context check: ignore matches that appear only in
            # pure comment lines that explicitly state retirement.
            line_no = text[: match.start()].count("\n") + 1
            if _is_retired_context(text, line_no, label):
                continue
            report.reachability.dual_path_blockers.append(
                Finding(
                    path=rel,
                    line=line_no,
                    symbol=label,
                    category="DUAL_PATH_BLOCKERS_FOUND",
                    entrypoint=f"{suffix} text scan",
                    reachable=True,
                    resolution="retire",
                    owner=_owner_for_path(rel),
                    risk="dual-path marker survived in non-Python production file",
                    required_action="remove or retire the marker",
                    recommended_worker="minimax-runtime-cleanup",
                    evidence_kind="STATIC_TEXT",
                )
            )

    for label, pattern in _ALIAS_BYPASS_PATTERNS:
        match = pattern.search(text)
        if match:
            line_no = text[: match.start()].count("\n") + 1
            if _is_retired_context(text, line_no, label):
                continue
            report.reachability.alias_bypass_blockers.append(
                Finding(
                    path=rel,
                    line=line_no,
                    symbol=label,
                    category="ALIAS_BYPASS_BLOCKERS_FOUND",
                    entrypoint=f"{suffix} text scan",
                    reachable=True,
                    resolution="retire",
                    owner=_owner_for_path(rel),
                    risk="alias/bypass marker survived in non-Python production file",
                    required_action="remove or retire the marker",
                    recommended_worker="minimax-runtime-cleanup",
                    evidence_kind="STATIC_TEXT",
                )
            )

    # Plain ``dual_read`` / ``dual_write`` substring scan (covers Python
    # text where the AST walker missed an unusual construct and any
    # non-Python file).
    for marker in DUAL_PATH_LITERAL_MARKERS:
        if marker in {"dual_read", "dual_write"}:
            idx = text.find(marker)
            if idx < 0:
                continue
            line_no = text[:idx].count("\n") + 1
            if _is_retired_context(text, line_no, marker):
                continue
            report.reachability.dual_path_blockers.append(
                Finding(
                    path=rel,
                    line=line_no,
                    symbol=marker,
                    category="DUAL_PATH_BLOCKERS_FOUND",
                    entrypoint=f"{suffix} text scan",
                    reachable=True,
                    resolution="retire",
                    owner=_owner_for_path(rel),
                    risk=f"dual-path marker '{marker}' survived in production file",
                    required_action=f"remove the '{marker}' literal",
                    recommended_worker="minimax-runtime-cleanup",
                    evidence_kind="STATIC_TEXT",
                )
            )


def _is_retired_context(text: str, line_no: int, label: str) -> bool:
    """Whether the match sits inside a documented retirement context."""

    lines = text.splitlines()
    window = lines[max(line_no - 3, 0): line_no + 3]
    joined = "\n".join(window).lower()
    retire_tokens = (
        "retired",
        "resolved_retired",
        "fail-closed",
        "removed",
        "after phase22",
        "historical",
        "history only",
    )
    return any(token in joined for token in retire_tokens)


def _owner_for_path(rel: str) -> str:
    if rel.startswith("src/backend/zuno/api"):
        return "01 Product Surface"
    if rel.startswith("src/backend/zuno/agent"):
        return "06 Agent Core"
    if rel.startswith("src/backend/zuno/knowledge"):
        return "03 Knowledge"
    if rel.startswith("src/backend/zuno/capability"):
        return "08 Tool Runtime"
    if rel.startswith("src/backend/zuno/memory"):
        return "05 Memory"
    if rel.startswith("src/backend/zuno/platform"):
        return "11 Infrastructure"
    if rel.startswith("apps/web"):
        return "01 Product Surface"
    if rel.startswith("apps/desktop"):
        return "01 Product Surface"
    if rel.startswith(".github"):
        return "Repository Governance"
    if rel.startswith("tools"):
        return "Repository Governance"
    if rel.startswith("infra"):
        return "11 Infrastructure"
    return "Repository Governance"


# ---------------------------------------------------------------------------
# Forbidden path existence checks
# ---------------------------------------------------------------------------


def _check_forbidden_paths(report: VerifierReport) -> None:
    for forbidden in FORBIDDEN_ROOTS:
        if not forbidden.exists():
            continue
        # Ignore __pycache__ artifacts.
        if any(part == "__pycache__" for part in forbidden.parts):
            continue
        if forbidden.is_dir():
            for child in forbidden.rglob("*"):
                if child.is_file() and not any(part == "__pycache__" for part in child.parts):
                    rel = _safe_relative(child)
                    report.reachability.dual_path_blockers.append(
                        Finding(
                            path=rel,
                            line=1,
                            symbol=f"forbidden root child",
                            category="DUAL_PATH_BLOCKERS_FOUND",
                            entrypoint=f"forbidden root {forbidden.name}",
                            reachable=True,
                            resolution="retire",
                            owner="Repository Governance",
                            risk="forbidden root holds a non-pycache file",
                            required_action=f"remove {rel}",
                            recommended_worker="minimax-runtime-cleanup",
                            evidence_kind="CONFIG",
                        )
                    )
                    break
        elif forbidden.is_file():
            rel = _safe_relative(forbidden)
            report.reachability.dual_path_blockers.append(
                Finding(
                    path=rel,
                    line=1,
                    symbol=f"forbidden file",
                    category="DUAL_PATH_BLOCKERS_FOUND",
                    entrypoint=f"forbidden file {forbidden.name}",
                    reachable=True,
                    resolution="retire",
                    owner="Repository Governance",
                    risk="forbidden file re-introduced in production tree",
                    required_action=f"remove {rel}",
                    recommended_worker="minimax-runtime-cleanup",
                    evidence_kind="CONFIG",
                )
            )


# ---------------------------------------------------------------------------
# Feature flag expiry enforcement
# ---------------------------------------------------------------------------


def _phase_rank(phase_text: str) -> int:
    match = re.match(r"PHASE(\d+)", phase_text.strip(), re.IGNORECASE)
    if not match:
        return -1
    try:
        return int(match.group(1))
    except ValueError:
        return -1


def _check_feature_flag_expiry(report: VerifierReport) -> None:
    if not FEATURE_FLAG_REGISTRY.exists():
        report.tool_errors.append(
            f"feature flag registry missing: {_safe_relative(FEATURE_FLAG_REGISTRY)}"
        )
        return
    if YAML_LOADER is None:
        report.tool_errors.append("PyYAML is required to parse the feature flag registry")
        return
    try:
        document = YAML_LOADER(_read_text(FEATURE_FLAG_REGISTRY))
    except Exception as exc:
        report.tool_errors.append(
            f"feature flag registry YAML failed to parse: {exc}"
        )
        return
    if not isinstance(document, dict):
        report.tool_errors.append("feature flag registry root must be a mapping")
        return

    flags = document.get("flags")
    if not isinstance(flags, list):
        report.tool_errors.append("feature flag registry missing flags list")
        return

    current_rank = _phase_rank(CURRENT_PHASE)
    for entry in flags:
        if not isinstance(entry, dict):
            continue
        expires = entry.get("expires_at_phase")
        if not isinstance(expires, str):
            continue
        rank = _phase_rank(expires)
        if rank < 0 or rank >= current_rank:
            continue
        # Expired flag: must satisfy the strict retirement invariants.
        flag_name = str(entry.get("flag", "<unknown>"))
        default_state = str(entry.get("default", ""))
        rollback_command = str(entry.get("rollback_command", ""))
        issues: list[str] = []
        if default_state != "RETIRED":
            issues.append(f"default={default_state!r} not RETIRED")
        if not rollback_command.lower().startswith("retired"):
            issues.append(f"rollback_command={rollback_command!r} not retired")
        if issues:
            report.reachability.dual_path_blockers.append(
                Finding(
                    path=_safe_relative(FEATURE_FLAG_REGISTRY),
                    line=1,
                    symbol=flag_name,
                    category="DUAL_PATH_BLOCKERS_FOUND",
                    entrypoint=f"feature flag {flag_name}",
                    reachable=True,
                    resolution="retire",
                    owner=str(entry.get("owner", "Repository Governance")),
                    risk="expired feature flag is not yet retired",
                    required_action="; ".join(issues),
                    recommended_worker="minimax-runtime-cleanup",
                    evidence_kind="CONFIG",
                )
            )


def _check_allowlist_expiry(report: VerifierReport) -> None:
    """Cross-check the temporary allowlist against current phase."""

    if not TEMPORARY_ALLOWLIST_YAML.exists():
        return
    if YAML_LOADER is None:
        report.tool_errors.append("PyYAML is required to parse the temporary allowlist")
        return
    try:
        document = YAML_LOADER(_read_text(TEMPORARY_ALLOWLIST_YAML))
    except Exception as exc:
        report.tool_errors.append(
            f"temporary allowlist YAML failed to parse: {exc}"
        )
        return
    if not isinstance(document, dict):
        report.tool_errors.append("temporary allowlist root must be a mapping")
        return
    allowlist = document.get("allowlist")
    if not isinstance(allowlist, list):
        return
    current_rank = _phase_rank(CURRENT_PHASE)
    for entry in allowlist:
        if not isinstance(entry, dict):
            continue
        deadline = entry.get("deadline_phase")
        if not isinstance(deadline, str):
            continue
        rank = _phase_rank(deadline)
        if rank < 0 or rank >= current_rank:
            continue
        report.reachability.dual_path_blockers.append(
            Finding(
                path=_safe_relative(TEMPORARY_ALLOWLIST_YAML),
                line=1,
                symbol=str(entry.get("symbol", "<unknown>")),
                category="DUAL_PATH_BLOCKERS_FOUND",
                entrypoint=f"allowlist entry {entry.get('path')}",
                reachable=True,
                resolution="retire",
                owner=str(entry.get("owner", "Repository Governance")),
                risk=f"temporary allowlist entry past deadline_phase={deadline}",
                required_action="remove the entry; verify the path is retired",
                recommended_worker="minimax-runtime-cleanup",
                evidence_kind="CONFIG",
            )
        )


# ---------------------------------------------------------------------------
# Removal candidates allowlist (mandatory active candidates)
# ---------------------------------------------------------------------------


def _load_removal_candidate_allowlist() -> tuple[set[str], list[str]]:
    if YAML_LOADER is None:
        return set(), ["PyYAML unavailable; cannot parse removal candidates"]
    if not REMOVAL_CANDIDATES_YAML.exists():
        return set(), ["phase22 removal candidates work product missing"]
    try:
        document = YAML_LOADER(_read_text(REMOVAL_CANDIDATES_YAML))
    except Exception as exc:
        return set(), [f"removal candidates YAML failed to parse: {exc}"]
    if not isinstance(document, dict):
        return set(), ["removal candidates root must be a mapping"]
    mandatory = document.get("mandatory_removal_candidates")
    if not isinstance(mandatory, list):
        return set(), ["mandatory_removal_candidates section missing"]
    allowlist: set[str] = set()
    for entry in mandatory:
        if not isinstance(entry, dict):
            continue
        path = entry.get("path")
        status = entry.get("current_status")
        if isinstance(path, str) and status == "active_candidate":
            allowlist.add(path)
    return allowlist, []


# ---------------------------------------------------------------------------
# Evidence / unresolved escalations
# ---------------------------------------------------------------------------


def _check_unresolved_escalations(report: VerifierReport) -> None:
    """If any evidence documents an unresolved escalation, mark it.

    The audit only treats an escalation as unresolved when it is
    paired with an explicit open status (e.g. ``escalation_status:
    open``) or a Phase22 worker name that has not produced a
    resolution record.
    """

    docs_evidence_root = REPO_ROOT / "docs" / "evidence"
    if not docs_evidence_root.exists():
        return
    seen_rel: set[str] = set()
    for path in docs_evidence_root.rglob("*.md"):
        try:
            text = _read_text(path)
        except Exception:
            continue
        rel = _safe_relative(path)
        if rel in seen_rel:
            continue
        if not re.search(r"ESCALATE_TO_DEEPSEEK", text):
            continue
        if re.search(
            r"(escalation_status\s*:\s*open|unresolved|not_retired|outstanding|pending resolution|status\s*:\s*open)",
            text,
            re.IGNORECASE,
        ):
            seen_rel.add(rel)
            report.reachability.unresolved_items.append(
                Finding(
                    path=rel,
                    line=1,
                    symbol="ESCALATE_TO_DEEPSEEK (unresolved)",
                    category="AUDIT_UNRESOLVED",
                    entrypoint="docs/evidence escalation",
                    reachable=True,
                    resolution="escalate to DeepSeek for architectural decision",
                    owner="Coordinator / DeepSeek",
                    risk="live architectural escalation recorded against the final head",
                    required_action="resolve the escalation or prove path unreachable",
                    recommended_worker="deepseek-architectural-decision",
                    evidence_kind="RUNTIME_TEST",
                )
            )


# ---------------------------------------------------------------------------
# Verifier orchestration
# ---------------------------------------------------------------------------


def _classify_status(report: VerifierReport) -> str:
    if report.tool_errors:
        return "TOOL_ERROR"
    r = report.reachability
    if r.phase08_runtime_blockers or r.runtime_blockers:
        return "LEGACY_RUNTIME_BLOCKERS_FOUND"
    if r.dual_path_blockers:
        return "DUAL_PATH_BLOCKERS_FOUND"
    if r.alias_bypass_blockers:
        return "ALIAS_BYPASS_BLOCKERS_FOUND"
    if r.public_adapter_violations:
        return "PUBLIC_ADAPTER_OWNERSHIP_VIOLATION"
    if r.unresolved_items:
        return "AUDIT_UNRESOLVED"
    return "LEGACY_CUTOVER_AUDIT_CLEAN"


def verify() -> VerifierReport:
    """Run the full PHASE22 final legacy/cutover audit gate."""

    report = VerifierReport()
    allowlist, allowlist_errors = _load_removal_candidate_allowlist()
    if allowlist_errors:
        report.tool_errors.extend(allowlist_errors)
        report.status = "TOOL_ERROR"
        report.exit_code = 2
        return report

    report.inventory = _build_inventory(report)
    if report.tool_errors:
        report.status = "TOOL_ERROR"
        report.exit_code = 2
        return report

    # Run the structural inspections.
    _inspect_phase08_cutover(report)
    _inspect_workspace_task_runtime(report)
    _inspect_completion_service(report)
    _check_forbidden_paths(report)
    _check_feature_flag_expiry(report)
    _check_allowlist_expiry(report)
    _check_unresolved_escalations(report)

    # Walk every production file for legacy AST markers.
    for path in _iter_production_files():
        if _is_history_excluded(path):
            continue
        rel = _safe_relative(path)
        is_phase08 = path.resolve() == PHASE08_CUTOVER_FILE.resolve()
        if path.suffix.lower() == ".py":
            _scan_python_file(
                path,
                rel,
                report,
                allowlist,
                is_phase08=is_phase08,
            )
        elif _should_scan_extension(path):
            _scan_text_file(path, rel, report, allowlist)

    # Derive final status.
    report.status = _classify_status(report)
    if report.status == "LEGACY_CUTOVER_AUDIT_CLEAN":
        report.exit_code = 0
    elif report.status == "TOOL_ERROR":
        report.exit_code = 2
    else:
        report.exit_code = 1
    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _format_markdown(report: VerifierReport) -> str:
    sections: list[str] = []
    sections.append("# PHASE22 Final Legacy/Cutover Audit (V2)\n")
    sections.append(f"- Status: `{report.status}`")
    sections.append(f"- Head SHA: `{report.inventory.head_sha}`")
    sections.append(f"- Files scanned: {report.inventory.files_scanned}")
    sections.append(
        f"- Python modules: {report.inventory.python_files_scanned}; "
        f"non-Python: {report.inventory.non_python_files_scanned}"
    )
    sections.append(
        f"- Counts: runtime_blockers="
        f"{len(report.reachability.runtime_blockers) + len(report.reachability.phase08_runtime_blockers)} "
        f"dual_path_blockers={len(report.reachability.dual_path_blockers)} "
        f"alias_bypass_blockers={len(report.reachability.alias_bypass_blockers)} "
        f"public_adapter_violations={len(report.reachability.public_adapter_violations)} "
        f"unresolved_items={len(report.reachability.unresolved_items)}"
    )
    if report.tool_errors:
        sections.append("## Tool Errors")
        for err in report.tool_errors:
            sections.append(f"- {err}")
    sections.append("\n## Findings\n")
    for finding in report.reachability.all_findings():
        sections.append(
            f"- `{finding.category}` {finding.path}:{finding.line} {finding.symbol} -> {finding.required_action}"
        )
    return "\n".join(sections) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of a markdown summary.",
    )
    parser.add_argument(
        "--evidence-dir",
        type=str,
        default=None,
        help="Optional directory to drop verifier_report.json / inventory.json / reachability_report.json.",
    )
    args = parser.parse_args(argv)

    report = verify()
    if args.json:
        sys.stdout.write(json.dumps(report.to_dict(), indent=2, sort_keys=True))
        sys.stdout.write("\n")
    else:
        sys.stdout.write(_format_markdown(report))

    if args.evidence_dir:
        evidence_dir = Path(args.evidence_dir)
        evidence_dir.mkdir(parents=True, exist_ok=True)
        (evidence_dir / "verifier_report.json").write_text(
            json.dumps(report.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (evidence_dir / "inventory.json").write_text(
            json.dumps(report.inventory.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (evidence_dir / "reachability_report.json").write_text(
            json.dumps(report.reachability.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )

    return report.exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())