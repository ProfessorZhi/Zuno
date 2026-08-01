"""PHASE22 Benchmark Preflight Contract (v2).

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
  ``input_type_invalid_*``, ``input_invalid_number`` (NaN/Infinity), profile
  set errors, and unparseable structure.
* ``BLOCKED`` is reserved for value-level surface failures. A missing
  required field is always a BLOCKED produced by the gate that owns it,
  never INVALID.
* ``INCOMPARABLE`` is reserved for cross-profile disagreement on the
  shared comparability surface.

The evaluator enforces the documented gate priority. The input
fingerprint is always derived from the raw payload (never from the
evaluator's state) so that any two structurally distinct inputs produce
distinct fingerprints, and any two structurally identical inputs produce
the same fingerprint.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Tuple


CONTRACT_VERSION = "phase22-benchmark-preflight.v2"

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
    """Declared preflight surface for a single canonical profile."""

    profile_name: str
    case_set_ref: str
    dataset_version: str
    corpus_snapshot_ref: str
    security_epoch: str
    budget_policy_ref: str
    runtime_name: str
    runtime_version: str
    product_runtime_attested: bool
    formal_adapter_wired: bool
    knowledge_runtime_available: bool
    index_runtime_available: bool
    agent_run_runtime_available: bool
    trace_adapter_available: bool
    result_store_available: bool
    artifact_store_available: bool
    usage_receipt_provider_available: bool
    budget_settlement_provider_available: bool


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
    """True for a finite ``int`` or ``float`` (not NaN, not Inf)."""

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
    """Return a canonicalised copy of the payload for fingerprinting.

    Profile order is normalised so reordering the input does not change
    the fingerprint. The fingerprint is purely a structural hash of the
    input; it is never computed from the evaluator's state.
    """

    out: Dict[str, Any] = {}
    for key, value in payload.items():
        if key == "profiles" and isinstance(value, list):
            out[key] = sorted(value, key=_sort_key_for_profile)
        else:
            out[key] = value
    return out


def compute_input_fingerprint(payload: Any) -> str:
    """Compute the input fingerprint for any payload that survived JSON
    parsing. Returns an empty string for non-object payloads (those
    fail ``input_not_object`` before they can be hashed)."""

    if not isinstance(payload, Mapping):
        return ""
    try:
        return _canonical_sha256_hex(_normalize_payload_for_fingerprint(payload))
    except (TypeError, ValueError):
        return ""


def _coerce_profiles(
    profiles: Any,
) -> Tuple[Optional[Tuple[ProfilePreflightInput, ...]], Optional[str]]:
    """Validate the profile list. Returns either the parsed canonical
    tuple or ``(None, gap_code)``."""

    if not isinstance(profiles, list):
        return None, "profiles_not_a_list"

    seen: List[str] = []
    seen_set: set = set()
    parsed: List[ProfilePreflightInput] = []

    for item in profiles:
        if not isinstance(item, Mapping):
            return None, "profile_invalid_entry"

        profile_name = item.get("profile_name")
        if not isinstance(profile_name, str):
            return None, "profile_invalid_entry"

        if profile_name in seen_set:
            return None, "profile_duplicate"
        seen_set.add(profile_name)
        seen.append(profile_name)

        for field_name in REQUIRED_PROFILE_FIELDS:
            if field_name not in item:
                return None, f"profile_invalid_{profile_name}"
            value = item[field_name]
            if field_name in _BOOL_PROFILE_FIELDS:
                if not isinstance(value, bool):
                    return None, f"profile_invalid_{profile_name}"
            elif not isinstance(value, str):
                return None, f"profile_invalid_{profile_name}"

        parsed.append(
            ProfilePreflightInput(
                profile_name=profile_name,
                case_set_ref=item["case_set_ref"],
                dataset_version=item["dataset_version"],
                corpus_snapshot_ref=item["corpus_snapshot_ref"],
                security_epoch=item["security_epoch"],
                budget_policy_ref=item["budget_policy_ref"],
                runtime_name=item["runtime_name"],
                runtime_version=item["runtime_version"],
                product_runtime_attested=item["product_runtime_attested"],
                formal_adapter_wired=item["formal_adapter_wired"],
                knowledge_runtime_available=item["knowledge_runtime_available"],
                index_runtime_available=item["index_runtime_available"],
                agent_run_runtime_available=item["agent_run_runtime_available"],
                trace_adapter_available=item["trace_adapter_available"],
                result_store_available=item["result_store_available"],
                artifact_store_available=item["artifact_store_available"],
                usage_receipt_provider_available=item[
                    "usage_receipt_provider_available"
                ],
                budget_settlement_provider_available=item[
                    "budget_settlement_provider_available"
                ],
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


def _default_bool(value: Any) -> bool:
    return value if isinstance(value, bool) else False


def _default_int(value: Any) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _default_float(value: Any) -> float:
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, (int, float)) and math.isfinite(value):
        return float(value)
    return 0.0


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------


class BenchmarkPreflightEvaluator:
    """Deterministic PHASE22 benchmark preflight evaluator."""

    def evaluate(self, payload: Any) -> BenchmarkPreflightReport:
        fingerprint = compute_input_fingerprint(payload)

        # Gate 1: Input Structure -- only shape/types, never presence.
        gate1 = self._gate_input_structure(payload)
        if gate1 is not None:
            return self._build(gate1[0], gate1[1], (), fingerprint)

        # Coerce profiles before any business gate.
        parsed_profiles, profile_error = _coerce_profiles(payload["profiles"])
        if profile_error is not None:
            return self._build(STATE_INVALID, (profile_error,), (), fingerprint)
        assert parsed_profiles is not None

        input_obj = BenchmarkPreflightInput(
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

        # Gate 2: Comparability must run before business gates so that
        # uncomparable profiles are surfaced distinctly.
        comparability = self._gate_comparability(input_obj)
        if comparability is not None:
            return self._build(comparability[0], comparability[1], (), fingerprint)

        # Gates 3..10: business gates. Lower-numbered gates short-circuit.
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
                profile_name=p.profile_name,
                state=STATE_READY,
                gap_codes=(),
            )
            for p in input_obj.profiles
        )
        return self._build(STATE_READY, (), profile_results, fingerprint)

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
            if not isinstance(value, expected_types):
                return STATE_INVALID, (f"input_type_invalid_{field_name}",)

        # NaN / Infinity detection for numeric fields.
        for numeric_field in ("provider_cost_limit", "token_limit"):
            if numeric_field in payload:
                value = payload[numeric_field]
                if isinstance(value, float) and not math.isfinite(value):
                    return STATE_INVALID, ("input_invalid_number",)

        # dataset_hash must be a valid SHA-256 hex string when present.
        if "dataset_hash" in payload:
            if not _is_valid_sha256_hex(payload["dataset_hash"]):
                return STATE_INVALID, ("input_type_invalid_dataset_hash",)

        # profiles must be a list when present.
        if "profiles" in payload and not isinstance(payload["profiles"], list):
            return STATE_INVALID, ("profiles_not_a_list",)

        return None

    # ------------------------------------------------------------------
    # Gate 2: Comparability
    # ------------------------------------------------------------------

    def _gate_comparability(
        self, input_obj: BenchmarkPreflightInput
    ) -> Optional[Tuple[str, Tuple[str, ...]]]:
        first = input_obj.profiles[0]
        # When any comparability field is empty, the appropriate ownership
        # gate (Dataset / Security / Budget) must produce the *missing
        # gap code. We therefore skip the mismatch check so the empty
        # surface is reported as ``*_missing`` rather than ``*_mismatch``.
        snapshot_refs = [p.corpus_snapshot_ref for p in input_obj.profiles]
        if all(snapshot_refs) and len(set(snapshot_refs)) != 1:
            return STATE_INCOMPARABLE, ("corpus_snapshot_mismatch",)

        for other in input_obj.profiles[1:]:
            if first.case_set_ref and other.case_set_ref and \
                    first.case_set_ref != other.case_set_ref:
                return STATE_INCOMPARABLE, ("case_set_mismatch",)
            if first.dataset_version and other.dataset_version and \
                    first.dataset_version != other.dataset_version:
                return STATE_INCOMPARABLE, ("dataset_version_mismatch",)
            if first.security_epoch and other.security_epoch and \
                    first.security_epoch != other.security_epoch:
                return STATE_INCOMPARABLE, ("security_epoch_mismatch",)
            if first.budget_policy_ref and other.budget_policy_ref and \
                    first.budget_policy_ref != other.budget_policy_ref:
                return STATE_INCOMPARABLE, ("budget_policy_mismatch",)

        if input_obj.case_set_ref and first.case_set_ref and \
                input_obj.case_set_ref != first.case_set_ref:
            return STATE_INCOMPARABLE, ("case_set_mismatch",)
        if input_obj.dataset_version and first.dataset_version and \
                input_obj.dataset_version != first.dataset_version:
            return STATE_INCOMPARABLE, ("dataset_version_mismatch",)
        if input_obj.security_epoch and first.security_epoch and \
                input_obj.security_epoch != first.security_epoch:
            return STATE_INCOMPARABLE, ("security_epoch_mismatch",)
        if input_obj.budget_policy_ref and first.budget_policy_ref and \
                input_obj.budget_policy_ref != first.budget_policy_ref:
            return STATE_INCOMPARABLE, ("budget_policy_mismatch",)

        return None

    # ------------------------------------------------------------------
    # Gate 3: Governance
    # ------------------------------------------------------------------

    def _gate_governance(
        self, input_obj: BenchmarkPreflightInput
    ) -> Optional[Tuple[str, Tuple[str, ...], Tuple[ProfilePreflightResult, ...]]]:
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
    # Gate 4: Dataset and Snapshot
    # ------------------------------------------------------------------

    def _gate_dataset(
        self, input_obj: BenchmarkPreflightInput
    ) -> Optional[Tuple[str, Tuple[str, ...], Tuple[ProfilePreflightResult, ...]]]:
        gaps: List[str] = []
        if not input_obj.case_set_ref:
            gaps.append("case_set_ref_missing")
        if not input_obj.dataset_version:
            gaps.append("dataset_version_missing")
        if not input_obj.dataset_hash:
            gaps.append("dataset_hash_missing")
        if input_obj.candidate_count <= 0:
            gaps.append("candidate_count_invalid")
        snapshot_refs = [p.corpus_snapshot_ref for p in input_obj.profiles]
        if any(not s for s in snapshot_refs):
            gaps.append("corpus_snapshot_missing")
        if gaps:
            return STATE_BLOCKED, tuple(gaps), ()
        return None

    # ------------------------------------------------------------------
    # Gate 5: Gold Evidence Firewall
    # ------------------------------------------------------------------

    def _gate_gold_firewall(
        self, input_obj: BenchmarkPreflightInput
    ) -> Optional[Tuple[str, Tuple[str, ...], Tuple[ProfilePreflightResult, ...]]]:
        if input_obj.runtime_request_schema_gold_free is not True:
            return STATE_BLOCKED, ("gold_firewall_not_proven",), ()
        return None

    # ------------------------------------------------------------------
    # Gate 6: Runtime
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
            if not profile.runtime_name:
                gaps.append("runtime_name_missing")
            if not profile.runtime_version:
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
                        profile_name=profile.profile_name,
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
                        profile_name=profile.profile_name,
                        state=STATE_READY,
                        gap_codes=(),
                    )
                )

        if global_gaps:
            return STATE_BLOCKED, tuple(global_gaps), tuple(per_profile)
        return None

    # ------------------------------------------------------------------
    # Gate 7: Security
    # ------------------------------------------------------------------

    def _gate_security(
        self, input_obj: BenchmarkPreflightInput
    ) -> Optional[Tuple[str, Tuple[str, ...], Tuple[ProfilePreflightResult, ...]]]:
        gaps: List[str] = []
        if not input_obj.authorization_ref:
            gaps.append("authorization_ref_missing")
        if not input_obj.security_epoch:
            gaps.append("security_epoch_missing")
        if input_obj.security_epoch_stale is not False:
            gaps.append("security_epoch_stale")
        if input_obj.formal_execution_approved is not True:
            gaps.append("formal_execution_not_approved")
        if gaps:
            return STATE_BLOCKED, tuple(gaps), ()
        return None

    # ------------------------------------------------------------------
    # Gate 8: Budget
    # ------------------------------------------------------------------

    def _gate_budget(
        self, input_obj: BenchmarkPreflightInput
    ) -> Optional[Tuple[str, Tuple[str, ...], Tuple[ProfilePreflightResult, ...]]]:
        gaps: List[str] = []
        if input_obj.human_budget_approved is not True:
            gaps.append("human_budget_not_approved")
        if not input_obj.budget_policy_ref:
            gaps.append("budget_policy_ref_missing")
        if (
            not _is_finite_real(input_obj.provider_cost_limit)
            or input_obj.provider_cost_limit <= 0
        ):
            gaps.append("provider_cost_limit_invalid")
        if input_obj.token_limit <= 0:
            gaps.append("token_limit_invalid")
        if not input_obj.deadline:
            gaps.append("deadline_missing")
        if gaps:
            return STATE_BLOCKED, tuple(gaps), ()
        return None

    # ------------------------------------------------------------------
    # Gate 9: Credentials and Formal Execution
    # ------------------------------------------------------------------

    def _gate_credentials(
        self, input_obj: BenchmarkPreflightInput
    ) -> Optional[Tuple[str, Tuple[str, ...], Tuple[ProfilePreflightResult, ...]]]:
        gaps: List[str] = []
        if not input_obj.credential_ref:
            gaps.append("credential_ref_missing")
        if input_obj.has_formal_credentials is not True:
            gaps.append("formal_credentials_missing")
        if input_obj.formal_execution_requested is not True:
            gaps.append("formal_execution_not_requested")
        if gaps:
            return STATE_BLOCKED, tuple(gaps), ()
        return None

    # ------------------------------------------------------------------
    # Gate 10: Output Contract
    # ------------------------------------------------------------------

    def _gate_output_contract(
        self, input_obj: BenchmarkPreflightInput
    ) -> Optional[Tuple[str, Tuple[str, ...], Tuple[ProfilePreflightResult, ...]]]:
        if not input_obj.output_artifact_ref:
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


def evaluate_payload(payload: Mapping[str, Any]) -> BenchmarkPreflightReport:
    """Convenience wrapper around :class:`BenchmarkPreflightEvaluator`."""

    return BenchmarkPreflightEvaluator().evaluate(payload)


__all__ = [
    "CONTRACT_VERSION",
    "CANONICAL_PROFILES",
    "STATE_READY",
    "STATE_BLOCKED",
    "STATE_INCOMPARABLE",
    "STATE_INVALID",
    "LEGAL_STATES",
    "ProfilePreflightInput",
    "BenchmarkPreflightInput",
    "ProfilePreflightResult",
    "BenchmarkPreflightReport",
    "BenchmarkPreflightEvaluator",
    "evaluate_payload",
    "report_to_dict",
    "compute_input_fingerprint",
]
