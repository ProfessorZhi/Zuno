"""PHASE22 Runtime Evidence Binding Contract (validation only, v3).

This module implements a deterministic, fail-closed, validation-only contract
that binds a claimed Product Runtime execution to its serialized evidence.
Version 2 repaired the review findings from PR #58; version 3 closes the
final fail-closed defects:

* Two identical unknown ``receipt_type`` values never raise ``KeyError``:
  unknown types are handled before the known-type duplicate map, so every
  unknown type (distinct or repeated) maps to the single fixed, deduplicated
  code ``unknown_receipt_type``.
* Blank (empty or whitespace-only) top-level ``runtime_version`` and
  ``corpus_snapshot_ref`` are BLOCKED, exactly like missing values.
* INCOMPARABLE is only ever produced when BOTH sides of a comparison are
  non-blank and differ; a blank receipt side or blank top-level side is not
  an inconsistency claim.
* The public validator never raises for any input, and every gap code comes
  from the fixed closed ``ALL_GAP_CODES`` vocabulary.

Version 2 repairs (kept):

P1 - Gap codes are a fixed closed vocabulary

P1 - Gap codes are a fixed closed vocabulary
    Every gap code is a fixed lowercase snake_case string that matches
    ``^[a-z][a-z0-9_]*$``.  Codes that distinguish a schema field or a known
    receipt type are derived ONLY from fixed module constants, never from
    input values; the full closed vocabulary is exposed as ``ALL_GAP_CODES``.
    Unknown receipt types always map to the single fixed code
    ``unknown_receipt_type`` (deduplicated).  Gap codes never contain refs,
    hashes, tenants, workspaces, receipt type raw values, secrets or the
    runtime name.

P1 - Never-raise covers every public path (Mapping-only validator)
    ``validate`` accepts only serialized evidence: a ``Mapping``.  A
    ``RuntimeEvidenceBinding`` instance or any other object is INVALID with
    ``input_type_invalid``.  The immutable dataclasses are internal frozen
    structures and are never an unvalidated public input.  The validator
    never raises on malformed input and never returns VALID via a broad
    except.

P1 - INCOMPARABLE state semantics are frozen
    INCOMPARABLE: requested_profile != actual_profile; any receipt
    runtime_version != top-level runtime_version; any receipt snapshot_ref !=
    top-level corpus_snapshot_ref; local GraphRAG artifact snapshot mismatch.
    BLOCKED: runtime version missing, snapshot missing, receipt missing,
    owner mismatch, reference binding errors, reference binding hash error.
    INVALID: field type errors, hash format errors, illegal profile, illegal
    receipt structure.  When an early INVALID and a later INCOMPARABLE occur
    together, the earliest failing stage's state wins while gap codes are
    still returned completely for every stage that can safely run.

P2 - Hash helper exception contract
    ``compute_reference_binding_hash(Mapping)`` raises ValueError for missing
    fields, wrong types, non-mapping receipts and illegal collections, with a
    fixed message that never contains input values.  The validator converts
    any such condition into a validation state and never raises.

Contract boundaries (unchanged from v1)
----------------------------------------
- Only serialized evidence (Mapping) is accepted; runtime objects and
  self-declared authority fields (``is_test_double``, ``__zuno_product_authority__``)
  are never trusted.
- Unknown keys are ignored: not validated, never hashed.
- ``tenant_id`` / ``workspace_id`` are optional; present-but-empty is
  INVALID; no default tenant/workspace/snapshot is invented.
- The validator never mutates its input and never writes a hash back.
- This contract never creates a Product Runtime, never calls a model or
  external service, never generates receipts, never auto-completes evidence,
  and never returns RUNTIME_OBSERVED or MEASURED.

Validation priority (fixed; first failing stage's state wins)
-------------------------------------------------------------
1.  Input Structure        -> INVALID
2.  Identity               -> INVALID
3.  Profile                -> INVALID or INCOMPARABLE
4.  Runtime Identity       -> BLOCKED
5.  Snapshot               -> BLOCKED
6.  Required Receipts      -> BLOCKED
7.  Receipt Owner          -> BLOCKED
8.  Runtime Version Consis -> INCOMPARABLE
9.  Snapshot Consistency   -> INCOMPARABLE
10. Payload Hash Format    -> INVALID
11. Receipt Ref Binding    -> BLOCKED
12. Reference Binding Hash -> BLOCKED

Profiles and required receipts
------------------------------
Only ``standard_rag``, ``local_graphrag``, ``deep_graphrag`` and
``agentic_graphrag`` are accepted.  Required receipt types:

- standard_rag / local_graphrag / deep_graphrag: security_decision, trace,
  usage_receipt, budget_settlement, artifact_receipt.  PlanVersion /
  RunOutcome are NOT forced for these profiles (the repository contract
  provides no evidence that they are mandatory for deep_graphrag).
- agentic_graphrag: security_decision, plan_version, run_outcome,
  usage_receipt, budget_settlement, trace, artifact_receipt.

For ``local_graphrag`` the graph index is covered by the top-level binding:
the artifact receipt must carry the same snapshot as the top-level
``corpus_snapshot_ref`` (INCOMPARABLE otherwise).  No separate "index"
receipt type exists and none is invented.

Hash contract
-------------
Canonical JSON (``sort_keys=True``, stable separators ``(",", ":")``,
UTF-8), SHA-256, lowercase 64-char hex.  Field insertion order and receipt
list order do not affect the result; any bound field change changes the
result.  The canonical payload contains no secret, no token, no expected
answer, no gold document / gold evidence and no citation ground truth.

Exception semantics
-------------------
The validator never raises on malformed input.  The hash helper raises
``ValueError`` (uniform, fixed message) for malformed mappings and is
documented accordingly.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Iterable, Mapping

_SHA256_HEX_CHARS = frozenset("0123456789abcdef")

ALLOWED_PROFILES: tuple[str, ...] = (
    "standard_rag",
    "local_graphrag",
    "deep_graphrag",
    "agentic_graphrag",
)

# Single source of truth for receipt ownership.  Owner strings must never be
# duplicated in implementation or tests; both use this map.
RECEIPT_OWNERS: Mapping[str, str] = MappingProxyType(
    {
        "security_decision": "security",
        "plan_version": "agent_core",
        "run_outcome": "agent_core",
        "usage_receipt": "model_gateway",
        "budget_settlement": "budget",
        "trace": "observability",
        "artifact_receipt": "artifact_store",
    }
)

# Minimum required receipt types per accepted profile.
REQUIRED_RECEIPTS: Mapping[str, tuple[str, ...]] = MappingProxyType(
    {
        "standard_rag": (
            "security_decision",
            "trace",
            "usage_receipt",
            "budget_settlement",
            "artifact_receipt",
        ),
        "local_graphrag": (
            "security_decision",
            "trace",
            "usage_receipt",
            "budget_settlement",
            "artifact_receipt",
        ),
        "deep_graphrag": (
            "security_decision",
            "trace",
            "usage_receipt",
            "budget_settlement",
            "artifact_receipt",
        ),
        "agentic_graphrag": (
            "security_decision",
            "plan_version",
            "run_outcome",
            "usage_receipt",
            "budget_settlement",
            "trace",
            "artifact_receipt",
        ),
    }
)

# Top-level binding field that holds the reference for each receipt type.
REF_FIELD_BY_RECEIPT_TYPE: Mapping[str, str] = MappingProxyType(
    {
        "security_decision": "security_decision_ref",
        "plan_version": "plan_version_ref",
        "run_outcome": "run_outcome_ref",
        "usage_receipt": "usage_receipt_ref",
        "budget_settlement": "budget_settlement_ref",
        "trace": "trace_id",
        "artifact_receipt": "artifact_receipt_ref",
    }
)

_TOP_LEVEL_REQUIRED_FIELDS: tuple[str, ...] = (
    "eval_run_id",
    "case_id",
    "requested_profile",
    "actual_profile",
    "runtime_name",
    "runtime_version",
    "corpus_snapshot_ref",
    "trace_id",
    "security_decision_ref",
    "plan_version_ref",
    "run_outcome_ref",
    "usage_receipt_ref",
    "budget_settlement_ref",
    "artifact_receipt_ref",
    "artifact_payload_hash",
    "result_payload_hash",
    "reference_binding_hash",
    "receipts",
)

_OPTIONAL_TOP_LEVEL_FIELDS: tuple[str, ...] = ("tenant_id", "workspace_id")

_RECEIPT_REQUIRED_FIELDS: tuple[str, ...] = (
    "receipt_type",
    "receipt_ref",
    "owner",
    "runtime_version",
    "snapshot_ref",
    "payload_hash",
)

# ── Fixed gap code vocabulary ─────────────────────────────────────────────
# Gap codes are fixed lowercase snake_case strings.  Codes that distinguish a
# schema field or a known receipt type are derived ONLY from fixed module
# constants (never from input values).  Unknown receipt types always map to
# the single fixed code UNKNOWN_RECEIPT_TYPE, deduplicated.  The complete
# closed vocabulary is exposed as ALL_GAP_CODES.


def _field_codes(prefix: str, fields: Iterable[str]) -> Mapping[str, str]:
    return MappingProxyType({name: f"{prefix}_{name}" for name in fields})


def _receipt_codes(suffix: str) -> Mapping[str, str]:
    return MappingProxyType({name: f"{name}_{suffix}" for name in RECEIPT_OWNERS})


INPUT_FIELD_MISSING_CODES: Mapping[str, str] = _field_codes(
    "input_field_missing", _TOP_LEVEL_REQUIRED_FIELDS
)
INPUT_FIELD_WRONG_TYPE_CODES: Mapping[str, str] = _field_codes(
    "input_field_wrong_type", _TOP_LEVEL_REQUIRED_FIELDS + _OPTIONAL_TOP_LEVEL_FIELDS
)
RECEIPT_FIELD_MISSING_CODES: Mapping[str, str] = _field_codes(
    "receipt_field_missing", _RECEIPT_REQUIRED_FIELDS
)
RECEIPT_FIELD_WRONG_TYPE_CODES: Mapping[str, str] = _field_codes(
    "receipt_field_wrong_type", _RECEIPT_REQUIRED_FIELDS
)
REF_MISSING_CODES: Mapping[str, str] = MappingProxyType(
    {field: f"{field}_missing" for field in REF_FIELD_BY_RECEIPT_TYPE.values()}
)
RECEIPT_OWNER_MISMATCH_CODES: Mapping[str, str] = _receipt_codes(
    "receipt_owner_mismatch"
)
RECEIPT_RUNTIME_VERSION_MISMATCH_CODES: Mapping[str, str] = _receipt_codes(
    "receipt_runtime_version_mismatch"
)
RECEIPT_SNAPSHOT_MISMATCH_CODES: Mapping[str, str] = _receipt_codes(
    "receipt_snapshot_mismatch"
)
RECEIPT_PAYLOAD_HASH_INVALID_CODES: Mapping[str, str] = _receipt_codes(
    "receipt_payload_hash_invalid"
)
RECEIPT_TYPE_DUPLICATE_CODES: Mapping[str, str] = _receipt_codes(
    "receipt_type_duplicate"
)
RECEIPT_REF_UNBOUND_CODES: Mapping[str, str] = _receipt_codes("receipt_ref_unbound")
RECEIPT_REF_MISMATCH_CODES: Mapping[str, str] = _receipt_codes("receipt_ref_mismatch")
TOP_LEVEL_REF_UNBOUND_CODES: Mapping[str, str] = _receipt_codes("ref_unbound")

# Stable per-type "receipt missing" gap codes (fixed vocabulary).
_RECEIPT_MISSING_CODES: Mapping[str, str] = MappingProxyType(
    {
        "security_decision": "security_decision_receipt_missing",
        "plan_version": "plan_version_receipt_missing",
        "run_outcome": "run_outcome_receipt_missing",
        "usage_receipt": "usage_receipt_missing",
        "budget_settlement": "budget_settlement_missing",
        "trace": "trace_receipt_missing",
        "artifact_receipt": "artifact_receipt_missing",
    }
)

INPUT_TYPE_INVALID = "input_type_invalid"
INPUT_RECEIPT_NOT_MAPPING = "input_receipt_not_mapping"
EVAL_RUN_ID_MISSING = "eval_run_id_missing"
CASE_ID_MISSING = "case_id_missing"
TENANT_ID_EMPTY = "tenant_id_empty"
WORKSPACE_ID_EMPTY = "workspace_id_empty"
REQUESTED_PROFILE_MISSING = "requested_profile_missing"
UNKNOWN_REQUESTED_PROFILE = "unknown_requested_profile"
ACTUAL_PROFILE_MISSING = "actual_profile_missing"
UNKNOWN_ACTUAL_PROFILE = "unknown_actual_profile"
PROFILE_MISMATCH = "profile_mismatch"
RUNTIME_NAME_MISSING = "runtime_name_missing"
RUNTIME_VERSION_MISSING = "runtime_version_missing"
CORPUS_SNAPSHOT_REF_MISSING = "corpus_snapshot_ref_missing"
TRACE_ID_MISSING = "trace_id_missing"
LOCAL_GRAPH_INDEX_SNAPSHOT_UNCOVERED = "local_graphrag_index_snapshot_uncovered"
ARTIFACT_PAYLOAD_HASH_INVALID = "artifact_payload_hash_invalid"
RESULT_PAYLOAD_HASH_INVALID = "result_payload_hash_invalid"
REFERENCE_BINDING_HASH_MISSING = "reference_binding_hash_missing"
REFERENCE_BINDING_HASH_INVALID = "reference_binding_hash_invalid"
RECEIPT_REF_MISSING = "receipt_ref_missing"
RECEIPT_REF_DUPLICATE = "receipt_ref_duplicate"
UNKNOWN_RECEIPT_TYPE = "unknown_receipt_type"
REFERENCE_BINDING_HASH_MISMATCH = "reference_binding_hash_mismatch"

_FIXED_GAP_CODE_CONSTANTS: tuple[str, ...] = (
    INPUT_TYPE_INVALID,
    INPUT_RECEIPT_NOT_MAPPING,
    EVAL_RUN_ID_MISSING,
    CASE_ID_MISSING,
    TENANT_ID_EMPTY,
    WORKSPACE_ID_EMPTY,
    REQUESTED_PROFILE_MISSING,
    UNKNOWN_REQUESTED_PROFILE,
    ACTUAL_PROFILE_MISSING,
    UNKNOWN_ACTUAL_PROFILE,
    PROFILE_MISMATCH,
    RUNTIME_NAME_MISSING,
    RUNTIME_VERSION_MISSING,
    CORPUS_SNAPSHOT_REF_MISSING,
    TRACE_ID_MISSING,
    LOCAL_GRAPH_INDEX_SNAPSHOT_UNCOVERED,
    ARTIFACT_PAYLOAD_HASH_INVALID,
    RESULT_PAYLOAD_HASH_INVALID,
    REFERENCE_BINDING_HASH_MISSING,
    REFERENCE_BINDING_HASH_INVALID,
    RECEIPT_REF_MISSING,
    RECEIPT_REF_DUPLICATE,
    UNKNOWN_RECEIPT_TYPE,
    REFERENCE_BINDING_HASH_MISMATCH,
    *_RECEIPT_MISSING_CODES.values(),
)

# The complete, closed gap code vocabulary.  The validator only ever returns
# codes from this set; tests enforce the closure.
ALL_GAP_CODES: frozenset[str] = frozenset(
    _FIXED_GAP_CODE_CONSTANTS
    + tuple(INPUT_FIELD_MISSING_CODES.values())
    + tuple(INPUT_FIELD_WRONG_TYPE_CODES.values())
    + tuple(RECEIPT_FIELD_MISSING_CODES.values())
    + tuple(RECEIPT_FIELD_WRONG_TYPE_CODES.values())
    + tuple(REF_MISSING_CODES.values())
    + tuple(RECEIPT_OWNER_MISMATCH_CODES.values())
    + tuple(RECEIPT_RUNTIME_VERSION_MISMATCH_CODES.values())
    + tuple(RECEIPT_SNAPSHOT_MISMATCH_CODES.values())
    + tuple(RECEIPT_PAYLOAD_HASH_INVALID_CODES.values())
    + tuple(RECEIPT_TYPE_DUPLICATE_CODES.values())
    + tuple(RECEIPT_REF_UNBOUND_CODES.values())
    + tuple(RECEIPT_REF_MISMATCH_CODES.values())
    + tuple(TOP_LEVEL_REF_UNBOUND_CODES.values())
)


def _is_sha256_hex(value: str) -> bool:
    return len(value) == 64 and all(c in _SHA256_HEX_CHARS for c in value)


def _is_blank(value: str) -> bool:
    """True for an empty or whitespace-only string.

    Required for the fail-closed BLOCKED semantics: a blank ``runtime_version``
    or ``snapshot_ref`` is treated exactly like a missing one, and an
    INCOMPARABLE comparison is only ever produced when BOTH sides are
    non-blank and differ.
    """
    return not bool(value.strip())


def _structure_errors(data: Mapping[str, Any]) -> tuple[str, ...]:
    """Fixed structural checks shared by the validator and the hash helper.

    Returns fixed gap codes for missing fields, wrong field types, a
    non-list receipts collection and malformed receipt entries.  Never reads
    input values into the returned codes.
    """
    gaps: list[str] = []
    for name in _TOP_LEVEL_REQUIRED_FIELDS:
        if name not in data:
            gaps.append(INPUT_FIELD_MISSING_CODES[name])
        elif name == "receipts":
            if not isinstance(data[name], (list, tuple)):
                gaps.append(INPUT_FIELD_WRONG_TYPE_CODES[name])
        elif not isinstance(data[name], str):
            gaps.append(INPUT_FIELD_WRONG_TYPE_CODES[name])
    for name in _OPTIONAL_TOP_LEVEL_FIELDS:
        if name in data and not isinstance(data[name], str):
            gaps.append(INPUT_FIELD_WRONG_TYPE_CODES[name])
    receipts = data.get("receipts")
    if isinstance(receipts, (list, tuple)):
        for item in receipts:
            if not isinstance(item, Mapping):
                gaps.append(INPUT_RECEIPT_NOT_MAPPING)
                continue
            for name in _RECEIPT_REQUIRED_FIELDS:
                if name not in item:
                    gaps.append(RECEIPT_FIELD_MISSING_CODES[name])
                elif not isinstance(item[name], str):
                    gaps.append(RECEIPT_FIELD_WRONG_TYPE_CODES[name])
    return tuple(gaps)


class BindingValidationState(StrEnum):
    """Validation outcome of a runtime evidence binding.

    VALID means the evidence is structurally complete and consistently bound
    against the reference binding hash.  VALID is NOT RUNTIME_OBSERVED, NOT
    MEASURED, NOT QUALITY_PROVEN and NOT PRODUCTION_READY: this contract never
    claims that a runtime ran, that a benchmark was measured, or that a
    quality level is proven.
    """

    VALID = "VALID"
    BLOCKED = "BLOCKED"
    INCOMPARABLE = "INCOMPARABLE"
    INVALID = "INVALID"


@dataclass(frozen=True, slots=True)
class RuntimeReceiptBinding:
    """Immutable internal receipt evidence structure (not a public input)."""

    receipt_type: str
    receipt_ref: str
    owner: str
    runtime_version: str
    snapshot_ref: str
    payload_hash: str


@dataclass(frozen=True, slots=True)
class RuntimeEvidenceBinding:
    """Immutable internal binding structure (not a public input).

    ``tenant_id`` / ``workspace_id`` are optional and never default to an
    invented tenant or workspace: the empty string means "not provided".
    """

    eval_run_id: str
    case_id: str
    requested_profile: str
    actual_profile: str
    runtime_name: str
    runtime_version: str
    corpus_snapshot_ref: str
    trace_id: str
    security_decision_ref: str
    plan_version_ref: str
    run_outcome_ref: str
    usage_receipt_ref: str
    budget_settlement_ref: str
    artifact_receipt_ref: str
    artifact_payload_hash: str
    result_payload_hash: str
    reference_binding_hash: str
    receipts: tuple[RuntimeReceiptBinding, ...]
    tenant_id: str = ""
    workspace_id: str = ""

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "RuntimeEvidenceBinding":
        """Build the internal structure from a serialized mapping.

        Unknown keys are ignored.  Raises (KeyError / TypeError) if a
        required key is missing or has the wrong type; the validator performs
        its structural checks before calling this, and the hash helper
        converts any such failure into a uniform ValueError.
        """
        receipts = tuple(
            RuntimeReceiptBinding(
                receipt_type=item["receipt_type"],
                receipt_ref=item["receipt_ref"],
                owner=item["owner"],
                runtime_version=item["runtime_version"],
                snapshot_ref=item["snapshot_ref"],
                payload_hash=item["payload_hash"],
            )
            for item in data["receipts"]
        )
        return cls(
            eval_run_id=data["eval_run_id"],
            case_id=data["case_id"],
            requested_profile=data["requested_profile"],
            actual_profile=data["actual_profile"],
            runtime_name=data["runtime_name"],
            runtime_version=data["runtime_version"],
            corpus_snapshot_ref=data["corpus_snapshot_ref"],
            trace_id=data["trace_id"],
            security_decision_ref=data["security_decision_ref"],
            plan_version_ref=data["plan_version_ref"],
            run_outcome_ref=data["run_outcome_ref"],
            usage_receipt_ref=data["usage_receipt_ref"],
            budget_settlement_ref=data["budget_settlement_ref"],
            artifact_receipt_ref=data["artifact_receipt_ref"],
            artifact_payload_hash=data["artifact_payload_hash"],
            result_payload_hash=data["result_payload_hash"],
            reference_binding_hash=data["reference_binding_hash"],
            receipts=receipts,
            tenant_id=data.get("tenant_id", ""),
            workspace_id=data.get("workspace_id", ""),
        )


@dataclass(frozen=True, slots=True)
class BindingValidationResult:
    """Deterministic validation outcome: one state plus ordered gap codes."""

    state: BindingValidationState
    gap_codes: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return self.state is BindingValidationState.VALID


def canonical_binding_payload(
    binding: RuntimeEvidenceBinding,
) -> dict[str, Any]:
    """Canonical payload bound by the reference binding hash.

    Contains only the bound fields.  Receipts are sorted by
    ``(receipt_type, receipt_ref)`` so receipt list order does not affect the
    hash.  No secret, token, expected answer, gold document, gold evidence or
    citation ground truth can appear here.
    """
    receipts = sorted(
        binding.receipts,
        key=lambda r: (r.receipt_type, r.receipt_ref),
    )
    payload: dict[str, Any] = {
        "eval_run_id": binding.eval_run_id,
        "case_id": binding.case_id,
        "requested_profile": binding.requested_profile,
        "actual_profile": binding.actual_profile,
        "runtime_name": binding.runtime_name,
        "runtime_version": binding.runtime_version,
        "corpus_snapshot_ref": binding.corpus_snapshot_ref,
        "trace_id": binding.trace_id,
        "security_decision_ref": binding.security_decision_ref,
        "plan_version_ref": binding.plan_version_ref,
        "run_outcome_ref": binding.run_outcome_ref,
        "usage_receipt_ref": binding.usage_receipt_ref,
        "budget_settlement_ref": binding.budget_settlement_ref,
        "artifact_receipt_ref": binding.artifact_receipt_ref,
        "artifact_payload_hash": binding.artifact_payload_hash,
        "result_payload_hash": binding.result_payload_hash,
        "receipts": [
            {
                "receipt_type": r.receipt_type,
                "receipt_ref": r.receipt_ref,
                "owner": r.owner,
                "runtime_version": r.runtime_version,
                "snapshot_ref": r.snapshot_ref,
                "payload_hash": r.payload_hash,
            }
            for r in receipts
        ],
    }
    if binding.tenant_id:
        payload["tenant_id"] = binding.tenant_id
    if binding.workspace_id:
        payload["workspace_id"] = binding.workspace_id
    return payload


_HASH_HELPER_ERROR_MESSAGE = (
    "binding must be a well-formed runtime evidence binding mapping"
)


def compute_reference_binding_hash(
    binding: RuntimeEvidenceBinding | Mapping[str, Any],
) -> str:
    """Compute the reference binding hash (SHA-256, lowercase 64 hex).

    Accepts the internal :class:`RuntimeEvidenceBinding` or a serialized
    mapping.  For a mapping, missing fields, wrong types, non-mapping
    receipts and illegal collections raise a uniform ``ValueError`` whose
    message never contains input values.  Unknown keys are ignored.

    Deterministic: canonical JSON with ``sort_keys=True`` and stable
    separators ``(",", ":")`` encoded as UTF-8, hashed with SHA-256.  Field
    insertion order and receipt list order do not affect the result; any
    change to a bound field changes the result.
    """
    if isinstance(binding, Mapping):
        if _structure_errors(binding):
            raise ValueError(_HASH_HELPER_ERROR_MESSAGE)
        try:
            binding = RuntimeEvidenceBinding.from_dict(binding)
        except (KeyError, TypeError, IndexError, AttributeError) as exc:
            raise ValueError(_HASH_HELPER_ERROR_MESSAGE) from None
    payload = canonical_binding_payload(binding)
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


class RuntimeEvidenceBindingValidator:
    """Deterministic, fail-closed validator for runtime evidence bindings.

    Public input is a serialized ``Mapping`` only.  Never raises on malformed
    input and never mutates its input.  Stages run in the fixed priority
    order documented in the module docstring; gap codes are returned in stage
    order and state is the highest-priority failing stage's state.
    """

    # -- Stage 1: Input Structure (INVALID) ---------------------------------

    def _check_input_structure(self, data: Mapping[str, Any]) -> tuple[str, ...]:
        return _structure_errors(data)

    # -- Stage 2: Identity (INVALID) ----------------------------------------

    def _check_identity(
        self,
        evidence: RuntimeEvidenceBinding,
        optional_present: frozenset[str],
    ) -> tuple[str, ...]:
        gaps: list[str] = []
        if _is_blank(evidence.eval_run_id):
            gaps.append(EVAL_RUN_ID_MISSING)
        if _is_blank(evidence.case_id):
            gaps.append(CASE_ID_MISSING)
        if "tenant_id" in optional_present and _is_blank(evidence.tenant_id):
            gaps.append(TENANT_ID_EMPTY)
        if "workspace_id" in optional_present and _is_blank(evidence.workspace_id):
            gaps.append(WORKSPACE_ID_EMPTY)
        return tuple(gaps)

    # -- Stage 3: Profile (INVALID or INCOMPARABLE) -------------------------

    def _check_profile(
        self,
        evidence: RuntimeEvidenceBinding,
    ) -> tuple[tuple[str, ...], BindingValidationState]:
        gaps: list[str] = []
        if not evidence.requested_profile:
            gaps.append(REQUESTED_PROFILE_MISSING)
        elif evidence.requested_profile not in ALLOWED_PROFILES:
            gaps.append(UNKNOWN_REQUESTED_PROFILE)
        if not evidence.actual_profile:
            gaps.append(ACTUAL_PROFILE_MISSING)
        elif evidence.actual_profile not in ALLOWED_PROFILES:
            gaps.append(UNKNOWN_ACTUAL_PROFILE)
        requested_known = evidence.requested_profile in ALLOWED_PROFILES
        actual_known = evidence.actual_profile in ALLOWED_PROFILES
        if (
            requested_known
            and actual_known
            and evidence.requested_profile != evidence.actual_profile
        ):
            gaps.append(PROFILE_MISMATCH)
        if gaps:
            state = (
                BindingValidationState.INCOMPARABLE
                if PROFILE_MISMATCH in gaps
                else BindingValidationState.INVALID
            )
            return tuple(gaps), state
        return (), BindingValidationState.VALID

    # -- Stage 4: Runtime Identity (BLOCKED) --------------------------------

    def _check_runtime_identity(
        self, evidence: RuntimeEvidenceBinding
    ) -> tuple[str, ...]:
        gaps: list[str] = []
        if _is_blank(evidence.runtime_name):
            gaps.append(RUNTIME_NAME_MISSING)
        if _is_blank(evidence.runtime_version):
            gaps.append(RUNTIME_VERSION_MISSING)
        return tuple(gaps)

    # -- Stage 5: Snapshot (BLOCKED) ----------------------------------------

    def _check_snapshot(self, evidence: RuntimeEvidenceBinding) -> tuple[str, ...]:
        gaps: list[str] = []
        if _is_blank(evidence.corpus_snapshot_ref):
            gaps.append(CORPUS_SNAPSHOT_REF_MISSING)
        if _is_blank(evidence.trace_id):
            gaps.append(TRACE_ID_MISSING)
        return tuple(gaps)

    # -- Stage 6: Required Receipts (BLOCKED) -------------------------------

    def _check_required_receipts(
        self, evidence: RuntimeEvidenceBinding
    ) -> tuple[str, ...]:
        gaps: list[str] = []
        required = REQUIRED_RECEIPTS[evidence.actual_profile]
        by_type = {r.receipt_type: r for r in evidence.receipts}
        for receipt_type in required:
            field = REF_FIELD_BY_RECEIPT_TYPE[receipt_type]
            if receipt_type != "trace" and _is_blank(getattr(evidence, field)):
                gaps.append(REF_MISSING_CODES[field])
            if receipt_type not in by_type:
                gaps.append(_RECEIPT_MISSING_CODES[receipt_type])
        return tuple(gaps)

    # -- Stage 7: Receipt Owner (BLOCKED) -----------------------------------

    def _check_receipt_owners(
        self, evidence: RuntimeEvidenceBinding
    ) -> tuple[str, ...]:
        gaps: list[str] = []
        for receipt in evidence.receipts:
            if receipt.receipt_type not in RECEIPT_OWNERS:
                continue
            if receipt.owner != RECEIPT_OWNERS[receipt.receipt_type]:
                gaps.append(RECEIPT_OWNER_MISMATCH_CODES[receipt.receipt_type])
        return tuple(gaps)

    # -- Stage 8: Runtime Version Consistency (INCOMPARABLE) ----------------

    def _check_receipt_runtime_versions(
        self, evidence: RuntimeEvidenceBinding
    ) -> tuple[str, ...]:
        if _is_blank(evidence.runtime_version):
            # The blank top-level version is reported by stage 4; comparing
            # receipts against "" would only add noise.
            return ()
        gaps: list[str] = []
        for receipt in evidence.receipts:
            if receipt.receipt_type not in RECEIPT_OWNERS:
                continue
            if _is_blank(receipt.runtime_version):
                # INCOMPARABLE requires BOTH sides non-blank; a blank receipt
                # side is not an inconsistency claim.
                continue
            if receipt.runtime_version != evidence.runtime_version:
                gaps.append(
                    RECEIPT_RUNTIME_VERSION_MISMATCH_CODES[receipt.receipt_type]
                )
        return tuple(gaps)

    # -- Stage 9: Snapshot Consistency (INCOMPARABLE) -----------------------

    def _check_receipt_snapshots(
        self, evidence: RuntimeEvidenceBinding
    ) -> tuple[str, ...]:
        if _is_blank(evidence.corpus_snapshot_ref):
            # The blank top-level snapshot is reported by stage 5; comparing
            # receipts against "" would only add noise.
            return ()
        gaps: list[str] = []
        for receipt in evidence.receipts:
            if receipt.receipt_type not in RECEIPT_OWNERS:
                continue
            if _is_blank(receipt.snapshot_ref):
                # INCOMPARABLE requires BOTH sides non-blank; a blank receipt
                # side is not an inconsistency claim.
                continue
            if receipt.snapshot_ref == evidence.corpus_snapshot_ref:
                continue
            if (
                receipt.receipt_type == "artifact_receipt"
                and evidence.actual_profile == "local_graphrag"
            ):
                # For local_graphrag the artifact receipt is the dedicated
                # graph-index snapshot coverage check with its own fixed code.
                gaps.append(LOCAL_GRAPH_INDEX_SNAPSHOT_UNCOVERED)
            else:
                gaps.append(RECEIPT_SNAPSHOT_MISMATCH_CODES[receipt.receipt_type])
        return tuple(gaps)

    # -- Stage 10: Payload Hash Format (INVALID) ----------------------------

    def _check_payload_hash_formats(
        self, evidence: RuntimeEvidenceBinding
    ) -> tuple[str, ...]:
        gaps: list[str] = []
        if not _is_sha256_hex(evidence.artifact_payload_hash):
            gaps.append(ARTIFACT_PAYLOAD_HASH_INVALID)
        if not _is_sha256_hex(evidence.result_payload_hash):
            gaps.append(RESULT_PAYLOAD_HASH_INVALID)
        if not evidence.reference_binding_hash:
            gaps.append(REFERENCE_BINDING_HASH_MISSING)
        elif not _is_sha256_hex(evidence.reference_binding_hash):
            gaps.append(REFERENCE_BINDING_HASH_INVALID)
        for receipt in evidence.receipts:
            if receipt.receipt_type not in RECEIPT_OWNERS:
                continue
            if not _is_sha256_hex(receipt.payload_hash):
                gaps.append(RECEIPT_PAYLOAD_HASH_INVALID_CODES[receipt.receipt_type])
        return tuple(gaps)

    # -- Stage 11: Receipt Reference Binding (BLOCKED) ----------------------

    def _check_receipt_reference_binding(
        self, evidence: RuntimeEvidenceBinding
    ) -> tuple[str, ...]:
        gaps: list[str] = []
        seen_refs: set[str] = set()
        seen_types: set[str] = set()
        unknown_reported = False
        present_types = {r.receipt_type for r in evidence.receipts}
        for receipt in evidence.receipts:
            if not receipt.receipt_ref:
                gaps.append(RECEIPT_REF_MISSING)
            if receipt.receipt_ref in seen_refs:
                gaps.append(RECEIPT_REF_DUPLICATE)
            if receipt.receipt_type not in RECEIPT_OWNERS:
                # Unknown receipt types are unified: any number of distinct
                # (or repeated) unknown types yields the single fixed code,
                # reported once.  This branch runs BEFORE the known-type
                # duplicate map so that two identical unknown receipt types
                # never raise KeyError.
                if not unknown_reported:
                    gaps.append(UNKNOWN_RECEIPT_TYPE)
                    unknown_reported = True
            else:
                if receipt.receipt_type in seen_types:
                    gaps.append(RECEIPT_TYPE_DUPLICATE_CODES[receipt.receipt_type])
                field = REF_FIELD_BY_RECEIPT_TYPE[receipt.receipt_type]
                top_level_ref = getattr(evidence, field)
                if _is_blank(top_level_ref):
                    gaps.append(RECEIPT_REF_UNBOUND_CODES[receipt.receipt_type])
                elif top_level_ref != receipt.receipt_ref:
                    gaps.append(RECEIPT_REF_MISMATCH_CODES[receipt.receipt_type])
            seen_refs.add(receipt.receipt_ref)
            seen_types.add(receipt.receipt_type)
        for receipt_type in REF_FIELD_BY_RECEIPT_TYPE:
            field = REF_FIELD_BY_RECEIPT_TYPE[receipt_type]
            if getattr(evidence, field) and receipt_type not in present_types:
                gaps.append(TOP_LEVEL_REF_UNBOUND_CODES[receipt_type])
        return tuple(gaps)

    # -- Stage 12: Reference Binding Hash (BLOCKED) -------------------------

    def _check_reference_binding_hash(
        self, evidence: RuntimeEvidenceBinding
    ) -> tuple[str, ...]:
        recomputed = compute_reference_binding_hash(evidence)
        if recomputed != evidence.reference_binding_hash:
            return (REFERENCE_BINDING_HASH_MISMATCH,)
        return ()

    # -- Entry point --------------------------------------------------------

    def validate(self, binding: Mapping[str, Any]) -> BindingValidationResult:
        """Validate a serialized runtime evidence binding.

        Mapping-only: a ``RuntimeEvidenceBinding`` instance or any other
        object is INVALID with ``input_type_invalid``.  Deterministic and
        fail-closed.  Never raises on malformed input and never mutates
        ``binding``.
        """
        if not isinstance(binding, Mapping):
            return BindingValidationResult(
                BindingValidationState.INVALID, (INPUT_TYPE_INVALID,)
            )
        structural = self._check_input_structure(binding)
        if structural:
            return BindingValidationResult(BindingValidationState.INVALID, structural)
        evidence = RuntimeEvidenceBinding.from_dict(binding)
        optional_present = frozenset(
            name for name in _OPTIONAL_TOP_LEVEL_FIELDS if name in binding
        )

        gaps: list[str] = []
        state: BindingValidationState | None = None

        # Stage 2: Identity
        stage_gaps = self._check_identity(evidence, optional_present)
        if stage_gaps:
            gaps.extend(stage_gaps)
            state = state or BindingValidationState.INVALID

        # Stage 3: Profile
        stage_gaps, stage_state = self._check_profile(evidence)
        if stage_gaps:
            gaps.extend(stage_gaps)
            state = state or stage_state

        # Stage 4: Runtime Identity
        stage_gaps = self._check_runtime_identity(evidence)
        if stage_gaps:
            gaps.extend(stage_gaps)
            state = state or BindingValidationState.BLOCKED

        # Stage 5: Snapshot
        stage_gaps = self._check_snapshot(evidence)
        if stage_gaps:
            gaps.extend(stage_gaps)
            state = state or BindingValidationState.BLOCKED

        # Stage 6: Required Receipts (safe only with a known, consistent profile)
        if not self._check_profile(evidence)[0]:
            stage_gaps = self._check_required_receipts(evidence)
            if stage_gaps:
                gaps.extend(stage_gaps)
                state = state or BindingValidationState.BLOCKED

        # Stage 7: Receipt Owner
        stage_gaps = self._check_receipt_owners(evidence)
        if stage_gaps:
            gaps.extend(stage_gaps)
            state = state or BindingValidationState.BLOCKED

        # Stage 8: Runtime Version Consistency
        stage_gaps = self._check_receipt_runtime_versions(evidence)
        if stage_gaps:
            gaps.extend(stage_gaps)
            state = state or BindingValidationState.INCOMPARABLE

        # Stage 9: Snapshot Consistency
        stage_gaps = self._check_receipt_snapshots(evidence)
        if stage_gaps:
            gaps.extend(stage_gaps)
            state = state or BindingValidationState.INCOMPARABLE

        # Stage 10: Payload Hash Format
        stage_gaps = self._check_payload_hash_formats(evidence)
        if stage_gaps:
            gaps.extend(stage_gaps)
            state = state or BindingValidationState.INVALID

        # Stage 11: Receipt Reference Binding
        stage_gaps = self._check_receipt_reference_binding(evidence)
        if stage_gaps:
            gaps.extend(stage_gaps)
            state = state or BindingValidationState.BLOCKED

        # Stage 12: Reference Binding Hash (meaningful only when the binding
        # fields are complete and every hash format is legal)
        identity_clean = not self._check_identity(evidence, optional_present)
        profile_clean = not self._check_profile(evidence)[0]
        runtime_clean = not self._check_runtime_identity(evidence)
        snapshot_clean = not self._check_snapshot(evidence)
        hash_format_clean = not self._check_payload_hash_formats(evidence)
        if identity_clean and profile_clean and runtime_clean and snapshot_clean:
            if hash_format_clean:
                stage_gaps = self._check_reference_binding_hash(evidence)
                if stage_gaps:
                    gaps.extend(stage_gaps)
                    state = state or BindingValidationState.BLOCKED

        if gaps:
            return BindingValidationResult(
                state if state is not None else BindingValidationState.BLOCKED,
                tuple(gaps),
            )
        return BindingValidationResult(BindingValidationState.VALID, ())
