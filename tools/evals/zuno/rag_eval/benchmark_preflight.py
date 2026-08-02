"""PHASE22 Benchmark Preflight Contract (v5).

Deterministic, read-only preflight evaluation that answers exactly one
question: whether the upstream confirmed-contract surfaces (governance,
dataset, snapshot, gold firewall, runtime attestation, security, budget,
credentials, output contract) are sufficient to request the start of a
formal PHASE22 benchmark.

This module:

* does NOT execute retrieval, agents, or models
* does NOT touch the network, environment secrets, or real runtime objects
* does NOT generate runtime evidence, receipts, or measurements
* does NOT declare ``RUNTIME_OBSERVED``, ``MEASURED``, or
  ``PRODUCTION_READY``

The four preflight states are:

* ``READY``        -- contract satisfied; benchmark may be requested
* ``BLOCKED``      -- required surface value is missing or failed
* ``INCOMPARABLE`` -- the four canonical profiles disagree on case set,
                       snapshot, security epoch, or budget policy
* ``INVALID``      -- input structure, profile set, or field type is illegal

State ownership rules (frozen):

* ``INVALID`` is reserved for ``input_not_object``, ``input_unknown_field``,
  ``input_type_invalid_<field>``, ``input_invalid_number`` (NaN/Infinity),
  ``profiles_missing``, ``profiles_not_a_list``, profile set errors, and
  unparseable structure.
* ``BLOCKED`` is reserved for value-level surface failures. A missing
  required field is always a BLOCKED produced by the gate that owns it,
  never INVALID. Profile business field missing/empty values are routed
  to the owning gate as BLOCKED.
* ``INCOMPARABLE`` is reserved for cross-profile disagreement on the
  shared comparability surface.

Version 4 closes the final fail-closed defects:

* ``case_set_ref``, ``dataset_version``, ``security_epoch`` and
  ``budget_policy_ref`` that are missing, empty or whitespace-only are
  BLOCKED by the gate that owns the field (Dataset / Security / Budget),
  at both top level and per-profile level.
* ``dataset_hash`` that is missing, empty or whitespace-only is BLOCKED
  with ``dataset_hash_missing``; a non-empty but illegal hash is INVALID.
* INCOMPARABLE is only produced when every compared value is present and
  non-blank and at least one pair differs; blank values stay owned by
  their gates.
* ``READY`` still requires every one of the 11 gates to pass.
* The public evaluator, the convenience wrapper and the CLI never raise;
  the CLI emits no traceback, no raw OS exception, no absolute path, no
  user name and no secret.
* ``bool`` never impersonates ``int``/``float``; NaN/Infinity are INVALID.
* Every gap code is fixed and never embeds user input.

Version 5 closes the Product Runtime attestation gap:

* ``product_runtime_attested`` remains a boolean readiness declaration, but
  it is not sufficient to pass the Runtime gate.
* Every profile must include a serialized ``product_runtime_attestation``
  mapping bound to the profile/runtime/snapshot/security surface.
* The attestation hash is canonical JSON SHA-256 over the attestation fields
  except ``attestation_hash`` itself.
* Missing, malformed, mismatched, or hash-inconsistent attestations fail
  closed with fixed Runtime-gate gap codes.

The evaluator enforces the documented 11 gate priority and never raises
an exception for any input.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Tuple


CONTRACT_VERSION = "phase22-benchmark-preflight.v5"
PRODUCT_RUNTIME_ATTESTATION_VERSION = "phase22-product-runtime-attestation.v1"

CANONICAL_PROFILES: Tuple[str, ...] = (
    "standard_rag",
    "local_graphrag",
    "deep_graphrag",
    "agentic_graphrag",
)

STATE_READY = "READY"
STATE_BLOCKED = "BLOCKED"
STATE_INCOMPARABLE = "INCOMPARABLE"
STATE_INVALID = "INVALID"

LEGAL_STATES = frozenset(
    {STATE_READY, STATE_BLOCKED, STATE_INCOMPARABLE, STATE_INVALID}
)

GAP_CODE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

REQUIRED_TOP_FIELDS: Tuple[str, ...] = (
    "eval_run_id",
    "case_set_ref",
    "dataset_version",
    "dataset_hash",
    "candidate_count",
    "reviewer_status",
    "benchmark_eligible",
    "license_status",
    "integrity_status",
    "runtime_request_schema_gold_free",
    "authorization_ref",
    "security_epoch",
    "security_epoch_stale",
    "formal_execution_approved",
    "human_budget_approved",
    "budget_policy_ref",
    "provider_cost_limit",
    "token_limit",
    "deadline",
    "credential_ref",
    "has_formal_credentials",
    "formal_execution_requested",
    "output_artifact_ref",
    "profiles",
)

REQUIRED_PROFILE_FIELDS: Tuple[str, ...] = (
    "profile_name",
    "case_set_ref",
    "dataset_version",
    "corpus_snapshot_ref",
    "security_epoch",
    "budget_policy_ref",
    "runtime_name",
    "runtime_version",
    "product_runtime_attested",
    "product_runtime_attestation",
    "formal_adapter_wired",
    "knowledge_runtime_available",
    "index_runtime_available",
    "agent_run_runtime_available",
    "trace_adapter_available",
    "result_store_available",
    "artifact_store_available",
    "usage_receipt_provider_available",
    "budget_settlement_provider_available",
)

_BOOL_PROFILE_FIELDS = frozenset(
    {
        "product_runtime_attested",
        "formal_adapter_wired",
        "knowledge_runtime_available",
        "index_runtime_available",
        "agent_run_runtime_available",
        "trace_adapter_available",
        "result_store_available",
        "artifact_store_available",
        "usage_receipt_provider_available",
        "budget_settlement_provider_available",
    }
)

_STRING_PROFILE_FIELDS = frozenset(
    {
        "profile_name",
        "case_set_ref",
        "dataset_version",
        "corpus_snapshot_ref",
        "security_epoch",
        "budget_policy_ref",
        "runtime_name",
        "runtime_version",
    }
)

_REQUIRED_PRODUCT_RUNTIME_ATTESTATION_FIELDS: Tuple[str, ...] = (
    "attestation_ref",
    "profile_name",
    "runtime_name",
    "runtime_version",
    "corpus_snapshot_ref",
    "security_epoch",
    "formal_adapter_ref",
    "runtime_evidence_contract_version",
    "attestation_hash",
)

TOP_FIELD_TYPES: Dict[str, Tuple[type, ...]] = {
    "eval_run_id": (str,),
    "case_set_ref": (str,),
    "dataset_version": (str,),
    "dataset_hash": (str,),
    "candidate_count": (int,),
    "reviewer_status": (str,),
    "benchmark_eligible": (bool,),
    "license_status": (str,),
    "integrity_status": (str,),
    "runtime_request_schema_gold_free": (bool,),
    "authorization_ref": (str,),
    "security_epoch": (str,),
    "security_epoch_stale": (bool,),
    "formal_execution_approved": (bool,),
    "human_budget_approved": (bool,),
    "budget_policy_ref": (str,),
    "provider_cost_limit": (int, float),
    "token_limit": (int,),
    "deadline": (str,),
    "credential_ref": (str,),
    "has_formal_credentials": (bool,),
    "formal_execution_requested": (bool,),
    "output_artifact_ref": (str,),
}


@dataclass(frozen=True)
class ProfilePreflightInput:
    """Declared preflight surface for a single canonical profile.

    Missing business fields (``None``) are tolerated by the constructor
    and routed to the appropriate ownership gate as BLOCKED.
    """

    profile_name: Optional[str]
    case_set_ref: Optional[str]
    dataset_version: Optional[str]
    corpus_snapshot_ref: Optional[str]
    security_epoch: Optional[str]
    budget_policy_ref: Optional[str]
    runtime_name: Optional[str]
    runtime_version: Optional[str]
    product_runtime_attested: Optional[bool]
    product_runtime_attestation: Optional[Mapping[str, Any]]
    formal_adapter_wired: Optional[bool]
    knowledge_runtime_available: Optional[bool]
    index_runtime_available: Optional[bool]
    agent_run_runtime_available: Optional[bool]
    trace_adapter_available: Optional[bool]
    result_store_available: Optional[bool]
    artifact_store_available: Optional[bool]
    usage_receipt_provider_available: Optional[bool]
    budget_settlement_provider_available: Optional[bool]


@dataclass(frozen=True)
class BenchmarkPreflightInput:
    """Top-level preflight input for a PHASE22 benchmark request."""

    eval_run_id: str
    case_set_ref: str
    dataset_version: str
    dataset_hash: str
    candidate_count: int
    reviewer_status: str
    benchmark_eligible: bool
    license_status: str
    integrity_status: str
    runtime_request_schema_gold_free: bool
    authorization_ref: str
    security_epoch: str
    security_epoch_stale: bool
    formal_execution_approved: bool
    human_budget_approved: bool
    budget_policy_ref: str
    provider_cost_limit: float
    token_limit: int
    deadline: str
    credential_ref: str
    has_formal_credentials: bool
    formal_execution_requested: bool
    output_artifact_ref: str
    profiles: Tuple[ProfilePreflightInput, ...]


@dataclass(frozen=True)
class ProfilePreflightResult:
    """Per-profile preflight verdict."""

    profile_name: str
    state: str
    gap_codes: Tuple[str, ...]


@dataclass(frozen=True)
class BenchmarkPreflightReport:
    """Final preflight report returned to the caller."""

    state: str
    gap_codes: Tuple[str, ...]
    profile_results: Tuple[ProfilePreflightResult, ...]
    input_fingerprint: str
    contract_version: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _is_finite_real(value: Any) -> bool:
    """True for a finite ``int`` or ``float`` (not NaN, not Inf), and
    explicitly ``not bool``."""

    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    if isinstance(value, float):
        return math.isfinite(value)
    return False


def _is_valid_sha256_hex(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    return all(c in "0123456789abcdefABCDEF" for c in value)


def _canonical_sha256_hex(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def compute_product_runtime_attestation_hash(attestation: Mapping[str, Any]) -> str:
    """Canonical hash over a serialized Product Runtime attestation.

    ``attestation_hash`` is excluded so callers can validate a self-contained
    attestation payload without mutating it.
    """

    payload = {
        key: value
        for key, value in attestation.items()
        if key != "attestation_hash"
    }
    return _canonical_sha256_hex(payload)


def _sort_key_for_profile(item: Any) -> Tuple[int, int, str]:
    """Stable sort key: canonical profiles first in canonical order, then
    unknown profiles sorted by name, then malformed entries."""

    canonical_index = {name: i for i, name in enumerate(CANONICAL_PROFILES)}
    if isinstance(item, Mapping):
        name = item.get("profile_name", "")
        if isinstance(name, str) and name in canonical_index:
            return (0, canonical_index[name], name)
        return (1, 0, str(name))
    return (2, 0, "")


def _normalize_payload_for_fingerprint(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a canonicalised copy of the payload for fingerprinting."""

    out: Dict[str, Any] = {}
    for key, value in payload.items():
        if key == "profiles" and isinstance(value, list):
            out[key] = sorted(value, key=_sort_key_for_profile)
        else:
            out[key] = value
    return out


def compute_input_fingerprint(payload: Any) -> str:
    """Compute the input fingerprint for any payload that survived JSON
    parsing. Returns an empty string for non-object payloads."""

    if not isinstance(payload, Mapping):
        return ""
    try:
        return _canonical_sha256_hex(_normalize_payload_for_fingerprint(payload))
    except (TypeError, ValueError):
        return ""


def _coerce_profiles(
    profiles: Any,
) -> Tuple[Optional[Tuple[ProfilePreflightInput, ...]], Optional[str]]:
    """Validate the profile set. Returns either the parsed canonical
    tuple or ``(None, gap_code)``. Profile business fields may be
    missing -- they are routed to their ownership gates as BLOCKED."""

    if not isinstance(profiles, list):
        return None, "profiles_not_a_list"

    seen: List[str] = []
    seen_set: set = set()
    parsed: List[ProfilePreflightInput] = []

    for idx, item in enumerate(profiles):
        if not isinstance(item, Mapping):
            return None, "profile_invalid_entry"

        profile_name = item.get("profile_name")
        if not isinstance(profile_name, str):
            return None, "profile_name_type_invalid"
        if not profile_name:
            return None, "profile_name_missing"

        if profile_name in seen_set:
            return None, "profile_duplicate"
        seen_set.add(profile_name)
        seen.append(profile_name)

        # Validate types per profile field. Missing fields are NOT
        # rejected here -- they are routed to the owning gate as BLOCKED.
        for field_name in REQUIRED_PROFILE_FIELDS:
            if field_name not in item:
                continue
            value = item[field_name]
            if field_name == "profile_name":
                if not isinstance(value, str):
                    return None, "profile_name_type_invalid"
                continue
            if field_name in _STRING_PROFILE_FIELDS:
                if not isinstance(value, str):
                    return None, "profile_string_field_type_invalid"
            elif field_name in _BOOL_PROFILE_FIELDS:
                if isinstance(value, bool):
                    pass
                elif value is None:
                    pass
                elif not isinstance(value, bool):
                    return None, "profile_boolean_field_type_invalid"
            elif field_name == "product_runtime_attestation":
                if value is not None and not isinstance(value, Mapping):
                    return None, "profile_attestation_type_invalid"

        parsed.append(
            ProfilePreflightInput(
                profile_name=profile_name,
                case_set_ref=item.get("case_set_ref"),
                dataset_version=item.get("dataset_version"),
                corpus_snapshot_ref=item.get("corpus_snapshot_ref"),
                security_epoch=item.get("security_epoch"),
                budget_policy_ref=item.get("budget_policy_ref"),
                runtime_name=item.get("runtime_name"),
                runtime_version=item.get("runtime_version"),
                product_runtime_attested=item.get("product_runtime_attested"),
                product_runtime_attestation=item.get(
                    "product_runtime_attestation"
                ),
                formal_adapter_wired=item.get("formal_adapter_wired"),
                knowledge_runtime_available=item.get(
                    "knowledge_runtime_available"
                ),
                index_runtime_available=item.get("index_runtime_available"),
                agent_run_runtime_available=item.get(
                    "agent_run_runtime_available"
                ),
                trace_adapter_available=item.get("trace_adapter_available"),
                result_store_available=item.get("result_store_available"),
                artifact_store_available=item.get("artifact_store_available"),
                usage_receipt_provider_available=item.get(
                    "usage_receipt_provider_available"
                ),
                budget_settlement_provider_available=item.get(
                    "budget_settlement_provider_available"
                ),
            )
        )

    canonical_set = frozenset(CANONICAL_PROFILES)
    seen_set_frozen = frozenset(seen)
    if seen_set_frozen != canonical_set:
        extra = [p for p in seen if p not in canonical_set]
        if extra:
            return None, "profile_unknown"
        missing = [p for p in CANONICAL_PROFILES if p not in seen_set_frozen]
        if missing:
            return None, "profile_set_missing_" + missing[0]
        return None, "profile_unknown"

    by_name = {p.profile_name: p for p in parsed}
    ordered = tuple(by_name[name] for name in CANONICAL_PROFILES)
    return ordered, None


def _default_str(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _has_non_empty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _default_bool(value: Any) -> bool:
    return value if isinstance(value, bool) else False


def _default_int(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value
    return 0


def _default_float(value: Any) -> float:
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, (int, float)) and math.isfinite(value):
        return float(value)
    return 0.0


def _product_runtime_attestation_gap(profile: ProfilePreflightInput) -> Optional[str]:
    attestation = profile.product_runtime_attestation
    if attestation is None:
        return "product_runtime_attestation_missing"
    if not isinstance(attestation, Mapping):
        return "product_runtime_attestation_invalid"

    for field_name in _REQUIRED_PRODUCT_RUNTIME_ATTESTATION_FIELDS:
        value = attestation.get(field_name)
        if not _has_non_empty(value):
            return "product_runtime_attestation_field_missing"

    if (
        attestation.get("runtime_evidence_contract_version")
        != PRODUCT_RUNTIME_ATTESTATION_VERSION
    ):
        return "product_runtime_attestation_version_mismatch"

    if not _is_valid_sha256_hex(attestation.get("attestation_hash")):
        return "product_runtime_attestation_hash_invalid"

    try:
        expected_hash = compute_product_runtime_attestation_hash(attestation)
    except (TypeError, ValueError):
        return "product_runtime_attestation_invalid"

    if attestation.get("attestation_hash") != expected_hash:
        return "product_runtime_attestation_hash_mismatch"

    if attestation.get("profile_name") != profile.profile_name:
        return "product_runtime_attestation_runtime_mismatch"

    if (
        _has_non_empty(profile.runtime_name)
        and _has_non_empty(attestation.get("runtime_name"))
        and attestation.get("runtime_name") != profile.runtime_name
    ):
        return "product_runtime_attestation_runtime_mismatch"
    if (
        _has_non_empty(profile.runtime_version)
        and _has_non_empty(attestation.get("runtime_version"))
        and attestation.get("runtime_version") != profile.runtime_version
    ):
        return "product_runtime_attestation_runtime_mismatch"

    if (
        _has_non_empty(profile.corpus_snapshot_ref)
        and _has_non_empty(attestation.get("corpus_snapshot_ref"))
        and attestation.get("corpus_snapshot_ref") != profile.corpus_snapshot_ref
    ):
        return "product_runtime_attestation_scope_mismatch"
    if (
        _has_non_empty(profile.security_epoch)
        and _has_non_empty(attestation.get("security_epoch"))
        and attestation.get("security_epoch") != profile.security_epoch
    ):
        return "product_runtime_attestation_scope_mismatch"

    return None


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------


class BenchmarkPreflightEvaluator:
    """Deterministic PHASE22 benchmark preflight evaluator.

    Maintains a strict 11-gate priority and never raises an exception;
    every input produces a structured report.
    """

    def evaluate(self, payload: Any) -> BenchmarkPreflightReport:
        try:
            return self._evaluate_inner(payload)
        except Exception:
            fingerprint = compute_input_fingerprint(payload)
            return self._build(
                STATE_INVALID, ("internal_evaluation_failed",), (), fingerprint
            )

    def _evaluate_inner(self, payload: Any) -> BenchmarkPreflightReport:
        fingerprint = compute_input_fingerprint(payload)

        # Gate 1: Input Structure
        gate1 = self._gate_input_structure(payload)
        if gate1 is not None:
            return self._build(gate1[0], gate1[1], (), fingerprint)

        # Gate 2: Profile Set
        gate2 = self._gate_profile_set(payload)
        if gate2 is not None:
            return self._build(gate2[0], gate2[1], (), fingerprint)

        # Coerce profiles for downstream gates.
        parsed_profiles, profile_error = _coerce_profiles(payload["profiles"])
        if profile_error is not None or parsed_profiles is None:
            return self._build(
                STATE_INVALID, (profile_error or "profile_invalid_entry",), (), fingerprint
            )

        input_obj = self._build_input_obj(payload, parsed_profiles)

        # Gate 3: Comparability
        comparability = self._gate_comparability(input_obj)
        if comparability is not None:
            return self._build(comparability[0], comparability[1], (), fingerprint)

        # Gates 4..11 in fixed order. Lower-numbered gates short-circuit.
        for gate in (
            lambda: self._gate_governance(input_obj),
            lambda: self._gate_dataset(input_obj),
            lambda: self._gate_gold_firewall(input_obj),
            lambda: self._gate_runtime(input_obj),
            lambda: self._gate_security(input_obj),
            lambda: self._gate_budget(input_obj),
            lambda: self._gate_credentials(input_obj),
            lambda: self._gate_output_contract(input_obj),
        ):
            verdict = gate()
            if verdict is not None:
                state, gaps, profile_results = verdict
                return self._build(state, gaps, profile_results, fingerprint)

        profile_results = tuple(
            ProfilePreflightResult(
                profile_name=p.profile_name or "",
                state=STATE_READY,
                gap_codes=(),
            )
            for p in input_obj.profiles
        )
        return self._build(STATE_READY, (), profile_results, fingerprint)

    def _build_input_obj(
        self,
        payload: Any,
        parsed_profiles: Tuple[ProfilePreflightInput, ...],
    ) -> BenchmarkPreflightInput:
        return BenchmarkPreflightInput(
            eval_run_id=_default_str(payload.get("eval_run_id")),
            case_set_ref=_default_str(payload.get("case_set_ref")),
            dataset_version=_default_str(payload.get("dataset_version")),
            dataset_hash=_default_str(payload.get("dataset_hash")),
            candidate_count=_default_int(payload.get("candidate_count")),
            reviewer_status=_default_str(payload.get("reviewer_status")),
            benchmark_eligible=_default_bool(payload.get("benchmark_eligible")),
            license_status=_default_str(payload.get("license_status")),
            integrity_status=_default_str(payload.get("integrity_status")),
            runtime_request_schema_gold_free=_default_bool(
                payload.get("runtime_request_schema_gold_free")
            ),
            authorization_ref=_default_str(payload.get("authorization_ref")),
            security_epoch=_default_str(payload.get("security_epoch")),
            security_epoch_stale=_default_bool(
                payload.get("security_epoch_stale")
            ),
            formal_execution_approved=_default_bool(
                payload.get("formal_execution_approved")
            ),
            human_budget_approved=_default_bool(
                payload.get("human_budget_approved")
            ),
            budget_policy_ref=_default_str(payload.get("budget_policy_ref")),
            provider_cost_limit=_default_float(payload.get("provider_cost_limit")),
            token_limit=_default_int(payload.get("token_limit")),
            deadline=_default_str(payload.get("deadline")),
            credential_ref=_default_str(payload.get("credential_ref")),
            has_formal_credentials=_default_bool(
                payload.get("has_formal_credentials")
            ),
            formal_execution_requested=_default_bool(
                payload.get("formal_execution_requested")
            ),
            output_artifact_ref=_default_str(payload.get("output_artifact_ref")),
            profiles=parsed_profiles,
        )

    # ------------------------------------------------------------------
    # Gate 1: Input Structure
    # ------------------------------------------------------------------

    def _gate_input_structure(
        self, payload: Any
    ) -> Optional[Tuple[str, Tuple[str, ...]]]:
        if not isinstance(payload, Mapping):
            return STATE_INVALID, ("input_not_object",)

        unknown = [k for k in payload.keys() if k not in REQUIRED_TOP_FIELDS]
        if unknown:
            return STATE_INVALID, ("input_unknown_field",)

        for field_name, expected_types in TOP_FIELD_TYPES.items():
            if field_name not in payload:
                continue
            value = payload[field_name]
            # bool is a subclass of int; reject explicitly first.
            if field_name in ("candidate_count", "token_limit"):
                if isinstance(value, bool):
                    return STATE_INVALID, (f"input_type_invalid_{field_name}",)
            if field_name == "provider_cost_limit":
                if isinstance(value, bool):
                    return STATE_INVALID, ("input_type_invalid_provider_cost_limit",)
            if not isinstance(value, expected_types):
                return STATE_INVALID, (f"input_type_invalid_{field_name}",)

        # NaN / Infinity detection for numeric fields.
        for numeric_field in ("provider_cost_limit", "token_limit"):
            if numeric_field in payload:
                value = payload[numeric_field]
                if isinstance(value, float) and not math.isfinite(value):
                    return STATE_INVALID, ("input_invalid_number",)

        # dataset_hash must be a valid SHA-256 hex string when present and
        # non-blank.  A blank dataset_hash (empty or whitespace-only) is a
        # value-level failure owned by the Dataset gate, which reports it as
        # BLOCKED dataset_hash_missing -- never as INVALID here.
        if "dataset_hash" in payload:
            value = payload["dataset_hash"]
            if isinstance(value, str) and value.strip():
                if not _is_valid_sha256_hex(value):
                    return STATE_INVALID, ("input_type_invalid_dataset_hash",)

        return None

    # ------------------------------------------------------------------
    # Gate 2: Profile Set
    # ------------------------------------------------------------------

    def _gate_profile_set(
        self, payload: Any
    ) -> Optional[Tuple[str, Tuple[str, ...]]]:
        if "profiles" not in payload:
            return STATE_INVALID, ("profiles_missing",)
        profiles = payload["profiles"]
        if not isinstance(profiles, list):
            return STATE_INVALID, ("profiles_not_a_list",)
        if not profiles:
            return STATE_INVALID, ("profile_set_missing_standard_rag",)
        names = []
        for entry in profiles:
            if not isinstance(entry, Mapping):
                return STATE_INVALID, ("profile_invalid_entry",)
            name = entry.get("profile_name")
            if not isinstance(name, str):
                return STATE_INVALID, ("profile_name_type_invalid",)
            if not name:
                return STATE_INVALID, ("profile_name_missing",)
            names.append(name)
        if len(set(names)) != len(names):
            return STATE_INVALID, ("profile_duplicate",)
        seen_set = set(names)
        canonical_set = set(CANONICAL_PROFILES)
        if seen_set != canonical_set:
            extra = [n for n in names if n not in canonical_set]
            if extra:
                return STATE_INVALID, ("profile_unknown",)
            missing = [n for n in CANONICAL_PROFILES if n not in seen_set]
            if missing:
                return STATE_INVALID, ("profile_set_missing_" + missing[0],)
        return None

    # ------------------------------------------------------------------
    # Gate 3: Comparability
    # ------------------------------------------------------------------

    def _gate_comparability(
        self, input_obj: BenchmarkPreflightInput
    ) -> Optional[Tuple[str, Tuple[str, ...]]]:
        first = input_obj.profiles[0]
        snapshot_refs = [p.corpus_snapshot_ref for p in input_obj.profiles]
        # INCOMPARABLE requires every profile's fixed comparison dimension to
        # be present and non-blank: a blank side is a value-level failure
        # owned by its gate (BLOCKED), never a cross-profile inconsistency.
        if all(_has_non_empty(r) for r in snapshot_refs) and len(set(snapshot_refs)) != 1:
            return STATE_INCOMPARABLE, ("corpus_snapshot_mismatch",)

        for other in input_obj.profiles[1:]:
            if _has_non_empty(first.case_set_ref) and _has_non_empty(other.case_set_ref) and \
                    first.case_set_ref != other.case_set_ref:
                return STATE_INCOMPARABLE, ("case_set_mismatch",)
            if _has_non_empty(first.dataset_version) and _has_non_empty(other.dataset_version) and \
                    first.dataset_version != other.dataset_version:
                return STATE_INCOMPARABLE, ("dataset_version_mismatch",)
            if _has_non_empty(first.corpus_snapshot_ref) and _has_non_empty(other.corpus_snapshot_ref) and \
                    first.corpus_snapshot_ref != other.corpus_snapshot_ref:
                return STATE_INCOMPARABLE, ("corpus_snapshot_mismatch",)
            if _has_non_empty(first.security_epoch) and _has_non_empty(other.security_epoch) and \
                    first.security_epoch != other.security_epoch:
                return STATE_INCOMPARABLE, ("security_epoch_mismatch",)
            if _has_non_empty(first.budget_policy_ref) and _has_non_empty(other.budget_policy_ref) and \
                    first.budget_policy_ref != other.budget_policy_ref:
                return STATE_INCOMPARABLE, ("budget_policy_mismatch",)

        if _has_non_empty(input_obj.case_set_ref) and _has_non_empty(first.case_set_ref) and \
                input_obj.case_set_ref != first.case_set_ref:
            return STATE_INCOMPARABLE, ("case_set_mismatch",)
        if _has_non_empty(input_obj.dataset_version) and _has_non_empty(first.dataset_version) and \
                input_obj.dataset_version != first.dataset_version:
            return STATE_INCOMPARABLE, ("dataset_version_mismatch",)
        if _has_non_empty(input_obj.security_epoch) and _has_non_empty(first.security_epoch) and \
                input_obj.security_epoch != first.security_epoch:
            return STATE_INCOMPARABLE, ("security_epoch_mismatch",)
        if _has_non_empty(input_obj.budget_policy_ref) and _has_non_empty(first.budget_policy_ref) and \
                input_obj.budget_policy_ref != first.budget_policy_ref:
            return STATE_INCOMPARABLE, ("budget_policy_mismatch",)

        return None

    # ------------------------------------------------------------------
    # Gate 4: Governance
    # ------------------------------------------------------------------

    def _gate_governance(
        self, input_obj: BenchmarkPreflightInput
    ) -> Optional[Tuple[str, Tuple[str, ...], Tuple[ProfilePreflightResult, ...]]]:
        # eval_run_id is the first governance check. Formal benchmark
        # approval and every downstream artifact must be bound to a
        # non-empty, non-whitespace run identity.
        if not _has_non_empty(input_obj.eval_run_id):
            return STATE_BLOCKED, ("eval_run_id_missing",), ()

        gaps: List[str] = []
        if input_obj.reviewer_status != "approved":
            gaps.append("reviewer_not_approved")
        if input_obj.benchmark_eligible is not True:
            gaps.append("benchmark_not_eligible")
        if input_obj.license_status != "verified":
            gaps.append("license_not_verified")
        if input_obj.integrity_status != "verified":
            gaps.append("integrity_not_verified")
        if gaps:
            return STATE_BLOCKED, tuple(gaps), ()
        return None

    # ------------------------------------------------------------------
    # Gate 5: Dataset and Snapshot
    # ------------------------------------------------------------------

    def _gate_dataset(
        self, input_obj: BenchmarkPreflightInput
    ) -> Optional[Tuple[str, Tuple[str, ...], Tuple[ProfilePreflightResult, ...]]]:
        gaps: List[str] = []
        # Missing, empty or whitespace-only business preconditions are BLOCKED
        # by the gate that owns the field.
        if not _has_non_empty(input_obj.case_set_ref):
            gaps.append("case_set_ref_missing")
        if not _has_non_empty(input_obj.dataset_version):
            gaps.append("dataset_version_missing")
        if not _has_non_empty(input_obj.dataset_hash):
            gaps.append("dataset_hash_missing")
        if input_obj.candidate_count <= 0:
            gaps.append("candidate_count_invalid")
        if any(not _has_non_empty(p.corpus_snapshot_ref) for p in input_obj.profiles):
            gaps.append("corpus_snapshot_missing")
        for p in input_obj.profiles:
            if not _has_non_empty(p.case_set_ref):
                gaps.append("profile_case_set_ref_missing")
                break
        for p in input_obj.profiles:
            if not _has_non_empty(p.dataset_version):
                gaps.append("profile_dataset_version_missing")
                break
        if gaps:
            return STATE_BLOCKED, tuple(gaps), ()
        return None

    # ------------------------------------------------------------------
    # Gate 6: Gold Evidence Firewall
    # ------------------------------------------------------------------

    def _gate_gold_firewall(
        self, input_obj: BenchmarkPreflightInput
    ) -> Optional[Tuple[str, Tuple[str, ...], Tuple[ProfilePreflightResult, ...]]]:
        if input_obj.runtime_request_schema_gold_free is not True:
            return STATE_BLOCKED, ("gold_firewall_not_proven",), ()
        return None

    # ------------------------------------------------------------------
    # Gate 7: Runtime
    # ------------------------------------------------------------------

    def _gate_runtime(
        self, input_obj: BenchmarkPreflightInput
    ) -> Optional[Tuple[str, Tuple[str, ...], Tuple[ProfilePreflightResult, ...]]]:
        per_profile: List[ProfilePreflightResult] = []
        global_gaps: List[str] = []

        for profile in input_obj.profiles:
            gaps: List[str] = []
            if profile.product_runtime_attested is not True:
                gaps.append("product_runtime_not_attested")
            attestation_gap = _product_runtime_attestation_gap(profile)
            if attestation_gap is not None:
                gaps.append(attestation_gap)
            if not _has_non_empty(profile.runtime_name):
                gaps.append("runtime_name_missing")
            if not _has_non_empty(profile.runtime_version):
                gaps.append("runtime_version_missing")
            if profile.formal_adapter_wired is not True:
                gaps.append("runtime_adapter_unwired")
            if profile.knowledge_runtime_available is not True:
                gaps.append("knowledge_runtime_unavailable")
            if profile.trace_adapter_available is not True:
                gaps.append("trace_adapter_unavailable")
            if profile.result_store_available is not True:
                gaps.append("result_store_unavailable")
            if profile.artifact_store_available is not True:
                gaps.append("artifact_store_unavailable")
            if profile.usage_receipt_provider_available is not True:
                gaps.append("usage_receipt_provider_unavailable")
            if profile.budget_settlement_provider_available is not True:
                gaps.append("budget_settlement_provider_unavailable")
            if profile.profile_name == "local_graphrag":
                if profile.index_runtime_available is not True:
                    gaps.append("index_runtime_unavailable")
            elif profile.profile_name == "agentic_graphrag":
                if profile.agent_run_runtime_available is not True:
                    gaps.append("agent_run_runtime_unavailable")

            if gaps:
                per_profile.append(
                    ProfilePreflightResult(
                        profile_name=profile.profile_name or "",
                        state=STATE_BLOCKED,
                        gap_codes=tuple(gaps),
                    )
                )
                for code in gaps:
                    if code not in global_gaps:
                        global_gaps.append(code)
            else:
                per_profile.append(
                    ProfilePreflightResult(
                        profile_name=profile.profile_name or "",
                        state=STATE_READY,
                        gap_codes=(),
                    )
                )

        if global_gaps:
            return STATE_BLOCKED, tuple(global_gaps), tuple(per_profile)
        return None

    # ------------------------------------------------------------------
    # Gate 8: Security
    # ------------------------------------------------------------------

    def _gate_security(
        self, input_obj: BenchmarkPreflightInput
    ) -> Optional[Tuple[str, Tuple[str, ...], Tuple[ProfilePreflightResult, ...]]]:
        gaps: List[str] = []
        if not _has_non_empty(input_obj.authorization_ref):
            gaps.append("authorization_ref_missing")
        if not _has_non_empty(input_obj.security_epoch):
            gaps.append("security_epoch_missing")
        for p in input_obj.profiles:
            if not _has_non_empty(p.security_epoch):
                gaps.append("profile_security_epoch_missing")
                break
        if input_obj.security_epoch_stale is not False:
            gaps.append("security_epoch_stale")
        if input_obj.formal_execution_approved is not True:
            gaps.append("formal_execution_not_approved")
        if gaps:
            return STATE_BLOCKED, tuple(gaps), ()
        return None

    # ------------------------------------------------------------------
    # Gate 9: Budget
    # ------------------------------------------------------------------

    def _gate_budget(
        self, input_obj: BenchmarkPreflightInput
    ) -> Optional[Tuple[str, Tuple[str, ...], Tuple[ProfilePreflightResult, ...]]]:
        gaps: List[str] = []
        if input_obj.human_budget_approved is not True:
            gaps.append("human_budget_not_approved")
        if not _has_non_empty(input_obj.budget_policy_ref):
            gaps.append("budget_policy_ref_missing")
        for p in input_obj.profiles:
            if not _has_non_empty(p.budget_policy_ref):
                gaps.append("profile_budget_policy_ref_missing")
                break
        if (
            not _is_finite_real(input_obj.provider_cost_limit)
            or input_obj.provider_cost_limit <= 0
        ):
            gaps.append("provider_cost_limit_invalid")
        if input_obj.token_limit <= 0:
            gaps.append("token_limit_invalid")
        if not _has_non_empty(input_obj.deadline):
            gaps.append("deadline_missing")
        if gaps:
            return STATE_BLOCKED, tuple(gaps), ()
        return None

    # ------------------------------------------------------------------
    # Gate 10: Credentials and Formal Execution
    # ------------------------------------------------------------------

    def _gate_credentials(
        self, input_obj: BenchmarkPreflightInput
    ) -> Optional[Tuple[str, Tuple[str, ...], Tuple[ProfilePreflightResult, ...]]]:
        gaps: List[str] = []
        if not _has_non_empty(input_obj.credential_ref):
            gaps.append("credential_ref_missing")
        if input_obj.has_formal_credentials is not True:
            gaps.append("formal_credentials_missing")
        if input_obj.formal_execution_requested is not True:
            gaps.append("formal_execution_not_requested")
        if gaps:
            return STATE_BLOCKED, tuple(gaps), ()
        return None

    # ------------------------------------------------------------------
    # Gate 11: Output Contract
    # ------------------------------------------------------------------

    def _gate_output_contract(
        self, input_obj: BenchmarkPreflightInput
    ) -> Optional[Tuple[str, Tuple[str, ...], Tuple[ProfilePreflightResult, ...]]]:
        if not _has_non_empty(input_obj.output_artifact_ref):
            return STATE_BLOCKED, ("output_artifact_ref_missing",), ()
        return None

    # ------------------------------------------------------------------
    # Report assembly
    # ------------------------------------------------------------------

    def _build(
        self,
        state: str,
        gap_codes: Tuple[str, ...],
        profile_results: Tuple[ProfilePreflightResult, ...],
        fingerprint: str,
    ) -> BenchmarkPreflightReport:
        return BenchmarkPreflightReport(
            state=state,
            gap_codes=gap_codes,
            profile_results=profile_results,
            input_fingerprint=fingerprint,
            contract_version=CONTRACT_VERSION,
        )


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def report_to_dict(report: BenchmarkPreflightReport) -> Dict[str, Any]:
    """Serialise a :class:`BenchmarkPreflightReport` into a stable dict."""

    return {
        "contract_version": report.contract_version,
        "state": report.state,
        "gap_codes": list(report.gap_codes),
        "profile_results": [
            {
                "profile_name": pr.profile_name,
                "state": pr.state,
                "gap_codes": list(pr.gap_codes),
            }
            for pr in report.profile_results
        ],
        "input_fingerprint": report.input_fingerprint,
    }


def validate_gap_code(code: str) -> bool:
    """Return True if ``code`` matches the fixed gap-code vocabulary."""

    return bool(isinstance(code, str) and GAP_CODE_PATTERN.match(code))


def evaluate_payload(payload: Mapping[str, Any]) -> BenchmarkPreflightReport:
    """Convenience wrapper around :class:`BenchmarkPreflightEvaluator`."""

    return BenchmarkPreflightEvaluator().evaluate(payload)


__all__ = [
    "CONTRACT_VERSION",
    "PRODUCT_RUNTIME_ATTESTATION_VERSION",
    "CANONICAL_PROFILES",
    "STATE_READY",
    "STATE_BLOCKED",
    "STATE_INCOMPARABLE",
    "STATE_INVALID",
    "LEGAL_STATES",
    "GAP_CODE_PATTERN",
    "ProfilePreflightInput",
    "BenchmarkPreflightInput",
    "ProfilePreflightResult",
    "BenchmarkPreflightReport",
    "BenchmarkPreflightEvaluator",
    "evaluate_payload",
    "report_to_dict",
    "compute_input_fingerprint",
    "compute_product_runtime_attestation_hash",
    "validate_gap_code",
]
