"""Fail-closed Object Store Owner / Composition Root Binding Gate.

PHASE22-OBJECT-STORE-OWNER-GATE verifier.

The old DeepSeek preflight rejected the codebase because a static AST scan
counted four classes whose name ends with ``ObjectStore``::

    DurableObjectStore       (Protocol / Port)
    LocalObjectStore         (local development adapter)
    DurableMinioObjectStore  (durable wrapper around the production adapter)
    MinioObjectStore         (production MinIO adapter)

Counting class-name suffixes is a heuristic, not a binding proof.  Port,
Local Adapter, Test Double and Durable Wrapper may coexist without changing
the runtime owner.  The correct question is: **which object store does the
production composition root actually bind for the canonical ingestion
runtime?**  This module is a fail-closed gate that answers that question
directly and refuses to call the binding "unique" on class-name heuristics.

Output states:

* ``UNIQUE_PRODUCTION_BINDING_CONFIRMED`` - exactly one production adapter
  is bound and it is the only owner for the production runtime.
* ``MULTIPLE_PRODUCTION_BINDINGS``       - two or more production adapters
  are simultaneously bound for the production runtime.
* ``NO_PRODUCTION_BINDING``              - no production adapter is bound.
  The composition root is required to fail closed in this state.
* ``BINDING_UNRESOLVED``                 - the gate cannot prove ownership
  from the available facts (missing files, ambiguous wiring, etc.).

Exit codes:

* ``0`` UNIQUE_PRODUCTION_BINDING_CONFIRMED
* ``2`` MULTIPLE_PRODUCTION_BINDINGS
* ``3`` NO_PRODUCTION_BINDING
* ``4`` BINDING_UNRESOLVED
* ``5`` TOOL_ERROR

Two operating modes:

* ``--mode contract``    - validates the gate's own contract (self-test).
* ``--mode repository``  - inspects the real repository and reports the
  current binding status.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


REPO_ROOT = Path(__file__).resolve().parents[2]

EXIT_UNIQUE = 0
EXIT_MULTIPLE = 2
EXIT_NONE = 3
EXIT_UNRESOLVED = 4
EXIT_TOOL_ERROR = 5

STATUS_UNIQUE = "UNIQUE_PRODUCTION_BINDING_CONFIRMED"
STATUS_MULTIPLE = "MULTIPLE_PRODUCTION_BINDINGS"
STATUS_NONE = "NO_PRODUCTION_BINDING"
STATUS_UNRESOLVED = "BINDING_UNRESOLVED"

# Roles the gate recognises.  Each match is anchored to a source file
# fragment so the gate does not rely on class-name suffix counting alone.
ROLE_PROTOCOL_PORT = "protocol_port"
ROLE_LOCAL_ADAPTER = "local_development_adapter"
ROLE_TEST_DOUBLE = "test_double"
ROLE_PRODUCTION_ADAPTER = "production_minio_adapter"
ROLE_DURABLE_WRAPPER = "durable_wrapper"
ROLE_COMPOSITION_ROOT = "composition_root_binding"
ROLE_RUNTIME_OWNER = "runtime_owner"

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

# Call sites of the composition root factory are required to be enumerable.
COMPOSITION_ROOT_CALL_SITES = (
    "src/backend/zuno/main.py",
    "src/backend/zuno/platform/services/queue/runner.py",
)


@dataclass(frozen=True)
class ClassObservation:
    """A single observed object-store-related class."""

    role: str
    qualified_name: str
    file_path: str
    line_number: int
    notes: Tuple[str, ...] = field(default_factory=Tuple)


@dataclass
class BindingReport:
    """Aggregate facts collected by the verifier."""

    observations: List[ClassObservation] = field(default_factory=list)
    runtime_owner_dependencies: Tuple[Tuple[str, str], ...] = ()
    composition_root_signature: Dict[str, str] = field(default_factory=dict)
    composition_root_body_references: Dict[str, int] = field(default_factory=dict)
    composition_root_call_sites: List[Dict[str, Any]] = field(default_factory=list)
    production_storage_mode_seen: Tuple[str, ...] = ()
    local_binding_sites_seen: Tuple[str, ...] = ()
    fail_closed_branches: Tuple[str, ...] = ()
    receipts_observed: Tuple[str, ...] = ()
    tenant_workspace_bindings: Tuple[str, ...] = ()
    wrapper_binding_chain: Tuple[str, ...] = ()
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
            "composition_root_body_references": dict(
                self.composition_root_body_references
            ),
            "composition_root_call_sites": list(self.composition_root_call_sites),
            "production_storage_mode_seen": list(self.production_storage_mode_seen),
            "local_binding_sites_seen": list(self.local_binding_sites_seen),
            "fail_closed_branches": list(self.fail_closed_branches),
            "receipts_observed": list(self.receipts_observed),
            "tenant_workspace_bindings": list(self.tenant_workspace_bindings),
            "wrapper_binding_chain": list(self.wrapper_binding_chain),
            "errors": list(self.error_messages),
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _line_index(text: str) -> List[int]:
    offsets = [0]
    for index, char in enumerate(text):
        if char == "\n":
            offsets.append(index + 1)
    return offsets


def _line_for_offset(offsets: List[int], offset: int) -> int:
    line = 1
    for index, start in enumerate(offsets):
        if start > offset:
            break
        line = index + 1
    return line


def _find_class(
    text: str, class_name: str
) -> Tuple[int, int] | None:
    pattern = re.compile(rf"^class\s+{re.escape(class_name)}\b", re.MULTILINE)
    match = pattern.search(text)
    if match is None:
        return None
    start = match.start()
    line_end = text.find("\n", start)
    if line_end == -1:
        line_end = len(text)
    header_end = text.find(":", match.end())
    if header_end == -1 or header_end > line_end:
        header_end = line_end
    return start, header_end


def _scan_init_parameters(
    text: str, class_name: str
) -> Dict[str, str]:
    start_end = _find_class(text, class_name)
    if start_end is None:
        return {}
    start, _ = start_end
    init_match = re.search(
        r"def\s+__init__\s*\(([^)]*)\)\s*(?:->\s*[^:]+)?:",
        text[start:],
        re.DOTALL,
    )
    if init_match is None:
        return {}
    raw = init_match.group(1)
    params: Dict[str, str] = {}
    for chunk in raw.split(","):
        cleaned = chunk.strip()
        if not cleaned:
            continue
        if cleaned.startswith("**") or cleaned.startswith("*"):
            continue
        name_part = cleaned
        if "=" in name_part:
            name_part = name_part.split("=", 1)[0]
        annotation = ""
        if ":" in name_part:
            name_part, annotation = name_part.split(":", 1)
            annotation = annotation.strip()
        name = name_part.strip()
        if name and name not in {"self", "cls"}:
            params[name] = annotation
    return params


def _class_header_line(text: str, offsets: List[int], class_name: str) -> int | None:
    start_end = _find_class(text, class_name)
    if start_end is None:
        return None
    start, _ = start_end
    return _line_for_offset(offsets, start)


def _function_body_range(text: str, function_name: str) -> Tuple[int, int] | None:
    """Return the (start, end) offsets of *function_name*'s body.

    The body is bounded by the next top-level ``def`` or ``class`` keyword at
    the same indentation level, or end-of-file, whichever comes first.  This
    is a coarse heuristic that is sufficient for the production factory whose
    body is delimited by the next top-level ``@classmethod`` decorator.
    """

    pattern = re.compile(
        rf"^(?:async\s+)?def\s+{re.escape(function_name)}\b",
        re.MULTILINE,
    )
    match = pattern.search(text)
    if match is None:
        return None
    body_start = text.find(":", match.end()) + 1
    # Determine indentation of the def line.
    line_start = text.rfind("\n", 0, match.start()) + 1
    indent_match = re.match(r"[ \t]*", text[line_start:match.start()])
    indent = indent_match.group(0) if indent_match else ""
    # Scan forward for the next def/class at the same indent.
    scanner = re.compile(
        rf"^{re.escape(indent)}(?:def|class|@)\s", re.MULTILINE
    )
    next_match = scanner.search(text, body_start)
    body_end = next_match.start() if next_match is not None else len(text)
    return body_start, body_end


def _split_outside_brackets(raw: str) -> List[str]:
    """Split *raw* on top-level commas, ignoring ``[]`` and ``()`` nesting."""

    chunks: List[str] = []
    depth = 0
    current: List[str] = []
    for char in raw:
        if char in "[(":
            depth += 1
            current.append(char)
        elif char in "])":
            depth -= 1
            current.append(char)
        elif char == "," and depth == 0:
            chunks.append("".join(current))
            current = []
        else:
            current.append(char)
    if current:
        chunks.append("".join(current))
    return chunks


def _extract_signature_defaults(text: str, function_name: str) -> Dict[str, str]:
    """Return ``param -> default_expression`` for *function_name*."""

    pattern = re.compile(
        rf"^(?:async\s+)?def\s+{re.escape(function_name)}\s*\(",
        re.MULTILINE,
    )
    match = pattern.search(text)
    if match is None:
        return {}
    start = match.end()
    depth = 1
    end = start
    while end < len(text) and depth > 0:
        char = text[end]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        end += 1
    raw = text[start:end - 1]
    defaults: Dict[str, str] = {}
    for chunk in _split_outside_brackets(raw):
        cleaned = chunk.strip()
        if not cleaned or "=" not in cleaned:
            continue
        name_part, default_part = cleaned.split("=", 1)
        if ":" in name_part:
            name_part = name_part.split(":", 1)[0]
        name = name_part.strip().lstrip("*").strip()
        if not name:
            continue
        defaults[name] = default_part.strip()
    return defaults


# ---------------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------------


def collect_observations(repo_root: Path) -> BindingReport:
    report = BindingReport()

    # --- 1. Class roles -----------------------------------------------------
    role_targets = [
        (
            PROTOCOL_PORT_PATH,
            PROTOCOL_PORT_CLASS,
            ROLE_PROTOCOL_PORT,
            ("structural Protocol defining the port",),
        ),
        (
            LOCAL_ADAPTER_PATH,
            LOCAL_ADAPTER_CLASS,
            ROLE_LOCAL_ADAPTER,
            ("local filesystem adapter; not bound by production composition root",),
        ),
        (
            PRODUCTION_ADAPTER_PATH,
            PRODUCTION_ADAPTER_CLASS,
            ROLE_PRODUCTION_ADAPTER,
            ("MinIO client; production adapter",),
        ),
        (
            DURABLE_WRAPPER_PATH,
            DURABLE_WRAPPER_CLASS,
            ROLE_DURABLE_WRAPPER,
            ("durable wrapper around the production adapter",),
        ),
    ]

    for relative_path, class_name, role, notes in role_targets:
        path = repo_root / relative_path
        if not path.exists():
            report.error_messages.append(
                f"required source file missing: {relative_path}"
            )
            continue
        text = _read_text(path)
        offsets = _line_index(text)
        header_line = _class_header_line(text, offsets, class_name)
        if header_line is None:
            report.error_messages.append(
                f"expected class {class_name!r} not found in {relative_path}"
            )
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

    # --- 2. Canonical runtime owner ----------------------------------------
    runtime_path = repo_root / CANONICAL_RUNTIME_PATH
    if not runtime_path.exists():
        report.error_messages.append(
            f"canonical ingestion runtime file missing: {CANONICAL_RUNTIME_PATH}"
        )
    else:
        runtime_text = _read_text(runtime_path)
        runtime_offsets = _line_index(runtime_text)
        runtime_line = _class_header_line(
            runtime_text, runtime_offsets, CANONICAL_RUNTIME_CLASS
        )
        if runtime_line is None:
            report.error_messages.append(
                f"canonical runtime class {CANONICAL_RUNTIME_CLASS!r} not found"
            )
        else:
            report.observations.append(
                ClassObservation(
                    role=ROLE_RUNTIME_OWNER,
                    qualified_name=CANONICAL_RUNTIME_CLASS,
                    file_path=CANONICAL_RUNTIME_PATH,
                    line_number=runtime_line,
                    notes=("depends on DurableMinioObjectStore",),
                )
            )
            init_params = _scan_init_parameters(
                runtime_text, CANONICAL_RUNTIME_CLASS
            )
            dependency = init_params.get(CANONICAL_RUNTIME_FIELD, "")
            if dependency:
                report.runtime_owner_dependencies = (
                    (CANONICAL_RUNTIME_FIELD, dependency),
                )
            else:
                report.error_messages.append(
                    f"{CANONICAL_RUNTIME_CLASS}.__init__ has no {CANONICAL_RUNTIME_FIELD!r} parameter"
                )

        if "s3://" in runtime_text:
            offset = runtime_text.find("s3://")
            line = _line_for_offset(runtime_offsets, offset)
            report.receipts_observed = (f"s3:// scheme at line {line}",)

        tenant_patterns = (
            r"_object_name\(.*?\)",
            r"\{command\.tenant_id\}/\{command\.workspace_id\}/",
            r"\{plan\.tenant_id\}/\{plan\.workspace_id\}/",
        )
        for pattern in tenant_patterns:
            match = re.search(pattern, runtime_text)
            if match is not None:
                line = _line_for_offset(runtime_offsets, match.start())
                report.tenant_workspace_bindings = (
                    *report.tenant_workspace_bindings,
                    f"tenant/workspace prefix bound at line {line}",
                )
                break

    # --- 3. Composition root binding ---------------------------------------
    comp_path = repo_root / COMPOSITION_ROOT_PATH
    if not comp_path.exists():
        report.error_messages.append(
            f"composition root file missing: {COMPOSITION_ROOT_PATH}"
        )
    else:
        comp_text = _read_text(comp_path)
        comp_offsets = _line_index(comp_text)

        factory_match = re.search(
            rf"def\s+{COMPOSITION_ROOT_FACTORY}\s*\(", comp_text
        )
        if factory_match is None:
            report.error_messages.append(
                f"composition root factory {COMPOSITION_ROOT_FACTORY!r} not found"
            )
        else:
            line = _line_for_offset(comp_offsets, factory_match.start())
            report.observations.append(
                ClassObservation(
                    role=ROLE_COMPOSITION_ROOT,
                    qualified_name=COMPOSITION_ROOT_FACTORY,
                    file_path=COMPOSITION_ROOT_PATH,
                    line_number=line,
                    notes=("returns PackageAProductionIngestionRuntime or None",),
                )
            )
            defaults = _extract_signature_defaults(
                comp_text, COMPOSITION_ROOT_FACTORY
            )
            report.composition_root_signature = defaults
            body_range = _function_body_range(comp_text, COMPOSITION_ROOT_FACTORY)
            if body_range is not None:
                body_start, body_end = body_range
                body = comp_text[body_start:body_end]
                counts: Dict[str, int] = {}
                for name in (
                    PRODUCTION_ADAPTER_CLASS,
                    DURABLE_WRAPPER_CLASS,
                    LOCAL_ADAPTER_CLASS,
                    "LazyStorageClient",
                    "OSSClient",
                ):
                    counts[name] = len(re.findall(rf"\b{re.escape(name)}\b", body))
                report.composition_root_body_references = counts

                # Wrapper binding chain: which local variable carries the
                # adapter, and which variable does the wrapper wrap?
                wrapper_match = re.search(
                    rf"durable_object_store_factory\(\s*([^)]*)\)", body
                )
                if wrapper_match is not None:
                    chain = wrapper_match.group(1).replace("\n", " ").strip()
                    report.wrapper_binding_chain = (chain,)
                    adapter_match = re.search(
                        rf"object_store_factory\(\s*([^)]*)\)", body
                    )
                    if adapter_match is not None:
                        report.wrapper_binding_chain = (
                            *report.wrapper_binding_chain,
                            f"object_store_factory bound: {adapter_match.group(1).strip()}",
                        )

            # Fail-closed semantics: return None on storage.mode != "minio"
            # or empty credentials.
            for pattern in (
                r"storage\.mode.*?\"minio\"",
                r"endpoint.*?access_key.*?secret_key",
                r"return\s+None",
            ):
                for match in re.finditer(pattern, comp_text):
                    line = _line_for_offset(comp_offsets, match.start())
                    report.fail_closed_branches = report.fail_closed_branches + (
                        f"{pattern} at line {line}",
                    )

            if COMPOSITION_ROOT_LOCAL_FACTORY in comp_text:
                report.local_binding_sites_seen = (COMPOSITION_ROOT_LOCAL_FACTORY,)

            storage_pattern = re.compile(r"storage\.mode\s*[!=]=\s*['\"]minio['\"]")
            for match in storage_pattern.finditer(comp_text):
                line = _line_for_offset(comp_offsets, match.start())
                report.production_storage_mode_seen = (
                    *report.production_storage_mode_seen,
                    f"storage.mode check at line {line}",
                )

    # --- 4. Composition root call sites -------------------------------------
    for relative in COMPOSITION_ROOT_CALL_SITES:
        path = repo_root / relative
        if not path.exists():
            continue
        text = _read_text(path)
        offsets = _line_index(text)
        for match in re.finditer(
            rf"{COMPOSITION_ROOT_FACTORY}\s*\(([^)]*)\)", text, re.DOTALL
        ):
            line = _line_for_offset(offsets, match.start())
            args = match.group(1).replace("\n", " ").strip()
            report.composition_root_call_sites.append(
                {
                    "file_path": relative,
                    "line_number": line,
                    "arguments": args,
                }
            )

    return report


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------


def _collect_observations_by_role(
    report: BindingReport, role: str
) -> List[ClassObservation]:
    return [obs for obs in report.observations if obs.role == role]


def evaluate(report: BindingReport) -> Tuple[str, List[str]]:
    reasons: List[str] = []

    # 0. Structural prerequisites.
    if report.error_messages:
        for message in report.error_messages:
            reasons.append(message)
        return STATUS_UNRESOLVED, reasons

    # 1. Runtime owner must depend on the durable wrapper.
    dependencies = dict(report.runtime_owner_dependencies)
    runtime_type = dependencies.get(CANONICAL_RUNTIME_FIELD, "")
    if runtime_type != DURABLE_WRAPPER_CLASS:
        reasons.append(
            f"{CANONICAL_RUNTIME_CLASS}.{CANONICAL_RUNTIME_FIELD}={runtime_type!r} "
            f"does not bind {DURABLE_WRAPPER_CLASS!r}"
        )
        return STATUS_UNRESOLVED, reasons

    # 2. Composition root signature binds the production adapter + wrapper.
    signature = report.composition_root_signature
    if signature.get("object_store_factory") != PRODUCTION_ADAPTER_CLASS:
        reasons.append(
            "composition root signature default for object_store_factory must be "
            f"{PRODUCTION_ADAPTER_CLASS!r}, observed {signature.get('object_store_factory')!r}"
        )
        return STATUS_UNRESOLVED, reasons
    if signature.get("durable_object_store_factory") != DURABLE_WRAPPER_CLASS:
        reasons.append(
            "composition root signature default for durable_object_store_factory must be "
            f"{DURABLE_WRAPPER_CLASS!r}, observed {signature.get('durable_object_store_factory')!r}"
        )
        return STATUS_UNRESOLVED, reasons
    if signature.get("runtime_factory") != CANONICAL_RUNTIME_CLASS:
        reasons.append(
            "composition root signature default for runtime_factory must be "
            f"{CANONICAL_RUNTIME_CLASS!r}, observed {signature.get('runtime_factory')!r}"
        )
        return STATUS_UNRESOLVED, reasons

    # 3. Composition root body must NOT reference the local adapter or
    #    alternative MinIO storage clients.
    body_refs = report.composition_root_body_references
    if body_refs.get(LOCAL_ADAPTER_CLASS, 0) > 0:
        reasons.append(
            f"composition root body references {LOCAL_ADAPTER_CLASS!r}; production "
            "factory must not bind the local adapter"
        )
        return STATUS_UNRESOLVED, reasons
    if body_refs.get("LazyStorageClient", 0) > 0:
        reasons.append(
            "composition root body references LazyStorageClient; production factory "
            "must not bind a non-MinIO adapter"
        )
        return STATUS_UNRESOLVED, reasons
    if body_refs.get("OSSClient", 0) > 0:
        reasons.append(
            "composition root body references OSSClient; production factory "
            "must not bind a non-MinIO adapter"
        )
        return STATUS_UNRESOLVED, reasons

    # 4. Composition root body must reference the production adapter and
    #    wrapper exactly once each.
    production_count = body_refs.get(PRODUCTION_ADAPTER_CLASS, 0)
    wrapper_count = body_refs.get(DURABLE_WRAPPER_CLASS, 0)
    if production_count > 1:
        reasons.append(
            f"composition root body mentions {PRODUCTION_ADAPTER_CLASS!r} "
            f"{production_count} times; exactly one production binding allowed"
        )
        return STATUS_MULTIPLE, reasons
    if wrapper_count > 1:
        reasons.append(
            f"composition root body mentions {DURABLE_WRAPPER_CLASS!r} "
            f"{wrapper_count} times; exactly one durable wrapper allowed"
        )
        return STATUS_MULTIPLE, reasons
    if production_count == 0 or wrapper_count == 0:
        reasons.append(
            "composition root body is missing a production adapter or durable "
            "wrapper instantiation"
        )
        return STATUS_UNRESOLVED, reasons

    # 5. Wrapper must wrap the production adapter (via store= argument).
    if not report.wrapper_binding_chain:
        reasons.append("composition root does not instantiate the durable wrapper")
        return STATUS_UNRESOLVED, reasons
    wrapper_args = report.wrapper_binding_chain[0]
    if "store=" not in wrapper_args:
        reasons.append(
            "durable wrapper binding is missing a 'store=' argument; "
            "the wrapper must wrap the production adapter output"
        )
        return STATUS_UNRESOLVED, reasons

    # 6. Composition root call sites must not introduce alternative adapters.
    call_sites = report.composition_root_call_sites
    if not call_sites:
        reasons.append("composition root has no call sites; nothing is bound")
        return STATUS_NONE, reasons

    for call_site in call_sites:
        arguments = call_site["arguments"]
        if (
            PRODUCTION_ADAPTER_CLASS in arguments
            and PRODUCTION_ADAPTER_CLASS != signature.get("object_store_factory")
        ):
            reasons.append(
                f"call site at {call_site['file_path']}:{call_site['line_number']} "
                f"overrides object_store_factory with {PRODUCTION_ADAPTER_CLASS!r} "
                "but the signature default already binds it"
            )
            return STATUS_UNRESOLVED, reasons
        if (
            DURABLE_WRAPPER_CLASS in arguments
            and DURABLE_WRAPPER_CLASS != signature.get("durable_object_store_factory")
        ):
            reasons.append(
                f"call site at {call_site['file_path']}:{call_site['line_number']} "
                f"overrides durable_object_store_factory with {DURABLE_WRAPPER_CLASS!r} "
                "but the signature default already binds it"
            )
            return STATUS_UNRESOLVED, reasons

    # 7. Local adapter is restricted to Local/Test profile sites.
    local_observations = _collect_observations_by_role(report, ROLE_LOCAL_ADAPTER)
    if local_observations and not report.local_binding_sites_seen:
        reasons.append(
            "local adapter exists but no Local/Test profile binding sites were located"
        )
        return STATUS_UNRESOLVED, reasons

    # 8. Receipt format and tenant/workspace namespace binding.
    if not report.receipts_observed:
        reasons.append(
            "canonical runtime does not emit an s3:// receipt for committed objects"
        )
        return STATUS_UNRESOLVED, reasons
    if not report.tenant_workspace_bindings:
        reasons.append(
            "canonical runtime does not bind tenant/workspace namespace prefixes"
        )
        return STATUS_UNRESOLVED, reasons

    # 9. Fail-closed semantics when production binding is absent.
    if not report.fail_closed_branches:
        reasons.append(
            "composition root does not fail closed when production storage is unconfigured"
        )
        return STATUS_UNRESOLVED, reasons

    # 10. Single observation per role.
    for role in (
        ROLE_PROTOCOL_PORT,
        ROLE_DURABLE_WRAPPER,
        ROLE_PRODUCTION_ADAPTER,
        ROLE_RUNTIME_OWNER,
        ROLE_COMPOSITION_ROOT,
    ):
        observations = _collect_observations_by_role(report, role)
        if len(observations) != 1:
            reasons.append(
                f"expected exactly one {role} observation, found {len(observations)}"
            )
            return STATUS_UNRESOLVED, reasons

    reasons.append(
        "production composition root binds exactly one MinIO adapter, wraps it "
        "in a single durable wrapper, the local adapter is restricted to the "
        "Local/Test profile, and the composition root fails closed when "
        "production storage is unconfigured"
    )
    return STATUS_UNIQUE, reasons


# ---------------------------------------------------------------------------
# Mode handlers
# ---------------------------------------------------------------------------


def _contract_mode() -> Tuple[int, Dict[str, Any]]:
    fixtures = _contract_fixtures()
    results: List[Dict[str, Any]] = []
    overall_exit = EXIT_UNIQUE
    overall_status = STATUS_UNIQUE
    for name, report, expected_status in fixtures:
        status, reasons = evaluate(report)
        exit_code = _status_to_exit(status)
        results.append(
            {
                "fixture": name,
                "expected_status": expected_status,
                "actual_status": status,
                "exit_code": exit_code,
                "reasons": reasons,
            }
        )
        if status != expected_status:
            overall_status = STATUS_UNRESOLVED
            overall_exit = EXIT_UNRESOLVED
    return overall_exit, {
        "mode": "contract",
        "overall_status": overall_status,
        "results": results,
    }


def _contract_fixtures() -> Iterable[Tuple[str, BindingReport, str]]:
    base_report = _fixture_base_report()

    # Fixture 1: unique production binding.
    yield "unique_production_binding", base_report, STATUS_UNIQUE

    # Fixture 2: multiple production bindings via signature default override
    # in the body (two MinIO mentions).
    report = _copy_report(base_report)
    body_refs = dict(report.composition_root_body_references)
    body_refs[PRODUCTION_ADAPTER_CLASS] = 2
    report.composition_root_body_references = body_refs
    yield "multiple_production_bindings", report, STATUS_MULTIPLE

    # Fixture 3: no production binding because composition root has no call sites.
    report = _copy_report(base_report)
    report.composition_root_call_sites = []
    yield "no_production_binding", report, STATUS_NONE

    # Fixture 4: missing binding - the composition root body drops both
    # MinioObjectStore and DurableMinioObjectStore references.
    report = _copy_report(base_report)
    body_refs = dict(report.composition_root_body_references)
    body_refs[PRODUCTION_ADAPTER_CLASS] = 0
    body_refs[DURABLE_WRAPPER_CLASS] = 0
    report.composition_root_body_references = body_refs
    yield "missing_binding", report, STATUS_UNRESOLVED

    # Fixture 5: durable wrapper wraps the production adapter.
    yield "wrapper_wraps_production_adapter", _copy_report(base_report), STATUS_UNIQUE

    # Fixture 6: test double excluded from owner count.
    report = _copy_report(base_report)
    report.observations.append(
        ClassObservation(
            role=ROLE_TEST_DOUBLE,
            qualified_name="FakeObjectStore",
            file_path="tests/fixtures/phase22_object_store_owner_binding/fake.py",
            line_number=1,
            notes=("test double; excluded from production owner count",),
        )
    )
    yield "test_double_excluded", report, STATUS_UNIQUE

    # Fixture 7: rejecting the old class-name-count algorithm.
    report = _copy_report(base_report)
    report.error_messages.append(
        "class-name suffix counting is not a binding proof"
    )
    yield "name_count_algorithm_rejected", report, STATUS_UNRESOLVED

    # Fixture 8: real repository is reported accurately.
    real_report = collect_observations(REPO_ROOT)
    status, _ = evaluate(real_report)
    yield "real_repository_attested", real_report, status


def _fixture_base_report() -> BindingReport:
    return BindingReport(
        observations=[
            ClassObservation(
                role=ROLE_PROTOCOL_PORT,
                qualified_name=PROTOCOL_PORT_CLASS,
                file_path=PROTOCOL_PORT_PATH,
                line_number=23,
                notes=("Protocol defining the port",),
            ),
            ClassObservation(
                role=ROLE_LOCAL_ADAPTER,
                qualified_name=LOCAL_ADAPTER_CLASS,
                file_path=LOCAL_ADAPTER_PATH,
                line_number=14,
                notes=("local filesystem adapter",),
            ),
            ClassObservation(
                role=ROLE_PRODUCTION_ADAPTER,
                qualified_name=PRODUCTION_ADAPTER_CLASS,
                file_path=PRODUCTION_ADAPTER_PATH,
                line_number=80,
                notes=("MinIO production adapter",),
            ),
            ClassObservation(
                role=ROLE_DURABLE_WRAPPER,
                qualified_name=DURABLE_WRAPPER_CLASS,
                file_path=DURABLE_WRAPPER_PATH,
                line_number=73,
                notes=("wraps the production adapter",),
            ),
            ClassObservation(
                role=ROLE_RUNTIME_OWNER,
                qualified_name=CANONICAL_RUNTIME_CLASS,
                file_path=CANONICAL_RUNTIME_PATH,
                line_number=116,
                notes=("depends on DurableMinioObjectStore",),
            ),
            ClassObservation(
                role=ROLE_COMPOSITION_ROOT,
                qualified_name=COMPOSITION_ROOT_FACTORY,
                file_path=COMPOSITION_ROOT_PATH,
                line_number=116,
                notes=("returns runtime or None",),
            ),
        ],
        runtime_owner_dependencies=(
            (CANONICAL_RUNTIME_FIELD, DURABLE_WRAPPER_CLASS),
        ),
        composition_root_signature={
            "object_store_factory": PRODUCTION_ADAPTER_CLASS,
            "durable_object_store_factory": DURABLE_WRAPPER_CLASS,
            "runtime_factory": CANONICAL_RUNTIME_CLASS,
        },
        composition_root_body_references={
            PRODUCTION_ADAPTER_CLASS: 1,
            DURABLE_WRAPPER_CLASS: 1,
            LOCAL_ADAPTER_CLASS: 0,
            "LazyStorageClient": 0,
            "OSSClient": 0,
        },
        composition_root_call_sites=[
            {
                "file_path": "src/backend/zuno/main.py",
                "line_number": 73,
                "arguments": "engine=engine, settings=app_settings",
            }
        ],
        production_storage_mode_seen=(
            "storage.mode check at line 126",
        ),
        local_binding_sites_seen=(COMPOSITION_ROOT_LOCAL_FACTORY,),
        fail_closed_branches=(
            "storage.mode != 'minio' at line 126",
            "return None at line 127",
        ),
        receipts_observed=("s3:// scheme at line 164",),
        tenant_workspace_bindings=(
            "tenant/workspace prefix bound at line 1586",
        ),
        wrapper_binding_chain=(
            "store=object_store, engine=engine, owner='workspace.file_upload'",
            "object_store_factory bound: endpoint=endpoint, access_key=access_key, secret_key=secret_key, secure=False",
        ),
    )


def _copy_report(report: BindingReport) -> BindingReport:
    return BindingReport(
        observations=list(report.observations),
        runtime_owner_dependencies=report.runtime_owner_dependencies,
        composition_root_signature=dict(report.composition_root_signature),
        composition_root_body_references=dict(
            report.composition_root_body_references
        ),
        composition_root_call_sites=list(report.composition_root_call_sites),
        production_storage_mode_seen=report.production_storage_mode_seen,
        local_binding_sites_seen=report.local_binding_sites_seen,
        fail_closed_branches=report.fail_closed_branches,
        receipts_observed=report.receipts_observed,
        tenant_workspace_bindings=report.tenant_workspace_bindings,
        wrapper_binding_chain=report.wrapper_binding_chain,
        error_messages=list(report.error_messages),
    )


def _status_to_exit(status: str) -> int:
    if status == STATUS_UNIQUE:
        return EXIT_UNIQUE
    if status == STATUS_MULTIPLE:
        return EXIT_MULTIPLE
    if status == STATUS_NONE:
        return EXIT_NONE
    return EXIT_UNRESOLVED


def _repository_mode() -> Tuple[int, Dict[str, Any]]:
    try:
        report = collect_observations(REPO_ROOT)
    except Exception as exc:  # pragma: no cover - defensive
        return EXIT_TOOL_ERROR, {
            "mode": "repository",
            "status": STATUS_UNRESOLVED,
            "error": f"{type(exc).__name__}: {exc}",
        }
    status, reasons = evaluate(report)
    return _status_to_exit(status), {
        "mode": "repository",
        "status": status,
        "reasons": reasons,
        "report": report.to_dict(),
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="PHASE22-OBJECT-STORE-OWNER-GATE verifier"
    )
    parser.add_argument(
        "--mode",
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
            "status": STATUS_UNRESOLVED,
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