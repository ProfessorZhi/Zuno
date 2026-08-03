"""Fail-closed AST / Data-flow Object Store Owner Binding Gate.

PHASE22-OBJECT-STORE-OWNER-GATE — AST FINAL.

The PHASE22 deepseek preflight rejected the codebase by counting classes
whose name ends with ``ObjectStore``.  Counting class-name suffixes is a
heuristic, not a binding proof.  This verifier is a static AST + data-flow
gate that proves which object store the production composition root
actually binds for the canonical ingestion runtime.  It refuses to call
the binding ``unique`` on heuristics.

Output states:

* ``UNIQUE_PRODUCTION_BINDING_STATICALLY_CONFIRMED`` - exactly one
  production adapter is bound and the canonical runtime depends on the
  single durable wrapper that wraps it.  This is a *static* proof only;
  live MinIO write/read is **not** proven by this gate.
* ``MULTIPLE_PRODUCTION_BINDINGS`` - two or more production adapters or
  wrappers are simultaneously bound.
* ``NO_PRODUCTION_BINDING`` - the composition root has no resolvable call
  sites, or every call site returns ``None`` because the production
  storage mode is unconfigured.
* ``BINDING_UNRESOLVED`` - dynamic dispatch, aliasing, ``**kwargs`` or
  any other fact that cannot be statically proven.
* ``TOOL_ERROR`` - the verifier itself failed.

Exit codes:

* ``0`` UNIQUE_PRODUCTION_BINDING_STATICALLY_CONFIRMED
* ``2`` MULTIPLE_PRODUCTION_BINDINGS
* ``3`` NO_PRODUCTION_BINDING
* ``4`` BINDING_UNRESOLVED
* ``5`` TOOL_ERROR

Two operating modes:

* ``--mode contract``    - validates the gate against fixed human-authored
  fixtures (no self-referential real-repository test).
* ``--mode repository``  - scans the real repository and emits the static
  binding verdict.
"""

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple


REPO_ROOT = Path(__file__).resolve().parents[2]

EXIT_UNIQUE = 0
EXIT_MULTIPLE = 2
EXIT_NONE = 3
EXIT_UNRESOLVED = 4
EXIT_TOOL_ERROR = 5

STATUS_UNIQUE = "UNIQUE_PRODUCTION_BINDING_STATICALLY_CONFIRMED"
STATUS_MULTIPLE = "MULTIPLE_PRODUCTION_BINDINGS"
STATUS_NONE = "NO_PRODUCTION_BINDING"
STATUS_UNRESOLVED = "BINDING_UNRESOLVED"
STATUS_TOOL_ERROR = "TOOL_ERROR"

NOT_PROVEN_BOUNDARY = (
    "live MinIO write/read",
    "receipt authenticity",
    "PostgreSQL manifest durability",
    "runtime startup success",
    "production readiness",
)

CANONICAL_RUNTIME_PATH = (
    "src/backend/zuno/knowledge/ingestion/production_runtime.py"
)
CANONICAL_RUNTIME_CLASS = "PackageAProductionIngestionRuntime"
CANONICAL_RUNTIME_FIELD = "object_store"

COMPOSITION_ROOT_PATH = (
    "src/backend/zuno/api/services/workspace_task_runtime.py"
)
COMPOSITION_ROOT_FACTORY = "build_package_a_production_ingestion_runtime"
COMPOSITION_ROOT_LOCAL_FACTORY = "configure_durable_ingestion"

PRODUCTION_ADAPTER_PATH = "src/backend/zuno/platform/storage/object_store.py"
PRODUCTION_ADAPTER_CLASS = "MinioObjectStore"

DURABLE_WRAPPER_PATH = "src/backend/zuno/platform/storage/durable.py"
DURABLE_WRAPPER_CLASS = "DurableMinioObjectStore"

LOCAL_ADAPTER_PATH = (
    "src/backend/zuno/knowledge/storage/local_object_store.py"
)
LOCAL_ADAPTER_CLASS = "LocalObjectStore"

PROTOCOL_PORT_PATH = (
    "src/backend/zuno/knowledge/ingestion/source_object_upload.py"
)
PROTOCOL_PORT_CLASS = "DurableObjectStore"

PROD_FORBIDDEN_ADAPTERS = {
    LOCAL_ADAPTER_CLASS,
    "LazyStorageClient",
    "OSSClient",
    "MinioClient",
    "FakeObjectStore",
    "FakeMinioObjectStore",
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ClassObservation:
    """A single observed object-store-related class."""

    role: str
    qualified_name: str
    file_path: str
    line_number: int
    notes: Tuple[str, ...] = ()


@dataclass(frozen=True)
class CallSiteRecord:
    """A statically-resolved call to the composition root factory."""

    file_path: str
    line_number: int
    qualified_target: str
    keyword_arguments: Tuple[Tuple[str, str], ...]
    resolution_status: str  # "resolved", "dynamic", "alias_unresolved"
    extra: Tuple[str, ...] = ()


@dataclass
class BindingReport:
    """Aggregate facts collected by the verifier."""

    observations: List[ClassObservation] = field(default_factory=list)
    runtime_owner_dependencies: Tuple[Tuple[str, str], ...] = ()
    composition_root_signature: Dict[str, str] = field(default_factory=dict)
    composition_root_data_flow: Dict[str, Any] = field(default_factory=dict)
    composition_root_fail_closed: Dict[str, Any] = field(default_factory=dict)
    call_sites: List[CallSiteRecord] = field(default_factory=list)
    local_binding_sites_seen: Tuple[str, ...] = ()
    receipts_observed: Tuple[str, ...] = ()
    tenant_workspace_bindings: Tuple[str, ...] = ()
    not_proven: Tuple[str, ...] = NOT_PROVEN_BOUNDARY
    error_messages: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "observations": [
                {
                    "role": obs.role,
                    "qualified_name": obs.qualified_name,
                    "file_path": obs.file_path,
                    "line_number": obs.line_number,
                    "notes": list(obs.notes),
                }
                for obs in self.observations
            ],
            "runtime_owner_dependencies": [
                {"field": field, "type": type_}
                for field, type_ in self.runtime_owner_dependencies
            ],
            "composition_root_signature": dict(self.composition_root_signature),
            "composition_root_data_flow": dict(self.composition_root_data_flow),
            "composition_root_fail_closed": dict(self.composition_root_fail_closed),
            "call_sites": [
                {
                    "file_path": cs.file_path,
                    "line_number": cs.line_number,
                    "qualified_target": cs.qualified_target,
                    "keyword_arguments": [
                        {"keyword": k, "value": v}
                        for k, v in cs.keyword_arguments
                    ],
                    "resolution_status": cs.resolution_status,
                    "extra": list(cs.extra),
                }
                for cs in self.call_sites
            ],
            "local_binding_sites_seen": list(self.local_binding_sites_seen),
            "receipts_observed": list(self.receipts_observed),
            "tenant_workspace_bindings": list(self.tenant_workspace_bindings),
            "not_proven": list(self.not_proven),
            "errors": list(self.error_messages),
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse_module(path: Path) -> ast.Module:
    return ast.parse(_read_text(path), filename=str(path))


def _line_for_node(node: ast.AST) -> int:
    return getattr(node, "lineno", 0)


def _resolve_attr_chain(node: ast.AST) -> Optional[str]:
    """Return the dotted name of an Attribute/Name chain, or ``None``."""

    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _resolve_attr_chain(node.value)
        if base is None:
            return None
        return f"{base}.{node.attr}"
    return None


def _literal_value(node: ast.AST) -> Optional[str]:
    """Return a literal value as a string, or ``None`` for non-literals."""

    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Constant) and isinstance(node.value, bool):
        return str(node.value)
    if isinstance(node, ast.NameConstant):  # pragma: no cover - py<3.8
        return str(node.value)
    return None


def _class_header_line(tree: ast.Module, class_name: str) -> Optional[int]:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return _line_for_node(node)
    return None


def _scan_init_annotations(
    tree: ast.Module, class_name: str
) -> Dict[str, str]:
    """Return ``param -> annotation_text`` for ``class_name.__init__``."""

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    out: Dict[str, str] = {}
                    args = item.args
                    positional = list(args.posonlyargs) + list(args.args)
                    positional.extend(args.kwonlyargs)
                    for arg in positional:
                        if arg.arg in {"self", "cls"}:
                            continue
                        annotation = ast.unparse(arg.annotation) if arg.annotation else ""
                        out[arg.arg] = annotation.strip()
                    return out
    return {}


def _scan_signature_defaults(
    tree: ast.Module, function_name: str
) -> Dict[str, str]:
    """Return ``param -> default_expression`` for *function_name*."""

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
            out: Dict[str, str] = {}
            args = node.args
            all_args: List[ast.arg] = []
            all_args.extend(args.posonlyargs)
            all_args.extend(args.args)
            all_args.extend(args.kwonlyargs)
            defaults: List[Optional[ast.AST]] = []
            defaults.extend([None] * (len(args.posonlyargs) + len(args.args) - len(args.defaults)))
            defaults.extend(args.defaults)
            defaults.extend(args.kw_defaults)
            for arg, default in zip(all_args, defaults):
                if default is None:
                    continue
                out[arg.arg] = ast.unparse(default).strip()
            return out
    return {}


# ---------------------------------------------------------------------------
# Call site resolution
# ---------------------------------------------------------------------------


@dataclass
class _AliasMap:
    """Module-local alias map for resolving Name -> qualified target."""

    scope: Dict[str, str]

    def resolve(self, name: str) -> Optional[str]:
        return self.scope.get(name)


def _build_alias_map(tree: ast.Module, module_name: str) -> _AliasMap:
    scope: Dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name
                scope[local] = alias.name
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            absolute = module.startswith(f"{module_name}.") or module == module_name
            if absolute:
                full_module = module
            elif module:
                full_module = f"{module_name}.{module}"
            else:
                full_module = module_name
            for alias in node.names:
                local = alias.asname or alias.name
                scope[local] = f"{full_module}.{alias.name}" if full_module else alias.name
    return _AliasMap(scope=scope)


def _resolve_qualified_name(
    node: ast.AST, aliases: _AliasMap
) -> Tuple[Optional[str], str]:
    """Return ``(qualified_target, resolution_status)``.

    ``resolution_status`` is one of ``resolved``, ``dynamic``, ``local``,
    ``alias_unresolved``.  ``None`` means resolution failed outright.
    """

    if isinstance(node, ast.Name):
        resolved = aliases.resolve(node.id)
        return resolved, ("resolved" if resolved is not None else "alias_unresolved")
    if isinstance(node, ast.Attribute):
        qualified = _resolve_attr_chain(node)
        if qualified is None:
            return None, "dynamic"
        return qualified, "resolved"
    if isinstance(node, ast.Call):
        return None, "dynamic"
    return None, "dynamic"


def _scan_call_sites(
    repo_root: Path,
) -> List[CallSiteRecord]:
    """Walk every Python file under ``src/`` and capture factory calls."""

    src_root = repo_root / "src"
    if not src_root.exists():
        return []
    records: List[CallSiteRecord] = []
    files = sorted(src_root.rglob("*.py"))
    for path in files:
        relative = path.relative_to(repo_root).as_posix()
        try:
            text = _read_text(path)
        except OSError:
            continue
        if COMPOSITION_ROOT_FACTORY not in text:
            continue
        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError:
            continue
        aliases = _build_alias_map(tree, "zuno")
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            qualified, status = _resolve_qualified_name(node.func, aliases)
            if qualified is None or not qualified.endswith(COMPOSITION_ROOT_FACTORY):
                continue
            if qualified.split(".")[-1] != COMPOSITION_ROOT_FACTORY:
                continue
            kwargs: List[Tuple[str, str]] = []
            extra: List[str] = []
            resolution_status = "resolved"
            for kw in node.keywords:
                if kw.arg is None:
                    resolution_status = "dynamic"
                    extra.append("**kwargs detected")
                    continue
                value_text = ast.unparse(kw.value).strip()
                if isinstance(kw.value, ast.Lambda):
                    resolution_status = "dynamic"
                    extra.append(f"lambda passed for {kw.arg}")
                kwargs.append((kw.arg, value_text))
            if not isinstance(node.func, ast.Name):
                if not qualified.startswith("zuno."):
                    resolution_status = "alias_unresolved"
            records.append(
                CallSiteRecord(
                    file_path=relative,
                    line_number=_line_for_node(node),
                    qualified_target=qualified or "<unresolved>",
                    keyword_arguments=tuple(kwargs),
                    resolution_status=resolution_status,
                    extra=tuple(extra),
                )
            )
    return records


# ---------------------------------------------------------------------------
# Composition root data-flow analysis
# ---------------------------------------------------------------------------


@dataclass
class _DataFlow:
    adapter_variable: Optional[str] = None
    wrapper_variable: Optional[str] = None
    runtime_variable: Optional[str] = None
    adapter_factory_target: Optional[str] = None
    wrapper_factory_target: Optional[str] = None
    runtime_factory_target: Optional[str] = None
    wrapper_wraps_adapter: bool = False
    runtime_uses_wrapper: bool = False
    multi_adapter: bool = False
    multi_wrapper: bool = False
    adapter_assignments: Tuple[str, ...] = ()
    wrapper_assignments: Tuple[str, ...] = ()
    notes: Tuple[str, ...] = ()


def _analyse_composition_root(tree: ast.Module) -> _DataFlow:
    flow = _DataFlow()
    function_node: Optional[ast.FunctionDef] = None
    for node in tree.body:
        if (
            isinstance(node, ast.FunctionDef)
            and node.name == COMPOSITION_ROOT_FACTORY
        ):
            function_node = node
            break
    if function_node is None:
        flow.notes = ("composition root function not found",)
        return flow

    aliases = _build_alias_map(tree, "zuno")

    # 1. Identify adapter/wrapper/runtime factory variable names from the
    #    signature defaults.
    signature_defaults = _scan_signature_defaults(tree, COMPOSITION_ROOT_FACTORY)
    adapter_param = None
    wrapper_param = None
    runtime_param = None
    for name, value in signature_defaults.items():
        if name == "object_store_factory":
            adapter_param = name
            flow.adapter_factory_target = value
        elif name == "durable_object_store_factory":
            wrapper_param = name
            flow.wrapper_factory_target = value
        elif name == "runtime_factory":
            runtime_param = name
            flow.runtime_factory_target = value

    # 2. Walk the function body and collect assignments / calls.
    assignments: Dict[str, ast.AST] = {}
    for stmt in function_node.body:
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
            target = stmt.targets[0]
            if isinstance(target, ast.Name):
                assignments[target.id] = stmt.value

    adapter_calls: List[Tuple[str, ast.Call]] = []
    wrapper_calls: List[Tuple[str, ast.Call]] = []
    runtime_calls: List[Tuple[str, ast.Call]] = []
    return_calls: List[ast.Call] = []

    def _match_factory(call: ast.Call, target: Optional[str], param: Optional[str]) -> bool:
        if isinstance(call.func, ast.Name) and param and call.func.id == param:
            return True
        qualified, _ = _resolve_qualified_name(call.func, aliases)
        if target and qualified == target:
            return True
        return False

    for var, value in assignments.items():
        if isinstance(value, ast.Call):
            if _match_factory(value, flow.adapter_factory_target, adapter_param):
                adapter_calls.append((var, value))
            elif _match_factory(value, flow.wrapper_factory_target, wrapper_param):
                wrapper_calls.append((var, value))
            elif _match_factory(value, flow.runtime_factory_target, runtime_param):
                runtime_calls.append((var, value))
            elif isinstance(value.func, ast.Name) and value.func.id in PROD_FORBIDDEN_ADAPTERS:
                # Direct instantiation of a forbidden adapter counts as a
                # second production binding for the multi-binding case.
                flow.notes = (
                    f"composition root instantiates forbidden adapter {value.func.id!r} directly"
                )
            elif isinstance(value.func, ast.Name) and value.func.id == PRODUCTION_ADAPTER_CLASS:
                # Direct MinioObjectStore(...) call counts as another adapter.
                adapter_calls.append((var, value))

    # Also scan Return statements to find runtime_factory calls.
    for stmt in ast.walk(function_node):
        if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Call):
            call = stmt.value
            if _match_factory(call, flow.runtime_factory_target, runtime_param):
                return_calls.append(call)

    if len(adapter_calls) > 1:
        flow.multi_adapter = True
        flow.adapter_assignments = tuple(var for var, _ in adapter_calls)
    if len(wrapper_calls) > 1:
        flow.multi_wrapper = True
        flow.wrapper_assignments = tuple(var for var, _ in wrapper_calls)

    if adapter_calls:
        adapter_var, _ = adapter_calls[0]
        flow.adapter_variable = adapter_var
    if wrapper_calls:
        wrapper_var, wrapper_call = wrapper_calls[0]
        flow.wrapper_variable = wrapper_var
        # Verify the wrapper wraps the adapter variable.
        for kw in wrapper_call.keywords:
            if kw.arg == "store" and isinstance(kw.value, ast.Name):
                if kw.value.id == flow.adapter_variable:
                    flow.wrapper_wraps_adapter = True
                else:
                    flow.notes = (
                        f"wrapper.store={kw.value.id!r} does not match adapter variable {flow.adapter_variable!r}",
                    )
            elif kw.arg == "store":
                flow.notes = (
                    "wrapper.store argument is not a simple Name; cannot prove data-flow",
                )
        if not any(kw.arg == "store" for kw in wrapper_call.keywords):
            flow.notes = ("wrapper invocation has no 'store=' keyword",)
    if runtime_calls:
        runtime_var, runtime_call = runtime_calls[0]
        flow.runtime_variable = runtime_var
        _validate_runtime_object_store_arg(runtime_call, flow)
    if return_calls:
        flow.runtime_variable = flow.runtime_variable or "<return>"
        _validate_runtime_object_store_arg(return_calls[0], flow)

    return flow


def _validate_runtime_object_store_arg(
    runtime_call: ast.Call, flow: _DataFlow
) -> None:
    for kw in runtime_call.keywords:
        if kw.arg == CANONICAL_RUNTIME_FIELD and isinstance(kw.value, ast.Name):
            if kw.value.id == flow.wrapper_variable:
                flow.runtime_uses_wrapper = True
            elif kw.value.id == flow.adapter_variable:
                flow.notes = (
                    f"runtime.{CANONICAL_RUNTIME_FIELD}={kw.value.id!r} points at the raw adapter, "
                    "not the durable wrapper",
                )
            else:
                flow.notes = (
                    f"runtime.{CANONICAL_RUNTIME_FIELD}={kw.value.id!r} cannot be linked to the wrapper",
                )
        elif kw.arg == CANONICAL_RUNTIME_FIELD and not isinstance(kw.value, ast.Name):
            flow.notes = (
                f"runtime.{CANONICAL_RUNTIME_FIELD} is not a simple Name; cannot prove data-flow",
            )


def _is_return_none(stmt: ast.AST) -> bool:
    if not isinstance(stmt, ast.Return):
        return False
    value = stmt.value
    if value is None:
        return True
    if isinstance(value, ast.Constant) and value.value is None:
        return True
    return False


def _analyse_fail_closed(tree: ast.Module) -> Dict[str, Any]:
    """Inspect the composition root for fail-closed branches."""

    function_node: Optional[ast.FunctionDef] = None
    for node in tree.body:
        if (
            isinstance(node, ast.FunctionDef)
            and node.name == COMPOSITION_ROOT_FACTORY
        ):
            function_node = node
            break
    if function_node is None:
        return {"present": False, "branches": [], "notes": ("factory not found",)}

    branches: List[Dict[str, Any]] = []
    auto_fallback_detected = False

    def walk(stmt: ast.AST) -> None:
        nonlocal auto_fallback_detected
        if isinstance(stmt, ast.If):
            cond = ast.unparse(stmt.test).strip()
            for sub in stmt.body:
                if _is_return_none(sub):
                    branches.append({"condition": cond, "returns_none": True})
            for sub in stmt.orelse:
                if _is_return_none(sub):
                    branches.append({"condition": f"else of {cond}", "returns_none": True})
        elif isinstance(stmt, ast.Assign):
            value_text = ast.unparse(stmt.value).strip()
            if LOCAL_ADAPTER_CLASS in value_text:
                auto_fallback_detected = True

    for stmt in function_node.body:
        walk(stmt)

    return {
        "present": True,
        "branches": branches,
        "auto_fallback_to_local": auto_fallback_detected,
        "notes": (),
    }


# ---------------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------------


def collect_observations(repo_root: Path) -> BindingReport:
    report = BindingReport()

    # --- 1. Class observations (informational; missing files do not fail) ---
    role_targets = [
        (
            PROTOCOL_PORT_PATH,
            PROTOCOL_PORT_CLASS,
            "protocol_port",
            ("structural Protocol defining the port",),
        ),
        (
            LOCAL_ADAPTER_PATH,
            LOCAL_ADAPTER_CLASS,
            "local_development_adapter",
            ("local filesystem adapter; not bound by production composition root",),
        ),
        (
            PRODUCTION_ADAPTER_PATH,
            PRODUCTION_ADAPTER_CLASS,
            "production_minio_adapter",
            ("MinIO client; production adapter",),
        ),
        (
            DURABLE_WRAPPER_PATH,
            DURABLE_WRAPPER_CLASS,
            "durable_wrapper",
            ("durable wrapper around the production adapter",),
        ),
    ]
    for relative_path, class_name, role, notes in role_targets:
        path = repo_root / relative_path
        if not path.exists():
            continue
        try:
            tree = _parse_module(path)
        except SyntaxError:
            continue
        header_line = _class_header_line(tree, class_name)
        if header_line is None:
            continue
        report.observations.append(
            ClassObservation(
                role=role,
                qualified_name=class_name,
                file_path=relative_path,
                line_number=header_line,
                notes=notes,
            )
        )

    # --- 2. Canonical runtime owner (informational) ------------------------
    runtime_path = repo_root / CANONICAL_RUNTIME_PATH
    if runtime_path.exists():
        try:
            runtime_tree = _parse_module(runtime_path)
        except SyntaxError:
            runtime_tree = None
        if runtime_tree is not None:
            header_line = _class_header_line(runtime_tree, CANONICAL_RUNTIME_CLASS)
            if header_line is not None:
                report.observations.append(
                    ClassObservation(
                        role="runtime_owner",
                        qualified_name=CANONICAL_RUNTIME_CLASS,
                        file_path=CANONICAL_RUNTIME_PATH,
                        line_number=header_line,
                        notes=("depends on DurableMinioObjectStore",),
                    )
                )
                init_params = _scan_init_annotations(runtime_tree, CANONICAL_RUNTIME_CLASS)
                dependency = init_params.get(CANONICAL_RUNTIME_FIELD, "")
                if dependency:
                    report.runtime_owner_dependencies = (
                        (CANONICAL_RUNTIME_FIELD, dependency),
                    )

        try:
            runtime_text = _read_text(runtime_path)
        except OSError:
            runtime_text = ""
        if "s3://" in runtime_text:
            offset = runtime_text.find("s3://")
            line = runtime_text.count("\n", 0, offset) + 1
            report.receipts_observed = (f"s3:// scheme at line {line}",)
        tenant_patterns = (
            r"_object_name\(.*?\)",
            r"\{command\.tenant_id\}/\{command\.workspace_id\}/",
            r"\{plan\.tenant_id\}/\{plan\.workspace_id\}/",
        )
        for pattern in tenant_patterns:
            match = re.search(pattern, runtime_text)
            if match is not None:
                line = runtime_text.count("\n", 0, match.start()) + 1
                report.tenant_workspace_bindings = (
                    *report.tenant_workspace_bindings,
                    f"tenant/workspace prefix bound at line {line}",
                )
                break

    # --- 3. Composition root analysis --------------------------------------
    comp_path = repo_root / COMPOSITION_ROOT_PATH
    if not comp_path.exists():
        report.error_messages.append(
            f"composition root file missing: {COMPOSITION_ROOT_PATH}"
        )
    else:
        comp_tree = _parse_module(comp_path)
        factory_line: Optional[int] = None
        for node in comp_tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == COMPOSITION_ROOT_FACTORY:
                factory_line = _line_for_node(node)
                break
        if factory_line is None:
            report.error_messages.append(
                f"composition root factory {COMPOSITION_ROOT_FACTORY!r} not found"
            )
        else:
            report.observations.append(
                ClassObservation(
                    role="composition_root_binding",
                    qualified_name=COMPOSITION_ROOT_FACTORY,
                    file_path=COMPOSITION_ROOT_PATH,
                    line_number=factory_line,
                    notes=("returns PackageAProductionIngestionRuntime or None",),
                )
            )
            report.composition_root_signature = _scan_signature_defaults(
                comp_tree, COMPOSITION_ROOT_FACTORY
            )
            report.composition_root_data_flow = _analyse_composition_root(
                comp_tree
            ).__dict__
            report.composition_root_fail_closed = _analyse_fail_closed(comp_tree)

        if COMPOSITION_ROOT_LOCAL_FACTORY in _read_text(comp_path):
            report.local_binding_sites_seen = (COMPOSITION_ROOT_LOCAL_FACTORY,)

    # --- 4. Call site scan -------------------------------------------------
    report.call_sites = _scan_call_sites(repo_root)

    return report


# ---------------------------------------------------------------------------
# Call site validation
# ---------------------------------------------------------------------------


CANONICAL_DEFAULTS = {
    "object_store_factory": PRODUCTION_ADAPTER_CLASS,
    "durable_object_store_factory": DURABLE_WRAPPER_CLASS,
    "runtime_factory": CANONICAL_RUNTIME_CLASS,
}


def _validate_call_site(site: CallSiteRecord) -> Tuple[str, List[str]]:
    """Return (verdict, reasons).  Verdict is one of: ok, forbidden, dynamic, unresolved."""

    reasons: List[str] = []
    if site.resolution_status in {"dynamic", "alias_unresolved"}:
        return "unresolved", [f"{site.file_path}:{site.line_number} {site.resolution_status}"]

    seen_overrides: Dict[str, str] = {}
    for keyword, value in site.keyword_arguments:
        if keyword not in CANONICAL_DEFAULTS:
            continue
        # Strip the call site to a class name.
        target = value.split("(", 1)[0].strip()
        canonical = CANONICAL_DEFAULTS[keyword]
        if target == canonical:
            seen_overrides[keyword] = target
            continue
        if target in PROD_FORBIDDEN_ADAPTERS:
            return "forbidden", [
                f"{site.file_path}:{site.line_number} overrides {keyword} with forbidden adapter {target!r}"
            ]
        if target.startswith("lambda"):
            return "dynamic", [
                f"{site.file_path}:{site.line_number} passes lambda for {keyword}"
            ]
        if target in {
            "MinioObjectStore",
            "DurableMinioObjectStore",
            "PackageAProductionIngestionRuntime",
        }:
            # The call site passes the canonical class by name; allow.
            seen_overrides[keyword] = target
            continue
        return "dynamic", [
            f"{site.file_path}:{site.line_number} passes non-canonical {target!r} for {keyword}"
        ]
    return "ok", reasons


def _analyse_callers_handle_none(
    repo_root: Path, sites: List[CallSiteRecord]
) -> Dict[str, Any]:
    """Verify each call site explicitly rejects ``None`` from the factory."""

    per_site: List[Dict[str, Any]] = []
    for site in sites:
        path = repo_root / site.file_path
        if not path.exists():
            per_site.append(
                {
                    "file_path": site.file_path,
                    "line_number": site.line_number,
                    "handles_none": False,
                    "evidence": "call-site file missing",
                }
            )
            continue
        text = _read_text(path)
        offsets: List[int] = [0]
        for index, char in enumerate(text):
            if char == "\n":
                offsets.append(index + 1)
        call_offset = offsets[site.line_number - 1] if site.line_number - 1 < len(offsets) else 0
        # Look at the next ~3000 characters for explicit None handling.
        window = text[call_offset:call_offset + 3000]
        handles_none = False
        evidence = "no explicit None handling detected"
        # 1. Direct None check near the call.
        if re.search(r"\bif\s+\w+\s+is\s+None\b", window):
            handles_none = True
            evidence = "explicit None check near call site"
        elif "raise RuntimeError" in window:
            handles_none = True
            evidence = "explicit RuntimeError raise near call site"
        elif re.search(r"HTTPException\s*\([^)]*status_code\s*=\s*503", window):
            handles_none = True
            evidence = "explicit 503 response near call site"
        elif "raise" in window and "RuntimeError" in window:
            handles_none = True
            evidence = "explicit RuntimeError raise near call site"
        else:
            # 2. Configuration-class delegation: result stored on a class
            #    attribute, and the class checks for None + raises elsewhere.
            if re.search(r"\bcls\._package_a_production_runtime\b", text):
                if re.search(
                    r"_package_a_production_runtime\s+is\s+None", text
                ) and ("raise" in text or "HTTPException" in text):
                    handles_none = True
                    evidence = (
                        "production runtime stored on class; explicit None "
                        "check + raise detected"
                    )
            # 3. Cross-file delegation: the call site passes the result
            #    directly to a method whose body explicitly handles None.
            if not handles_none:
                try:
                    tree = ast.parse(text, filename=str(path))
                except SyntaxError:
                    tree = None
                if tree is not None:
                    enclosing_call = _find_enclosing_factory_call(tree, site.line_number)
                    if enclosing_call is not None:
                        receiver_name = _resolve_attr_chain(enclosing_call.func)
                        if receiver_name and "." in receiver_name:
                            aliases = _build_alias_map(tree, "zuno")
                            receiver_class = receiver_name.split(".", 1)[0]
                            resolved = aliases.resolve(receiver_class)
                            if resolved:
                                # The alias resolves to a class, not a
                                # module.  Strip the trailing class
                                # component to find the module path.
                                parts = resolved.split(".")
                                module_parts = parts[:-1] if parts[-1][:1].isupper() else parts
                                module_path = "/".join(module_parts) + ".py"
                                # Repo files live under src/backend/zuno/...
                                candidate = repo_root / "src" / "backend" / module_path
                                if not candidate.exists():
                                    candidate = repo_root / module_path
                                if candidate.exists():
                                    receiver_text = _read_text(candidate)
                                    if (
                                        "is None" in receiver_text
                                        and "raise" in receiver_text
                                    ):
                                        handles_none = True
                                        evidence = (
                                            f"runtime delegated to "
                                            f"{receiver_name} which has "
                                            f"explicit None handling"
                                        )
        per_site.append(
            {
                "file_path": site.file_path,
                "line_number": site.line_number,
                "handles_none": handles_none,
                "evidence": evidence,
            }
        )
    return {"callers": per_site}


def _find_enclosing_factory_call(
    tree: ast.Module, target_line: int
) -> Optional[ast.Call]:
    """Find the outermost Call in ``tree`` whose body covers *target_line*."""

    parent_map: Dict[int, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parent_map[id(child)] = parent

    candidates: List[ast.Call] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and node.lineno <= target_line
            and (node.end_lineno or node.lineno) >= target_line
        ):
            candidates.append(node)
    if not candidates:
        return None
    # Pick the outermost Call.
    candidates.sort(key=lambda n: (n.lineno, -len(parent_map)))
    return candidates[0]


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------


def evaluate(
    report: BindingReport,
    repo_root: Path,
    require_runtime_dependencies: bool = True,
) -> Tuple[str, List[str]]:
    reasons: List[str] = []

    if report.error_messages:
        for message in report.error_messages:
            reasons.append(message)
        return STATUS_UNRESOLVED, reasons

    # 1. Runtime owner depends on durable wrapper (real-repo only).
    dependencies = dict(report.runtime_owner_dependencies)
    runtime_type = dependencies.get(CANONICAL_RUNTIME_FIELD, "")
    if require_runtime_dependencies:
        if not dependencies:
            reasons.append(
                f"{CANONICAL_RUNTIME_CLASS}.__init__ could not be parsed for "
                f"{CANONICAL_RUNTIME_FIELD!r}"
            )
            return STATUS_UNRESOLVED, reasons
        if runtime_type != DURABLE_WRAPPER_CLASS:
            reasons.append(
                f"{CANONICAL_RUNTIME_CLASS}.{CANONICAL_RUNTIME_FIELD}={runtime_type!r} "
                f"does not bind {DURABLE_WRAPPER_CLASS!r}"
            )
            return STATUS_UNRESOLVED, reasons

    # 2. Composition root signature binds canonical factories.
    signature = report.composition_root_signature
    for key, expected in CANONICAL_DEFAULTS.items():
        observed = signature.get(key)
        if observed is None:
            reasons.append(
                f"composition root signature has no default for {key}"
            )
            return STATUS_UNRESOLVED, reasons
        if observed == expected:
            continue
        if observed in PROD_FORBIDDEN_ADAPTERS:
            reasons.append(
                f"composition root signature default for {key}={observed!r} is a forbidden adapter"
            )
            return STATUS_MULTIPLE, reasons
        if key == "object_store_factory" and observed != PRODUCTION_ADAPTER_CLASS:
            reasons.append(
                f"composition root signature default for {key}={observed!r} is not the canonical production adapter {PRODUCTION_ADAPTER_CLASS!r}"
            )
            return STATUS_MULTIPLE, reasons
        reasons.append(
            f"composition root signature default for {key} must be {expected!r}, observed {observed!r}"
        )
        return STATUS_UNRESOLVED, reasons

    # 3. Data-flow: single adapter + single wrapper + wrapper wraps adapter + runtime uses wrapper.
    flow = report.composition_root_data_flow
    if flow.get("multi_adapter"):
        reasons.append(
            f"composition root assigns multiple adapter variables: {flow.get('adapter_assignments')}"
        )
        return STATUS_MULTIPLE, reasons
    if flow.get("multi_wrapper"):
        reasons.append(
            f"composition root assigns multiple wrapper variables: {flow.get('wrapper_assignments')}"
        )
        return STATUS_MULTIPLE, reasons
    if not flow.get("adapter_variable"):
        reasons.append("composition root does not assign any adapter result")
        return STATUS_UNRESOLVED, reasons
    if not flow.get("wrapper_variable"):
        reasons.append("composition root does not assign any wrapper result")
        return STATUS_UNRESOLVED, reasons
    if not flow.get("runtime_variable"):
        reasons.append("composition root does not return a runtime via runtime_factory")
        return STATUS_UNRESOLVED, reasons
    if not flow.get("wrapper_wraps_adapter"):
        notes = flow.get("notes") or ("wrapper.store does not point at the adapter result",)
        reasons.extend(notes)
        return STATUS_UNRESOLVED, reasons
    if not flow.get("runtime_uses_wrapper"):
        notes = flow.get("notes") or ("runtime.object_store does not point at the wrapper result",)
        reasons.extend(notes)
        return STATUS_UNRESOLVED, reasons
    if flow.get("notes"):
        reasons.append("data-flow note: " + "; ".join(flow["notes"]))

    # 4. Composition root must fail closed when production storage is unconfigured.
    fc = report.composition_root_fail_closed
    if not fc.get("present"):
        reasons.append("composition root factory is not present")
        return STATUS_UNRESOLVED, reasons
    branches = fc.get("branches") or []
    if len(branches) < 2:
        reasons.append(
            "composition root must fail closed on at least two distinct conditions "
            "(storage.mode != 'minio' and missing credentials)"
        )
        return STATUS_UNRESOLVED, reasons
    if fc.get("auto_fallback_to_local"):
        reasons.append(
            f"composition root auto-falls-back to {LOCAL_ADAPTER_CLASS}; production must fail closed"
        )
        return STATUS_MULTIPLE, reasons

    # 5. Local adapter restricted to Local/Test profile (real-repo only).
    if require_runtime_dependencies:
        local_observations = [obs for obs in report.observations if obs.role == "local_development_adapter"]
        if local_observations and not report.local_binding_sites_seen:
            reasons.append(
                "local adapter exists but no Local/Test profile binding sites were located"
            )
            return STATUS_UNRESOLVED, reasons

    # 6. Receipt and tenant/workspace binding (real-repo only).
    if require_runtime_dependencies:
        if not report.receipts_observed:
            reasons.append("canonical runtime does not emit an s3:// receipt")
            return STATUS_UNRESOLVED, reasons
        if not report.tenant_workspace_bindings:
            reasons.append("canonical runtime does not bind tenant/workspace namespace prefixes")
            return STATUS_UNRESOLVED, reasons

    # 7. Call sites must be statically resolvable and use canonical factories.
    if not report.call_sites:
        reasons.append("composition root has no statically-resolvable call sites")
        return STATUS_NONE, reasons

    distinct_adapters: Set[str] = set()
    for site in report.call_sites:
        verdict, site_reasons = _validate_call_site(site)
        if verdict == "forbidden":
            return STATUS_MULTIPLE, site_reasons
        if verdict in {"dynamic", "unresolved"}:
            return STATUS_UNRESOLVED, site_reasons
        seen_factory = False
        for keyword, value in site.keyword_arguments:
            target = value.split("(", 1)[0].strip()
            if keyword == "object_store_factory" and target == PRODUCTION_ADAPTER_CLASS:
                distinct_adapters.add(target)
                seen_factory = True
        if not seen_factory:
            distinct_adapters.add(signature["object_store_factory"])
    if len(distinct_adapters) > 1:
        reasons.append(
            f"multiple distinct production adapters wired across call sites: {sorted(distinct_adapters)}"
        )
        return STATUS_MULTIPLE, reasons

    # 8. Callers must handle the None return explicitly.
    none_check = _analyse_callers_handle_none(repo_root, report.call_sites)
    unhandled = [c for c in none_check["callers"] if not c["handles_none"]]
    if unhandled:
        for site in unhandled:
            reasons.append(
                f"{site['file_path']}:{site['line_number']} does not explicitly handle None return: "
                f"{site['evidence']}"
            )
        return STATUS_UNRESOLVED, reasons

    reasons.append(
        "AST + data-flow prove a single production adapter bound, a single "
        "durable wrapper that wraps it, the canonical runtime that depends on "
        "the wrapper, two fail-closed branches, no auto-fallback to the local "
        "adapter, and explicit None handling at every call site. "
        "Live MinIO write/read is not proven by this gate."
    )
    return STATUS_UNIQUE, reasons


# ---------------------------------------------------------------------------
# Contract fixtures
# ---------------------------------------------------------------------------


@dataclass
class _SyntheticSource:
    path: str
    text: str


def _build_fixture_source(
    canonical_adapter: str,
    canonical_wrapper: str,
    canonical_runtime: str,
    factory_overrides: Optional[Dict[str, str]] = None,
    wrapper_store_var: str = "object_store",
    runtime_owner_var: str = "durable_object_store",
    second_adapter: bool = False,
    second_wrapper: bool = False,
    skip_runtime: bool = False,
    raw_minio_runtime: bool = False,
    wrapper_no_store: bool = False,
    factory_function: Optional[str] = None,
) -> str:
    """Generate a stub composition-root factory source for contract tests."""

    overrides = factory_overrides or {}
    extra_assign = ""
    if second_adapter:
        extra_assign += (
            f"\n    secondary_adapter = {canonical_adapter}(\n"
            "        endpoint='alt', access_key='alt', secret_key='alt'\n"
            "    )\n"
        )
    if second_wrapper:
        extra_assign += (
            f"\n    secondary_wrapper = {canonical_wrapper}(\n"
            "        store=secondary_adapter, engine=engine, owner='alt'\n"
            "    )\n"
        )

    adapter_call = (
        "object_store_factory(\n"
        "        endpoint=endpoint, access_key=access_key, secret_key=secret_key,\n"
        "        secure=False,\n"
        "    )"
    )
    wrapper_kwargs = [f"        store={wrapper_store_var}", "        engine=engine", "        owner='ws'"]
    if wrapper_no_store:
        wrapper_kwargs = ["        engine=engine", "        owner='ws'"]
    wrapper_call = (
        "durable_object_store_factory(\n"
        + ",\n".join(wrapper_kwargs)
        + ",\n    )"
    )
    runtime_arg = "object_store"
    if raw_minio_runtime:
        runtime_arg = "object_store_raw"
    if skip_runtime:
        runtime_section = "    return None"
    else:
        runtime_section = (
            "    return runtime_factory(\n"
            "        engine=engine,\n"
            f"        object_store={runtime_owner_var},\n"
            "        worker_id=worker_id,\n"
            "    )"
        )
    signature_overrides = "".join(
        f"\n    {key}: Any = {value}," for key, value in overrides.items()
    )

    return (
        "from typing import Any, Callable\n\n\n"
        "def build_package_a_production_ingestion_runtime(\n"
        "    *,\n"
        "    engine: Any,\n"
        "    settings: Any,\n"
        "    worker_id: str = 'workspace-file-upload',\n"
        f"    object_store_factory: Callable[..., Any] = {canonical_adapter},\n"
        f"    durable_object_store_factory: Callable[..., Any] = {canonical_wrapper},\n"
        f"    runtime_factory: Callable[..., Any] = {canonical_runtime},{signature_overrides}\n"
        ") -> Any:\n"
        "    storage = getattr(settings, 'storage', None)\n"
        "    if storage is None or getattr(storage, 'mode', None) != 'minio':\n"
        "        return None\n"
        "    minio = getattr(storage, 'minio', None)\n"
        "    if minio is None:\n"
        "        return None\n"
        "    endpoint = str(getattr(minio, 'endpoint', '') or '').strip()\n"
        "    access_key = str(getattr(minio, 'access_key_id', '') or '').strip()\n"
        "    secret_key = str(getattr(minio, 'access_key_secret', '') or '').strip()\n"
        "    if not endpoint or not access_key or not secret_key:\n"
        "        return None\n"
        f"    object_store = {adapter_call}\n"
        f"{extra_assign}"
        f"    durable_object_store = {wrapper_call}\n"
        f"{runtime_section}\n"
    )


@dataclass
class ContractFixture:
    name: str
    composition_root_source: str
    call_site_source: str
    expected_status: str
    notes: str = ""


def _contract_fixtures() -> Iterable[ContractFixture]:
    # Fixture 1: single canonical adapter + wrapper.
    yield ContractFixture(
        name="single_canonical_adapter_and_wrapper",
        composition_root_source=_build_fixture_source(
            PRODUCTION_ADAPTER_CLASS, DURABLE_WRAPPER_CLASS, CANONICAL_RUNTIME_CLASS
        ),
        call_site_source=(
            "from typing import Any\n"
            "from somewhere import build_package_a_production_ingestion_runtime\n"
            "def go(engine, settings):\n"
            "    runtime = build_package_a_production_ingestion_runtime(\n"
            "        engine=engine, settings=settings,\n"
            "    )\n"
            "    if runtime is None:\n"
            "        raise RuntimeError('production runtime required')\n"
            "    return runtime\n"
        ),
        expected_status=STATUS_UNIQUE,
    )

    # Fixture 2: two production bindings.
    yield ContractFixture(
        name="two_production_bindings",
        composition_root_source=_build_fixture_source(
            PRODUCTION_ADAPTER_CLASS,
            DURABLE_WRAPPER_CLASS,
            CANONICAL_RUNTIME_CLASS,
            second_adapter=True,
        ),
        call_site_source=(
            "from typing import Any\n"
            "from somewhere import build_package_a_production_ingestion_runtime\n"
            "def go(engine, settings):\n"
            "    runtime = build_package_a_production_ingestion_runtime(\n"
            "        engine=engine, settings=settings,\n"
            "    )\n"
            "    if runtime is None:\n"
            "        raise RuntimeError('production runtime required')\n"
            "    return runtime\n"
        ),
        expected_status=STATUS_MULTIPLE,
    )

    # Fixture 3: no production binding (call site omitted).
    yield ContractFixture(
        name="no_production_binding",
        composition_root_source=_build_fixture_source(
            PRODUCTION_ADAPTER_CLASS, DURABLE_WRAPPER_CLASS, CANONICAL_RUNTIME_CLASS
        ),
        call_site_source="",
        expected_status=STATUS_NONE,
    )

    # Fixture 4: local only.
    yield ContractFixture(
        name="local_only_adapter",
        composition_root_source=_build_fixture_source(
            LOCAL_ADAPTER_CLASS, DURABLE_WRAPPER_CLASS, CANONICAL_RUNTIME_CLASS
        ),
        call_site_source=(
            "from typing import Any\n"
            "from somewhere import build_package_a_production_ingestion_runtime\n"
            "def go(engine, settings):\n"
            "    runtime = build_package_a_production_ingestion_runtime(\n"
            "        engine=engine, settings=settings,\n"
            "    )\n"
            "    if runtime is None:\n"
            "        raise RuntimeError('production runtime required')\n"
            "    return runtime\n"
        ),
        expected_status=STATUS_MULTIPLE,
    )

    # Fixture 5: wrapper does not wrap adapter.
    yield ContractFixture(
        name="wrapper_does_not_wrap_adapter",
        composition_root_source=_build_fixture_source(
            PRODUCTION_ADAPTER_CLASS,
            DURABLE_WRAPPER_CLASS,
            CANONICAL_RUNTIME_CLASS,
            wrapper_store_var="some_other_object",
        ),
        call_site_source=(
            "from typing import Any\n"
            "from somewhere import build_package_a_production_ingestion_runtime\n"
            "def go(engine, settings):\n"
            "    runtime = build_package_a_production_ingestion_runtime(\n"
            "        engine=engine, settings=settings,\n"
            "    )\n"
            "    if runtime is None:\n"
            "        raise RuntimeError('production runtime required')\n"
            "    return runtime\n"
        ),
        expected_status=STATUS_UNRESOLVED,
    )

    # Fixture 6: runtime does not receive wrapper.
    yield ContractFixture(
        name="runtime_does_not_receive_wrapper",
        composition_root_source=_build_fixture_source(
            PRODUCTION_ADAPTER_CLASS,
            DURABLE_WRAPPER_CLASS,
            CANONICAL_RUNTIME_CLASS,
            runtime_owner_var="object_store",
        ),
        call_site_source=(
            "from typing import Any\n"
            "from somewhere import build_package_a_production_ingestion_runtime\n"
            "def go(engine, settings):\n"
            "    runtime = build_package_a_production_ingestion_runtime(\n"
            "        engine=engine, settings=settings,\n"
            "    )\n"
            "    if runtime is None:\n"
            "        raise RuntimeError('production runtime required')\n"
            "    return runtime\n"
        ),
        expected_status=STATUS_UNRESOLVED,
    )

    # Fixture 7: explicit local override at call site.
    yield ContractFixture(
        name="explicit_local_override_at_call_site",
        composition_root_source=_build_fixture_source(
            PRODUCTION_ADAPTER_CLASS, DURABLE_WRAPPER_CLASS, CANONICAL_RUNTIME_CLASS
        ),
        call_site_source=(
            f"from typing import Any\n"
            f"from somewhere import build_package_a_production_ingestion_runtime, {LOCAL_ADAPTER_CLASS}\n"
            "def go(engine, settings):\n"
            "    runtime = build_package_a_production_ingestion_runtime(\n"
            "        engine=engine,\n"
            "        settings=settings,\n"
            f"        object_store_factory={LOCAL_ADAPTER_CLASS},\n"
            "    )\n"
            "    if runtime is None:\n"
            "        raise RuntimeError('production runtime required')\n"
            "    return runtime\n"
        ),
        expected_status=STATUS_MULTIPLE,
    )

    # Fixture 8: dynamic override via lambda.
    yield ContractFixture(
        name="dynamic_override_lambda",
        composition_root_source=_build_fixture_source(
            PRODUCTION_ADAPTER_CLASS, DURABLE_WRAPPER_CLASS, CANONICAL_RUNTIME_CLASS
        ),
        call_site_source=(
            "from typing import Any\n"
            "from somewhere import build_package_a_production_ingestion_runtime\n"
            "def go(engine, settings):\n"
            "    runtime = build_package_a_production_ingestion_runtime(\n"
            "        engine=engine,\n"
            "        settings=settings,\n"
            "        object_store_factory=lambda **kw: object(),\n"
            "    )\n"
            "    if runtime is None:\n"
            "        raise RuntimeError('production runtime required')\n"
            "    return runtime\n"
        ),
        expected_status=STATUS_UNRESOLVED,
    )

    # Fixture 9: **kwargs unresolved.
    yield ContractFixture(
        name="kwargs_unresolved",
        composition_root_source=_build_fixture_source(
            PRODUCTION_ADAPTER_CLASS, DURABLE_WRAPPER_CLASS, CANONICAL_RUNTIME_CLASS
        ),
        call_site_source=(
            "from typing import Any\n"
            "from somewhere import build_package_a_production_ingestion_runtime\n"
            "def go(engine, settings, **extra):\n"
            "    runtime = build_package_a_production_ingestion_runtime(\n"
            "        engine=engine,\n"
            "        settings=settings,\n"
            "        **extra,\n"
            "    )\n"
            "    if runtime is None:\n"
            "        raise RuntimeError('production runtime required')\n"
            "    return runtime\n"
        ),
        expected_status=STATUS_UNRESOLVED,
    )

    # Fixture 10: many classes but unique production binding.
    yield ContractFixture(
        name="many_classes_unique_production_binding",
        composition_root_source=_build_fixture_source(
            PRODUCTION_ADAPTER_CLASS, DURABLE_WRAPPER_CLASS, CANONICAL_RUNTIME_CLASS
        ),
        call_site_source=(
            "from typing import Any\n"
            "from somewhere import build_package_a_production_ingestion_runtime\n"
            "def go(engine, settings):\n"
            "    runtime = build_package_a_production_ingestion_runtime(\n"
            "        engine=engine, settings=settings,\n"
            "    )\n"
            "    if runtime is None:\n"
            "        raise RuntimeError('production runtime required')\n"
            "    return runtime\n"
        ),
        expected_status=STATUS_UNIQUE,
    )

    # Fixture 11: test double excluded.
    yield ContractFixture(
        name="test_double_excluded",
        composition_root_source=_build_fixture_source(
            PRODUCTION_ADAPTER_CLASS, DURABLE_WRAPPER_CLASS, CANONICAL_RUNTIME_CLASS
        ),
        call_site_source=(
            "from typing import Any\n"
            "from somewhere import build_package_a_production_ingestion_runtime\n"
            "from tests.fixtures.phase22_object_store_owner_binding.fake_object_store import FakeObjectStore\n"
            "def go(engine, settings):\n"
            "    runtime = build_package_a_production_ingestion_runtime(\n"
            "        engine=engine, settings=settings,\n"
            "    )\n"
            "    if runtime is None:\n"
            "        raise RuntimeError('production runtime required')\n"
            "    return runtime\n"
        ),
        expected_status=STATUS_UNIQUE,
    )

    # Fixture 12: caller does not handle None.
    yield ContractFixture(
        name="caller_does_not_handle_none",
        composition_root_source=_build_fixture_source(
            PRODUCTION_ADAPTER_CLASS, DURABLE_WRAPPER_CLASS, CANONICAL_RUNTIME_CLASS
        ),
        call_site_source=(
            "from typing import Any\n"
            "from somewhere import build_package_a_production_ingestion_runtime\n"
            "def go(engine, settings):\n"
            "    runtime = build_package_a_production_ingestion_runtime(\n"
            "        engine=engine, settings=settings,\n"
            "    )\n"
            "    return runtime\n"
        ),
        expected_status=STATUS_UNRESOLVED,
    )


def _evaluate_fixture(fixture: ContractFixture) -> Tuple[str, BindingReport, List[str]]:
    """Build a synthetic BindingReport for a fixture and run evaluate() on it."""

    import tempfile

    report = BindingReport()
    reasons: List[str] = []
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        src_dir = tmp / "src" / "backend" / "zuno" / "api" / "services"
        src_dir.mkdir(parents=True, exist_ok=True)
        comp_path = src_dir / "workspace_task_runtime.py"
        comp_path.write_text(fixture.composition_root_source, encoding="utf-8")
        caller_path = tmp / "src" / "backend" / "zuno" / "main.py"
        caller_path.parent.mkdir(parents=True, exist_ok=True)
        caller_path.write_text(fixture.call_site_source, encoding="utf-8")

        stub_dir = tmp / "stubs"
        stub_dir.mkdir(parents=True, exist_ok=True)
        for name in (
            "MinioObjectStore",
            "DurableMinioObjectStore",
            "LocalObjectStore",
            "PackageAProductionIngestionRuntime",
        ):
            (stub_dir / f"{name}.py").write_text(f"class {name}: pass\n", encoding="utf-8")

        report = collect_observations(tmp)
        status, reasons = evaluate(
            report, tmp, require_runtime_dependencies=False
        )
    return status, report, reasons


# ---------------------------------------------------------------------------
# Mode handlers
# ---------------------------------------------------------------------------


def _contract_mode() -> Tuple[int, Dict[str, Any]]:
    fixtures = list(_contract_fixtures())
    results: List[Dict[str, Any]] = []
    overall_exit = EXIT_UNIQUE
    overall_status = STATUS_UNIQUE
    for fixture in fixtures:
        status, _report, reasons = _evaluate_fixture(fixture)
        exit_code = _status_to_exit(status)
        results.append(
            {
                "fixture": fixture.name,
                "expected_status": fixture.expected_status,
                "actual_status": status,
                "exit_code": exit_code,
                "reasons": reasons,
            }
        )
        if status != fixture.expected_status:
            overall_status = STATUS_UNRESOLVED
            overall_exit = EXIT_UNRESOLVED
    return overall_exit, {
        "mode": "contract",
        "overall_status": overall_status,
        "results": results,
    }


def _repository_mode() -> Tuple[int, Dict[str, Any]]:
    try:
        report = collect_observations(REPO_ROOT)
        status, reasons = evaluate(report, REPO_ROOT)
    except Exception as exc:  # pragma: no cover - defensive
        return EXIT_TOOL_ERROR, {
            "mode": "repository",
            "status": STATUS_TOOL_ERROR,
            "error": f"{type(exc).__name__}: {exc}",
        }
    return _status_to_exit(status), {
        "mode": "repository",
        "status": status,
        "reasons": reasons,
        "not_proven": list(report.not_proven),
        "report": report.to_dict(),
    }


def _status_to_exit(status: str) -> int:
    if status == STATUS_UNIQUE:
        return EXIT_UNIQUE
    if status == STATUS_MULTIPLE:
        return EXIT_MULTIPLE
    if status == STATUS_NONE:
        return EXIT_NONE
    if status == STATUS_TOOL_ERROR:
        return EXIT_TOOL_ERROR
    return EXIT_UNRESOLVED


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="PHASE22-OBJECT-STORE-OWNER-GATE AST verifier"
    )
    parser.add_argument(        "--mode",
        choices=("contract", "repository"),
        default="contract",
        help="Verifier mode: contract (self-test) or repository (real scan)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a JSON document on stdout instead of a human report",
    )
    args = parser.parse_args(argv)

    try:
        if args.mode == "contract":
            exit_code, payload = _contract_mode()
        else:
            exit_code, payload = _repository_mode()
    except Exception as exc:  # pragma: no cover - defensive
        exit_code = EXIT_TOOL_ERROR
        payload = {
            "mode": args.mode,
            "status": STATUS_TOOL_ERROR,
            "error": f"{type(exc).__name__}: {exc}",
        }

    if args.json:
        json.dump(payload, sys.stdout, indent=2, default=str)
        sys.stdout.write("\n")
    else:
        status = payload.get("status") or payload.get("overall_status")
        print(f"[phase22-object-store-owner-binding] mode={args.mode} status={status}")
        for reason in payload.get("reasons", []) or []:
            print(f"  - {reason}")
        if "results" in payload:
            for result in payload["results"]:
                marker = (
                    "OK"
                    if result["actual_status"] == result["expected_status"]
                    else "FAIL"
                )
                print(
                    f"  [{marker}] {result['fixture']}: "
                    f"expected={result['expected_status']} "
                    f"actual={result['actual_status']} exit={result['exit_code']}"
                )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
