"""PHASE22 Runtime Evidence Binding Contract (validation only).

This module implements a deterministic, fail-closed, validation-only contract
that binds a claimed Product Runtime execution to its serialized evidence.

Problem
-------
The eval layer must not believe that a formal Product Runtime execution
happened merely because a runtime returned some fields.  Formal runtime
evidence must prove and bind:

- Eval Run / Case / Requested Profile / Actual Profile
- Runtime Name / Runtime Version
- Corpus Snapshot / Trace
- SecurityDecision / PlanVersion / RunOutcome
- UsageReceipt / BudgetSettlement / ArtifactReceipt
- Result Payload / Receipt Owner / Payload Hash / Reference Binding Hash

This module only VALIDATES a binding.  It never creates a Product Runtime,
never calls a model or an external service, never generates a receipt, never
auto-completes missing evidence, and never returns RUNTIME_OBSERVED or
MEASURED.

Contract boundaries
-------------------
- The validator accepts only serialized evidence (a Mapping) or the immutable
  :class:`RuntimeEvidenceBinding` instance of this module.  It does NOT accept
  runtime objects and it never trusts declarations such as
  ``is_test_double = false`` or ``__zuno_product_authority__ = ...``.
- Unknown keys on the top-level binding or on a receipt are ignored: they are
  not validated and they never enter the reference binding hash.  A runtime
  may claim anything it wants; only the canonical fields below are bound.
- ``tenant_id`` / ``workspace_id`` are optional.  When explicitly present in
  the serialized input they must be non-empty; when absent they are not part
  of the binding.  No default tenant/workspace/snapshot is invented.
- The validator never mutates its input and never writes a hash back.

Validation priority
-------------------
Stages run in the fixed priority order below.  Every stage that is safe to
evaluate runs; gap codes are returned in stage order, then in within-stage
order.  The result state is the state of the highest-priority failing stage,
or VALID when no stage fails.

1.  Input Structure        -> INVALID
2.  Identity               -> INVALID
3.  Profile                -> INVALID or INCOMPARABLE
4.  Runtime Identity       -> BLOCKED
5.  Snapshot               -> BLOCKED
6.  Required Receipts      -> BLOCKED
7.  Receipt Owner          -> BLOCKED
8.  Runtime Version Consis -> BLOCKED
9.  Snapshot Consistency   -> BLOCKED
10. Payload Hash Format    -> INVALID
11. Receipt Ref Binding    -> BLOCKED
12. Reference Binding Hash -> BLOCKED

Gap codes are stable lowercase snake_case strings, ordered, machine readable,
never contain secrets, never contain full input values, and are deterministic
for the same input.

Consistency comparisons (stages 8 and 9) are skipped when the top-level
runtime version or corpus snapshot is empty (that missing value is already
reported by stages 4/5, so comparing receipts against "" would only add
noise).  For ``local_graphrag`` the artifact receipt snapshot is validated by
the dedicated index-snapshot coverage check in stage 6 and is not
double-reported by stage 9.

Profiles
--------
Only ``standard_rag``, ``local_graphrag``, ``deep_graphrag`` and
``agentic_graphrag`` are accepted.  Unknown profiles are INVALID;
requested != actual is INCOMPARABLE.

Required receipts per profile (exact minimum; extra known receipt types are
allowed only when they are fully bound one-to-one with a non-empty top-level
reference):

- standard_rag / local_graphrag / deep_graphrag: security_decision, trace,
  usage_receipt, budget_settlement, artifact_receipt.
  PlanVersion / RunOutcome are NOT forced for these profiles (the repository
  contract provides no evidence that they are mandatory for deep_graphrag).
- agentic_graphrag: security_decision, plan_version, run_outcome,
  usage_receipt, budget_settlement, trace, artifact_receipt.

For ``local_graphrag`` the graph index is covered by the top-level binding:
the artifact receipt must carry the same snapshot as the top-level
``corpus_snapshot_ref``.  No separate "index" receipt type exists and none is
invented.

Hash contract
-------------
``compute_reference_binding_hash`` uses only the Python standard library:
canonical JSON (``sort_keys=True``, stable separators ``(",", ":")``,
UTF-8), SHA-256, output is lowercase 64-char hex.  Field insertion order does
not affect the result; any bound field change changes the result.  Receipts
are sorted by ``(receipt_type, receipt_ref)`` so receipt list order does not
affect the hash.  The canonical payload contains no secret, no token, no
expected answer, no gold document / gold evidence, and no citation ground
truth.  The validator only verifies a provided ``reference_binding_hash``;
it never writes one back.

Exception semantics
-------------------
The validator never raises on malformed input: wrong types, missing fields,
illegal collections, illegal hashes, duplicate receipts and unknown receipt
types are returned as stable INVALID / BLOCKED / INCOMPARABLE results.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping

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


def _is_sha256_hex(value: str) -> bool:
    return len(value) == 64 and all(c in _SHA256_HEX_CHARS for c in value)


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
    """Immutable serialized receipt evidence bound to a runtime evidence record."""

    receipt_type: str
    receipt_ref: str
    owner: str
    runtime_version: str
    snapshot_ref: str
    payload_hash: str


@dataclass(frozen=True, slots=True)
class RuntimeEvidenceBinding:
    """Immutable runtime evidence binding record.

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
        """Build an immutable binding from a serialized mapping.

        Unknown keys are ignored.  Raises ValueError if a required key is
        missing or has the wrong type; callers that must never raise (the
        validator) perform their structural checks before calling this.
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


def compute_reference_binding_hash(
    binding: RuntimeEvidenceBinding | Mapping[str, Any],
) -> str:
    """Compute the reference binding hash (SHA-256, lowercase 64 hex).

    Accepts an immutable :class:`RuntimeEvidenceBinding` or a serialized
    mapping.  For a mapping, unknown keys are ignored and missing or
    mistyped required keys raise ValueError.

    Deterministic: canonical JSON with ``sort_keys=True`` and stable
    separators ``(",", ":")`` encoded as UTF-8, hashed with SHA-256.  Field
    insertion order and receipt list order do not affect the result; any
    change to a bound field changes the result.
    """
    if isinstance(binding, Mapping):
        binding = RuntimeEvidenceBinding.from_dict(binding)
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

    Never raises on malformed input and never mutates its input.  Stages run
    in the fixed priority order documented in the module docstring; gap codes
    are returned in stage order and state is the highest-priority failing
    stage's state.
    """

    # -- Stage 1: Input Structure (INVALID) ---------------------------------

    def _check_input_structure(self, data: Mapping[str, Any]) -> tuple[str, ...]:
        gaps: list[str] = []
        for name in _TOP_LEVEL_REQUIRED_FIELDS:
            if name not in data:
                gaps.append(f"input_field_missing:{name}")
            elif name == "receipts":
                if not isinstance(data[name], (list, tuple)):
                    gaps.append("input_field_wrong_type:receipts")
            elif not isinstance(data[name], str):
                gaps.append(f"input_field_wrong_type:{name}")
        for name in _OPTIONAL_TOP_LEVEL_FIELDS:
            if name in data and not isinstance(data[name], str):
                gaps.append(f"input_field_wrong_type:{name}")
        receipts = data.get("receipts")
        if isinstance(receipts, (list, tuple)):
            for item in receipts:
                if not isinstance(item, Mapping):
                    gaps.append("input_receipt_not_mapping")
                    continue
                for name in _RECEIPT_REQUIRED_FIELDS:
                    if name not in item:
                        gaps.append(f"receipt_field_missing:{name}")
                    elif not isinstance(item[name], str):
                        gaps.append(f"receipt_field_wrong_type:{name}")
        return tuple(gaps)

    # -- Stage 2: Identity (INVALID) ----------------------------------------

    def _check_identity(
        self,
        evidence: RuntimeEvidenceBinding,
        optional_present: frozenset[str],
    ) -> tuple[str, ...]:
        gaps: list[str] = []
        if not evidence.eval_run_id:
            gaps.append("eval_run_id_missing")
        if not evidence.case_id:
            gaps.append("case_id_missing")
        if "tenant_id" in optional_present and not evidence.tenant_id:
            gaps.append("tenant_id_empty")
        if "workspace_id" in optional_present and not evidence.workspace_id:
            gaps.append("workspace_id_empty")
        return tuple(gaps)

    # -- Stage 3: Profile (INVALID or INCOMPARABLE) -------------------------

    def _check_profile(
        self,
        evidence: RuntimeEvidenceBinding,
    ) -> tuple[tuple[str, ...], BindingValidationState]:
        gaps: list[str] = []
        if not evidence.requested_profile:
            gaps.append("requested_profile_missing")
        elif evidence.requested_profile not in ALLOWED_PROFILES:
            gaps.append("unknown_requested_profile")
        if not evidence.actual_profile:
            gaps.append("actual_profile_missing")
        elif evidence.actual_profile not in ALLOWED_PROFILES:
            gaps.append("unknown_actual_profile")
        requested_known = evidence.requested_profile in ALLOWED_PROFILES
        actual_known = evidence.actual_profile in ALLOWED_PROFILES
        if (
            requested_known
            and actual_known
            and evidence.requested_profile != evidence.actual_profile
        ):
            gaps.append("profile_mismatch")
        if gaps:
            state = (
                BindingValidationState.INCOMPARABLE
                if "profile_mismatch" in gaps
                else BindingValidationState.INVALID
            )
            return tuple(gaps), state
        return (), BindingValidationState.VALID

    # -- Stage 4: Runtime Identity (BLOCKED) --------------------------------

    def _check_runtime_identity(
        self, evidence: RuntimeEvidenceBinding
    ) -> tuple[str, ...]:
        gaps: list[str] = []
        if not evidence.runtime_name:
            gaps.append("runtime_name_missing")
        if not evidence.runtime_version:
            gaps.append("runtime_version_missing")
        return tuple(gaps)

    # -- Stage 5: Snapshot (BLOCKED) ----------------------------------------

    def _check_snapshot(self, evidence: RuntimeEvidenceBinding) -> tuple[str, ...]:
        gaps: list[str] = []
        if not evidence.corpus_snapshot_ref:
            gaps.append("corpus_snapshot_ref_missing")
        if not evidence.trace_id:
            gaps.append("trace_id_missing")
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
            if receipt_type != "trace" and not getattr(evidence, field):
                gaps.append(f"{field}_missing")
            if receipt_type not in by_type:
                gaps.append(_RECEIPT_MISSING_CODES[receipt_type])
        if (
            evidence.actual_profile == "local_graphrag"
            and "artifact_receipt" in by_type
        ):
            artifact = by_type["artifact_receipt"]
            if artifact.snapshot_ref != evidence.corpus_snapshot_ref:
                gaps.append("local_graphrag_index_snapshot_uncovered")
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
                gaps.append(f"receipt_owner_mismatch:{receipt.receipt_type}")
        return tuple(gaps)

    # -- Stage 8: Runtime Version Consistency (BLOCKED) ---------------------

    def _check_receipt_runtime_versions(
        self, evidence: RuntimeEvidenceBinding
    ) -> tuple[str, ...]:
        if not evidence.runtime_version:
            # The missing top-level version is reported by stage 4; comparing
            # receipts against "" would only add noise.
            return ()
        gaps: list[str] = []
        for receipt in evidence.receipts:
            if receipt.receipt_type not in RECEIPT_OWNERS:
                continue
            if receipt.runtime_version != evidence.runtime_version:
                gaps.append(
                    f"receipt_runtime_version_mismatch:{receipt.receipt_type}"
                )
        return tuple(gaps)

    # -- Stage 9: Snapshot Consistency (BLOCKED) ----------------------------

    def _check_receipt_snapshots(
        self, evidence: RuntimeEvidenceBinding
    ) -> tuple[str, ...]:
        if not evidence.corpus_snapshot_ref:
            # The missing top-level snapshot is reported by stage 5; comparing
            # receipts against "" would only add noise.
            return ()
        gaps: list[str] = []
        for receipt in evidence.receipts:
            if receipt.receipt_type not in RECEIPT_OWNERS:
                continue
            if (
                receipt.receipt_type == "artifact_receipt"
                and evidence.actual_profile == "local_graphrag"
            ):
                # The artifact receipt snapshot is the dedicated
                # local_graphrag index-snapshot coverage check in stage 6;
                # do not double-report it here.
                continue
            if receipt.snapshot_ref != evidence.corpus_snapshot_ref:
                gaps.append(f"receipt_snapshot_mismatch:{receipt.receipt_type}")
        return tuple(gaps)

    # -- Stage 10: Payload Hash Format (INVALID) ----------------------------

    def _check_payload_hash_formats(
        self, evidence: RuntimeEvidenceBinding
    ) -> tuple[str, ...]:
        gaps: list[str] = []
        if not _is_sha256_hex(evidence.artifact_payload_hash):
            gaps.append("artifact_payload_hash_invalid")
        if not _is_sha256_hex(evidence.result_payload_hash):
            gaps.append("result_payload_hash_invalid")
        if not evidence.reference_binding_hash:
            gaps.append("reference_binding_hash_missing")
        elif not _is_sha256_hex(evidence.reference_binding_hash):
            gaps.append("reference_binding_hash_invalid")
        for receipt in evidence.receipts:
            if receipt.receipt_type not in RECEIPT_OWNERS:
                continue
            if not _is_sha256_hex(receipt.payload_hash):
                gaps.append(
                    f"receipt_payload_hash_invalid:{receipt.receipt_type}"
                )
        return tuple(gaps)

    # -- Stage 11: Receipt Reference Binding (BLOCKED) ----------------------

    def _check_receipt_reference_binding(
        self, evidence: RuntimeEvidenceBinding
    ) -> tuple[str, ...]:
        gaps: list[str] = []
        seen_refs: set[str] = set()
        seen_types: set[str] = set()
        present_types = {r.receipt_type for r in evidence.receipts}
        for receipt in evidence.receipts:
            if not receipt.receipt_ref:
                gaps.append(f"receipt_ref_missing:{receipt.receipt_type}")
            if receipt.receipt_ref in seen_refs:
                gaps.append("receipt_ref_duplicate")
            if receipt.receipt_type in seen_types:
                gaps.append(f"receipt_type_duplicate:{receipt.receipt_type}")
            if receipt.receipt_type not in RECEIPT_OWNERS:
                gaps.append(f"unknown_receipt_type:{receipt.receipt_type}")
            else:
                field = REF_FIELD_BY_RECEIPT_TYPE[receipt.receipt_type]
                top_level_ref = getattr(evidence, field)
                if not top_level_ref:
                    gaps.append(f"receipt_ref_unbound:{receipt.receipt_type}")
                elif top_level_ref != receipt.receipt_ref:
                    gaps.append(f"receipt_ref_mismatch:{receipt.receipt_type}")
            seen_refs.add(receipt.receipt_ref)
            seen_types.add(receipt.receipt_type)
        for receipt_type in REF_FIELD_BY_RECEIPT_TYPE:
            field = REF_FIELD_BY_RECEIPT_TYPE[receipt_type]
            if getattr(evidence, field) and receipt_type not in present_types:
                gaps.append(f"{receipt_type}_ref_unbound")
        return tuple(gaps)

    # -- Stage 12: Reference Binding Hash (BLOCKED) -------------------------

    def _check_reference_binding_hash(
        self, evidence: RuntimeEvidenceBinding
    ) -> tuple[str, ...]:
        recomputed = compute_reference_binding_hash(evidence)
        if recomputed != evidence.reference_binding_hash:
            return ("reference_binding_hash_mismatch",)
        return ()

    # -- Entry point --------------------------------------------------------

    def validate(
        self,
        binding: RuntimeEvidenceBinding | Mapping[str, Any],
    ) -> BindingValidationResult:
        """Validate a runtime evidence binding.

        Deterministic and fail-closed.  Never raises on malformed input and
        never mutates ``binding``.
        """
        if isinstance(binding, RuntimeEvidenceBinding):
            evidence = binding
            optional_present = frozenset()
        elif isinstance(binding, Mapping):
            structural = self._check_input_structure(binding)
            if structural:
                return BindingValidationResult(
                    BindingValidationState.INVALID, structural
                )
            evidence = RuntimeEvidenceBinding.from_dict(binding)
            optional_present = frozenset(
                name
                for name in _OPTIONAL_TOP_LEVEL_FIELDS
                if name in binding
            )
        else:
            return BindingValidationResult(
                BindingValidationState.INVALID, ("input_type_invalid",)
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
            state = state or BindingValidationState.BLOCKED

        # Stage 9: Snapshot Consistency
        stage_gaps = self._check_receipt_snapshots(evidence)
        if stage_gaps:
            gaps.extend(stage_gaps)
            state = state or BindingValidationState.BLOCKED

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
