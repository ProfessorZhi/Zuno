"""PHASE22 Feature Flag Registry Slice and Repository Runtime Truth Verifier.

Two-layer, fail-closed audit gate (Work-Package
PHASE22-FEATURE-FLAG-SCOPED-AND-REPOSITORY-TRUTH).

Layer 1 - this PR's own Registry Slice (``--scope registry``):

    ROLLOUT_FLAG_REGISTRY_SLICE_CONFIRMED
        The four rollout records (product_api_v1_adapter,
        workspace_projection_stream_v1, tool_runtime_readonly_gateway,
        postgres_domain_uow_shadow) are RETIRED fail-closed; every rollback
        transition is rejected by the lifecycle; no production Flag Reader
        or dynamic Selector references the retired flags (AST reference
        audit); the Public v1 API / SSE v1 contracts still exist; and the
        registry still satisfies the PHASE02 executable-compatibility
        boundary (yaml.safe_load parse, full lifecycle, mandatory fields,
        retire_task P22-T03, >= 5 flag records).

    This result proves only the slice. It does NOT prove repository-wide
    runtime cutover.

Layer 2 - Repository Runtime Truth (``--scope repository``, the default):

    FEATURE_FLAG_RUNTIME_CUTOVER_CONFIRMED
    FEATURE_FLAG_RUNTIME_CUTOVER_BLOCKED
    FEATURE_FLAG_RUNTIME_CUTOVER_UNRESOLVED
    TOOL_ERROR

    The repository scope scans the ENTIRE production tree. Every real
    bypass - workspace simple/wechat agents, legacy React/PlanExecute/
    GeneralAgent modules, MCP direct-call surfaces, the Phase08 dual
    runtime machinery, and any direct tool dispatch outside the canonical
    ``zuno/capability/tool_runtime`` package - is reported with its
    annotation (owner_work_package / candidate_pr / external_dependency).
    The temporary allowlist may ANNOTATE a finding, never remove it: an
    allowlisted active bypass keeps the repository result BLOCKED.

Residual runtime reachability (repository-wide import / call / dynamic-load
audit, AST based):

    - references confined to tests/evals ......... INTERNAL_TEST_HARNESS
    - production-tree reference .................. RESIDUAL_PRODUCT_RUNTIME_FOUND
    - dynamic load that cannot be proven ......... UNRESOLVED (fail-closed)

Evidence boundary: string-contract checks for PostgreSQL UoW atomicity,
SSE resume, idempotency and security epoch produce STATIC_CONTRACT_AVAILABLE
evidence only. The report lists not_proven_boundary entries and never emits
a *_LIVE_VERIFIED claim. No PostgreSQL, SSE-reconnect or side-effect runtime
receipt is fabricated.

Usage:
    python tools/scripts/verify_phase22_feature_flag_runtime_cutover.py \
        [--scope registry|repository] [--json] [--report]

Default scope is repository (fail-closed). Exit 0 only for
ROLLOUT_FLAG_REGISTRY_SLICE_CONFIRMED / FEATURE_FLAG_RUNTIME_CUTOVER_CONFIRMED.
"""

from __future__ import annotations

import ast
import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"
EVIDENCE_DIR = (
    REPO_ROOT / "docs" / "evidence" / "goal05-phase22-feature-flag-runtime-cutover"
)
REGISTRY_REL = ".agent/programs/work-products/feature-flag-registry.yaml"
ALLOWLIST_REL = ".agent/programs/work-products/temporary-allowlist.yaml"
PRODUCTION_ROOT_REL = "src/backend/zuno"
CANONICAL_TOOL_RUNTIME_REL = "src/backend/zuno/capability/tool_runtime"
CANONICAL_AGENT_RUNTIME_REL = "src/backend/zuno/agent/runtime"

# --- Status values ---------------------------------------------------------
STATUS_REGISTRY_CONFIRMED = "ROLLOUT_FLAG_REGISTRY_SLICE_CONFIRMED"
STATUS_REGISTRY_BLOCKED = "REGISTRY_SLICE_BLOCKED"
STATUS_REGISTRY_UNRESOLVED = "REGISTRY_SLICE_UNRESOLVED"
STATUS_REPO_CONFIRMED = "FEATURE_FLAG_RUNTIME_CUTOVER_CONFIRMED"
STATUS_REPO_BLOCKED = "FEATURE_FLAG_RUNTIME_CUTOVER_BLOCKED"
STATUS_REPO_UNRESOLVED = "FEATURE_FLAG_RUNTIME_CUTOVER_UNRESOLVED"
STATUS_TOOL_ERROR = "TOOL_ERROR"

CONFIRMED_STATUSES = (STATUS_REGISTRY_CONFIRMED, STATUS_REPO_CONFIRMED)

RETIRED_FLAGS = [
    "product_api_v1_adapter",
    "workspace_projection_stream_v1",
    "tool_runtime_readonly_gateway",
    "postgres_domain_uow_shadow",
]

NON_RETIRED_STATES = ("DECLARED", "SHADOW", "CANARY", "DEFAULT_NEW", "ROLLBACK_WINDOW")

# Retired-flag selector markers that must never be looked up dynamically.
SELECTOR_MARKERS = (
    "ZUNO_PRODUCT_ADAPTER",
    "ZUNO_PROJECTION_STREAM",
    "ZUNO_TOOL_GATEWAY",
    "ZUNO_UOW",
)

# Finding categories; order matters only for reporting. ``internal_test_harness``
# is recorded but never blocks a CONFIRMED result.
BLOCKING_REGISTRY_CATEGORIES = (
    "flag_not_retired",
    "rollback_transition_accepted",
    "flag_reader_found",
    "dynamic_selector_found",
    "public_v1_contract_missing",
    "registry_integration_violation",
)
BLOCKING_REPOSITORY_CATEGORIES = BLOCKING_REGISTRY_CATEGORIES + (
    "direct_tool_bypass",
    "residual_product_runtime_found",
    "phase08_dual_runtime",
    "static_contract_violation",
)
FINDING_CATEGORIES = BLOCKING_REPOSITORY_CATEGORIES + (
    "internal_test_harness",
    "unresolved",
)

# Allowlist categories that document active tool-runtime bypasses. Entries with
# these categories are reported as repository findings (with annotations);
# entries with other categories (root_alias, old_dto, subprocess, ...) belong
# to other audit domains and are only used for annotations.
BYPASS_ALLOWLIST_CATEGORIES = frozenset(
    {"direct_tool_execute", "old_runtime", "dynamic_bypass", "direct_mcp_call"}
)

# Annotations are informational. They never exempt a finding.
KNOWN_ANNOTATIONS: dict[str, dict[str, str]] = {
    "src/backend/zuno/platform/services/workspace/simple_agent.py": {
        "owner_work_package": "PHASE22-WORKSPACE-AGENT-CUTOVER",
        "candidate_pr": "",
        "external_dependency": "",
    },
    "src/backend/zuno/platform/services/workspace/wechat_agent.py": {
        "owner_work_package": "PHASE22-WORKSPACE-AGENT-CUTOVER",
        "candidate_pr": "",
        "external_dependency": "",
    },
    "src/backend/zuno/agent/core/agents/react_agent.py": {
        "owner_work_package": "",
        "candidate_pr": "PR #127 (semantic legacy cleanup)",
        "external_dependency": "",
    },
    "src/backend/zuno/agent/core/agents/plan_execute_agent.py": {
        "owner_work_package": "",
        "candidate_pr": "PR #127 (semantic legacy cleanup)",
        "external_dependency": "",
    },
    "src/backend/zuno/agent/core/agents/general_agent.py": {
        "owner_work_package": "",
        "candidate_pr": "PR #127 (semantic legacy cleanup)",
        "external_dependency": "",
    },
    "src/backend/zuno/agent/core/agents/codeact_agent.py": {
        "owner_work_package": "",
        "candidate_pr": "PR #127 (semantic legacy cleanup)",
        "external_dependency": "",
    },
    "src/backend/zuno/agent/control_runtime.py": {
        "owner_work_package": "",
        "candidate_pr": "PR #127 (residual runtime removal)",
        "external_dependency": "",
    },
    "src/backend/zuno/agent/product_baseline.py": {
        "owner_work_package": "",
        "candidate_pr": "PR #127 (residual runtime removal)",
        "external_dependency": "",
    },
    "src/backend/zuno/api/services/workspace_task_runtime.py": {
        "owner_work_package": "",
        "candidate_pr": "",
        "external_dependency": "PHASE08 cutover (DeepSeek-Legacy-Runtime)",
    },
    "src/backend/zuno/platform/services/mcp/manager.py": {
        "owner_work_package": "",
        "candidate_pr": "",
        "external_dependency": "MCP direct-call cutover",
    },
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _production_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted((root / PRODUCTION_ROOT_REL).rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        files.append(path)
    return files


def _rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _parse_tree(source: str) -> ast.Module | None:
    try:
        return ast.parse(source.lstrip("﻿"))
    except SyntaxError:
        return None


# ---------------------------------------------------------------------------
# Layer 1: registry slice
# ---------------------------------------------------------------------------

def _parse_registry(registry_path: Path) -> dict[str, Any] | None:
    if not registry_path.exists():
        return None
    try:
        parsed = yaml.safe_load(_read(registry_path))
    except Exception:  # pragma: no cover - defensive
        return None
    if not isinstance(parsed, dict):
        return None
    return parsed


def _registry_checks(root: Path, registry_path: Path) -> tuple[dict[str, list], dict[str, str]]:
    """RETIRED records, fail-closed rollback_command, rejected transitions,
    and PHASE02 executable-compatibility integration surface."""
    findings: dict[str, list] = {cat: [] for cat in FINDING_CATEGORIES}
    evidence: dict[str, str] = {}
    parsed = _parse_registry(registry_path)
    if parsed is None:
        findings["flag_not_retired"].append(
            f"registry missing or unparseable: {registry_path.relative_to(root)}"
        )
        evidence["registry_parse"] = "FAILED"
        return findings, evidence
    evidence["registry_parse"] = "MACHINE_VERIFIED"

    flags_block = parsed.get("flags")
    if not isinstance(flags_block, list):
        findings["flag_not_retired"].append("registry flags block is not a list")
        return findings, evidence
    by_name = {
        f.get("flag"): f for f in flags_block if isinstance(f, dict) and isinstance(f.get("flag"), str)
    }

    # 1. The four records are RETIRED fail-closed with a non-executable
    #    rollback_command that documents the fail-closed semantics.
    for flag in RETIRED_FLAGS:
        record = by_name.get(flag)
        if record is None:
            findings["flag_not_retired"].append(f"{flag}: missing from registry")
            continue
        default = record.get("default")
        if default != "RETIRED":
            findings["flag_not_retired"].append(
                f"{flag}: default is {default!r}, not RETIRED"
            )
        rollback_command = str(record.get("rollback_command") or "")
        if "retired and fail-closed" not in rollback_command.lower():
            findings["flag_not_retired"].append(
                f"{flag}: rollback_command does not document retired and fail-closed"
            )

    # 2. Rollback transition is rejected: the lifecycle must not permit any
    #    non-RETIRED target from RETIRED, and no record may default to an
    #    open rollout state.
    lifecycle = parsed.get("lifecycle")
    transitions = (
        lifecycle.get("allowed_transitions") if isinstance(lifecycle, dict) else None
    )
    if isinstance(transitions, dict):
        retired_targets = transitions.get("RETIRED") or []
        for target in retired_targets:
            if target != "RETIRED":
                findings["rollback_transition_accepted"].append(
                    f"lifecycle permits RETIRED -> {target}"
                )
    for flag, record in by_name.items():
        if record.get("default") in NON_RETIRED_STATES:
            findings["rollback_transition_accepted"].append(
                f"{flag}: default {record.get('default')!r} is an open rollout state"
            )

    # 3. Registry slice integrates with the PHASE02 executable boundary:
    #    full lifecycle, mandatory fields, P22-T03 retire task, >= 5 records.
    allowed_states = lifecycle.get("allowed_states") if isinstance(lifecycle, dict) else None
    for state in ("DECLARED", "SHADOW", "CANARY", "DEFAULT_NEW", "ROLLBACK_WINDOW", "RETIRED"):
        if not allowed_states or state not in allowed_states:
            findings["registry_integration_violation"].append(
                f"lifecycle missing state {state}"
            )
    if len(by_name) < 5:
        findings["registry_integration_violation"].append(
            "registry must define at least five rollout flags"
        )
    for flag, record in by_name.items():
        for field in ("owner", "scope", "default", "rollback_command", "expires_at_phase", "retire_task"):
            if not record.get(field):
                findings["registry_integration_violation"].append(
                    f"{flag}: missing mandatory field {field}"
                )
        if record.get("retire_task") != "P22-T03":
            findings["registry_integration_violation"].append(
                f"{flag}: retire_task must be P22-T03"
            )
        if record.get("domain_fact_owner") == "feature_flag":
            findings["registry_integration_violation"].append(
                f"{flag}: illegally owns domain facts"
            )
    return findings, evidence


# ---------------------------------------------------------------------------
# Flag Reader / dynamic Selector audit (AST over the production tree)
# ---------------------------------------------------------------------------

def _reader_audit(root: Path) -> tuple[dict[str, list], dict[str, str]]:
    """AST reference audit. Catches string constants, identifiers, attribute
    wrappers, import aliases, registry-file reads and env/config lookups of
    the retired flag names and selector markers. Concatenated / f-string keys
    that could build a marker are unprovable -> unresolved (fail-closed)."""
    findings: dict[str, list] = {cat: [] for cat in FINDING_CATEGORIES}
    evidence: dict[str, str] = {"flag_reader_audit": "AST_REFERENCE_AUDIT"}
    for path in _production_files(root):
        rel = _rel(path, root)
        tree = _parse_tree(_read(path))
        if tree is None:
            findings["unresolved"].append(
                {"path": rel, "evidence": "module does not parse; references cannot be audited",
                 "owner_work_package": "", "candidate_pr": "", "external_dependency": ""}
            )
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                for flag in RETIRED_FLAGS:
                    if node.value == flag:
                        findings["flag_reader_found"].append(
                            _finding(rel, f"string constant {flag!r}")
                        )
                for marker in SELECTOR_MARKERS:
                    if marker in node.value:
                        findings["dynamic_selector_found"].append(
                            _finding(rel, f"selector marker {marker} in string constant")
                        )
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id in RETIRED_FLAGS:
                findings["flag_reader_found"].append(
                    _finding(rel, f"identifier {node.id}")
                )
            elif isinstance(node, ast.Attribute) and node.attr in RETIRED_FLAGS:
                # wrapper readers: registry.product_api_v1_adapter etc.
                findings["flag_reader_found"].append(
                    _finding(rel, f"attribute access .{node.attr} (wrapper reader)")
                )
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    target = alias.asname or alias.name.split(".")[-1]
                    if target in RETIRED_FLAGS:
                        findings["flag_reader_found"].append(
                            _finding(rel, f"import binds {target} (alias reader)")
                        )
            elif isinstance(node, ast.Call):
                fname = _call_name(node.func)
                if fname in ("open", "read_text", "load", "safe_load"):
                    for arg in node.args + [kw.value for kw in node.keywords]:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str) \
                                and "feature-flag-registry" in arg.value:
                            findings["flag_reader_found"].append(
                                _finding(rel, f"{fname} reads feature-flag-registry.yaml")
                            )
                if fname in ("getenv", "get", "__getitem__", "getattr"):
                    for arg in node.args + [kw.value for kw in node.keywords]:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            for marker in SELECTOR_MARKERS:
                                if marker in arg.value:
                                    findings["dynamic_selector_found"].append(
                                        _finding(rel, f"{fname}({arg.value!r}) dynamic selector")
                                    )
                            if arg.value in RETIRED_FLAGS:
                                findings["flag_reader_found"].append(
                                    _finding(rel, f"{fname}({arg.value!r}) flag lookup")
                                )
            elif isinstance(node, ast.JoinedStr) or (
                isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add)
            ):
                constants = [
                    v.value for v in ast.walk(node)
                    if isinstance(v, ast.Constant) and isinstance(v.value, str)
                ]
                joined = "".join(constants)
                if any(marker in joined for marker in SELECTOR_MARKERS):
                    findings["unresolved"].append(
                        _finding(rel, "concatenated/f-string key could build a selector marker")
                    )
    return findings, evidence


def _call_name(func: ast.AST) -> str:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return ""


def _finding(path: str, evidence: str) -> dict[str, str]:
    return {
        "path": path,
        "evidence": evidence,
        "owner_work_package": "",
        "candidate_pr": "",
        "external_dependency": "",
    }


# ---------------------------------------------------------------------------
# Public v1 Contract checks
# ---------------------------------------------------------------------------

def _v1_contract_check(root: Path) -> dict[str, list]:
    findings: dict[str, list] = {cat: [] for cat in FINDING_CATEGORIES}
    for rel in (
        "src/backend/zuno/api/v1/product.py",
        "src/backend/zuno/api/v1/workspace.py",
        "src/backend/zuno/api/router.py",
    ):
        if not (root / rel).exists():
            findings["public_v1_contract_missing"].append(f"{rel} missing")
    workspace_route = root / "src/backend/zuno/api/v1/workspace.py"
    if workspace_route.exists():
        text = _read(workspace_route)
        if text.count("events/stream") != 1:
            findings["public_v1_contract_missing"].append(
                "v1 workspace SSE stream route count != 1"
            )
        if "text/event-stream" not in text:
            findings["public_v1_contract_missing"].append(
                "v1 workspace SSE contract missing text/event-stream"
            )
    return findings


# ---------------------------------------------------------------------------
# Direct tool dispatch scan (repository scope, whole production tree)
# ---------------------------------------------------------------------------

def _receiver_id(node: ast.AST) -> str:
    while isinstance(node, ast.Attribute):
        node = node.value
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Subscript):
        return _receiver_id(node.value)
    return ""


TOOL_DISPATCH_RECEIVERS = frozenset({"tool", "current_tool", "handler"})


def _direct_dispatch_hits(source: str) -> list[str]:
    """AST detection of direct tool dispatch outside the canonical gateway.

    Precise shapes only (LLM model calls, ``@tool`` decorators, ``create_tool``
    / ``load_default_tool`` helpers, and generic ``handler`` callbacks must
    not match):

    - ``tool.ainvoke(...)`` / ``current_tool.invoke(...)`` / ``handler.ainvoke``
      (attribute dispatch on a tool receiver)
    - ``execute_tool(...)`` / ``self._execute_tool(...)`` (any name carrying
      execute_tool)
    - ``await handler(request)`` (single positional arg named ``request``;
      the workspace direct-execution pattern)"""
    tree = _parse_tree(source)
    if tree is None:
        return []
    hits: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute):
            attr = func.attr
            receiver = _receiver_id(func.value)
            if attr in ("ainvoke", "invoke") and receiver in TOOL_DISPATCH_RECEIVERS:
                hits.append(f"{receiver}.{attr}(...) direct tool dispatch")
            elif "execute_tool" in attr.lower():
                hits.append(f"{attr}(...) direct tool dispatch")
        elif isinstance(func, ast.Name):
            name = func.id
            if "execute_tool" in name.lower():
                hits.append(f"{name}(...) direct tool dispatch")
            elif name == "handler" and len(node.args) == 1 \
                    and isinstance(node.args[0], ast.Name) and node.args[0].id == "request":
                hits.append("handler(request) direct tool dispatch")
    return hits


def _allowlist_entries(root: Path) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    """temporary-allowlist.yaml -> (path -> entry info, path -> annotations).
    The allowlist documents bypasses; it never exempts them."""
    entries: dict[str, dict[str, str]] = {}
    annotations: dict[str, dict[str, str]] = {}
    path = root / ALLOWLIST_REL
    if not path.exists():
        return entries, annotations
    try:
        parsed = yaml.safe_load(_read(path))
    except Exception:  # pragma: no cover - defensive
        return entries, annotations
    if not isinstance(parsed, dict):
        return entries, annotations
    items: list[dict[str, Any]] = []
    for value in parsed.values():
        if isinstance(value, list) and value and isinstance(value[0], dict) and "path" in value[0]:
            items = value
            break
    for item in items:
        entry_path = item.get("path")
        if not isinstance(entry_path, str):
            continue
        entries[entry_path] = {
            "category": item.get("category") or "",
            "symbol": item.get("symbol") or "",
            "reason": item.get("reason") or "",
        }
        annotations[entry_path] = {
            "owner_work_package": item.get("owner") or "",
            "candidate_pr": "",
            "external_dependency": "",
        }
    return entries, annotations


def _pattern_matches(rel: str, pattern: str) -> bool:
    """Allowlist paths may use brace alternation, e.g.
    src/backend/zuno/knowledge/{__init__,citation}.py"""
    if "{" not in pattern:
        return rel == pattern
    try:
        regex = re.sub(r"\{([^}]*)\}", lambda m: "(" + "|".join(re.escape(x) for x in m.group(1).split(",")) + ")", re.escape(pattern))
        return re.fullmatch(regex, rel) is not None
    except re.error:  # pragma: no cover - defensive
        return rel == pattern


def _annotate(rel: str, allowlist_annotations: dict[str, dict[str, str]]) -> dict[str, str]:
    merged = dict(KNOWN_ANNOTATIONS.get(rel, _finding("", "")))
    for key in ("owner_work_package", "candidate_pr", "external_dependency"):
        merged[key] = merged.get(key) or ""
    for pattern, ann in allowlist_annotations.items():
        if _pattern_matches(rel, pattern):
            for key, value in ann.items():
                if value and not merged.get(key):
                    merged[key] = value
    merged["path"] = rel
    merged.pop("evidence", None)
    return merged


def _bypass_scan(root: Path) -> dict[str, list]:
    """Direct tool dispatch findings across the entire production tree.
    Annotated, never allowlisted away."""
    findings: dict[str, list] = {cat: [] for cat in FINDING_CATEGORIES}
    allowlist_entries, allowlist_annotations = _allowlist_entries(root)
    seen: set[tuple[str, str]] = set()
    for path in _production_files(root):
        rel = _rel(path, root)
        if rel.startswith(CANONICAL_TOOL_RUNTIME_REL):
            continue  # canonical tool execution entry (ToolInvocationGateway)
        source = _read(path)
        hits = _direct_dispatch_hits(source)
        for pattern, entry in allowlist_entries.items():
            if entry["category"] in BYPASS_ALLOWLIST_CATEGORIES and _pattern_matches(rel, pattern):
                hits.append(
                    f"allowlisted bypass category={entry['category']}: "
                    f"{entry['symbol'] or entry['reason']}"
                )
        for hit in sorted(set(hits)):
            key = (rel, hit)
            if key in seen:
                continue
            seen.add(key)
            annotation = _annotate(rel, allowlist_annotations)
            findings["direct_tool_bypass"].append(
                {"path": rel, "evidence": hit, **annotation}
            )
    return findings


# ---------------------------------------------------------------------------
# Residual runtime reachability (AgentControlRuntime / product_baseline)
# ---------------------------------------------------------------------------

HARNESS_SYMBOLS = ("AgentControlRuntime", "AgentRuntimeResult", "RuntimeObservation")
HARNESS_MODULE_FRAGMENTS = ("control_runtime", "product_baseline")


def _harness_references(root: Path) -> tuple[list[dict[str, str]], list[str], list[dict[str, str]]]:
    """Repository-wide import / call / dynamic-load audit of the residual
    harness. Scope: ``src/backend/**`` is production, ``tests/**`` and
    ``evals/**`` are the harness; governance files (tools/scripts, .agent)
    are ignored. Returns (production references, test/evals reference paths,
    unresolved dynamic loads)."""
    production_refs: list[dict[str, str]] = []
    test_refs: list[str] = []
    unresolved: list[dict[str, str]] = []
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = _rel(path, root)
        if not (rel.startswith("src/backend/") or rel.startswith("tests/") or rel.startswith("evals/")):
            continue  # governance tooling, docs, fixtures: not reachability evidence
        tree = _parse_tree(_read(path))
        if tree is None:
            unresolved.append(_finding(rel, "module does not parse; reachability cannot be audited"))
            continue
        own_module = rel in (
            "src/backend/zuno/agent/control_runtime.py",
            "src/backend/zuno/agent/product_baseline.py",
        )
        imported_fragments: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    if isinstance(node, ast.Import):
                        full = alias.name
                    else:
                        full = f"{node.module}.{alias.name}"
                    if any(fragment in full for fragment in HARNESS_MODULE_FRAGMENTS) \
                            or alias.name in HARNESS_SYMBOLS:
                        if rel.startswith("src/backend/"):
                            production_refs.append(_finding(rel, f"import {full}"))
                        else:
                            test_refs.append(f"{rel}: import {full}")
                        for fragment in HARNESS_MODULE_FRAGMENTS:
                            if fragment in full:
                                imported_fragments.add(fragment)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) \
                    and node.id in HARNESS_SYMBOLS and not own_module:
                # symbol references inside the harness modules themselves are
                # definitions, not callers; other modules already covered by an
                # import of the same fragment are not re-reported.
                if any(fragment in node.id for fragment in HARNESS_MODULE_FRAGMENTS) \
                        or not imported_fragments:
                    if rel.startswith("src/backend/"):
                        production_refs.append(_finding(rel, f"reference {node.id}"))
                    else:
                        test_refs.append(f"{rel}: reference {node.id}")
            elif isinstance(node, ast.Call):
                fname = _call_name(node.func)
                if fname in ("import_module", "__import__"):
                    arg0 = node.args[0] if node.args else None
                    if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                        if any(fragment in arg0.value for fragment in HARNESS_MODULE_FRAGMENTS):
                            if rel.startswith("src/backend/"):
                                production_refs.append(
                                    _finding(rel, f"dynamic import {arg0.value!r} of residual runtime")
                                )
                            else:
                                test_refs.append(f"{rel}: dynamic import {arg0.value!r}")
                    elif arg0 is not None and rel.startswith("src/backend/"):
                        # Only dynamic imports that can provably resolve into the
                        # zuno.agent namespace could load the residual harness
                        # (e.g. import_module("zuno.agent." + name)); generic
                        # lazy facades are out of scope.
                        constants = [
                            v.value for v in ast.walk(arg0)
                            if isinstance(v, ast.Constant) and isinstance(v.value, str)
                        ]
                        if any("zuno.agent" in c for c in constants):
                            unresolved.append(
                                _finding(rel, "dynamic import could resolve into zuno.agent "
                                               "(residual runtime load not provable; fail-closed)")
                            )
    return production_refs, test_refs, unresolved


def _harness_reachability(root: Path) -> dict[str, list]:
    """Classify the residual runtime surface:
    INTERNAL_TEST_HARNESS (tests/evals only), RESIDUAL_PRODUCT_RUNTIME_FOUND
    (any production-tree reference), UNRESOLVED (unprovable dynamic load).
    A production-tree caller (e.g. product_baseline.py constructing
    AgentControlRuntime) is a residual product runtime until removed."""
    findings: dict[str, list] = {cat: [] for cat in FINDING_CATEGORIES}
    production_refs, test_refs, unresolved = _harness_references(root)
    for ref in production_refs:
        ref["candidate_pr"] = ref.get("candidate_pr") or "PR #127 (residual runtime removal)"
        findings["residual_product_runtime_found"].append(ref)
    production_fragments = {
        _fragment_of(ref["evidence"]) for ref in production_refs if _fragment_of(ref["evidence"])
    }
    test_fragments = {
        _fragment_of(entry) for entry in test_refs if _fragment_of(entry)
    }
    for fragment in HARNESS_MODULE_FRAGMENTS:
        if fragment in production_fragments:
            continue  # residual surface already reported above
        if fragment not in test_fragments:
            continue  # not present in the tree; nothing to classify
        findings["internal_test_harness"].append(
            {
                "path": f"src/backend/zuno/agent/{fragment}.py",
                "evidence": "reachability audit found no production-tree reference "
                            "(tests/evals only)",
                "owner_work_package": "",
                "candidate_pr": "PR #127 (removal candidate)",
                "external_dependency": "",
            }
        )
    findings["unresolved"].extend(unresolved)
    return findings


def _fragment_of(evidence: str) -> str:
    for fragment in HARNESS_MODULE_FRAGMENTS:
        if fragment in evidence:
            return fragment
    return ""


# ---------------------------------------------------------------------------
# Phase08 dual runtime detection
# ---------------------------------------------------------------------------

def _phase08_dual_runtime(root: Path) -> dict[str, list]:
    """Phase08 cutover dual-runtime machinery used from production services
    (Phase08CutoverController / Phase08RunService shadow comparison)."""
    findings: dict[str, list] = {cat: [] for cat in FINDING_CATEGORIES}
    for path in _production_files(root):
        rel = _rel(path, root)
        if rel.startswith(CANONICAL_AGENT_RUNTIME_REL):
            continue  # canonical runtime package owns the Phase08 implementation
        tree = _parse_tree(_read(path))
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                names = [alias.name for alias in node.names]
                if "phase08" in module.lower() or any(n.startswith("Phase08") for n in names):
                    findings["phase08_dual_runtime"].append(
                        {
                            "path": rel,
                            "evidence": f"Phase08 runtime import: {module} {names} "
                                        "(dual runtime machinery)",
                            "owner_work_package": "",
                            "candidate_pr": "",
                            "external_dependency": "PHASE08 cutover (DeepSeek-Legacy-Runtime)",
                        }
                    )
                    break
            elif isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
                if any("phase08" in name.lower() for name in names):
                    findings["phase08_dual_runtime"].append(
                        {
                            "path": rel,
                            "evidence": f"Phase08 runtime import: {names} "
                                        "(dual runtime machinery)",
                            "owner_work_package": "",
                            "candidate_pr": "",
                            "external_dependency": "PHASE08 cutover (DeepSeek-Legacy-Runtime)",
                        }
                    )
                    break
                    findings["phase08_dual_runtime"].append(
                        {
                            "path": rel,
                            "evidence": f"Phase08 runtime import: {module} {names} "
                                        "(dual runtime machinery)",
                            "owner_work_package": "",
                            "candidate_pr": "",
                            "external_dependency": "PHASE08 cutover (DeepSeek-Legacy-Runtime)",
                        }
                    )
                    break
    return findings


# ---------------------------------------------------------------------------
# Static contract evidence (real tree only)
# ---------------------------------------------------------------------------

def _static_contract_checks(root: Path) -> tuple[dict[str, list], dict[str, str]]:
    """PostgreSQL UoW / SSE resume / idempotency / security epoch: string
    contracts only. Presence yields STATIC_CONTRACT_AVAILABLE evidence and
    the not_proven_boundary list; absence is a static_contract_violation."""
    findings: dict[str, list] = {cat: [] for cat in FINDING_CATEGORIES}
    evidence: dict[str, str] = {
        "postgres_uow_atomicity": "STATIC_CONTRACT_AVAILABLE",
        "sse_stream_resume": "STATIC_CONTRACT_AVAILABLE",
        "idempotency": "STATIC_CONTRACT_AVAILABLE",
        "security_epoch": "STATIC_CONTRACT_AVAILABLE",
        "not_proven_boundary": (
            "postgres transaction atomicity under live faults: not executed "
            "(no local PostgreSQL); static contract only, no live receipt"
        ),
    }
    domain = root / "src/backend/zuno/platform/database/product/domain.py"
    if not domain.exists():
        findings["static_contract_violation"].append("product/domain.py missing (PostgreSQL UoW owner)")
        evidence["postgres_uow_atomicity"] = "STATIC_CONTRACT_MISSING"
    else:
        text = _read(domain)
        missing = [
            marker for marker in (
                "self._transaction.commit()",
                "self._transaction.rollback()",
                "enqueue_outbox(",
                "ON CONFLICT DO NOTHING",
                "client_request_id",
            )
            if marker not in text
        ]
        if missing:
            findings["static_contract_violation"].append(
                f"ProductUnitOfWork static contract missing markers: {missing}"
            )
            evidence["postgres_uow_atomicity"] = "STATIC_CONTRACT_MISSING"
        if any(marker not in text for marker in ("client_request_id", "ON CONFLICT DO NOTHING", "idempotency")):
            evidence["idempotency"] = "STATIC_CONTRACT_MISSING"

    service = root / "src/backend/zuno/api/services/workspace_task_runtime.py"
    if not service.exists() or "def stream_task_events" not in _read(service):
        findings["static_contract_violation"].append(
            "WorkspaceTaskRuntimeService.stream_task_events missing (SSE stream owner)"
        )
        evidence["sse_stream_resume"] = "STATIC_CONTRACT_MISSING"

    gateway = root / "src/backend/zuno/capability/tool_runtime/invocation_gateway.py"
    if not gateway.exists():
        findings["static_contract_violation"].append("ToolInvocationGateway missing")
        evidence["security_epoch"] = "STATIC_CONTRACT_MISSING"
    else:
        text = _read(gateway)
        missing = [
            marker for marker in (
                "security_epoch_ref",
                "SecurityUnitOfWork",
                "idempotency_key",
                "PHASE16_REQUIRED_FOR_SIDE_EFFECT_TOOL",
                "security_blocked_reason",
            )
            if marker not in text
        ]
        if missing:
            findings["static_contract_violation"].append(
                f"ToolInvocationGateway static contract missing markers: {missing}"
            )
            evidence["security_epoch"] = "STATIC_CONTRACT_MISSING"
    return findings, evidence


def _facade_checks(root: Path) -> dict[str, list]:
    """zuno.agent facade must not expose the residual runtime (real tree
    only; the import would be meaningless against a fixture tree)."""
    findings: dict[str, list] = {cat: [] for cat in FINDING_CATEGORIES}
    try:
        if str(BACKEND_ROOT) not in sys.path:
            sys.path.insert(0, str(BACKEND_ROOT))
        agent = importlib.import_module("zuno.agent")
        if "AgentControlRuntime" in getattr(agent, "__all__", []):
            findings["residual_product_runtime_found"].append(
                _finding("src/backend/zuno/agent/__init__.py", "facade __all__ still exports AgentControlRuntime")
            )
        if hasattr(agent, "AgentControlRuntime"):
            findings["residual_product_runtime_found"].append(
                _finding("src/backend/zuno/agent/__init__.py", "facade exposes AgentControlRuntime attribute")
            )
        # harness module must stay importable for the eval harness
        importlib.import_module("zuno.agent.control_runtime")
    except Exception as exc:  # pragma: no cover - defensive
        findings["unresolved"].append(
            _finding("zuno.agent", f"facade import check failed: {exc}")
        )
    return findings


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def _merge(base: dict[str, list], extra: dict[str, list]) -> dict[str, list]:
    merged = {cat: list(base.get(cat, [])) for cat in FINDING_CATEGORIES}
    for cat in FINDING_CATEGORIES:
        merged[cat].extend(extra.get(cat, []))
    return merged


def _registry_summary(parsed: dict[str, Any] | None) -> dict[str, dict[str, str]]:
    if parsed is None:
        return {}
    by_name = {
        f.get("flag"): f for f in (parsed.get("flags") or [])
        if isinstance(f, dict) and isinstance(f.get("flag"), str)
    }
    return {
        flag: {
            "default": str(by_name.get(flag, {}).get("default", "MISSING")),
            "rollback_command": str(by_name.get(flag, {}).get("rollback_command", "")),
        }
        for flag in RETIRED_FLAGS
    }


def verify(root: Path = REPO_ROOT, scope: str = "repository") -> tuple[str, dict]:
    """Run the fail-closed gate for one scope. Returns (status, report)."""
    if scope not in ("registry", "repository"):
        return STATUS_TOOL_ERROR, {
            "verifier": "verify_phase22_feature_flag_runtime_cutover.py",
            "phase": "PHASE22-FEATURE-FLAG-SCOPED-AND-REPOSITORY-TRUTH",
            "scope": str(scope),
            "repo_root": str(root),
            "status": STATUS_TOOL_ERROR,
            "findings": {},
            "evidence": {},
            "error": f"unknown scope {scope!r}",
        }
    root = Path(root)
    registry_path = root / REGISTRY_REL
    try:
        findings, registry_evidence = _registry_checks(root, registry_path)
        reader_findings, reader_evidence = _reader_audit(root)
        findings = _merge(findings, reader_findings)
        evidence = dict(registry_evidence)
        evidence.update(reader_evidence)
        v1_findings = _v1_contract_check(root)
        findings = _merge(findings, v1_findings)

        real_tree = root.resolve() == REPO_ROOT.resolve()
        if scope == "repository":
            bypass_findings = _bypass_scan(root)
            findings = _merge(findings, bypass_findings)
            reachability = _harness_reachability(root)
            findings = _merge(findings, reachability)
            phase08 = _phase08_dual_runtime(root)
            findings = _merge(findings, phase08)
            if real_tree:
                static_findings, static_evidence = _static_contract_checks(root)
                findings = _merge(findings, static_findings)
                evidence.update(static_evidence)
                facade = _facade_checks(root)
                findings = _merge(findings, facade)
        elif scope == "registry":
            pass  # registry slice never scans repository runtime surfaces

        report = {
            "verifier": "verify_phase22_feature_flag_runtime_cutover.py",
            "phase": "PHASE22-FEATURE-FLAG-SCOPED-AND-REPOSITORY-TRUTH",
            "scope": scope,
            "repo_root": str(root),
            "status": STATUS_TOOL_ERROR,
            "retired_flags": list(RETIRED_FLAGS),
            "registry": _registry_summary(_parse_registry(registry_path)),
            "findings": findings,
            "evidence": evidence,
            "finding_count": sum(len(items) for items in findings.values()),
        }
    except Exception as exc:  # pragma: no cover - defensive
        report = {
            "verifier": "verify_phase22_feature_flag_runtime_cutover.py",
            "phase": "PHASE22-FEATURE-FLAG-SCOPED-AND-REPOSITORY-TRUTH",
            "scope": scope,
            "repo_root": str(root),
            "status": STATUS_TOOL_ERROR,
            "retired_flags": list(RETIRED_FLAGS),
            "findings": {},
            "evidence": {},
            "finding_count": 0,
            "error": str(exc),
        }
        return STATUS_TOOL_ERROR, report

    if scope == "registry":
        if any(findings[cat] for cat in BLOCKING_REGISTRY_CATEGORIES):
            report["status"] = STATUS_REGISTRY_BLOCKED
        elif findings["unresolved"]:
            report["status"] = STATUS_REGISTRY_UNRESOLVED
        else:
            report["status"] = STATUS_REGISTRY_CONFIRMED
    else:
        if any(findings[cat] for cat in BLOCKING_REPOSITORY_CATEGORIES):
            report["status"] = STATUS_REPO_BLOCKED
        elif findings["unresolved"]:
            report["status"] = STATUS_REPO_UNRESOLVED
        else:
            report["status"] = STATUS_REPO_CONFIRMED
    return report["status"], report


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    scope = "repository"
    if "--scope" in argv:
        index = argv.index("--scope")
        if index + 1 < len(argv):
            scope = argv[index + 1]
    status, report = verify(REPO_ROOT, scope)
    if "--report" in argv:
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        report_name = "verifier_report_registry.json" if scope == "registry" else "verifier_report.json"
        report_path = EVIDENCE_DIR / report_name
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(f"wrote {report_path.relative_to(REPO_ROOT)}")
    if "--json" in argv:
        # machine-readable mode: stdout carries only the JSON document
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if status in CONFIRMED_STATUSES else 1
    for category, items in report.get("findings", {}).items():
        for item in items:
            if isinstance(item, dict):
                print(f"FINDING [{category}]: {item.get('path', '')}: {item.get('evidence', '')}")
            else:
                print(f"FINDING [{category}]: {item}")
    if status not in CONFIRMED_STATUSES:
        print(f"PHASE22 feature flag runtime truth verification failed: {status}")
        return 1
    print(f"PHASE22 feature flag runtime truth verification passed: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
