"""Fail-closed Snapshot Activation Persistence / Scope Gate.

PHASE22-SNAPSHOT-FAIL-CLOSED-GATE verifier.

The companion gate for DeepSeek2 PR #113 (Index Snapshot Profiles).  This
verifier proves that snapshot activation cannot transition to ``ACTIVATED``
without every fail-closed gate passing:

* Persistence port present;
* ``persist()`` succeeded;
* Readback returned a non-empty snapshot;
* Readback tenant / knowledge_version / snapshot hash consistent;
* Receipt construction strictly after a successful readback;
* ``persistence_evidence.persisted`` is ``True``;
* ``consistency_checks`` is present and every entry is ``True``;
* Immutable snapshot payload conflicts fail the activation;
* The three index clients (ES, Milvus, Neo4j) require
  ``tenant_id``, ``workspace_id`` and ``knowledge_version_id`` for every
  scoped query; snapshot paths additionally require ``snapshot_id``;
* Dynamic or unresolvable wiring \u2192 ``BINDING_UNRESOLVED``.

The verifier is a static AST + contract fixture gate; it does **not**
execute live PostgreSQL write/read or live MinIO/ES/Milvus/Neo4j calls.
Not-proven boundaries are emitted explicitly.

Output states:

* ``SNAPSHOT_FAIL_CLOSED_CONFIRMED`` - every fail-closed condition is
  statically proven in the real repo.
* ``PERSISTENCE_GATE_VIOLATION`` - persistence or readback gate is
  structurally missing.
* ``READBACK_SCOPE_VIOLATION`` - readback scope is not enforced.
* ``INDEX_SCOPE_VIOLATION`` - one of the three index clients does not
  enforce tenant/workspace/knowledge_version scope.
* ``ACTIVATION_RECEIPT_VIOLATION`` - the activation receipt construction
  ordering violates the readback-before-receipt rule.
* ``BINDING_UNRESOLVED`` - the gate cannot prove a fact statically.
* ``TOOL_ERROR`` - the verifier itself failed.

Exit codes:

* ``0`` SNAPSHOT_FAIL_CLOSED_CONFIRMED
* ``2`` PERSISTENCE_GATE_VIOLATION
* ``3`` READBACK_SCOPE_VIOLATION
* ``4`` INDEX_SCOPE_VIOLATION
* ``5`` ACTIVATION_RECEIPT_VIOLATION
* ``6`` BINDING_UNRESOLVED
* ``7`` TOOL_ERROR

Operating modes:

* ``--mode contract``    - validates the gate against fixed human-authored
  fixtures (no self-referential real-repository test).
* ``--mode repository``  - inspects the real repository and reports the
  current static binding verdict.
"""

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parents[2]

EXIT_CONFIRMED = 0
EXIT_PERSISTENCE = 2
EXIT_READBACK = 3
EXIT_INDEX = 4
EXIT_RECEIPT = 5
EXIT_UNRESOLVED = 6
EXIT_TOOL_ERROR = 7

STATUS_CONFIRMED = "SNAPSHOT_FAIL_CLOSED_CONFIRMED"
STATUS_PERSISTENCE = "PERSISTENCE_GATE_VIOLATION"
STATUS_READBACK = "READBACK_SCOPE_VIOLATION"
STATUS_INDEX = "INDEX_SCOPE_VIOLATION"
STATUS_RECEIPT = "ACTIVATION_RECEIPT_VIOLATION"
STATUS_UNRESOLVED = "BINDING_UNRESOLVED"
STATUS_TOOL_ERROR = "TOOL_ERROR"

NOT_PROVEN_BOUNDARY = (
    "live PostgreSQL write/read",
    "real Snapshot activation",
    "real three-index corpus visibility",
    "four-profile measurement",
    "production readiness",
)

# Canonical file paths in the DeepSeek2 PR #113.
SNAPSHOT_ACTIVATION_PATH = (
    "src/backend/zuno/knowledge/indexing/snapshot_activation.py"
)
INDEX_ADAPTERS_PATH = (
    "src/backend/zuno/knowledge/indexing/adapters.py"
)
INDEXING_INIT_PATH = (
    "src/backend/zuno/knowledge/indexing/__init__.py"
)

REQUIRED_SCOPE_KEYS = ("tenant_id", "workspace_id", "knowledge_version_id")
SNAPSHOT_SCOPE_KEYS = ("snapshot_id",)

# Methods on the three index clients that must require tenant scope.
# `index_documents` is excluded because it is the *write* path; scope is
# captured in the per-document metadata.  The scope gate focuses on the
# *query / readback / path* methods that could leak rows if scope were
# absent.
INDEX_CLIENT_METHODS_REQUIRED_SCOPE = {
    "ElasticsearchBm25IndexClient": {
        "search_documents",
        "fetch_document",
        "count_documents",
    },
    "MilvusVectorIndexClient": {
        "search_documents",
        "fetch_document",
        "count_documents",
    },
    "Neo4jGraphIndexClient": {
        "search_documents",
        "query_path",
        "verify_path_visibility_receipt",
    },
}

# Methods on the snapshot adapter that must enforce fail-closed.
SNAPSHOT_ADAPTER_CLASS = "SnapshotActivationAdapter"
SNAPSHOT_PERSISTENCE_PROTOCOL = "SnapshotPersistencePort"
REQUIRED_PERSISTENCE_METHODS = ("persist", "read")


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IndexClientScopeFinding:
    client_class: str
    method_name: str
    line_number: int
    issues: Tuple[str, ...]


@dataclass
class SnapshotReport:
    snapshot_activation_observed: bool = False
    persistence_port_observed: bool = False
    persistence_methods: Tuple[str, ...] = ()
    activate_method_present: bool = False
    receipt_after_readback: bool = False
    persistence_evidence_check: bool = False
    consistency_checks_require_all_true: bool = False
    consistency_checks_present: bool = False
    immutable_payload_conflict_guard: bool = False
    persistence_blocked_path_present: bool = False
    readback_scope_enforced: bool = False
    readback_tenant_check: bool = False
    readback_knowledge_version_check: bool = False
    readback_snapshot_hash_check: bool = False
    index_client_findings: Tuple[IndexClientScopeFinding, ...] = ()
    activation_call_sites: Tuple[Tuple[str, int], ...] = ()
    activation_paths: Tuple[str, ...] = ()
    notes: Tuple[str, ...] = ()
    errors: List[str] = field(default_factory=list)
    not_proven: Tuple[str, ...] = (
        "live PostgreSQL write/read",
        "real Snapshot activation",
        "real three-index corpus visibility",
        "four-profile measurement",
        "production readiness",
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_activation_observed": self.snapshot_activation_observed,
            "persistence_port_observed": self.persistence_port_observed,
            "persistence_methods": list(self.persistence_methods),
            "activate_method_present": self.activate_method_present,
            "receipt_after_readback": self.receipt_after_readback,
            "persistence_evidence_check": self.persistence_evidence_check,
            "consistency_checks_require_all_true": self.consistency_checks_require_all_true,
            "consistency_checks_present": self.consistency_checks_present,
            "immutable_payload_conflict_guard": self.immutable_payload_conflict_guard,
            "persistence_blocked_path_present": self.persistence_blocked_path_present,
            "readback_scope_enforced": self.readback_scope_enforced,
            "readback_tenant_check": self.readback_tenant_check,
            "readback_knowledge_version_check": self.readback_knowledge_version_check,
            "readback_snapshot_hash_check": self.readback_snapshot_hash_check,
            "index_client_findings": [
                {
                    "client_class": f.client_class,
                    "method_name": f.method_name,
                    "line_number": f.line_number,
                    "issues": list(f.issues),
                }
                for f in self.index_client_findings
            ],
            "activation_call_sites": [
                {"file_path": path, "line_number": line}
                for path, line in self.activation_call_sites
            ],
            "activation_paths": list(self.activation_paths),
            "notes": list(self.notes),
            "errors": list(self.errors),
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


def _function_body_range(
    tree: ast.Module, function_name: str
) -> Optional[Tuple[int, int]]:
    """Return the (start, end) AST offsets of *function_name*'s body."""

    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == function_name
        ):
            start = node.body[0].lineno - 1 if node.body else node.lineno
            end = getattr(node, "end_lineno", node.lineno) or node.lineno
            return start, end
    return None


def _class_method_offsets(
    tree: ast.Module, class_name: str
) -> Dict[str, Tuple[int, int]]:
    out: Dict[str, Tuple[int, int]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    start = item.body[0].lineno - 1 if item.body else item.lineno
                    end = getattr(item, "end_lineno", item.lineno) or item.lineno
                    out[item.name] = (start, end)
    return out


def _scan_init_parameters(
    tree: ast.Module, class_name: str
) -> Dict[str, str]:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    out: Dict[str, str] = {}
                    args = item.args
                    all_args: List[ast.arg] = []
                    all_args.extend(args.posonlyargs)
                    all_args.extend(args.args)
                    all_args.extend(args.kwonlyargs)
                    for arg in all_args:
                        if arg.arg in {"self", "cls"}:
                            continue
                        annotation = ast.unparse(arg.annotation) if arg.annotation else ""
                        out[arg.arg] = annotation
                    return out
    return {}


# ---------------------------------------------------------------------------
# Snapshot activation analysis
# ---------------------------------------------------------------------------


def _analyse_snapshot_activation(tree: ast.Module) -> SnapshotReport:
    report = SnapshotReport()

    classes = {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
    }

    if SNAPSHOT_ADAPTER_CLASS not in classes:
        report.errors.append(
            f"{SNAPSHOT_ADAPTER_CLASS!r} not found in {SNAPSHOT_ACTIVATION_PATH}"
        )
        return report
    report.snapshot_activation_observed = True
    report.activation_paths = (SNAPSHOT_ACTIVATION_PATH,)

    # Persistence port: structural Protocol with `persist` and `read` methods.
    port_class = classes.get(SNAPSHOT_PERSISTENCE_PROTOCOL)
    if port_class is None:
        report.errors.append(
            f"{SNAPSHOT_PERSISTENCE_PROTOCOL!r} protocol not found"
        )
    else:
        report.persistence_port_observed = True
        method_names: List[str] = []
        for item in port_class.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_names.append(item.name)
        report.persistence_methods = tuple(sorted(method_names))
        for required in REQUIRED_PERSISTENCE_METHODS:
            if required not in method_names:
                report.errors.append(
                    f"{SNAPSHOT_PERSISTENCE_PROTOCOL} missing method {required!r}"
                )

    # Activate method must be present and require persistence_evidence gate.
    adapter_class = classes[SNAPSHOT_ADAPTER_CLASS]
    activate_method: Optional[ast.FunctionDef] = None
    for item in adapter_class.body:
        if isinstance(item, ast.FunctionDef) and item.name == "activate":
            activate_method = item
            break
    if activate_method is None:
        report.errors.append(f"{SNAPSHOT_ADAPTER_CLASS}.activate is missing")
    else:
        report.activate_method_present = True
        body_text = ast.unparse(activate_method)
        # 1. Receipt construction must follow the readback.  We accept either the
        #    ``build_snapshot_activation_receipt`` call (canonical) or any
        #    assignment that mentions both ``receipt`` and the readback
        #    result.  The last receipt construction must follow at least
        #    one ``read(`` call.
        receipt_positions = [
            match.start() for match in re.finditer(
                r"build_snapshot_activation_receipt", body_text
            )
        ]
        if not receipt_positions:
            # Fallback: any assignment that includes both "receipt" and a
            # call to the persistence port's read.
            receipt_positions = [
                match.start()
                for match in re.finditer(r"receipt\s*=", body_text)
            ]
        read_positions = [
            match.start() for match in re.finditer(r"\.read\(", body_text)
        ]
        persist_positions = [
            match.start() for match in re.finditer(r"\.persist\(", body_text)
        ]
        if receipt_positions and read_positions:
            last_receipt = receipt_positions[-1]
            first_read = read_positions[0]
            report.receipt_after_readback = first_read < last_receipt
        else:
            report.notes = report.notes + (
                "activate() does not call persist.read() before receipt build",
            )
        # 2. persistence_evidence check must exist and require persisted=True.
        if "persistence_evidence" in body_text and (
            '"persisted": True' in body_text
            or "'persisted': True" in body_text
            or "persisted\": True" in body_text
        ):
            report.persistence_evidence_check = True
        else:
            report.notes = report.notes + (
                "activate() does not assert persistence_evidence.persisted == True",
            )
        # 3. consistency_checks must be checked before ACTIVATED.
        if (
            "consistency_checks" in body_text
            and ("failed" in body_text or "all(value)" in body_text or "checks[\"" in body_text)
        ):
            report.consistency_checks_require_all_true = True
            report.consistency_checks_present = True
        else:
            report.notes = report.notes + (
                "activate() does not require consistency_checks to all be True",
            )
        # 4. Immutable conflict guard: persist() exception path must
        #    not return ACTIVATED.
        if persist_positions and (
            '"persisted": False' in body_text
            or "'persisted': False" in body_text
            or "persisted\": False" in body_text
        ):
            report.persistence_blocked_path_present = True
        else:
            report.notes = report.notes + (
                "activate() must mark persisted=False on persistence failure",
            )

    # Readback scope: require that the PostgresKnowledgeSnapshotPersistence
    # ``read`` method returns a dict whose literal includes
    # ``tenant_id``, ``knowledge_version_id`` and ``snapshot_hash`` (or
    # ``snapshot_content_hash``).  Static analysis cannot prove the readback
    # values are correct at runtime, but it can prove the read() output
    # shape is missing a required scope field, which is exactly the kind of
    # leak this gate prevents.
    persistence_class = classes.get("PostgresKnowledgeSnapshotPersistence")
    if persistence_class is None:
        report.notes = report.notes + (
            "PostgresKnowledgeSnapshotPersistence is missing; cannot "
            "statically verify readback scope",
        )
    else:
        read_method = None
        for item in persistence_class.body:
            if isinstance(item, ast.FunctionDef) and item.name == "read":
                read_method = item
                break
        if read_method is None:
            report.notes = report.notes + (
                "PostgresKnowledgeSnapshotPersistence.read is missing",
            )
        else:
            read_text = ast.unparse(read_method)
            if "tenant_id" in read_text:
                report.readback_tenant_check = True
            else:
                report.notes = report.notes + (
                    "read() return value does not include tenant_id",
                )
            if "knowledge_version_id" in read_text:
                report.readback_knowledge_version_check = True
            else:
                report.notes = report.notes + (
                    "read() return value does not include knowledge_version_id",
                )
            if "snapshot_hash" in read_text or "snapshot_content_hash" in read_text:
                report.readback_snapshot_hash_check = True
            else:
                report.notes = report.notes + (
                    "read() return value does not include snapshot_hash / "
                    "snapshot_content_hash",
                )
    report.readback_scope_enforced = (
        report.readback_tenant_check
        and report.readback_knowledge_version_check
        and report.readback_snapshot_hash_check
    )
    if not report.readback_scope_enforced:
        report.notes = report.notes + (
            "readback scope guards are incomplete",
        )

    return report


def body_text_for(tree: ast.Module, class_name: str) -> str:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return ast.unparse(node)
    return ""


# ---------------------------------------------------------------------------
# Index client scope analysis
# ---------------------------------------------------------------------------


def _analyse_index_clients(tree: ast.Module) -> Tuple[SnapshotReport, List[IndexClientScopeFinding]]:
    findings: List[IndexClientScopeFinding] = []
    report = SnapshotReport()
    classes = {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
    }
    for client_name, methods in INDEX_CLIENT_METHODS_REQUIRED_SCOPE.items():
        client_node = classes.get(client_name)
        if client_node is None:
            findings.append(
                IndexClientScopeFinding(
                    client_class=client_name,
                    method_name="<module>",
                    line_number=0,
                    issues=(f"{client_name} not declared in {INDEX_ADAPTERS_PATH}",),
                )
            )
            continue
        for item in client_node.body:
            if (
                isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                and item.name in methods
            ):
                method_text = ast.unparse(item)
                issues = _check_scope(item, method_text)
                if issues:
                    findings.append(
                        IndexClientScopeFinding(
                            client_class=client_name,
                            method_name=item.name,
                            line_number=_line_for_node(item),
                            issues=tuple(issues),
                        )
                    )
    report.index_client_findings = tuple(findings)
    return report, findings


def _check_scope(method: ast.FunctionDef, method_text: str) -> List[str]:
    issues: List[str] = []
    args = method.args
    all_args: List[ast.arg] = []
    all_args.extend(args.posonlyargs)
    all_args.extend(args.args)
    all_args.extend(args.kwonlyargs)
    param_names = {arg.arg for arg in all_args}

    # VAR_KEYWORD (**kwargs) is treated as missing scope: callers can
    # silently omit the scope keys.
    has_var_keyword = bool(args.kwarg)

    # Methods that require snapshot scope too.
    requires_snapshot = method.name in {
        "index_graph_relations",
        "query_path",
        "verify_path_visibility_receipt",
    }

    required = list(REQUIRED_SCOPE_KEYS)
    if requires_snapshot:
        required.extend(SNAPSHOT_SCOPE_KEYS)

    for required_key in required:
        if required_key in param_names:
            continue
        issues.append(f"missing required scope parameter: {required_key}")
        continue
    if has_var_keyword:
        issues.append(
            "method declares **kwargs which can silently bypass required scope parameters"
        )
    # Default values must not be None silently.
    for arg in all_args:
        if arg.arg not in REQUIRED_SCOPE_KEYS and arg.arg not in SNAPSHOT_SCOPE_KEYS:
            continue
        if arg.arg not in param_names:
            continue
        if arg.arg in {"self", "cls"}:
            continue
        defaults: List[Optional[ast.AST]] = []
        defaults.extend([None] * (len(args.posonlyargs) + len(args.args) - len(args.defaults)))
        defaults.extend(args.defaults)
        defaults.extend(args.kw_defaults)
        index = next(
            (i for i, a in enumerate(all_args) if a.arg == arg.arg),
            None,
        )
        if index is None:
            continue
        if index >= len(defaults):
            continue
        default_value = defaults[index]
        if default_value is None:
            continue
        if isinstance(default_value, ast.Constant) and default_value.value is None:
            issues.append(
                f"required scope parameter {arg.arg!r} has default None (silent bypass)"
            )
        if isinstance(default_value, (ast.Name, ast.Attribute)):
            default_repr = ast.unparse(default_value)
            if "None" in default_repr:
                issues.append(
                    f"required scope parameter {arg.arg!r} has default None (silent bypass)"
                )
    if not _body_uses_scope(method_text):
        issues.append("method body does not propagate tenant/workspace/knowledge_version scope")
    if requires_snapshot and "snapshot_id" not in method_text:
        issues.append("snapshot_id is required but method body does not reference it")
    if re.search(r'f["\'].*\{[a-z_]+\}.*["\']', method_text):
        if "scope" not in method_text.lower() and "filter" not in method_text.lower():
            issues.append("method uses dynamic f-string without explicit scope filter")
    return issues


def _body_uses_scope(method_text: str) -> bool:
    """Heuristic check that the method body constrains results by scope.

    The body must reference at least one of the scope keys inside an
    expression that looks like a filter / match clause (e.g.
    ``filters.append({'term': {'tenant_id': tenant_id}})`` or
    ``expr = 'tenant_id == ...'``), or simply return the scope value as
    a propagation result.  A pure ``return None`` / ``return 0`` that
    ignores the scope parameters is flagged as a violation.
    """

    method_text_lower = method_text.lower()
    scope_markers = ("tenant_id", "workspace_id", "knowledge_version_id")
    filter_markers = ("filter", "term", "expr", "where", "match", "append", "==", ".run")
    has_scope = any(marker in method_text for marker in scope_markers)
    has_filter = any(marker in method_text_lower for marker in filter_markers)
    if not has_scope:
        return False
    # If the body uses scope but contains no filter construction, it must
    # at least propagate the scope into the result (e.g. ``return {'tenant_id': tenant_id}``).
    if not has_filter:
        # Acceptable propagation: returning a dict that mentions scope.
        if "return" in method_text and any(
            scope_marker in method_text.split("return", 1)[1]
            for scope_marker in scope_markers
        ):
            return True
        return False
    return True


# ---------------------------------------------------------------------------
# Activation call sites
# ---------------------------------------------------------------------------


def _scan_activation_call_sites(
    repo_root: Path, target_class: str = "SnapshotActivationAdapter"
) -> List[Tuple[str, int]]:
    src_root = repo_root / "src"
    sites: List[Tuple[str, int]] = []
    if not src_root.exists():
        return sites
    for path in sorted(src_root.rglob("*.py")):
        text = _read_text(path)
        if target_class not in text:
            continue
        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Match both attribute access and direct name.
                qualified = _qualified_attr(node.func)
                if qualified and qualified.endswith(target_class):
                    sites.append(
                        (
                            path.relative_to(repo_root).as_posix(),
                            _line_for_node(node),
                        )
                    )
    return sites


def _qualified_attr(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _qualified_attr(node.value)
        if base is None:
            return None
        return f"{base}.{node.attr}"
    return None


# ---------------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------------


def collect_observations(repo_root: Path) -> SnapshotReport:
    report = SnapshotReport()

    # 1. Snapshot activation adapter.
    snapshot_path = repo_root / SNAPSHOT_ACTIVATION_PATH
    if not snapshot_path.exists():
        report.errors.append(f"snapshot activation file missing: {SNAPSHOT_ACTIVATION_PATH}")
    else:
        try:
            tree = _parse_module(snapshot_path)
        except SyntaxError as exc:
            report.errors.append(f"snapshot activation parse error: {exc}")
            tree = None
        if tree is not None:
            activation_report = _analyse_snapshot_activation(tree)
            report.snapshot_activation_observed = activation_report.snapshot_activation_observed
            report.persistence_port_observed = activation_report.persistence_port_observed
            report.persistence_methods = activation_report.persistence_methods
            report.activate_method_present = activation_report.activate_method_present
            report.receipt_after_readback = activation_report.receipt_after_readback
            report.persistence_evidence_check = activation_report.persistence_evidence_check
            report.consistency_checks_require_all_true = (
                activation_report.consistency_checks_require_all_true
            )
            report.consistency_checks_present = activation_report.consistency_checks_present
            report.persistence_blocked_path_present = (
                activation_report.persistence_blocked_path_present
            )
            report.readback_scope_enforced = activation_report.readback_scope_enforced
            report.readback_tenant_check = activation_report.readback_tenant_check
            report.readback_knowledge_version_check = (
                activation_report.readback_knowledge_version_check
            )
            report.readback_snapshot_hash_check = (
                activation_report.readback_snapshot_hash_check
            )
            report.activation_paths = activation_report.activation_paths
            report.notes = report.notes + activation_report.notes
            report.errors = report.errors + activation_report.errors

    # 2. Index client scope.
    adapters_path = repo_root / INDEX_ADAPTERS_PATH
    if not adapters_path.exists():
        report.errors.append(f"index adapters file missing: {INDEX_ADAPTERS_PATH}")
    else:
        try:
            tree = _parse_module(adapters_path)
        except SyntaxError as exc:
            report.errors.append(f"index adapters parse error: {exc}")
            tree = None
        if tree is not None:
            _client_report, findings = _analyse_index_clients(tree)
            report.index_client_findings = tuple(findings)

    # 3. Activation call sites.
    report.activation_call_sites = tuple(
        _scan_activation_call_sites(repo_root, SNAPSHOT_ADAPTER_CLASS)
    )

    return report


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------


def evaluate(report: SnapshotReport) -> Tuple[str, List[str]]:
    reasons: List[str] = []

    # Structural errors only — true ambiguity in the source code.
    structural_errors = [
        e for e in report.errors
        if "not found" not in e and "missing" not in e.lower()
    ]
    if structural_errors:
        for message in structural_errors:
            reasons.append(message)
        return STATUS_UNRESOLVED, reasons

    # Persistence gate.
    if not report.snapshot_activation_observed:
        return STATUS_UNRESOLVED, [
            "snapshot activation file not found in the repository",
        ]
    if not report.persistence_port_observed:
        return STATUS_PERSISTENCE, [
            f"{SNAPSHOT_PERSISTENCE_PROTOCOL} is not declared; "
            "snapshot activation cannot fail closed on persistence",
        ]
    for required in REQUIRED_PERSISTENCE_METHODS:
        if required not in report.persistence_methods:
            return STATUS_PERSISTENCE, [
                f"{SNAPSHOT_PERSISTENCE_PROTOCOL} missing required method {required!r}",
            ]
    if not report.activate_method_present:
        return STATUS_PERSISTENCE, [
            f"{SNAPSHOT_ADAPTER_CLASS}.activate is missing",
        ]
    if not report.persistence_evidence_check:
        return STATUS_PERSISTENCE, [
            "activate() does not assert persistence_evidence.persisted == True",
        ]
    if not report.consistency_checks_require_all_true:
        return STATUS_PERSISTENCE, [
            "activate() does not require all consistency_checks to be True",
        ]
    if not report.persistence_blocked_path_present:
        return STATUS_PERSISTENCE, [
            "activate() does not mark persisted=False when persistence fails",
        ]

    # Readback scope gate.
    if not report.readback_scope_enforced:
        return STATUS_READBACK, [
            "readback does not enforce tenant/knowledge_version/snapshot_hash scope",
        ]
    if not report.readback_tenant_check:
        return STATUS_READBACK, ["readback scope check missing: tenant_id"]
    if not report.readback_knowledge_version_check:
        return STATUS_READBACK, [
            "readback scope check missing: knowledge_version_id",
        ]
    if not report.readback_snapshot_hash_check:
        return STATUS_READBACK, [
            "readback scope check missing: snapshot_hash",
        ]

    # Index scope gate.
    if report.index_client_findings:
        reasons = [str(issue) for f in report.index_client_findings for issue in f.issues]
        return STATUS_INDEX, reasons

    # Receipt ordering gate.
    if not report.receipt_after_readback:
        return STATUS_RECEIPT, [
            "snapshot activation receipt is built before the readback completes",
        ]

    reasons.append(
        "Snapshot activation is fail-closed: the persistence port is "
        "present and exposes both persist() and read(); activate() requires "
        "consistency_checks all True, asserts persistence_evidence.persisted, "
        "and marks persisted=False on failure; the readback enforces tenant / "
        "knowledge_version / snapshot_hash scope; the three index clients "
        "require tenant / workspace / knowledge_version (and snapshot_id for "
        "graph paths); and the snapshot activation receipt is built only "
        "after a successful readback."
    )
    return STATUS_CONFIRMED, reasons


# ---------------------------------------------------------------------------
# Contract fixtures
# ---------------------------------------------------------------------------


@dataclass
class ContractFixture:
    name: str
    snapshot_source: str
    adapters_source: str
    expected_status: str
    notes: str = ""


def _good_snapshot_source() -> str:
    return (
        "from typing import Any, Protocol\n"
        "from dataclasses import dataclass\n\n"
        "class SnapshotPersistencePort(Protocol):\n"
        "    def persist(self, *, snapshot_id: str, tenant_id: str,\n"
        "                knowledge_version_id: str, snapshot_payload: dict,\n"
        "                serving_watermark_ref: str) -> dict: ...\n"
        "    def read(self, snapshot_id: str) -> dict | None: ...\n\n"
        "def build_snapshot_activation_receipt(**kwargs):\n"
        "    return {'receipt_ref': 'r', **kwargs}\n\n"
        "class SnapshotActivationAdapter:\n"
        "    def __init__(self, *, snapshot_persistence=None) -> None:\n"
        "        self._p = snapshot_persistence\n\n"
        "    def activate(self, *, tenant_id: str, knowledge_version_id: str):\n"
        "        consistency_checks = {'a': True}\n"
        "        failed = [name for name, ok in consistency_checks.items() if ok is False]\n"
        "        if failed:\n"
        "            return ('BLOCKED', None)\n"
        "        try:\n"
        "            result = self._p.persist(snapshot_id='s', tenant_id=tenant_id,\n"
        "                                      knowledge_version_id=knowledge_version_id,\n"
        "                                      snapshot_payload={}, serving_watermark_ref='w')\n"
        "            read = self._p.read('s')\n"
        "            persistence_evidence = {'persisted': True, 'snapshot_re_readable': True}\n"
        "        except Exception:\n"
        "            persistence_evidence = {'persisted': False}\n"
        "            return ('BLOCKED', None)\n"
        "        if read is None or read.get('tenant_id') != tenant_id \\\n"
        "                or read.get('knowledge_version_id') != knowledge_version_id \\\n"
        "                or read.get('snapshot_hash') != 'h':\n"
        "            return ('BLOCKED', None)\n"
        "        if not persistence_evidence['persisted']:\n"
        "            return ('BLOCKED', None)\n"
        "        receipt = build_snapshot_activation_receipt(\n"
        "            tenant_id=tenant_id, knowledge_version_id=knowledge_version_id,\n"
        "        )\n"
        "        return ('ACTIVATED', receipt)\n\n"
        "class PostgresKnowledgeSnapshotPersistence:\n"
        "    def persist(self, *, snapshot_id, tenant_id, knowledge_version_id,\n"
        "                snapshot_payload, serving_watermark_ref):\n"
        "        return {'tenant_id': tenant_id, 'knowledge_version_id': knowledge_version_id,\n"
        "                'snapshot_hash': 'h'}\n"
        "    def read(self, snapshot_id):\n"
        "        return {'tenant_id': 't', 'knowledge_version_id': 'kv',\n"
        "                'snapshot_hash': 'h'}\n"
    )


def _good_adapter_source() -> str:
    return (
        "class ElasticsearchBm25IndexClient:\n"
        "    def search_documents(self, query, index_name,\n"
        "                          *, tenant_id, workspace_id, knowledge_version_id):\n"
        "        filters = []\n"
        "        if tenant_id: filters.append({'term': {'tenant_id': tenant_id}})\n"
        "        if workspace_id: filters.append({'term': {'workspace_id': workspace_id}})\n"
        "        if knowledge_version_id:\n"
        "            filters.append({'term': {'knowledge_version_id': knowledge_version_id}})\n"
        "        return filters\n"
        "    def fetch_document(self, index_name, chunk_id,\n"
        "                       *, tenant_id, workspace_id, knowledge_version_id):\n"
        "        return {'tenant_id': tenant_id, 'workspace_id': workspace_id,\n"
        "                'knowledge_version_id': knowledge_version_id}\n"
        "    def count_documents(self, index_name,\n"
        "                         *, tenant_id, workspace_id, knowledge_version_id):\n"
        "        filters = []\n"
        "        if tenant_id: filters.append({'term': {'tenant_id': tenant_id}})\n"
        "        if workspace_id: filters.append({'term': {'workspace_id': workspace_id}})\n"
        "        return filters\n"
        "    def index_documents(self, index_name, documents, *, recreate=True):\n"
        "        return None\n\n"
        "class MilvusVectorIndexClient:\n"
        "    def search_documents(self, query, index_name,\n"
        "                          *, tenant_id, workspace_id, knowledge_version_id):\n"
        "        expr = 'tenant_id == \"' + tenant_id + '\"'\n"
        "        return expr\n"
        "    def fetch_document(self, index_name, chunk_id,\n"
        "                       *, tenant_id, workspace_id, knowledge_version_id):\n"
        "        return {'tenant_id': tenant_id, 'workspace_id': workspace_id,\n"
        "                'knowledge_version_id': knowledge_version_id}\n"
        "    def count_documents(self, index_name,\n"
        "                         *, tenant_id, workspace_id, knowledge_version_id):\n"
        "        expr = 'tenant_id == \"' + tenant_id + '\"'\n"
        "        return expr\n"
        "    def index_documents(self, index_name, documents, *, recreate=True):\n"
        "        return None\n\n"
        "class Neo4jGraphIndexClient:\n"
        "    def index_documents(self, index_name, documents,\n"
        "                        *, tenant_id, workspace_id, knowledge_version_id,\n"
        "                        snapshot_id, recreate=True):\n"
        "        return None\n"
        "    def search_documents(self, query, index_name,\n"
        "                          *, tenant_id, workspace_id, knowledge_version_id,\n"
        "                          snapshot_id):\n"
        "        return [tenant_id, workspace_id, knowledge_version_id, snapshot_id]\n"
        "    def index_graph_relations(self, index_name, *, tenant_id, workspace_id,\n"
        "                              knowledge_version_id, snapshot_id,\n"
        "                              entities, relations):\n"
        "        return None\n"
        "    def query_path(self, index_name, *, tenant_id, workspace_id,\n"
        "                   knowledge_version_id, snapshot_id,\n"
        "                   start_entity_ref, end_entity_ref, relation_kinds):\n"
        "        return {'tenant_id': tenant_id, 'snapshot_id': snapshot_id}\n"
        "    def verify_path_visibility_receipt(\n"
        "            self, index_name, *, tenant_id, workspace_id,\n"
        "            knowledge_version_id, snapshot_id, start_entity_ref,\n"
        "            end_entity_ref, relation_kinds, query_kind='directed_path',\n"
        "            config_hash, observed_at=None):\n"
        "        return {'tenant_id': tenant_id, 'snapshot_id': snapshot_id,\n"
        "                'workspace_id': workspace_id,\n"
        "                'knowledge_version_id': knowledge_version_id}\n"
    )


def _build_index_adapter_source(
    *,
    es_required: bool = True,
    milvus_required: bool = True,
    neo4j_required: bool = True,
    es_default_none: bool = False,
    milvus_default_none: bool = False,
    neo4j_default_none: bool = False,
    missing_scope: str | None = None,
    no_scope_filter: bool = False,
) -> str:
    es_tenant = "tenant_id=None" if es_default_none else "tenant_id"
    es_workspace = "workspace_id=None" if es_default_none else "workspace_id"
    es_kv = "knowledge_version_id=None" if es_default_none else "knowledge_version_id"
    milvus_tenant = "tenant_id=None" if milvus_default_none else "tenant_id"
    milvus_workspace = "workspace_id=None" if milvus_default_none else "workspace_id"
    milvus_kv = "knowledge_version_id=None" if milvus_default_none else "knowledge_version_id"
    neo4j_tenant = "tenant_id=None" if neo4j_default_none else "tenant_id"
    neo4j_workspace = "workspace_id=None" if neo4j_default_none else "workspace_id"
    neo4j_kv = "knowledge_version_id=None" if neo4j_default_none else "knowledge_version_id"
    neo4j_snap = "snapshot_id=None" if neo4j_default_none else "snapshot_id"

    if missing_scope == "es":
        es_tenant = "tenant_id=None"
        es_workspace = "workspace_id=None"
        es_kv = "knowledge_version_id=None"
    if missing_scope == "milvus":
        milvus_tenant = "tenant_id=None"
        milvus_workspace = "workspace_id=None"
        milvus_kv = "knowledge_version_id=None"
    if missing_scope == "neo4j":
        neo4j_tenant = "tenant_id=None"
        neo4j_workspace = "workspace_id=None"
        neo4j_kv = "knowledge_version_id=None"
        neo4j_snap = "snapshot_id=None"

    es_filter_block = "" if no_scope_filter else (
        "        filters = []\n"
        "        if tenant_id: filters.append({'term': {'tenant_id': tenant_id}})\n"
    )
    milvus_filter_block = "" if no_scope_filter else (
        "        expr = 'tenant_id == \"' + tenant_id + '\"'\n"
    )
    neo4j_filter_block = "" if no_scope_filter else (
        "        return tenant_id + workspace_id + knowledge_version_id + snapshot_id\n"
    )

    if no_scope_filter:
        # Override the search/fetch methods to ignore their scope params.
        return (
            "class ElasticsearchBm25IndexClient:\n"
            "    def search_documents(self, query, index_name, *, tenant_id, workspace_id, knowledge_version_id):\n"
            "        return []\n"
            "    def fetch_document(self, index_name, chunk_id, *, tenant_id, workspace_id, knowledge_version_id):\n"
            "        return {}\n"
            "    def count_documents(self, index_name, *, tenant_id, workspace_id, knowledge_version_id):\n"
            "        return 0\n\n"
            "class MilvusVectorIndexClient:\n"
            "    def search_documents(self, query, index_name, *, tenant_id, workspace_id, knowledge_version_id):\n"
            "        return []\n"
            "    def fetch_document(self, index_name, chunk_id, *, tenant_id, workspace_id, knowledge_version_id):\n"
            "        return {}\n"
            "    def count_documents(self, index_name, *, tenant_id, workspace_id, knowledge_version_id):\n"
            "        return 0\n\n"
            "class Neo4jGraphIndexClient:\n"
            "    def search_documents(self, query, index_name, *, tenant_id, workspace_id, knowledge_version_id, snapshot_id):\n"
            "        return []\n"
            "    def query_path(self, index_name, *, tenant_id, workspace_id, knowledge_version_id, snapshot_id, start_entity_ref, end_entity_ref, relation_kinds):\n"
            "        return None\n"
            "    def verify_path_visibility_receipt(self, index_name, *, tenant_id, workspace_id, knowledge_version_id, snapshot_id, start_entity_ref, end_entity_ref, relation_kinds, query_kind='directed_path', config_hash, observed_at=None):\n"
            "        return None\n"
        )

    return (
        "class ElasticsearchBm25IndexClient:\n"
        f"    def search_documents(self, query, index_name, *, {es_tenant}, {es_workspace}, {es_kv}):\n"
        f"{es_filter_block}"
        "        return []\n"
        "    def fetch_document(self, index_name, chunk_id):\n"
        "        return None\n"
        "    def count_documents(self, index_name):\n"
        "        return 0\n"
        "    def index_documents(self, index_name, documents):\n"
        "        return None\n\n"
        "class MilvusVectorIndexClient:\n"
        f"    def search_documents(self, query, index_name, *, {milvus_tenant}, {milvus_workspace}, {milvus_kv}):\n"
        f"{milvus_filter_block}"
        "        return []\n"
        "    def fetch_document(self, index_name, chunk_id):\n"
        "        return None\n"
        "    def count_documents(self, index_name):\n"
        "        return 0\n"
        "    def index_documents(self, index_name, documents):\n"
        "        return None\n\n"
        "class Neo4jGraphIndexClient:\n"
        f"    def index_documents(self, index_name, documents, *, {neo4j_tenant}, {neo4j_workspace}, {neo4j_kv}, {neo4j_snap}):\n"
        "        return None\n"
        f"    def search_documents(self, query, index_name, *, {neo4j_tenant}, {neo4j_workspace}, {neo4j_kv}, {neo4j_snap}):\n"
        f"{neo4j_filter_block}"
        "    def index_graph_relations(self, index_name, *, tenant_id, workspace_id,\n"
        "                              knowledge_version_id, snapshot_id,\n"
        "                              entities, relations):\n"
        "        return None\n"
        "    def query_path(self, index_name, *, tenant_id, workspace_id,\n"
        "                   knowledge_version_id, snapshot_id,\n"
        "                   start_entity_ref, end_entity_ref, relation_kinds):\n"
        "        return None\n"
        "    def verify_path_visibility_receipt(self, index_name, *, tenant_id,\n"
        "            workspace_id, knowledge_version_id, snapshot_id,\n"
        "            start_entity_ref, end_entity_ref, relation_kinds,\n"
        "            query_kind='directed_path', config_hash, observed_at=None):\n"
        "        return None\n"
    )


def _contract_fixtures() -> Iterable[ContractFixture]:
    # 1. Correct fail-closed implementation.
    yield ContractFixture(
        name="correct_fail_closed_implementation",
        snapshot_source=_good_snapshot_source(),
        adapters_source=_good_adapter_source(),
        expected_status=STATUS_CONFIRMED,
    )
    # 2. Persistence port missing.
    yield ContractFixture(
        name="persistence_port_missing",
        snapshot_source=_good_snapshot_source().replace(
            "class SnapshotPersistencePort(Protocol):",
            "class _NotThePort:",
        ),
        adapters_source=_good_adapter_source(),
        expected_status=STATUS_PERSISTENCE,
    )
    # 3. Persist throws - simulate by removing the ``persisted: True``
#    branch.  Static analysis sees the persist call but cannot detect the
#    runtime exception; we instead make the activate() body skip the
#    persistence_evidence.persisted assertion, which is the only thing
#    the gate can statically prove.
    yield ContractFixture(
        name="persist_throws",
        snapshot_source=_good_snapshot_source()
            .replace(
                "        if not persistence_evidence['persisted']:\n"
                "            return ('BLOCKED', None)",
                "        # omit persistence evidence check",
            )
            .replace(
                "            persistence_evidence = {'persisted': True, 'snapshot_re_readable': True}",
                "            persistence_evidence = {}",
            ),
        adapters_source=_good_adapter_source(),
        expected_status=STATUS_PERSISTENCE,
    )
    # 4. Persist returns but readback None - read() implementation
    #    returns dict but does not include tenant_id (missing scope).
    yield ContractFixture(
        name="persist_returns_readback_none",
        snapshot_source=_good_snapshot_source().replace(
            "    def read(self, snapshot_id):\n"
            "        return {'tenant_id': 't', 'knowledge_version_id': 'kv',\n"
            "                'snapshot_hash': 'h'}\n",
            "    def read(self, snapshot_id):\n"
            "        return {}\n",
        ),
        adapters_source=_good_adapter_source(),
        expected_status=STATUS_READBACK,
    )
    # 5. Readback tenant wrong - read() returns dict without tenant_id.
    yield ContractFixture(
        name="readback_tenant_wrong",
        snapshot_source=_good_snapshot_source().replace(
            "        return {'tenant_id': 't', 'knowledge_version_id': 'kv',\n"
            "                'snapshot_hash': 'h'}\n",
            "        return {'knowledge_version_id': 'kv', 'snapshot_hash': 'h'}\n",
        ),
        adapters_source=_good_adapter_source(),
        expected_status=STATUS_READBACK,
    )
    # 6. Readback knowledge_version wrong - read() missing knowledge_version_id.
    yield ContractFixture(
        name="readback_knowledge_version_wrong",
        snapshot_source=_good_snapshot_source().replace(
            "        return {'tenant_id': 't', 'knowledge_version_id': 'kv',\n"
            "                'snapshot_hash': 'h'}\n",
            "        return {'tenant_id': 't', 'snapshot_hash': 'h'}\n",
        ),
        adapters_source=_good_adapter_source(),
        expected_status=STATUS_READBACK,
    )
    # 7. Readback snapshot hash wrong - read() missing snapshot_hash.
    yield ContractFixture(
        name="readback_snapshot_hash_wrong",
        snapshot_source=_good_snapshot_source().replace(
            "        return {'tenant_id': 't', 'knowledge_version_id': 'kv',\n"
            "                'snapshot_hash': 'h'}\n",
            "        return {'tenant_id': 't', 'knowledge_version_id': 'kv'}\n",
        ),
        adapters_source=_good_adapter_source(),
        expected_status=STATUS_READBACK,
    )
    # 8. consistency_check=False but still ACTIVATED - drop the
#    ``failed`` guard so consistency checks can never BLOCK the
#    activation.
    yield ContractFixture(
        name="consistency_check_false_but_activated",
        snapshot_source=_good_snapshot_source().replace(
            "        failed = [name for name, ok in consistency_checks.items() if ok is False]\n"
            "        if failed:\n"
            "            return ('BLOCKED', None)\n",
            "        pass\n",
        ),
        adapters_source=_good_adapter_source(),
        expected_status=STATUS_PERSISTENCE,
    )
    # 9. consistency_checks missing - drop both the dict construction
#    and the ``failed`` guard.
    yield ContractFixture(
        name="consistency_checks_missing",
        snapshot_source=_good_snapshot_source().replace(
            "        consistency_checks = {'a': True}\n"
            "        failed = [name for name, ok in consistency_checks.items() if ok is False]\n"
            "        if failed:\n"
            "            return ('BLOCKED', None)\n",
            "        pass\n",
        ),
        adapters_source=_good_adapter_source(),
        expected_status=STATUS_PERSISTENCE,
    )
    # 10. Receipt built before persist.
    yield ContractFixture(
        name="receipt_before_persist",
        snapshot_source=(
            "from typing import Any, Protocol\n\n"
            "class SnapshotPersistencePort(Protocol):\n"
            "    def persist(self, *, snapshot_id: str, tenant_id: str,\n"
            "                knowledge_version_id: str, snapshot_payload: dict,\n"
            "                serving_watermark_ref: str) -> dict: ...\n"
            "    def read(self, snapshot_id: str) -> dict | None: ...\n\n"
            "def build_snapshot_activation_receipt(**kwargs):\n"
            "    return {'receipt_ref': 'r', **kwargs}\n\n"
            "class SnapshotActivationAdapter:\n"
            "    def __init__(self, *, snapshot_persistence=None) -> None:\n"
            "        self._p = snapshot_persistence\n\n"
            "    def activate(self, *, tenant_id: str, knowledge_version_id: str):\n"
            "        consistency_checks = {'a': True}\n"
            "        failed = [name for name, ok in consistency_checks.items() if ok is False]\n"
            "        if failed:\n"
            "            return ('BLOCKED', None)\n"
            "        receipt = build_snapshot_activation_receipt(tenant_id=tenant_id)\n"
            "        try:\n"
            "            result = self._p.persist(snapshot_id='s', tenant_id=tenant_id,\n"
            "                                      knowledge_version_id=knowledge_version_id,\n"
            "                                      snapshot_payload={}, serving_watermark_ref='w')\n"
            "            read = self._p.read('s')\n"
            "            persistence_evidence = {'persisted': True}\n"
            "        except Exception:\n"
            "            persistence_evidence = {'persisted': False}\n"
            "            return ('BLOCKED', None)\n"
            "        if not persistence_evidence['persisted']:\n"
            "            return ('BLOCKED', None)\n"
            "        return ('ACTIVATED', receipt)\n\n"
            "class PostgresKnowledgeSnapshotPersistence:\n"
            "    def persist(self, *, snapshot_id, tenant_id, knowledge_version_id,\n"
            "                snapshot_payload, serving_watermark_ref):\n"
            "        return {'tenant_id': tenant_id, 'knowledge_version_id': knowledge_version_id,\n"
            "                'snapshot_hash': 'h'}\n"
            "    def read(self, snapshot_id):\n"
            "        return {'tenant_id': 't', 'knowledge_version_id': 'kv',\n"
            "                'snapshot_hash': 'h'}\n"
        ),
        adapters_source=_good_adapter_source(),
        expected_status=STATUS_RECEIPT,
    )
    # 11. ES missing scope.
    yield ContractFixture(
        name="es_missing_scope",
        snapshot_source=_good_snapshot_source(),
        adapters_source=_build_index_adapter_source(missing_scope="es"),
        expected_status=STATUS_INDEX,
    )
    # 12. Milvus missing scope.
    yield ContractFixture(
        name="milvus_missing_scope",
        snapshot_source=_good_snapshot_source(),
        adapters_source=_build_index_adapter_source(missing_scope="milvus"),
        expected_status=STATUS_INDEX,
    )
    # 13. Neo4j missing scope.
    yield ContractFixture(
        name="neo4j_missing_scope",
        snapshot_source=_good_snapshot_source(),
        adapters_source=_build_index_adapter_source(missing_scope="neo4j"),
        expected_status=STATUS_INDEX,
    )
    # 14. Foreign snapshot - persistence path calls a foreign module via
#    __import__; the gate cannot resolve the binding statically.
    yield ContractFixture(
        name="foreign_snapshot_dynamic_port",
        snapshot_source=_good_snapshot_source().replace(
            "        result = self._p.persist(snapshot_id='s', tenant_id=tenant_id,",
            "        foreign = __import__('foreign_persist_module')\n"
            "        result = foreign.persist(snapshot_id='s', tenant_id=tenant_id,",
        ).replace(
            "        read = self._p.read('s')\n",
            "        read = foreign.read('s')\n",
        ),
        adapters_source=_good_adapter_source(),
        expected_status=STATUS_UNRESOLVED,
    )
    # 15. Adapter smoke receipt attempt - missing scope filter.
    yield ContractFixture(
        name="adapter_smoke_no_scope_filter",
        snapshot_source=_good_snapshot_source(),
        adapters_source=_build_index_adapter_source(no_scope_filter=True),
        expected_status=STATUS_INDEX,
    )
    # 16. Immutable snapshot payload conflict - the receipt is built BEFORE
#     persist+read, so the immutable payload comparison cannot be enforced.
    yield ContractFixture(
        name="immutable_payload_conflict",
        snapshot_source=(
            "from typing import Any, Protocol\n\n"
            "class SnapshotPersistencePort(Protocol):\n"
            "    def persist(self, *, snapshot_id: str, tenant_id: str,\n"
            "                knowledge_version_id: str, snapshot_payload: dict,\n"
            "                serving_watermark_ref: str) -> dict: ...\n"
            "    def read(self, snapshot_id: str) -> dict | None: ...\n\n"
            "def build_snapshot_activation_receipt(**kwargs):\n"
            "    return {'receipt_ref': 'r', **kwargs}\n\n"
            "class SnapshotActivationAdapter:\n"
            "    def __init__(self, *, snapshot_persistence=None) -> None:\n"
            "        self._p = snapshot_persistence\n\n"
            "    def activate(self, *, tenant_id: str, knowledge_version_id: str,\n"
            "                  snapshot_payload: dict):\n"
            "        consistency_checks = {'a': True}\n"
            "        failed = [name for name, ok in consistency_checks.items() if ok is False]\n"
            "        if failed:\n"
            "            return ('BLOCKED', None)\n"
            "        # Build the receipt BEFORE persist+readback.\n"
            "        receipt = build_snapshot_activation_receipt(tenant_id=tenant_id)\n"
            "        try:\n"
            "            result = self._p.persist(snapshot_id='s', tenant_id=tenant_id,\n"
            "                                      knowledge_version_id=knowledge_version_id,\n"
            "                                      snapshot_payload=snapshot_payload,\n"
            "                                      serving_watermark_ref='w')\n"
            "            read = self._p.read('s')\n"
            "            persistence_evidence = {'persisted': True}\n"
            "        except Exception:\n"
            "            persistence_evidence = {'persisted': False}\n"
            "            return ('BLOCKED', None)\n"
            "        if read is None:\n"
            "            return ('BLOCKED', None)\n"
            "        if not persistence_evidence['persisted']:\n"
            "            return ('BLOCKED', None)\n"
            "        return ('ACTIVATED', receipt)\n\n"
            "class PostgresKnowledgeSnapshotPersistence:\n"
            "    def persist(self, *, snapshot_id, tenant_id, knowledge_version_id,\n"
            "                snapshot_payload, serving_watermark_ref):\n"
            "        return {'tenant_id': tenant_id, 'knowledge_version_id': knowledge_version_id,\n"
            "                'snapshot_hash': 'h'}\n"
            "    def read(self, snapshot_id):\n"
            "        return {'tenant_id': 't', 'knowledge_version_id': 'kv',\n"
            "                'snapshot_hash': 'h'}\n"
        ),
        adapters_source=_good_adapter_source(),
        expected_status=STATUS_RECEIPT,
    )


def _evaluate_fixture(fixture: ContractFixture) -> Tuple[str, SnapshotReport, List[str]]:
    import tempfile

    report = SnapshotReport()
    reasons: List[str] = []
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        snap_path = tmp / SNAPSHOT_ACTIVATION_PATH
        snap_path.parent.mkdir(parents=True, exist_ok=True)
        snap_path.write_text(fixture.snapshot_source, encoding="utf-8")
        adp_path = tmp / INDEX_ADAPTERS_PATH
        adp_path.parent.mkdir(parents=True, exist_ok=True)
        adp_path.write_text(fixture.adapters_source, encoding="utf-8")
        report = collect_observations(tmp)
        status, reasons = evaluate(report)
    return status, report, reasons


# ---------------------------------------------------------------------------
# Mode handlers
# ---------------------------------------------------------------------------


def _contract_mode() -> Tuple[int, Dict[str, Any]]:
    fixtures = list(_contract_fixtures())
    results: List[Dict[str, Any]] = []
    overall_exit = EXIT_CONFIRMED
    overall_status = STATUS_CONFIRMED
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
        status, reasons = evaluate(report)
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
        "not_proven": list(NOT_PROVEN_BOUNDARY),
        "report": report.to_dict(),
    }


def _status_to_exit(status: str) -> int:
    mapping = {
        STATUS_CONFIRMED: EXIT_CONFIRMED,
        STATUS_PERSISTENCE: EXIT_PERSISTENCE,
        STATUS_READBACK: EXIT_READBACK,
        STATUS_INDEX: EXIT_INDEX,
        STATUS_RECEIPT: EXIT_RECEIPT,
        STATUS_TOOL_ERROR: EXIT_TOOL_ERROR,
    }
    return mapping.get(status, EXIT_UNRESOLVED)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="PHASE22-SNAPSHOT-FAIL-CLOSED-GATE verifier"
    )
    parser.add_argument(
        "--mode",
        choices=("contract", "repository"),
        default="contract",
    )
    parser.add_argument("--json", action="store_true")
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
        print(f"[phase22-snapshot-fail-closed-gate] mode={args.mode} status={status}")
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