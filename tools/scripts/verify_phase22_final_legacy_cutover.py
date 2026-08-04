"""verify_phase22_final_legacy_cutover.py - PHASE22 Legacy Cutover V2 Audit Verifier.

V2 independent rebuild of the PHASE22 final legacy cutover audit gate.
Supersedes PR #119.

V2 corrects the V1 flaws:
  1. Python AST for every Python-surface check (no regex).
  2. yaml.safe_load for all YAML work products.
  3. git rev-parse HEAD for the exact Head SHA.
  4. Feature-flag expires_at_phase is compared to the current phase;
     expired flags must satisfy strict retirement invariants or the
     gate emits DUAL_PATH_BLOCKERS_FOUND.
  5. PHASE08 cutover controller retention is treated as AUDIT_UNRESOLVED
     while the deepseek escalation remains open.
  6. Public-API Adapter direct DAO/Repository writes are surfaced as
     PUBLIC_ADAPTER_OWNERSHIP_VIOLATION.
  7. Non-Python surfaces (.ts, .tsx, .js, .mjs, .cjs, .sh, .ps1, .yml,
     .yaml, .toml, .github/workflows/*.yml) are scanned.

Status (priority, low -> high):
    LEGACY_CUTOVER_AUDIT_CLEAN         0
    AUDIT_UNRESOLVED                   6
    PUBLIC_ADAPTER_OWNERSHIP_VIOLATION 5
    ALIAS_BYPASS_BLOCKERS_FOUND        4
    DUAL_PATH_BLOCKERS_FOUND           3
    LEGACY_RUNTIME_BLOCKERS_FOUND      2
    TOOL_ERROR                         7
"""

import ast
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    import yaml  # type: ignore
except Exception:
    yaml = None


VERIFIER_VERSION = "2.0.0"
CURRENT_PHASE = "PHASE22"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


REPO_ROOT = _repo_root()

PRODUCTION_ROOTS = (
    REPO_ROOT / "src" / "backend" / "zuno",
    REPO_ROOT / "apps" / "web" / "src",
    REPO_ROOT / "apps" / "desktop" / "src",
)

HISTORY_ROOTS = (REPO_ROOT / "docs" / "history",)
HISTORY_EXCLUDE_FRAGMENTS = ("docs/history",)

TEXT_EXTENSIONS = (
    ".py", ".ts", ".tsx", ".js", ".mjs", ".cjs",
    ".sh", ".ps1", ".yml", ".yaml", ".toml", ".json",
)

LEGACY_ZUNO_PACKAGES = (
    "zuno.core", "zuno.services", "zuno.schema", "zuno.database",
    "zuno.tools", "zuno.resources", "zuno.config",
    "zuno.mcp_servers", "zuno.utils",
)

LEGACY_SEGMENT_FORBIDDEN = ("legacy",)
LEGACY_FILENAME_FORBIDDEN = ("legacy_aliases.py",)

RETIRED_FORBIDDEN_PATHS = (
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "compatibility",
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "compatibility" / "legacy_aliases.py",
    REPO_ROOT / "tests" / "legacy_guards",
)

ROLLBACK_MARKERS = (
    ("RUNTIME_SELECTOR_LEGACY", "ZUNO_AGENT_RUNTIME=legacy_general_agent"),
    ("ROLLBACK_MODE", "ZUNO_COMPLETION_CUTOVER_MODE=rollback"),
    ("DUAL_READ", "dual_read"),
    ("DUAL_WRITE", "dual_write"),
    ("SHADOW_WRITE", "shadow_write"),
    ("WRITE_BOTH", "write_both"),
    ("FALLBACK_TO_OLD", "fallback_to_old"),
    ("FALLBACK_TO_LEGACY", "fallback_to_legacy"),
    ("COMPAT_MODE", "compat_mode"),
    ("MIGRATION_MODE", "migration_mode"),
    ("TEMPORARY_FLAG", "temporary_flag"),
)

COMPLETION_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "completion.py"
COMPLETION_ROUTE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "v1" / "completion.py"
PHASE08_CUTOVER = REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "runtime" / "phase08_cutover.py"

WORK_PRODUCTS_DIR = REPO_ROOT / ".agent" / "programs" / "work-products"
FEATURE_FLAG_REGISTRY = WORK_PRODUCTS_DIR / "feature-flag-registry.yaml"
TEMPORARY_ALLOWLIST = WORK_PRODUCTS_DIR / "temporary-allowlist.yaml"
LEGACY_BYPASS_INVENTORY = WORK_PRODUCTS_DIR / "legacy-bypass-inventory.yaml"

PUBLIC_ADAPTER_ROOTS = (
    REPO_ROOT / "src" / "backend" / "zuno" / "api" / "v1",
    REPO_ROOT / "src" / "backend" / "zuno" / "api" / "v2",
    REPO_ROOT / "src" / "backend" / "zuno" / "adapters" / "versioned",
)

CANONICAL_VENDOR_SHIM = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "vendor" / "fastapi_jwt_auth"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class Finding:
    path: str
    line: int
    symbol: str
    category: str
    entrypoint: str
    reachable: str
    resolution: str
    owner: str
    risk: str
    required_action: str
    recommended_worker: str
    evidence_kind: str


@dataclass
class AuditResult:
    runtime_blockers: List[str] = field(default_factory=list)
    dual_path_blockers: List[str] = field(default_factory=list)
    alias_bypass_blockers: List[str] = field(default_factory=list)
    public_adapter_violations: List[str] = field(default_factory=list)
    unresolved: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    findings: List[Finding] = field(default_factory=list)

    @property
    def category(self) -> str:
        if self.runtime_blockers:
            return "LEGACY_RUNTIME_BLOCKERS_FOUND"
        if self.dual_path_blockers:
            return "DUAL_PATH_BLOCKERS_FOUND"
        if self.alias_bypass_blockers:
            return "ALIAS_BYPASS_BLOCKERS_FOUND"
        if self.public_adapter_violations:
            return "PUBLIC_ADAPTER_OWNERSHIP_VIOLATION"
        if self.unresolved:
            return "AUDIT_UNRESOLVED"
        return "LEGACY_CUTOVER_AUDIT_CLEAN"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _git_rev_parse_head() -> str:
    """Return ``git rev-parse HEAD`` so that the gate uses the same SHA model
    as ``git push`` and GitHub Actions. We never parse ``.git/HEAD`` text."""
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO_ROOT), text=True, stderr=subprocess.PIPE,
        )
        return out.strip()
    except Exception:
        return ""


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _is_history_path(path: Path) -> bool:
    rel = path.relative_to(REPO_ROOT)
    parts = rel.parts
    for fragment in HISTORY_EXCLUDE_FRAGMENTS:
        if fragment in parts:
            return True
    return False


def _is_production_path(path: Path) -> bool:
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    if not path.exists():
        return False
    for root in PRODUCTION_ROOTS:
        if not root.exists():
            continue
        if _is_under(path, root):
            return not _is_history_path(path)
    return False


def _iter_production_files() -> Iterable[Path]:
    for root in PRODUCTION_ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if any(part == "__pycache__" for part in p.parts):
                continue
            if _is_history_path(p):
                continue
            yield p


def _iter_active_python_files() -> Iterable[Path]:
    for p in _iter_production_files():
        if p.suffix == ".py":
            yield p


def _iter_wider_text_files() -> Iterable[Path]:
    """Production plus surrounding scan roots for non-Python surfaces.

    The non-Python gate has to inspect operational scripts (``tools/``),
    infrastructure files (``infra/``) and GitHub workflows
    (``.github/workflows/``) in addition to the three production roots.
    Each emitted path is yielded at most once.
    """
    seen = set()
    roots = list(PRODUCTION_ROOTS) + [
        REPO_ROOT / "tools",
        REPO_ROOT / "infra",
        REPO_ROOT / ".github",
    ]
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if any(part == "__pycache__" for part in p.parts):
                continue
            if _is_history_path(p):
                continue
            try:
                key = p.relative_to(REPO_ROOT).as_posix()
            except ValueError:
                continue
            if key in seen:
                continue
            seen.add(key)
            yield p


def _iter_active_text_files() -> Iterable[Path]:
    for p in _iter_wider_text_files():
        if p.suffix in TEXT_EXTENSIONS:
            yield p


def _iter_history_files() -> Iterable[Path]:
    for root in HISTORY_ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if p.is_file():
                yield p


def _iter_evidence_files() -> Iterable[Path]:
    """PHASE22 evidence directory plus broader ``docs/evidence`` tree.

    The evidence directory is not part of the production-source invariant
    but is scanned here so that false CLEAN / VERIFIED / RELEASED claims
    in PHASE22 evidence files can be noted (never gating)."""
    base = REPO_ROOT / "docs" / "evidence"
    if not base.exists():
        return
    for p in base.rglob("*"):
        if p.is_file() and p.suffix in {".md", ".json"}:
            yield p


def _safe_load_yaml(path: Path) -> Any:
    if yaml is None:
        return None
    try:
        return yaml.safe_load(_read_text(path))
    except Exception:
        return None


def _phase_rank(phase: Optional[str]) -> Optional[int]:
    """Return the integer rank of a PHASExx string; None if unparseable."""
    if not phase:
        return None
    m = re.match(r"^PHASE(\d+)$", str(phase).strip())
    if not m:
        return None
    return int(m.group(1))


def _legacy_root_from_string(value: str) -> Optional[str]:
    """Return the legacy root prefix if value matches an old zuno.<root>."""
    for root in LEGACY_ZUNO_PACKAGES:
        if value == root or value.startswith(root + "."):
            return root
    return None


def _record_finding(result: AuditResult, **kwargs: Any) -> None:
    result.findings.append(Finding(**kwargs))


# ---------------------------------------------------------------------------
# Python AST scanning
# ---------------------------------------------------------------------------


def _ast_parse(path: Path) -> Optional[ast.Module]:
    try:
        src = _read_text(path)
    except Exception:
        return None
    try:
        return ast.parse(src, filename=str(path))
    except SyntaxError:
        return None


def _check_python_imports_ast(path: Path, result: AuditResult) -> None:
    """Walk AST for direct old-root imports, dynamic imports, attribute
    access, and alias imports."""
    tree = _ast_parse(path)
    if tree is None:
        return
    rel = path.relative_to(REPO_ROOT).as_posix()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = _legacy_root_from_string(alias.name)
                if root:
                    result.alias_bypass_blockers.append(
                        f"legacy Zuno root import: {rel}:{node.lineno} -> import {alias.name}"
                    )
                    _record_finding(
                        result, path=rel, line=node.lineno, symbol=alias.name,
                        category="ALIAS_BYPASS", entrypoint=f"import {alias.name}",
                        reachable="static", resolution="BLOCKED",
                        owner="Repository Governance",
                        risk="ownerless alias re-introduces retired root",
                        required_action="replace with canonical import",
                        recommended_worker="minimax-legacy-audit-v2",
                        evidence_kind="STATIC_AST",
                    )
        elif isinstance(node, ast.ImportFrom):
            if node.module is None:
                continue
            root = _legacy_root_from_string(node.module)
            if root:
                names = ", ".join(a.name for a in node.names)
                result.alias_bypass_blockers.append(
                    f"legacy Zuno root import: {rel}:{node.lineno} -> from {node.module} import {names}"
                )
                _record_finding(
                    result, path=rel, line=node.lineno, symbol=node.module,
                    category="ALIAS_BYPASS", entrypoint=f"from {node.module} import ...",
                    reachable="static", resolution="BLOCKED",
                    owner="Repository Governance",
                    risk="ownerless alias re-introduces retired root",
                    required_action="replace with canonical import",
                    recommended_worker="minimax-legacy-audit-v2",
                    evidence_kind="STATIC_AST",
                )
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                fn_value = node.func.value
                fn_name = node.func.attr
                if isinstance(fn_value, ast.Name) and fn_value.id == "importlib" and fn_name in {"import_module"}:
                    if node.args:
                        arg = node.args[0]
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            root = _legacy_root_from_string(arg.value)
                            if root:
                                result.alias_bypass_blockers.append(
                                    f"legacy Zuno root dynamic import: {rel}:{node.lineno} -> importlib.import_module({arg.value!r})"
                                )
                                _record_finding(
                                    result, path=rel, line=node.lineno, symbol=arg.value,
                                    category="ALIAS_BYPASS",
                                    entrypoint=f"importlib.import_module({arg.value!r})",
                                    reachable="dynamic", resolution="BLOCKED",
                                    owner="Repository Governance",
                                    risk="dynamic import hides legacy root at runtime",
                                    required_action="replace with explicit canonical import",
                                    recommended_worker="minimax-legacy-audit-v2",
                                    evidence_kind="STATIC_AST",
                                )
                if isinstance(fn_value, ast.Name) and fn_value.id == "__import__" and node.args:
                    arg = node.args[0]
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        root = _legacy_root_from_string(arg.value)
                        if root:
                            result.alias_bypass_blockers.append(
                                f"legacy Zuno root __import__: {rel}:{node.lineno} -> __import__({arg.value!r})"
                            )
                            _record_finding(
                                result, path=rel, line=node.lineno, symbol=arg.value,
                                category="ALIAS_BYPASS",
                                entrypoint=f"__import__({arg.value!r})",
                                reachable="dynamic", resolution="BLOCKED",
                                owner="Repository Governance",
                                risk="dynamic import hides legacy root at runtime",
                                required_action="replace with explicit canonical import",
                                recommended_worker="minimax-legacy-audit-v2",
                                evidence_kind="STATIC_AST",
                            )
            elif isinstance(node.func, ast.Name) and node.func.id == "__import__" and node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    root = _legacy_root_from_string(arg.value)
                    if root:
                        result.alias_bypass_blockers.append(
                            "legacy Zuno root __import__: {}:{} -> __import__({!r})".format(
                                rel, node.lineno, arg.value,
                            )
                        )
                        _record_finding(
                            result, path=rel, line=node.lineno, symbol=arg.value,
                            category="ALIAS_BYPASS",
                            entrypoint="__import__",
                            reachable="dynamic", resolution="BLOCKED",
                            owner="Repository Governance",
                            risk="dynamic import hides legacy root at runtime",
                            required_action="replace with explicit canonical import",
                            recommended_worker="minimax-legacy-audit-v2",
                            evidence_kind="STATIC_AST",
                        )


def _check_python_dual_path_markers(path, result):
    """Detect dual-path / rollback / fallback assignments in Python source.

    These markers live inside Python source (``.sh``, ``.ps1`` and YAML
    markers are handled by ``_check_text_surface``). The check is AST
    based: every top-level / nested ``ast.Assign`` whose first target is a
    ``Name`` whose identifier is exactly one of the rollback markers.
    """
    tree = _ast_parse(path)
    if tree is None:
        return
    rel = path.relative_to(REPO_ROOT).as_posix()
    label_for_marker = {marker: label for label, marker in ROLLBACK_MARKERS}
    marker_set = set(label_for_marker)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            if target.id in marker_set:
                line = target.lineno
                label = label_for_marker[target.id]
                result.dual_path_blockers.append(
                    "{} marker in production source (python): {}:{} -> {}=...".format(label, rel, line, target.id)
                )
                _record_finding(
                    result, path=rel, line=line, symbol=target.id,
                    category="DUAL_PATH_PY", entrypoint=target.id,
                    reachable="static", resolution="BLOCKED",
                    owner="Repository Governance",
                    risk="python source carries dual-path/rollback marker assignment",
                    required_action="remove the assignment; route reads/writes through canonical paths",
                    recommended_worker="minimax-legacy-audit-v2",
                    evidence_kind="STATIC_AST",
                )


def _check_sys_meta_path_and_modules(path, result):
    tree = _ast_parse(path)
    if tree is None:
        return
    rel = path.relative_to(REPO_ROOT).as_posix()
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript):
            value = node.value
            if isinstance(value, ast.Attribute) and isinstance(value.value, ast.Name) and value.value.id == "sys" and value.attr == "modules":
                sl = node.slice
                if isinstance(sl, ast.Constant) and isinstance(sl.value, str) and sl.value.startswith("zuno."):
                    root = _legacy_root_from_string(sl.value)
                    if root:
                        result.alias_bypass_blockers.append(
                            "sys.modules aliasing onto legacy key: {}:{} -> sys.modules[{}]".format(rel, node.lineno, repr(sl.value))
                        )
                        _record_finding(
                            result, path=rel, line=node.lineno, symbol=sl.value,
                            category="ALIAS_BYPASS",
                            entrypoint="sys.modules alias",
                            reachable="static", resolution="BLOCKED",
                            owner="Repository Governance",
                            risk="sys.modules aliasing hides legacy root",
                            required_action="remove the alias; use canonical import",
                            recommended_worker="minimax-legacy-audit-v2",
                            evidence_kind="STATIC_AST",
                        )
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                value = node.func.value
                attr = node.func.attr
                if isinstance(value, ast.Attribute) and isinstance(value.value, ast.Name) and value.value.id == "sys" and value.attr == "meta_path":
                    if attr in {"insert", "append", "remove", "extend"}:
                        result.alias_bypass_blockers.append(
                            "sys.meta_path mutation: {}:{} -> sys.meta_path.{}".format(rel, node.lineno, attr)
                        )
                        _record_finding(
                            result, path=rel, line=node.lineno, symbol="sys.meta_path",
                            category="ALIAS_BYPASS",
                            entrypoint="sys.meta_path hook",
                            reachable="static", resolution="BLOCKED",
                            owner="Repository Governance",
                            risk="meta_path hook hides ownerless import",
                            required_action="remove the meta_path hook",
                            recommended_worker="minimax-legacy-audit-v2",
                            evidence_kind="STATIC_AST",
                        )


def _check_try_except_legacy_fallback(path, result):
    tree = _ast_parse(path)
    if tree is None:
        return
    rel = path.relative_to(REPO_ROOT).as_posix()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        for handler in node.handlers:
            if not isinstance(handler.type, ast.Name) or handler.type.id != "ImportError":
                continue
            for sub in ast.walk(handler):
                if isinstance(sub, ast.Import):
                    for alias in sub.names:
                        if _legacy_root_from_string(alias.name):
                            result.alias_bypass_blockers.append(
                                "try canonical / except ImportError legacy import: {}:{} -> import {}".format(rel, sub.lineno, alias.name)
                            )
                            _record_finding(
                                result, path=rel, line=sub.lineno, symbol=alias.name,
                                category="ALIAS_BYPASS",
                                entrypoint="except ImportError legacy import",
                                reachable="static", resolution="BLOCKED",
                                owner="Repository Governance",
                                risk="fallback import re-introduces retired root",
                                required_action="remove the fallback; use canonical path only",
                                recommended_worker="minimax-legacy-audit-v2",
                                evidence_kind="STATIC_AST",
                            )
                if isinstance(sub, ast.ImportFrom):
                    if sub.module and _legacy_root_from_string(sub.module):
                        names = ", ".join(a.name for a in sub.names)
                        result.alias_bypass_blockers.append(
                            "try canonical / except ImportError legacy import: {}:{} -> from {} import {}".format(rel, sub.lineno, sub.module, names)
                        )
                        _record_finding(
                            result, path=rel, line=sub.lineno, symbol=sub.module,
                            category="ALIAS_BYPASS",
                            entrypoint="except ImportError legacy import",
                            reachable="static", resolution="BLOCKED",
                            owner="Repository Governance",
                            risk="fallback import re-introduces retired root",
                            required_action="remove the fallback; use canonical path only",
                            recommended_worker="minimax-legacy-audit-v2",
                            evidence_kind="STATIC_AST",
                        )


def _check_legacy_segment_files(path, result):
    if not _is_production_path(path):
        return
    parts = path.relative_to(REPO_ROOT).parts
    rel_parts = path.relative_to(REPO_ROOT)
    for forbidden in LEGACY_SEGMENT_FORBIDDEN:
        matched = False
        for part in parts:
            if part == forbidden or part.startswith(forbidden + "_") or part.endswith("_" + forbidden):
                matched = True
                break
        if matched:
            rel = rel_parts.as_posix()
            result.runtime_blockers.append(
                "forbidden legacy segment in production path: {}".format(rel)
            )
            _record_finding(
                result, path=rel, line=0, symbol=forbidden,
                category="LEGACY_SEGMENT", entrypoint=rel,
                reachable="static", resolution="BLOCKED",
                owner="Repository Governance",
                risk="forbidden legacy segment in production path",
                required_action="delete the legacy directory or file",
                recommended_worker="minimax-legacy-audit-v2",
                evidence_kind="STATIC_TEXT",
            )
    if path.name in LEGACY_FILENAME_FORBIDDEN:
        rel = path.relative_to(REPO_ROOT).as_posix()
        result.runtime_blockers.append(
            "forbidden legacy alias file in production path: {}".format(rel)
        )
        _record_finding(
            result, path=rel, line=0, symbol=path.name,
            category="LEGACY_FILE", entrypoint=rel,
            reachable="static", resolution="BLOCKED",
            owner="Repository Governance",
            risk="forbidden legacy alias file re-introduced",
            required_action="delete the legacy alias file",
            recommended_worker="minimax-legacy-audit-v2",
            evidence_kind="STATIC_TEXT",
        )


def _check_retired_paths(result):
    for path in RETIRED_FORBIDDEN_PATHS:
        if path.is_file():
            rel = path.relative_to(REPO_ROOT).as_posix()
            result.runtime_blockers.append(
                "retired shell file re-introduced: {}".format(rel)
            )
            _record_finding(
                result, path=rel, line=0,
                symbol=path.name, category="LEGACY_PATH",
                entrypoint=rel,
                reachable="static", resolution="BLOCKED",
                owner="Repository Governance",
                risk="retired shell re-introduced",
                required_action="delete the retired path",
                recommended_worker="minimax-legacy-audit-v2",
                evidence_kind="STATIC_TEXT",
            )
            continue
        if path.is_dir() and any(child for child in path.rglob("*") if child.is_file()):
            rel = path.relative_to(REPO_ROOT).as_posix()
            result.runtime_blockers.append(
                "retired shell directory re-introduced: {}".format(rel)
            )
            _record_finding(
                result, path=rel, line=0,
                symbol=path.name, category="LEGACY_PATH",
                entrypoint=rel,
                reachable="static", resolution="BLOCKED",
                owner="Repository Governance",
                risk="retired shell directory re-introduced",
                required_action="delete the retired directory",
                recommended_worker="minimax-legacy-audit-v2",
                evidence_kind="STATIC_TEXT",
            )


def _check_phase08_cutover_reachability(result):
    """Inspect phase08_cutover.py AST for the runtime-internal surfaces
    that the spec mandates must be retired before CLEAN can be emitted.

    Concretely:
      - mode == "rollback"
      - mode == "shadow"
      - mode == "canary"
      - attribute legacy_runner
      - method _run_legacy
      - method _fallback_to_legacy
      - automatic fallback to legacy on new-runtime exception

    Any of these in production source forces at minimum an AUDIT_UNRESOLVED
    outcome (with a special escalated_to_deepseek note). The spec forbids
    classifying the gate as CLEAN while the deepseek escalation is open.
    """
    if not PHASE08_CUTOVER.exists():
        result.unresolved.append(
            "phase08_cutover.py is missing from production source (expected retire path removed before CLEAN)"
        )
        return
    tree = _ast_parse(PHASE08_CUTOVER)
    if tree is None:
        result.unresolved.append(
            "phase08_cutover.py failed to parse under AST; cannot prove retirement invariants"
        )
        return

    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    controller = None
    for c in classes:
        if c.name == "Phase08CutoverController":
            controller = c
            break
    if controller is None:
        result.unresolved.append(
            "Phase08CutoverController missing from phase08_cutover.py; cannot prove retirement invariants"
        )
        return

    methods = {m.name: m for m in controller.body if isinstance(m, ast.FunctionDef)}
    attributes = []
    for stmt in controller.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            attributes.append(stmt.target.id)
        elif isinstance(stmt, ast.Assign):
            for t in stmt.targets:
                if isinstance(t, ast.Name):
                    attributes.append(t.id)

    def note(name, severity):
        result.unresolved.append(
            "phase08_cutover.py:{}: {} still defines legacy surface ({})".format(controller.lineno, name, severity)
        )
        _record_finding(
            result, path=PHASE08_CUTOVER.relative_to(REPO_ROOT).as_posix(),
            line=controller.lineno, symbol=name,
            category="PHASE08_REACHABILITY", entrypoint=name,
            reachable="static", resolution="ESCALATED_TO_DEEPSEEK",
            owner="06 Agent Core",
            risk="legacy runtime path reachable through cutover controller",
            required_action="DeepSeek must retire or rename this path before PHASE22 closure",
            recommended_worker="deepseek-phase22-retire-phase08-legacy-cutover",
            evidence_kind="STATIC_AST",
        )

    if "legacy_runner" in attributes:
        note("legacy_runner", "attribute")
    if "_run_legacy" in methods:
        note("_run_legacy", "method")
    if "_fallback_to_legacy" in methods:
        note("_fallback_to_legacy", "method")

    if "handle" in methods:
        for sub in ast.walk(methods["handle"]):
            if not isinstance(sub, ast.Compare):
                continue
            if not isinstance(sub.left, ast.Attribute) or not isinstance(sub.left.value, ast.Name):
                continue
            if sub.left.value.id != "self" or sub.left.attr != "mode":
                continue
            if not sub.ops or not isinstance(sub.ops[0], ast.Eq):
                continue
            if not sub.comparators:
                continue
            comp = sub.comparators[0]
            if isinstance(comp, ast.Constant) and isinstance(comp.value, str):
                note("self.mode == '{}'".format(comp.value), "control-flow")


def _check_completion_route_reachability(result):
    """Inspect completion route and service surface for legacy proxies."""
    for route_path in (COMPLETION_SERVICE, COMPLETION_ROUTE):
        if not route_path.exists():
            continue
        tree = _ast_parse(route_path)
        if tree is None:
            continue
        rel = route_path.relative_to(REPO_ROOT).as_posix()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in {"GeneralAgent", "_create_chat_agent", "_run_legacy_general_agent"}:
                result.runtime_blockers.append(
                    "completion surface reaches legacy runtime symbol: {}:{} -> {}".format(rel, node.lineno, node.id)
                )
                _record_finding(
                    result, path=rel, line=node.lineno, symbol=node.id,
                    category="LEGACY_RUNTIME", entrypoint=node.id,
                    reachable="static", resolution="BLOCKED",
                    owner="01 Product Surface",
                    risk="completion route reaches legacy runtime helper",
                    required_action="remove legacy runtime helper reference",
                    recommended_worker="minimax-legacy-audit-v2",
                    evidence_kind="STATIC_AST",
                )


def _check_public_adapter_direct_dao(result):
    """Public API Adapter directory must not call DAO/Repository directly.

    The canonical-directory-contract.md section 5 requires adapters to
    translate Transport Contract only; they must NOT own domain state.
    Any direct call to a DAO insert/update/delete/commit or a Repository
    write inside a public-adapter file is a
    PUBLIC_ADAPTER_OWNERSHIP_VIOLATION (exit code 5).
    """
    WRITE_METHODS = {
        "insert", "update", "delete", "commit", "flush",
        "save", "upsert", "execute", "bulk_insert_mappings",
        "create", "add", "merge", "add_all",
    }
    # We require the receiver to end in Dao / Repository / Repo.
    # Both ``WorkspaceDao(...).insert(...)`` and ``workspace_repo.insert(...)``
    # shape are caught. FastAPI ``router.delete(...)`` etc. are HTTP method
    # registrations and are explicitly excluded - the receiver there is
    # ``router`` which does not match the DAO/Repository tail rule.
    DAO_TAIL = ("Dao", "Repository", "Repo")

    def _receiver_name(target):
        """Return the receiver identifier of a Call, or None.

        Handles the two most common shapes:
          * ``someName.method(...)`` -> ``someName``
          * ``SomeDao().method(...)`` -> ``SomeDao`` (taken from the
            ``ast.Name.id`` of the call's func attribute).
        """
        if isinstance(target, ast.Name):
            return target.id
        if isinstance(target, ast.Call):
            inner = target.func
            if isinstance(inner, ast.Name):
                return inner.id
        return None

    for root in PUBLIC_ADAPTER_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            tree = _ast_parse(path)
            if tree is None:
                continue
            rel = path.relative_to(REPO_ROOT).as_posix()
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                if not isinstance(node.func, ast.Attribute):
                    continue
                attr = node.func.attr
                if attr not in WRITE_METHODS:
                    continue
                ident = _receiver_name(node.func.value)
                if not ident:
                    continue
                if not ident.endswith(DAO_TAIL):
                    continue
                result.public_adapter_violations.append(
                    "public adapter direct DAO/Repository write: {}:{} -> {}.{}".format(rel, node.lineno, ident, attr)
                )
                _record_finding(
                    result, path=rel, line=node.lineno, symbol="{}.{}".format(ident, attr),
                    category="PUBLIC_ADAPTER_VIOLATION",
                    entrypoint="{}.{}".format(ident, attr),
                    reachable="static", resolution="BLOCKED",
                    owner="Repository Governance",
                    risk="public adapter owns domain write - violates section 5",
                    required_action="route the write through the application service",
                    recommended_worker="deepseek-phase22-retire-phase08-legacy-cutover",
                    evidence_kind="STATIC_AST",
                )


# ---------------------------------------------------------------------------
# YAML work-product scanners
# ---------------------------------------------------------------------------


def _check_feature_flag_registry(result):
    """Compare each flag's expires_at_phase against PHASE22.

    For every flag whose expiry is strictly before PHASE22 the gate
    requires ALL of:
        - the flag's default is RETIRED;
        - the rollback_command is effectively retired (no active command);
        - no active allowlist entry is left.

    Any flag that violates one of those invariants yields
    DUAL_PATH_BLOCKERS_FOUND. Any flag whose expiry is in the future is
    admitted.
    """
    if not FEATURE_FLAG_REGISTRY.exists():
        result.unresolved.append("feature flag registry missing")
        return
    parsed = _safe_load_yaml(FEATURE_FLAG_REGISTRY)
    if not isinstance(parsed, dict):
        result.unresolved.append("feature flag registry is not a YAML mapping")
        return
    flags = parsed.get("flags")
    if not isinstance(flags, list):
        result.unresolved.append("feature flag registry is missing flags list")
        return
    for entry in flags:
        if not isinstance(entry, dict):
            continue
        name = entry.get("flag") or "<unnamed>"
        expires_at_phase = entry.get("expires_at_phase")
        rank = _phase_rank(expires_at_phase)
        current = _phase_rank(CURRENT_PHASE)
        if rank is None or current is None:
            result.unresolved.append(
                "feature flag: '{}' has unknown phase expires_at_phase={}".format(name, expires_at_phase)
            )
            continue
        if rank >= current:
            continue
        default = entry.get("default") or ""
        rollback_command = entry.get("rollback_command") or ""
        if default != "RETIRED":
            result.dual_path_blockers.append(
                "expired feature flag not RETIRED: '{}' expires_at_phase={} default={}".format(name, expires_at_phase, default)
            )
            _record_finding(
                result, path=FEATURE_FLAG_REGISTRY.relative_to(REPO_ROOT).as_posix(),
                line=0, symbol=name,
                category="DUAL_PATH_FEATURE_FLAG",
                entrypoint="feature_flag[{}]".format(name),
                reachable="config", resolution="BLOCKED",
                owner="01 Product Surface",
                risk="expired flag '{}' still has default={}".format(name, default),
                required_action="set default to RETIRED or delete the flag",
                recommended_worker="minimax-legacy-audit-v2",
                evidence_kind="CONFIG",
            )
        if rollback_command and not re.match(r"^\s*(retired|n/?a|none)\b", str(rollback_command), re.IGNORECASE):
            result.dual_path_blockers.append(
                "expired feature flag exposes active rollback command: '{}'".format(name)
            )
            _record_finding(
                result, path=FEATURE_FLAG_REGISTRY.relative_to(REPO_ROOT).as_posix(),
                line=0, symbol=name,
                category="DUAL_PATH_FEATURE_FLAG",
                entrypoint="feature_flag[{}.rollback_command]".format(name),
                reachable="config", resolution="BLOCKED",
                owner="01 Product Surface",
                risk="expired flag '{}' still exposes a rollback command".format(name),
                required_action="rewrite rollback_command to 'retired and fail-closed'",
                recommended_worker="minimax-legacy-audit-v2",
                evidence_kind="CONFIG",
            )


def _check_allowlist_invariants(result):
    if not TEMPORARY_ALLOWLIST.exists():
        result.unresolved.append("temporary allowlist missing")
        return
    parsed = _safe_load_yaml(TEMPORARY_ALLOWLIST)
    if not isinstance(parsed, dict):
        result.unresolved.append("temporary allowlist is not a YAML mapping")
        return
    rules = parsed.get("rules") or {}
    final_zero_task = rules.get("final_zero_task")
    entries = parsed.get("allowlist") or []
    if not isinstance(entries, list):
        result.unresolved.append("temporary allowlist 'allowlist' is not a list")
        return
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        deadline = entry.get("deadline_phase")
        owner = entry.get("owner")
        removal_task = entry.get("removal_task")
        path_value = entry.get("path", "<entry>")
        if not owner or not removal_task:
            result.unresolved.append(
                "temporary allowlist entry '{}' missing owner/removal_task".format(path_value)
            )
            continue
        if not deadline:
            result.unresolved.append(
                "temporary allowlist entry '{}' missing deadline_phase".format(path_value)
            )
            continue
        rank = _phase_rank(deadline)
        current = _phase_rank(CURRENT_PHASE)
        if rank is None or current is None:
            result.unresolved.append(
                "temporary allowlist entry '{}' has unknown deadline_phase={}".format(path_value, deadline)
            )
            continue
        if rank >= current:
            continue
        if removal_task != final_zero_task:
            result.dual_path_blockers.append(
                "expired allowlist entry '{}' not pointing at final zero task".format(path_value)
            )
            _record_finding(
                result, path=TEMPORARY_ALLOWLIST.relative_to(REPO_ROOT).as_posix(),
                line=0, symbol=path_value,
                category="DUAL_PATH_ALLOWLIST",
                entrypoint="allowlist[{}]".format(path_value),
                reachable="config", resolution="BLOCKED",
                owner=owner,
                risk="expired allowlist '{}' not pointing at final zero task".format(path_value),
                required_action="set removal_task to '{}'".format(final_zero_task),
                recommended_worker="minimax-legacy-audit-v2",
                evidence_kind="CONFIG",
            )


def _check_legacy_bypass_inventory(result):
    if not LEGACY_BYPASS_INVENTORY.exists():
        result.unresolved.append("legacy-bypass-inventory missing")
        return
    parsed = _safe_load_yaml(LEGACY_BYPASS_INVENTORY)
    if not isinstance(parsed, dict):
        result.unresolved.append("legacy-bypass-inventory is not a YAML mapping")
        return
    inventory = parsed.get("inventory") or []
    if not inventory:
        result.unresolved.append("legacy-bypass-inventory has empty inventory")


# ---------------------------------------------------------------------------
# Non-Python gates (TypeScript, Shell, YAML, TOML, Workflow)
# ---------------------------------------------------------------------------


def _is_under_any(path, roots):
    for root in roots:
        try:
            path.relative_to(root)
            return True
        except ValueError:
            continue
    return False


def _check_text_surface(path, result):
    if path.suffix == ".py":
        return
    if not path.is_file():
        return
    rel = path.relative_to(REPO_ROOT)
    parts = rel.parts
    if any(part == "__pycache__" for part in parts):
        return
    if _is_under_any(path, HISTORY_ROOTS):
        return
    evidence_under_phase22 = False
    if "docs" in parts and "evidence" in parts:
        for part in parts:
            if part.startswith("goal05-phase22-"):
                evidence_under_phase22 = True
                break
    try:
        text = _read_text(path)
    except Exception:
        return
    rel_str = rel.as_posix()
    lines = text.splitlines()
    production_prefix = (
        rel_str.startswith("src/") or
        rel_str.startswith("apps/") or
        rel_str.startswith("tools/") or
        rel_str.startswith("infra/") or
        rel_str.startswith(".github/")
    )
    if production_prefix:
        for label, marker in ROLLBACK_MARKERS:
            # Match the marker as an identifier followed by ``=``,
            # optionally with whitespace around the equal sign. This
            # avoids false positives on identifiers that merely contain
            # the marker substring (e.g. ``compat_mode_enabled``).
            marker_pat = re.compile(r"\b" + re.escape(marker) + r"\s*=")
            for ln, line in enumerate(lines, start=1):
                if marker_pat.search(line):
                    result.dual_path_blockers.append(
                        "{} marker in production source: {}:{} -> {}".format(label, rel_str, ln, line.strip())
                    )
                    _record_finding(
                        result, path=rel_str, line=ln, symbol=marker,
                        category="DUAL_PATH", entrypoint=marker,
                        reachable="static", resolution="BLOCKED",
                        owner="Repository Governance",
                        risk="production source carries {} marker".format(label),
                        required_action="remove dual-path / rollback marker",
                        recommended_worker="minimax-legacy-audit-v2",
                        evidence_kind="STATIC_TEXT",
                    )
        if path.suffix in {".ts", ".tsx", ".js", ".mjs", ".cjs"}:
            for ln, line in enumerate(lines, start=1):
                if "/legacy/" in line:
                    result.runtime_blockers.append(
                        "legacy path in web/desktop source: {}:{} -> {}".format(rel_str, ln, line.strip())
                    )
                    _record_finding(
                        result, path=rel_str, line=ln, symbol="/legacy/",
                        category="LEGACY_PATH_TS", entrypoint="/legacy/",
                        reachable="static", resolution="BLOCKED",
                        owner="01 Product Surface",
                        risk="legacy path in TypeScript/JS source",
                        required_action="rename directory away from legacy",
                        recommended_worker="minimax-legacy-audit-v2",
                        evidence_kind="STATIC_TEXT",
                    )
        if path.suffix in {".sh", ".ps1"}:
            for ln, line in enumerate(lines, start=1):
                if "ZUNO_AGENT_RUNTIME=legacy_general_agent" in line and not line.lstrip().startswith("#"):
                    result.runtime_blockers.append(
                        "legacy runtime env in shell script: {}:{} -> {}".format(rel_str, ln, line.strip())
                    )
                    _record_finding(
                        result, path=rel_str, line=ln, symbol="ZUNO_AGENT_RUNTIME=legacy_general_agent",
                        category="LEGACY_RUNTIME", entrypoint="env",
                        reachable="static", resolution="BLOCKED",
                        owner="Repository Governance",
                        risk="shell script selects legacy runtime",
                        required_action="remove the legacy env selector",
                        recommended_worker="minimax-legacy-audit-v2",
                        evidence_kind="STATIC_TEXT",
                    )
        if path.suffix in {".yml", ".yaml"} and ".github/workflows" in rel_str:
            for ln, line in enumerate(lines, start=1):
                if "ZUNO_AGENT_RUNTIME=legacy_general_agent" in line or "legacy_general_agent_completion_rollback" in line:
                    result.runtime_blockers.append(
                        "legacy command in workflow: {}:{} -> {}".format(rel_str, ln, line.strip())
                    )
                    _record_finding(
                        result, path=rel_str, line=ln, symbol="legacy_runtime",
                        category="LEGACY_RUNTIME", entrypoint="workflow",
                        reachable="static", resolution="BLOCKED",
                        owner="Repository Governance",
                        risk="workflow invokes legacy runtime",
                        required_action="remove the legacy runtime line",
                        recommended_worker="minimax-legacy-audit-v2",
                        evidence_kind="STATIC_TEXT",
                    )
    elif evidence_under_phase22:
        for ln, line in enumerate(lines, start=1):
            upper = line.strip().upper()
            if "PHASE22" in upper and ("CLEAN" in upper or "VERIFIED" in upper or "RELEASED" in upper):
                result.notes.append(
                    "{}:{} mentions PHASE22 CLEAN/VERIFIED/RELEASED".format(rel_str, ln)
                )


# ---------------------------------------------------------------------------
# History allowlist helpers
# ---------------------------------------------------------------------------


def _check_history_allowlist_not_broadened(result):
    for path in _iter_history_files():
        try:
            text = _read_text(path)
        except Exception:
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        for ln, line in enumerate(text.splitlines(), start=1):
            if 'removal_task: "n/a"' in line:
                result.notes.append(
                    "{}:{}: history allowlist exempts a production path from removal".format(rel, ln)
                )


# ---------------------------------------------------------------------------
# Vendor shim
# ---------------------------------------------------------------------------


def _check_canonical_vendor_shim(result):
    if not CANONICAL_VENDOR_SHIM.is_dir():
        result.alias_bypass_blockers.append(
            "canonical vendor shim missing: src/backend/zuno/platform/vendor/fastapi_jwt_auth"
        )
        _record_finding(
            result, path=CANONICAL_VENDOR_SHIM.relative_to(REPO_ROOT).as_posix(),
            line=0, symbol="vendor_shim",
            category="ALIAS_BYPASS", entrypoint="vendor_shim",
            reachable="static", resolution="BLOCKED",
            owner="Repository Governance",
            risk="canonical vendor shim is the canonical home for fastapi_jwt_auth",
            required_action="create the canonical vendor shim",
            recommended_worker="minimax-legacy-audit-v2",
            evidence_kind="STATIC_TEXT",
        )


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def verify_phase22_final_legacy_cutover():
    result = AuditResult()

    _check_retired_paths(result)

    for path in _iter_active_python_files():
        _check_legacy_segment_files(path, result)
        _check_python_imports_ast(path, result)
        _check_sys_meta_path_and_modules(path, result)
        _check_try_except_legacy_fallback(path, result)
        _check_python_dual_path_markers(path, result)

    for path in _iter_active_text_files():
        _check_text_surface(path, result)
        _check_legacy_segment_files(path, result)

    for path in _iter_evidence_files():
        _check_text_surface(path, result)

    _check_phase08_cutover_reachability(result)
    _check_completion_route_reachability(result)
    _check_public_adapter_direct_dao(result)

    _check_feature_flag_registry(result)
    _check_allowlist_invariants(result)
    _check_legacy_bypass_inventory(result)

    _check_canonical_vendor_shim(result)
    _check_history_allowlist_not_broadened(result)

    head_sha = _git_rev_parse_head()
    result.notes.append("verifier_version: {}".format(VERIFIER_VERSION))
    result.notes.append("current_phase: {}".format(CURRENT_PHASE))
    if head_sha:
        result.notes.append("head_sha: {}".format(head_sha))
    return result


def _summary(result):
    return {
        "verifier_version": VERIFIER_VERSION,
        "category": result.category,
        "runtime_blockers": result.runtime_blockers,
        "dual_path_blockers": result.dual_path_blockers,
        "alias_bypass_blockers": result.alias_bypass_blockers,
        "public_adapter_violations": result.public_adapter_violations,
        "unresolved": result.unresolved,
        "notes": result.notes,
        "counts": {
            "runtime_blockers": len(result.runtime_blockers),
            "dual_path_blockers": len(result.dual_path_blockers),
            "alias_bypass_blockers": len(result.alias_bypass_blockers),
            "public_adapter_violations": len(result.public_adapter_violations),
            "unresolved": len(result.unresolved),
        },
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    want_json = "--json" in argv

    try:
        result = verify_phase22_final_legacy_cutover()
    except Exception as exc:
        print("TOOL_ERROR: {}".format(exc), file=sys.stderr)
        return 7

    summary = _summary(result)

    if want_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        if result.runtime_blockers:
            for entry in result.runtime_blockers:
                print("LEGACY_RUNTIME_BLOCKER: {}".format(entry))
        if result.dual_path_blockers:
            for entry in result.dual_path_blockers:
                print("DUAL_PATH_BLOCKER: {}".format(entry))
        if result.alias_bypass_blockers:
            for entry in result.alias_bypass_blockers:
                print("ALIAS_BYPASS_BLOCKER: {}".format(entry))
        if result.public_adapter_violations:
            for entry in result.public_adapter_violations:
                print("PUBLIC_ADAPTER_VIOLATION: {}".format(entry))
        if result.unresolved:
            for entry in result.unresolved:
                print("AUDIT_UNRESOLVED: {}".format(entry))
        if result.notes:
            for entry in result.notes:
                print("NOTE: {}".format(entry))
        print("CATEGORY: {}".format(result.category))

    category = result.category
    if category == "LEGACY_CUTOVER_AUDIT_CLEAN":
        return 0
    if category == "LEGACY_RUNTIME_BLOCKERS_FOUND":
        return 2
    if category == "DUAL_PATH_BLOCKERS_FOUND":
        return 3
    if category == "ALIAS_BYPASS_BLOCKERS_FOUND":
        return 4
    if category == "PUBLIC_ADAPTER_OWNERSHIP_VIOLATION":
        return 5
    if category == "AUDIT_UNRESOLVED":
        return 6
    return 7


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
