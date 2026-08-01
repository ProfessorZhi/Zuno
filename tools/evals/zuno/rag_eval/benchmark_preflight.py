"""PHASE22 Benchmark Preflight Contract.

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

* ``READY``       — contract satisfied; benchmark may be requested
* ``BLOCKED``     — required governance / runtime / security / budget /
                    credential surfaces are missing
* ``INCOMPARABLE``— the four canonical profiles disagree on case set,
                    snapshot, security epoch, or budget policy
* ``INVALID``     — input structure, profile set, or field type is illegal

The evaluator strictly enforces the documented gate priority so that
lower-priority failures can never be masked by later successes.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Mapping, Optional, Tuple


CONTRACT_VERSION = "phase22-benchmark-preflight.v1"

# Fixed canonical profile set. Order is the serialisation order.
CANONICAL_PROFILES: Tuple[str, ...] = (
    "standard_rag",
    "local_graphrag",
    "deep_graphrag",
    "agentic_graphrag",
)

# State constants. These are the only legal states for the evaluator.
STATE_READY = "READY"
STATE_BLOCKED = "BLOCKED"
STATE_INCOMPARABLE = "INCOMPARABLE"
STATE_INVALID = "INVALID"

LEGAL_STATES = frozenset(
    {STATE_READY, STATE_BLOCKED, STATE_INCOMPARABLE, STATE_INVALID}
)

# Top-level required fields on ``BenchmarkPreflightInput``.
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

# Required fields on each ``ProfilePreflightInput``.
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

# Top-level field type expectations. ``None`` indicates "any type is fine".
_TOP_FIELD_TYPES: Dict[str, Tuple[type, ...]] = {
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


# ---------------------------------------------------------------------------
# Input dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProfilePreflightInput:
    """Declared preflight surface for a single canonical profile.

    This is a *contractual* view. The evaluator only inspects the upstream
    attestations; it never touches the actual runtime objects.
    """

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


# ---------------------------------------------------------------------------
# Output dataclasses
# ---------------------------------------------------------------------------


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
    """Return True for a finite real number (int or float, not NaN/Inf)."""

    if isinstance(value, bool):  # bool is a subclass of int — disallow
        return False
    if isinstance(value, int):
        return True
    if isinstance(value, float):
        return math.isfinite(value)
    return False


def _canonical_sha256_hex(value: Any) -> str:
    """Deterministic SHA-256 over a canonical JSON encoding of ``value``.

    Keys are sorted and separators are fixed so that two semantically
    identical inputs always yield the same digest.
    """

    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _normalise_profiles(
    profiles: Any,
) -> Tuple[Optional[Tuple[ProfilePreflightInput, ...]], Optional[str]]:
    """Validate and freeze the profile list.

    Returns a tuple of ``ProfilePreflightInput`` on success, or ``(None,
    gap_code)`` on failure. The gap codes match the documented profile-set
    surface. Field-level type errors are reported as
    ``profile_invalid_<profile_name>``.
    """

    if not isinstance(profiles, list):
        return None, "profiles_not_a_list"

    seen: List[str] = []
    parsed: List[ProfilePreflightInput] = []
    seen_set: set = set()

    for idx, item in enumerate(profiles):
        if not isinstance(item, Mapping):
            return None, "profile_invalid_entry"

        profile_name = item.get("profile_name")
        if not isinstance(profile_name, str):
            return None, "profile_invalid_entry"

        if profile_name in seen_set:
            return None, "profile_duplicate"
        seen_set.add(profile_name)
        seen.append(profile_name)

        missing = [f for f in REQUIRED_PROFILE_FIELDS if f not in item]
        if missing:
            return None, f"profile_invalid_{profile_name}"

        for field_name in REQUIRED_PROFILE_FIELDS:
            value = item[field_name]
            if field_name == "index_runtime_available":
                if not isinstance(value, bool):
                    return None, f"profile_invalid_{profile_name}"
            elif field_name == "agent_run_runtime_available":
                if not isinstance(value, bool):
                    return None, f"profile_invalid_{profile_name}"
            elif field_name in {
                "product_runtime_attested",
                "formal_adapter_wired",
                "knowledge_runtime_available",
                "trace_adapter_available",
                "result_store_available",
                "artifact_store_available",
                "usage_receipt_provider_available",
                "budget_settlement_provider_available",
            }:
                if not isinstance(value, bool):
                    return None, f"profile_invalid_{profile_name}"
            else:
                if not isinstance(value, str):
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
                product_runtime_attested=item[
                    "product_runtime_attested"
                ],
                formal_adapter_wired=item["formal_adapter_wired"],
                knowledge_runtime_available=item[
                    "knowledge_runtime_available"
                ],
                index_runtime_available=item["index_runtime_available"],
                agent_run_runtime_available=item[
                    "agent_run_runtime_available"
                ],
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

    # Detect unknown / extra profiles and missing profiles.
    canonical_set = frozenset(CANONICAL_PROFILES)
    seen_set_frozen = frozenset(seen)
    if seen_set_frozen != canonical_set:
        # 1. Unknown / extra profiles take precedence over missing ones
        #    so the gap code is unambiguous.
        extra = [p for p in seen if p not in canonical_set]
        if extra:
            return None, "profile_unknown"
        missing = [p for p in CANONICAL_PROFILES if p not in seen_set_frozen]
        if missing:
            return None, "profile_set_missing_" + missing[0]
        # Same set but with duplicates / wrong multiplicity was caught above.
        return None, "profile_unknown"

    # Order the parsed profiles by canonical order so that output is stable
    # regardless of the input order.
    by_name = {p.profile_name: p for p in parsed}
    ordered = tuple(by_name[name] for name in CANONICAL_PROFILES)
    return ordered, None


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------


class BenchmarkPreflightEvaluator:
    """Deterministic, read-only PHASE22 benchmark preflight evaluator."""

    def evaluate(
        self, payload: Mapping[str, Any]
    ) -> BenchmarkPreflightReport:
        gate1 = self._gate_input_structure(payload)
        if gate1 is not None:
            return self._build_report(gate1[0], gate1[1], ())

        # Re-parse the frozen input from the validated payload.
        input_obj, parse_error = self._coerce_input(payload)
        if parse_error is not None:
            return self._build_report(STATE_INVALID, (parse_error,), ())
        assert input_obj is not None  # for type-checkers

        # Gate 2: profile set
        gate2 = self._gate_profile_set(input_obj.profiles)
        if gate2 is not None:
            return self._build_report(gate2[0], gate2[1], ())

        # Gate 3: comparability
        gate3 = self._gate_comparability(input_obj)
        if gate3 is not None:
            return self._build_report(gate3[0], gate3[1], ())

        # Gates 4..11
        # Each gate either returns ``None`` (passed) or a tuple
        # ``(state, gap_codes, profile_results)``. Once any gate fails we
        # MUST short-circuit so that later successes cannot mask earlier
        # failures.
        for gate in (
            lambda: self._gate_governance(input_obj),
            lambda: self._gate_dataset_snapshot(input_obj),
            lambda: self._gate_gold_firewall(input_obj),
            lambda: self._gate_runtime(input_obj),
            lambda: self._gate_security(input_obj),
            lambda: self._gate_budget(input_obj),
            lambda: self._gate_credentials(input_obj),
            lambda: self._gate_output_contract(input_obj),
        ):
            verdict = gate()
            if verdict is not None:
                state, gaps, profiles = verdict
                return self._build_report(state, gaps, profiles)

        # All gates passed.
        profile_results = tuple(
            ProfilePreflightResult(
                profile_name=p.profile_name,
                state=STATE_READY,
                gap_codes=(),
            )
            for p in input_obj.profiles
        )
        fingerprint = self.fingerprint(input_obj)
        return BenchmarkPreflightReport(
            state=STATE_READY,
            gap_codes=(),
            profile_results=profile_results,
            input_fingerprint=fingerprint,
            contract_version=CONTRACT_VERSION,
        )

    # ------------------------------------------------------------------
    # Gate 1: Input structure
    # ------------------------------------------------------------------

    def _gate_input_structure(
        self, payload: Mapping[str, Any]
    ) -> Optional[Tuple[str, Tuple[str, ...]]]:
        if not isinstance(payload, Mapping):
            return STATE_INVALID, ("input_not_object",)

        unknown = [k for k in payload.keys() if k not in REQUIRED_TOP_FIELDS]
        if unknown:
            return STATE_INVALID, ("input_unknown_field",)

        for field_name, expected_types in _TOP_FIELD_TYPES.items():
            if field_name not in payload:
                return STATE_INVALID, (f"input_missing_{field_name}",)
            value = payload[field_name]
            if not isinstance(value, expected_types):
                return STATE_INVALID, (f"input_type_invalid_{field_name}",)

            # Numeric sanity checks.
        candidate_count = payload["candidate_count"]
        if isinstance(candidate_count, bool) or not isinstance(
            candidate_count, int
        ) or candidate_count <= 0:
            return STATE_INVALID, ("input_type_invalid_candidate_count",)

        cost_limit = payload["provider_cost_limit"]
        if not _is_finite_real(cost_limit) or cost_limit <= 0:
            return STATE_INVALID, ("input_type_invalid_provider_cost_limit",)

        token_limit = payload["token_limit"]
        if (
            isinstance(token_limit, bool)
            or not isinstance(token_limit, int)
            or token_limit <= 0
        ):
            return STATE_INVALID, ("input_type_invalid_token_limit",)

        deadline = payload["deadline"]
        if not isinstance(deadline, str) or not deadline:
            return STATE_INVALID, ("input_type_invalid_deadline",)

        dataset_hash = payload["dataset_hash"]
        if (
            not isinstance(dataset_hash, str)
            or not _is_valid_sha256_hex(dataset_hash)
        ):
            return STATE_INVALID, ("input_type_invalid_dataset_hash",)

        # Authorise the profile list before doing any deeper gate work.
        parsed_profiles, profile_error = _normalise_profiles(
            payload["profiles"]
        )
        if profile_error is not None:
            return STATE_INVALID, (profile_error,)

        # Make sure the raw booleans / strings are also well-typed.
        for f in (
            "reviewer_status",
            "license_status",
            "integrity_status",
            "authorization_ref",
            "security_epoch",
            "budget_policy_ref",
            "credential_ref",
            "output_artifact_ref",
            "eval_run_id",
            "case_set_ref",
            "dataset_version",
        ):
            value = payload[f]
            if not isinstance(value, str) or not value:
                return STATE_INVALID, (f"input_type_invalid_{f}",)

        for f in (
            "benchmark_eligible",
            "runtime_request_schema_gold_free",
            "security_epoch_stale",
            "formal_execution_approved",
            "human_budget_approved",
            "has_formal_credentials",
            "formal_execution_requested",
        ):
            if not isinstance(payload[f], bool):
                return STATE_INVALID, (f"input_type_invalid_{f}",)

        return None

    # ------------------------------------------------------------------
    # Gate 2: Profile set
    # ------------------------------------------------------------------

    def _gate_profile_set(
        self, profiles: Tuple[ProfilePreflightInput, ...]
    ) -> Optional[Tuple[str, Tuple[str, ...]]]:
        if not profiles:
            return STATE_INVALID, ("profiles_empty",)

        names = [p.profile_name for p in profiles]
        if len(names) != len(CANONICAL_PROFILES):
            return STATE_INVALID, ("profile_set_missing_standard_rag",)
        if len(set(names)) != len(names):
            return STATE_INVALID, ("profile_duplicate",)
        if set(names) != set(CANONICAL_PROFILES):
            for name in names:
                if name not in CANONICAL_PROFILES:
                    return STATE_INVALID, ("profile_unknown",)
            # Missing members.
            for canonical in CANONICAL_PROFILES:
                if canonical not in names:
                    return STATE_INVALID, (
                        "profile_set_missing_" + canonical
                    )
        return None

    # ------------------------------------------------------------------
    # Gate 3: Comparability
    # ------------------------------------------------------------------

    def _gate_comparability(
        self, input_obj: BenchmarkPreflightInput
    ) -> Optional[Tuple[str, Tuple[str, ...]]]:
        first = input_obj.profiles[0]
        comparability_keys = (
            "case_set_ref",
            "dataset_version",
            "security_epoch",
            "budget_policy_ref",
        )
        # For corpus_snapshot_ref, emptiness is a "missing" (BLOCKED via
        # the Dataset gate) not a "mismatch" (INCOMPARABLE). We skip the
        # mismatch check when any snapshot is empty so the Dataset gate
        # can produce the documented gap code.
        snapshot_refs = [p.corpus_snapshot_ref for p in input_obj.profiles]
        if all(snapshot_refs) and len(set(snapshot_refs)) != 1:
            return STATE_INCOMPARABLE, ("corpus_snapshot_mismatch",)

        for other in input_obj.profiles[1:]:
            for key in comparability_keys:
                if getattr(first, key) != getattr(other, key):
                    if key == "case_set_ref":
                        gap = "case_set_mismatch"
                    elif key == "dataset_version":
                        gap = "dataset_version_mismatch"
                    elif key == "security_epoch":
                        gap = "security_epoch_mismatch"
                    elif key == "budget_policy_ref":
                        gap = "budget_policy_mismatch"
                    else:
                        gap = f"comparability_{key}_mismatch"
                    return STATE_INCOMPARABLE, (gap,)

        # Also compare the top-level case_set_ref / dataset_version /
        # security_epoch / budget_policy_ref.
        if input_obj.case_set_ref != first.case_set_ref:
            return STATE_INCOMPARABLE, ("case_set_mismatch",)
        if input_obj.dataset_version != first.dataset_version:
            return STATE_INCOMPARABLE, ("dataset_version_mismatch",)
        if input_obj.security_epoch != first.security_epoch:
            return STATE_INCOMPARABLE, ("security_epoch_mismatch",)
        if input_obj.budget_policy_ref != first.budget_policy_ref:
            return STATE_INCOMPARABLE, ("budget_policy_mismatch",)

        return None

    # ------------------------------------------------------------------
    # Gate 4: Governance
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
    # Gate 5: Dataset and snapshot
    # ------------------------------------------------------------------

    def _gate_dataset_snapshot(
        self, input_obj: BenchmarkPreflightInput
    ) -> Optional[Tuple[str, Tuple[str, ...], Tuple[ProfilePreflightResult, ...]]]:
        gaps: List[str] = []
        if not input_obj.case_set_ref:
            gaps.append("case_set_ref_missing")
        if not input_obj.dataset_version:
            gaps.append("dataset_version_missing")
        if not _is_valid_sha256_hex(input_obj.dataset_hash):
            gaps.append("dataset_hash_invalid")
        if input_obj.candidate_count <= 0:
            gaps.append("candidate_count_invalid")

        snapshot_refs = {
            p.corpus_snapshot_ref for p in input_obj.profiles
        }
        if not snapshot_refs or any(not s for s in snapshot_refs):
            gaps.append("corpus_snapshot_missing")
        elif len(snapshot_refs) != 1:
            gaps.append("corpus_snapshot_mismatch")

        if gaps:
            return STATE_BLOCKED, tuple(gaps), ()
        return None

    # ------------------------------------------------------------------
    # Gate 6: Gold evidence firewall
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

            # Profile-specific runtime ports.
            if profile.profile_name == "local_graphrag":
                if profile.index_runtime_available is not True:
                    gaps.append("index_runtime_unavailable")
            elif profile.profile_name == "agentic_graphrag":
                if profile.agent_run_runtime_available is not True:
                    gaps.append("agent_run_runtime_unavailable")

            if gaps:
                # Per-profile gaps are reported as the profile's gap_codes.
                # Global gaps duplicate these per profile so the top-level
                # gap_codes stays useful for one-line consumers.
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
    # Gate 8: Security
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
    # Gate 9: Budget
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
        if (
            isinstance(input_obj.token_limit, bool)
            or not isinstance(input_obj.token_limit, int)
            or input_obj.token_limit <= 0
        ):
            gaps.append("token_limit_invalid")
        if not input_obj.deadline:
            gaps.append("deadline_missing")
        if gaps:
            return STATE_BLOCKED, tuple(gaps), ()
        return None

    # ------------------------------------------------------------------
    # Gate 10: Credentials and formal execution
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
    # Gate 11: Output contract
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

    def _build_report(
        self,
        state: str,
        gap_codes: Tuple[str, ...],
        profile_results: Tuple[ProfilePreflightResult, ...],
    ) -> BenchmarkPreflightReport:
        # When we fail before the runtime gate, profile_results is empty;
        # synthesise an empty tuple so the report contract is uniform.
        normalised_profiles: Tuple[ProfilePreflightResult, ...] = (
            profile_results
        )
        if state == STATE_READY:
            fingerprint = self.fingerprint_from_state(state, gap_codes, ())
        else:
            fingerprint = self.fingerprint_from_state(
                state, gap_codes, normalised_profiles
            )
        return BenchmarkPreflightReport(
            state=state,
            gap_codes=gap_codes,
            profile_results=normalised_profiles,
            input_fingerprint=fingerprint,
            contract_version=CONTRACT_VERSION,
        )

    # ------------------------------------------------------------------
    # Coercion (only called after Gate 1 passed)
    # ------------------------------------------------------------------

    def _coerce_input(
        self, payload: Mapping[str, Any]
    ) -> Tuple[Optional[BenchmarkPreflightInput], Optional[str]]:
        parsed_profiles, profile_error = _normalise_profiles(
            payload["profiles"]
        )
        if profile_error is not None or parsed_profiles is None:
            return None, profile_error

        try:
            input_obj = BenchmarkPreflightInput(
                eval_run_id=payload["eval_run_id"],
                case_set_ref=payload["case_set_ref"],
                dataset_version=payload["dataset_version"],
                dataset_hash=payload["dataset_hash"],
                candidate_count=payload["candidate_count"],
                reviewer_status=payload["reviewer_status"],
                benchmark_eligible=payload["benchmark_eligible"],
                license_status=payload["license_status"],
                integrity_status=payload["integrity_status"],
                runtime_request_schema_gold_free=payload[
                    "runtime_request_schema_gold_free"
                ],
                authorization_ref=payload["authorization_ref"],
                security_epoch=payload["security_epoch"],
                security_epoch_stale=payload["security_epoch_stale"],
                formal_execution_approved=payload[
                    "formal_execution_approved"
                ],
                human_budget_approved=payload["human_budget_approved"],
                budget_policy_ref=payload["budget_policy_ref"],
                provider_cost_limit=float(payload["provider_cost_limit"]),
                token_limit=payload["token_limit"],
                deadline=payload["deadline"],
                credential_ref=payload["credential_ref"],
                has_formal_credentials=payload["has_formal_credentials"],
                formal_execution_requested=payload[
                    "formal_execution_requested"
                ],
                output_artifact_ref=payload["output_artifact_ref"],
                profiles=parsed_profiles,
            )
        except (TypeError, ValueError):
            return None, "input_construction_failed"
        return input_obj, None

    # ------------------------------------------------------------------
    # Fingerprint
    # ------------------------------------------------------------------

    def fingerprint(self, input_obj: BenchmarkPreflightInput) -> str:
        canonical = {
            "contract_version": CONTRACT_VERSION,
            "eval_run_id": input_obj.eval_run_id,
            "case_set_ref": input_obj.case_set_ref,
            "dataset_version": input_obj.dataset_version,
            "dataset_hash": input_obj.dataset_hash,
            "candidate_count": input_obj.candidate_count,
            "reviewer_status": input_obj.reviewer_status,
            "benchmark_eligible": input_obj.benchmark_eligible,
            "license_status": input_obj.license_status,
            "integrity_status": input_obj.integrity_status,
            "runtime_request_schema_gold_free": (
                input_obj.runtime_request_schema_gold_free
            ),
            "authorization_ref": input_obj.authorization_ref,
            "security_epoch": input_obj.security_epoch,
            "security_epoch_stale": input_obj.security_epoch_stale,
            "formal_execution_approved": (
                input_obj.formal_execution_approved
            ),
            "human_budget_approved": input_obj.human_budget_approved,
            "budget_policy_ref": input_obj.budget_policy_ref,
            "provider_cost_limit": input_obj.provider_cost_limit,
            "token_limit": input_obj.token_limit,
            "deadline": input_obj.deadline,
            "credential_ref": input_obj.credential_ref,
            "has_formal_credentials": input_obj.has_formal_credentials,
            "formal_execution_requested": (
                input_obj.formal_execution_requested
            ),
            "output_artifact_ref": input_obj.output_artifact_ref,
            "profiles": [
                {
                    "profile_name": p.profile_name,
                    "case_set_ref": p.case_set_ref,
                    "dataset_version": p.dataset_version,
                    "corpus_snapshot_ref": p.corpus_snapshot_ref,
                    "security_epoch": p.security_epoch,
                    "budget_policy_ref": p.budget_policy_ref,
                    "runtime_name": p.runtime_name,
                    "runtime_version": p.runtime_version,
                    "product_runtime_attested": (
                        p.product_runtime_attested
                    ),
                    "formal_adapter_wired": p.formal_adapter_wired,
                    "knowledge_runtime_available": (
                        p.knowledge_runtime_available
                    ),
                    "index_runtime_available": p.index_runtime_available,
                    "agent_run_runtime_available": (
                        p.agent_run_runtime_available
                    ),
                    "trace_adapter_available": p.trace_adapter_available,
                    "result_store_available": p.result_store_available,
                    "artifact_store_available": (
                        p.artifact_store_available
                    ),
                    "usage_receipt_provider_available": (
                        p.usage_receipt_provider_available
                    ),
                    "budget_settlement_provider_available": (
                        p.budget_settlement_provider_available
                    ),
                }
                for p in input_obj.profiles
            ],
        }
        return _canonical_sha256_hex(canonical)

    def fingerprint_from_state(
        self,
        state: str,
        gap_codes: Tuple[str, ...],
        profile_results: Tuple[ProfilePreflightResult, ...],
    ) -> str:
        canonical = {
            "contract_version": CONTRACT_VERSION,
            "state": state,
            "gap_codes": list(gap_codes),
            "profile_results": [
                {
                    "profile_name": p.profile_name,
                    "state": p.state,
                    "gap_codes": list(p.gap_codes),
                }
                for p in profile_results
            ],
        }
        return _canonical_sha256_hex(canonical)


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def _is_valid_sha256_hex(value: str) -> bool:
    if not isinstance(value, str):
        return False
    if len(value) != 64:
        return False
    for ch in value:
        if not ("0" <= ch <= "9" or "a" <= ch <= "f" or "A" <= ch <= "F"):
            return False
    return True


def report_to_dict(report: BenchmarkPreflightReport) -> Dict[str, Any]:
    """Serialise a :class:`BenchmarkPreflightReport` into a stable dict.

    Key order is fixed so that two semantically identical reports always
    byte-format identically. The schema is::

        {
            "contract_version": str,
            "state": str,
            "gap_codes": [str, ...],
            "profile_results": [
                {"profile_name": str, "state": str, "gap_codes": [str, ...]},
                ...
            ],
            "input_fingerprint": str,
        }
    """

    out: Dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
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
    return out


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
]
