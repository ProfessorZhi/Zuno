"""Phase22 PHASE22 Benchmark Release Decision Engine.

This module is independent, deterministic and fail-closed. It consumes only the
already generated four-profile result manifests, Comparability Fingerprint,
Measurement Status, Core Five, Citation/Safety, Critical Slice, Agent
Efficiency, Cost/Latency, Failure Buckets and Artifact Hash inputs. It does
not call any model, does not run any benchmark, and does not import
``runtime_evidence_binding`` or ``benchmark_preflight`` modules.

The engine produces a ReleaseDecision containing one of:

* PASSED       -- comparable, fully measured, every required gate is present,
                   every value satisfies its threshold.
* FAILED       -- comparable, fully measured, at least one gate value fails
                   a threshold or a high-risk failure bucket is present.
* BLOCKED      -- missing profile, profile not measured, evidence gap, or a
                   required gate block is absent.
* INCOMPARABLE -- exactly one comparability dimension differs across profiles.
* ERROR        -- input structure, type, range or hash is invalid.

All reason codes come from a fixed, closed set. Reasons never embed raw input
payloads, file paths, exceptions or secret material. Hashes come from
``zuno.platform.contracts.canonical.canonical_sha256`` and are stable across
runs and platforms. Two runs of the same input always produce byte-identical
output.

CLI Exit Code Contract:

* 0 -- PASSED
* 1 -- FAILED
* 2 -- BLOCKED
* 3 -- INCOMPARABLE
* 4 -- ERROR or CLI read/write/parse failure
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from enum import IntEnum, StrEnum
from typing import Any, Final

from zuno.platform.contracts.canonical import canonical_sha256


REQUIRED_PROFILE_IDS: Final[tuple[str, ...]] = (
    "standard_rag",
    "local_graphrag",
    "deep_graphrag",
    "agentic_graphrag",
)

CORE_FIVE_METRIC_NAMES: Final[tuple[str, ...]] = (
    "context_precision",
    "context_recall",
    "faithfulness",
    "answer_relevancy",
    "answer_correctness",
)

CITATION_SAFETY_METRIC_NAMES: Final[tuple[str, ...]] = (
    "citation_accuracy",
    "unsupported_claim_rate",
    "contradicted_claim_rate",
    "abstention_correctness",
)

FINGERPRINT_DIMENSIONS: Final[tuple[str, ...]] = (
    "dataset_version",
    "case_set_hash",
    "corpus_snapshot",
    "knowledge_snapshot",
    "graph_snapshot",
    "model_profile",
    "judge_policy",
    "embedding_profile",
    "metric_definition",
    "runtime_profile",
    "security_scope",
    "budget_class",
)

# Each gate is required; if the top-level block is missing or invalid, the
# decision is BLOCKED with a dedicated reason code.
REQUIRED_TOP_LEVEL_GATES: Final[tuple[str, ...]] = (
    "core_five",
    "citation_safety",
    "critical_slice",
    "critical_slice_baseline",
    "agent_efficiency",
    "cost_latency_budget",
    "failure_buckets",
)

HIGH_RISK_FAILURE_BUCKETS: Final[frozenset[str]] = frozenset(
    {
        "answer_unfaithful",
        "citation_binding_miss",
        "graph_source_grounding_miss",
        "fusion_dropped_gold_evidence",
        "rerank_demoted_gold_evidence",
    }
)

DEFAULT_AGENT_EFFICIENT_PROFILE_ID: Final[str] = "agentic_graphrag"


class ReleaseDecisionStatus(StrEnum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    INCOMPARABLE = "INCOMPARABLE"
    ERROR = "ERROR"


class ReleaseDecisionExitCode(IntEnum):
    PASSED = 0
    FAILED = 1
    BLOCKED = 2
    INCOMPARABLE = 3
    ERROR = 4


EXIT_CODE_BY_STATUS: Final[dict[ReleaseDecisionStatus, int]] = {
    ReleaseDecisionStatus.PASSED: int(ReleaseDecisionExitCode.PASSED),
    ReleaseDecisionStatus.FAILED: int(ReleaseDecisionExitCode.FAILED),
    ReleaseDecisionStatus.BLOCKED: int(ReleaseDecisionExitCode.BLOCKED),
    ReleaseDecisionStatus.INCOMPARABLE: int(ReleaseDecisionExitCode.INCOMPARABLE),
    ReleaseDecisionStatus.ERROR: int(ReleaseDecisionExitCode.ERROR),
}


PASSED_REASONS: Final[frozenset[str]] = frozenset({"all_gates_passed"})

FAILED_REASONS: Final[frozenset[str]] = frozenset(
    {
        "core_five_metric_below_threshold",
        "citation_accuracy_below_threshold",
        "unsupported_claim_rate_above_threshold",
        "contradicted_claim_rate_above_threshold",
        "abstention_correctness_below_threshold",
        "critical_slice_regression",
        "agent_efficiency_quality_constraint_failed",
        "cost_above_budget",
        "latency_above_budget",
        "high_risk_failure_bucket_present",
    }
)

BLOCKED_REASONS: Final[frozenset[str]] = frozenset(
    {
        "missing_profile",
        "profile_not_measured",
        "core_five_block_missing",
        "core_five_metric_missing",
        "citation_safety_block_missing",
        "citation_safety_metric_missing",
        "critical_slice_block_missing",
        "critical_slice_baseline_block_missing",
        "agent_efficiency_block_missing",
        "agent_efficiency_metric_missing",
        "cost_latency_budget_block_missing",
        "cost_latency_metric_missing",
        "failure_buckets_block_missing",
        "evidence_missing",
        "input_unreadable",
        "output_unwritable",
        "missing_input_path",
        "missing_output_path",
        "comparability_fingerprint_undeclared",
        "fingerprint_dimension_missing",
    }
)

INCOMPARABLE_REASONS: Final[frozenset[str]] = frozenset(
    {
        "dataset_version_mismatch",
        "case_set_hash_mismatch",
        "corpus_snapshot_mismatch",
        "knowledge_snapshot_mismatch",
        "graph_snapshot_mismatch",
        "model_profile_mismatch",
        "judge_policy_mismatch",
        "embedding_profile_mismatch",
        "metric_definition_mismatch",
        "runtime_profile_mismatch",
        "security_scope_mismatch",
        "budget_class_mismatch",
    }
)

ERROR_REASONS: Final[frozenset[str]] = frozenset(
    {
        "input_not_object",
        "input_not_json_mapping",
        "profiles_not_object",
        "comparability_fingerprint_malformed",
        "measurement_status_malformed",
        "score_not_real_number",
        "score_is_nan_or_infinity",
        "score_out_of_range",
        "artifact_hash_invalid",
        "failure_buckets_malformed",
        "unknown_top_level_field",
        "core_five_block_invalid",
        "citation_safety_block_invalid",
        "critical_slice_block_invalid",
        "critical_slice_baseline_block_invalid",
        "agent_efficiency_block_invalid",
        "cost_latency_budget_block_invalid",
        "failure_buckets_block_invalid",
        "evidence_refs_invalid",
        "decision_input_invalid",
    }
)


class ReleaseDecisionError(RuntimeError):
    """Raised when the Release Decision Engine itself cannot run."""


@dataclass(frozen=True, slots=True)
class GateFailure:
    gate: str
    reason: str
    profile_id: str | None
    metric: str | None
    detail_kind: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate": self.gate,
            "reason": self.reason,
            "profile_id": self.profile_id,
            "metric": self.metric,
            "detail_kind": self.detail_kind,
        }


@dataclass(frozen=True, slots=True)
class ReleaseDecision:
    status: ReleaseDecisionStatus
    reason_codes: tuple[str, ...]
    canonical_input_hash: str
    decision_hash: str
    profile_hashes: dict[str, str]
    comparability_fingerprint_hash: str
    gate_results: tuple[GateFailure, ...]
    evidence_refs: tuple[str, ...]
    reproduce_command_template: str
    decision_engine_version: str
    closed_set_version: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "reason_codes": list(self.reason_codes),
            "canonical_input_hash": self.canonical_input_hash,
            "decision_hash": self.decision_hash,
            "profile_hashes": dict(self.profile_hashes),
            "comparability_fingerprint_hash": self.comparability_fingerprint_hash,
            "gate_results": [item.to_dict() for item in self.gate_results],
            "evidence_refs": list(self.evidence_refs),
            "reproduce_command_template": self.reproduce_command_template,
            "decision_engine_version": self.decision_engine_version,
            "closed_set_version": self.closed_set_version,
            "exit_code": EXIT_CODE_BY_STATUS[self.status],
        }

    @property
    def exit_code(self) -> int:
        return EXIT_CODE_BY_STATUS[self.status]


DECISION_ENGINE_VERSION: Final[str] = "phase22-release-decision-v2"
CLOSED_SET_VERSION: Final[str] = "closed-set-v2"

REPRODUCE_COMMAND_TEMPLATE: Final[str] = (
    "python -m tools.evals.zuno.rag_eval.run_phase22_release_decision "
    "--input-json <INPUT_JSON_PATH> --output-json <OUTPUT_JSON_PATH>"
)


def _validate_closed_set(reason: str, allowed: frozenset[str]) -> None:
    if reason not in allowed:
        raise ReleaseDecisionError(f"reason code not in closed set: {reason!r}")


def _is_real_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    if isinstance(value, float):
        return math.isfinite(value)
    return False


def _validate_score(value: Any, *, field_path: str) -> float | None:
    if value is None:
        return None
    if not _is_real_number(value):
        raise ReleaseDecisionError(f"score not a real number at {field_path}")
    if isinstance(value, float) and not math.isfinite(value):
        raise ReleaseDecisionError(f"score not finite at {field_path}")
    if not 0.0 <= float(value) <= 1.0:
        raise ReleaseDecisionError(f"score out of [0,1] at {field_path}")
    return float(value)


def _validate_required_string(value: Any, *, field_path: str) -> str:
    if not isinstance(value, str) or not value:
        raise ReleaseDecisionError(f"required string at {field_path}")
    return value


def _validate_optional_string(value: Any, *, field_path: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ReleaseDecisionError(f"optional string invalid at {field_path}")
    return value


def _validate_string_hash(value: Any, *, field_path: str) -> str:
    if not isinstance(value, str) or not value:
        raise ReleaseDecisionError(f"hash string required at {field_path}")
    if len(value) < 8:
        raise ReleaseDecisionError(f"hash string too short at {field_path}")
    return value


def _validate_evidence_refs(value: Any, *, field_path: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise ReleaseDecisionError(
            f"evidence_refs must be a list of strings at {field_path}"
        )
    seen: set[str] = set()
    normalized: list[str] = []
    for entry in value:
        if not isinstance(entry, str) or not entry:
            raise ReleaseDecisionError(
                f"evidence_refs entries must be non-empty strings at {field_path}"
            )
        if entry in seen:
            continue
        seen.add(entry)
        normalized.append(entry)
    return tuple(normalized)


def _normalize_failure_buckets(value: Any, *, field_path: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise ReleaseDecisionError(f"failure buckets must be a list at {field_path}")
    seen: set[str] = set()
    normalized: list[str] = []
    for entry in value:
        if not isinstance(entry, str) or not entry:
            raise ReleaseDecisionError(f"failure bucket entry invalid at {field_path}")
        if entry in seen:
            continue
        seen.add(entry)
        normalized.append(entry)
    return tuple(sorted(normalized))


def _normalize_artifact_hash_block(
    block: Mapping[str, Any], *, field_path: str
) -> dict[str, str]:
    artifact_hash = block.get("artifact_hash")
    if artifact_hash is not None:
        _validate_string_hash(artifact_hash, field_path=f"{field_path}.artifact_hash")
    manifest_hash = block.get("manifest_hash")
    normalized: dict[str, str] = {}
    if artifact_hash is not None:
        normalized["artifact_hash"] = artifact_hash
    if manifest_hash is not None:
        if not isinstance(manifest_hash, str) or not manifest_hash:
            raise ReleaseDecisionError(f"manifest_hash string invalid at {field_path}")
        normalized["manifest_hash"] = manifest_hash
    return normalized


def _normalize_profile_block(
    block: Any,
    *,
    field_path: str,
    expected_fingerprint: Mapping[str, str | None],
) -> dict[str, Any]:
    if not isinstance(block, Mapping):
        raise ReleaseDecisionError(f"profile block must be a mapping at {field_path}")
    artifact = block.get("artifact", {})
    if not isinstance(artifact, Mapping):
        raise ReleaseDecisionError(f"profile artifact must be a mapping at {field_path}")
    measurement_status = block.get("measurement_status")
    if not isinstance(measurement_status, str) or not measurement_status:
        raise ReleaseDecisionError(f"measurement_status string required at {field_path}")
    evaluation_block = block.get("evaluation", {})
    if not isinstance(evaluation_block, Mapping):
        raise ReleaseDecisionError(f"evaluation block invalid at {field_path}")
    failure_buckets = _normalize_failure_buckets(
        block.get("failure_buckets") or [], field_path=f"{field_path}.failure_buckets"
    )
    artifact_ref = block.get("evidence_ref")
    declared_fingerprint = block.get("fingerprint")
    if declared_fingerprint is None:
        fingerprint = dict(expected_fingerprint)
    else:
        fingerprint = _normalize_comparability_fingerprint(
            declared_fingerprint, field_path=f"{field_path}.fingerprint"
        )
    return {
        "measurement_status": measurement_status,
        "artifact": _normalize_artifact_hash_block(
            artifact, field_path=f"{field_path}.artifact"
        ),
        "evaluation": dict(evaluation_block),
        "failure_buckets": failure_buckets,
        "evidence_ref": artifact_ref,
        "fingerprint": fingerprint,
    }


def _normalize_comparability_fingerprint(
    block: Any, *, field_path: str
) -> dict[str, str | None]:
    if not isinstance(block, Mapping):
        raise ReleaseDecisionError(f"comparability_fingerprint invalid at {field_path}")
    normalized: dict[str, str | None] = {}
    for dimension in FINGERPRINT_DIMENSIONS:
        if dimension not in block:
            raise ReleaseDecisionError(f"fingerprint dimension missing: {dimension}")
        normalized[dimension] = _validate_optional_string(
            block.get(dimension), field_path=f"{field_path}.{dimension}"
        )
    return normalized


def _validate_input_structure(payload: Any) -> str | None:
    if not isinstance(payload, Mapping):
        return "input_not_object"
    allowed_top = {
        "profiles",
        "comparability_fingerprint",
        "core_five",
        "citation_safety",
        "critical_slice",
        "critical_slice_baseline",
        "agent_efficiency",
        "cost_latency_budget",
        "failure_buckets",
        "evidence_refs",
        "run_id",
    }
    unknown = sorted(set(payload.keys()) - allowed_top)
    if unknown:
        return "unknown_top_level_field"
    return None


def _evaluate_comparability(
    profile_fingerprints: Mapping[str, Mapping[str, str | None]],
) -> tuple[bool, tuple[str, ...]]:
    """Compare per-profile fingerprints; return (comparable, mismatched dimension codes).

    Only dimensions whose value actually differs across profiles produce codes;
    a ``None`` value is treated the same as the string ``"None"`` literally
    only for equality comparison; it is not a missing dimension and the
    fingerprint was already required to declare every dimension at the top
    level.
    """
    if len(profile_fingerprints) < 2:
        return True, ()
    reference_profile_id = sorted(profile_fingerprints)[0]
    reference = profile_fingerprints[reference_profile_id]
    mismatches: list[str] = []
    for dimension in FINGERPRINT_DIMENSIONS:
        reference_value = reference.get(dimension)
        if reference_value is None:
            reference_value_normalized: str | None = None
        else:
            reference_value_normalized = str(reference_value)
        for profile_id, fingerprint in profile_fingerprints.items():
            if profile_id == reference_profile_id:
                continue
            other_value = fingerprint.get(dimension)
            if other_value is None:
                other_value_normalized: str | None = None
            else:
                other_value_normalized = str(other_value)
            if other_value_normalized != reference_value_normalized:
                mismatches.append(f"{dimension}_mismatch")
    return (not mismatches), tuple(sorted(set(mismatches)))


def _check_required_top_level_block(
    payload: Mapping[str, Any], key: str, *, gate: str
) -> tuple[bool, GateFailure | None]:
    value = payload.get(key)
    if value is None:
        return False, GateFailure(
            gate=gate,
            reason=f"{gate}_block_missing",
            profile_id=None,
            metric=None,
            detail_kind="missing_top_level_block",
        )
    if not isinstance(value, Mapping):
        # The block is present but its shape is wrong: this is an ERROR
        # reason, not a BLOCKED reason, so we surface it from the caller.
        return False, GateFailure(
            gate=gate,
            reason=f"{gate}_block_invalid",
            profile_id=None,
            metric=None,
            detail_kind="invalid_top_level_block",
        )
    return True, None


def _evaluate_core_five(
    block: Mapping[str, Any], *, profiles: Mapping[str, dict[str, Any]]
) -> tuple[list[GateFailure], list[GateFailure]]:
    """Return (blocked_failures, failed_failures) for the core_five gate."""
    blocked: list[GateFailure] = []
    failed: list[GateFailure] = []
    for profile_id in REQUIRED_PROFILE_IDS:
        profile_metrics = block.get(profile_id)
        if not isinstance(profile_metrics, Mapping):
            blocked.append(
                GateFailure(
                    gate="core_five",
                    reason="core_five_metric_missing",
                    profile_id=profile_id,
                    metric=None,
                    detail_kind="missing_metric_block",
                )
            )
            continue
        for metric in CORE_FIVE_METRIC_NAMES:
            value = profile_metrics.get(metric)
            if value is None:
                blocked.append(
                    GateFailure(
                        gate="core_five",
                        reason="core_five_metric_missing",
                        profile_id=profile_id,
                        metric=metric,
                        detail_kind="missing_metric_value",
                    )
                )
                continue
            normalized = _validate_score(
                value, field_path=f"core_five.{profile_id}.{metric}"
            )
            if normalized is None or normalized < 0.5:
                failed.append(
                    GateFailure(
                        gate="core_five",
                        reason="core_five_metric_below_threshold",
                        profile_id=profile_id,
                        metric=metric,
                        detail_kind="below_threshold",
                    )
                )
    return blocked, failed


def _evaluate_citation_safety(
    block: Mapping[str, Any], *, profiles: Mapping[str, dict[str, Any]]
) -> tuple[list[GateFailure], list[GateFailure]]:
    blocked: list[GateFailure] = []
    failed: list[GateFailure] = []
    for profile_id in REQUIRED_PROFILE_IDS:
        metric_block = block.get(profile_id)
        if not isinstance(metric_block, Mapping):
            blocked.append(
                GateFailure(
                    gate="citation_safety",
                    reason="citation_safety_metric_missing",
                    profile_id=profile_id,
                    metric=None,
                    detail_kind="missing_metric_block",
                )
            )
            continue
        for metric in CITATION_SAFETY_METRIC_NAMES:
            value = metric_block.get(metric)
            if value is None:
                # Citation/Safety metrics are optional for each profile; if
                # all four profiles are missing a metric we surface a single
                # blocked signal at the end.
                continue
            normalized = _validate_score(
                value, field_path=f"citation_safety.{profile_id}.{metric}"
            )
            if normalized is None:
                continue
            if metric == "citation_accuracy" and normalized < 0.85:
                failed.append(
                    GateFailure(
                        gate="citation_safety",
                        reason="citation_accuracy_below_threshold",
                        profile_id=profile_id,
                        metric=metric,
                        detail_kind="below_threshold",
                    )
                )
            elif metric == "unsupported_claim_rate" and normalized > 0.05:
                failed.append(
                    GateFailure(
                        gate="citation_safety",
                        reason="unsupported_claim_rate_above_threshold",
                        profile_id=profile_id,
                        metric=metric,
                        detail_kind="above_threshold",
                    )
                )
            elif metric == "contradicted_claim_rate" and normalized > 0.0:
                failed.append(
                    GateFailure(
                        gate="citation_safety",
                        reason="contradicted_claim_rate_above_threshold",
                        profile_id=profile_id,
                        metric=metric,
                        detail_kind="above_threshold",
                    )
                )
            elif metric == "abstention_correctness" and normalized < 0.5:
                failed.append(
                    GateFailure(
                        gate="citation_safety",
                        reason="abstention_correctness_below_threshold",
                        profile_id=profile_id,
                        metric=metric,
                        detail_kind="below_threshold",
                    )
                )
    return blocked, failed


def _evaluate_critical_slice(
    block: Mapping[str, Any],
    baseline_block: Mapping[str, Any],
) -> tuple[list[GateFailure], list[GateFailure]]:
    blocked: list[GateFailure] = []
    failed: list[GateFailure] = []
    for profile_id in REQUIRED_PROFILE_IDS:
        slice_block = block.get(profile_id)
        if not isinstance(slice_block, Mapping) or not slice_block:
            blocked.append(
                GateFailure(
                    gate="critical_slice",
                    reason="critical_slice_block_missing",
                    profile_id=profile_id,
                    metric=None,
                    detail_kind="missing_slice_block",
                )
            )
            continue
        baseline_for_profile = (
            baseline_block.get(profile_id) if isinstance(baseline_block, Mapping) else None
        )
        for slice_name, current_value in slice_block.items():
            if not isinstance(slice_name, str) or not slice_name:
                continue
            current = _validate_score(
                current_value,
                field_path=f"critical_slice.{profile_id}.{slice_name}",
            )
            baseline_value = (
                baseline_for_profile.get(slice_name)
                if isinstance(baseline_for_profile, Mapping)
                else None
            )
            baseline = (
                _validate_score(
                    baseline_value,
                    field_path=f"critical_slice_baseline.{profile_id}.{slice_name}",
                )
                if baseline_value is not None
                else None
            )
            if current is None:
                continue
            if baseline is not None and current + 1e-9 < baseline:
                failed.append(
                    GateFailure(
                        gate="critical_slice",
                        reason="critical_slice_regression",
                        profile_id=profile_id,
                        metric=slice_name,
                        detail_kind="regression_vs_baseline",
                    )
                )
            elif baseline is None and current < 0.5:
                failed.append(
                    GateFailure(
                        gate="critical_slice",
                        reason="critical_slice_regression",
                        profile_id=profile_id,
                        metric=slice_name,
                        detail_kind="below_floor",
                    )
                )
    return blocked, failed


def _evaluate_agent_efficiency(
    block: Mapping[str, Any],
) -> tuple[list[GateFailure], list[GateFailure]]:
    blocked: list[GateFailure] = []
    failed: list[GateFailure] = []
    target_metrics = block.get(DEFAULT_AGENT_EFFICIENT_PROFILE_ID)
    if not isinstance(target_metrics, Mapping):
        blocked.append(
            GateFailure(
                gate="agent_efficiency",
                reason="agent_efficiency_metric_missing",
                profile_id=DEFAULT_AGENT_EFFICIENT_PROFILE_ID,
                metric=None,
                detail_kind="missing_metric_block",
            )
        )
        return blocked, failed
    evidence_yield = target_metrics.get("evidence_yield")
    if evidence_yield is None:
        blocked.append(
            GateFailure(
                gate="agent_efficiency",
                reason="agent_efficiency_metric_missing",
                profile_id=DEFAULT_AGENT_EFFICIENT_PROFILE_ID,
                metric="evidence_yield",
                detail_kind="missing_metric_value",
            )
        )
        return blocked, failed
    score = _validate_score(
        evidence_yield,
        field_path=f"agent_efficiency.{DEFAULT_AGENT_EFFICIENT_PROFILE_ID}.evidence_yield",
    )
    if score is None or score < 0.5:
        failed.append(
            GateFailure(
                gate="agent_efficiency",
                reason="agent_efficiency_quality_constraint_failed",
                profile_id=DEFAULT_AGENT_EFFICIENT_PROFILE_ID,
                metric="evidence_yield",
                detail_kind="below_floor",
            )
        )
    return blocked, failed


def _evaluate_cost_latency(
    block: Mapping[str, Any],
) -> tuple[list[GateFailure], list[GateFailure]]:
    blocked: list[GateFailure] = []
    failed: list[GateFailure] = []
    max_cost = block.get("max_total_cost")
    max_latency = block.get("max_p95_latency_ms")
    if max_cost is None and max_latency is None:
        blocked.append(
            GateFailure(
                gate="cost_latency",
                reason="cost_latency_metric_missing",
                profile_id=None,
                metric=None,
                detail_kind="missing_budget",
            )
        )
        return blocked, failed
    measured: dict[str, dict[str, Any]] = {}
    for profile_id in REQUIRED_PROFILE_IDS:
        profile_metrics = block.get(profile_id)
        if isinstance(profile_metrics, Mapping):
            measured[profile_id] = dict(profile_metrics)
    if not measured:
        blocked.append(
            GateFailure(
                gate="cost_latency",
                reason="cost_latency_metric_missing",
                profile_id=None,
                metric=None,
                detail_kind="missing_measurements",
            )
        )
        return blocked, failed
    for profile_id, metrics in measured.items():
        if max_cost is not None:
            cost = metrics.get("total_cost")
            if isinstance(cost, (int, float)) and cost > max_cost:
                failed.append(
                    GateFailure(
                        gate="cost_latency",
                        reason="cost_above_budget",
                        profile_id=profile_id,
                        metric="total_cost",
                        detail_kind="above_budget",
                    )
                )
        if max_latency is not None:
            latency = metrics.get("p95_latency_ms")
            if isinstance(latency, (int, float)) and latency > max_latency:
                failed.append(
                    GateFailure(
                        gate="cost_latency",
                        reason="latency_above_budget",
                        profile_id=profile_id,
                        metric="p95_latency_ms",
                        detail_kind="above_budget",
                    )
                )
    return blocked, failed


def _evaluate_failure_buckets(
    block: Mapping[str, Any], *, profiles: Mapping[str, dict[str, Any]]
) -> tuple[list[GateFailure], list[GateFailure]]:
    blocked: list[GateFailure] = []
    failed: list[GateFailure] = []
    observed: set[str] = set()
    has_observation = False
    for profile_id in REQUIRED_PROFILE_IDS:
        profile_buckets = profiles.get(profile_id, {}).get("failure_buckets", ())
        if profile_buckets:
            has_observation = True
        observed.update(profile_buckets)
        extra = block.get(profile_id)
        if isinstance(extra, (list, tuple)):
            has_observation = True
            for entry in extra:
                if isinstance(entry, str) and entry:
                    observed.add(entry)
    if not has_observation:
        blocked.append(
            GateFailure(
                gate="failure_buckets",
                reason="failure_buckets_block_missing",
                profile_id=None,
                metric=None,
                detail_kind="missing_observation",
            )
        )
        return blocked, failed
    for bucket in sorted(observed):
        if bucket in HIGH_RISK_FAILURE_BUCKETS:
            failed.append(
                GateFailure(
                    gate="failure_buckets",
                    reason="high_risk_failure_bucket_present",
                    profile_id=None,
                    metric=bucket,
                    detail_kind="high_risk_bucket",
                )
            )
    return blocked, failed


def _collect_evidence_refs(
    payload: Mapping[str, Any], *, profiles: Mapping[str, dict[str, Any]]
) -> tuple[str, ...]:
    refs: set[str] = set()
    for profile in profiles.values():
        evidence_ref = profile.get("evidence_ref")
        if isinstance(evidence_ref, str) and evidence_ref:
            refs.add(evidence_ref)
        artifact_block = profile.get("artifact") or {}
        if isinstance(artifact_block, Mapping):
            artifact_hash = artifact_block.get("artifact_hash")
            if isinstance(artifact_hash, str) and artifact_hash:
                refs.add(artifact_hash)
    top_refs = payload.get("evidence_refs")
    if isinstance(top_refs, (list, tuple)):
        for entry in top_refs:
            if isinstance(entry, str) and entry:
                refs.add(entry)
    return tuple(sorted(refs))


def _canonical_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "payload": {
            key: payload[key]
            for key in sorted(payload.keys())
            if key in payload
        }
    }


def evaluate_release_decision(payload: Mapping[str, Any]) -> ReleaseDecision:
    """Evaluate the Phase22 Release Decision from a structured JSON Mapping.

    Raises ``ReleaseDecisionError`` only when the decision engine itself cannot
    run. Decision status ERROR is encoded inside the returned
    ``ReleaseDecision`` for any structural / type / range problem in the input.
    """
    safe_payload = payload if isinstance(payload, Mapping) else {}
    try:
        structure_reason = _validate_input_structure(safe_payload)
        if structure_reason is not None:
            return _error_decision(safe_payload, reason=structure_reason, gate_results=())
        profiles_block = safe_payload.get("profiles")
        if not isinstance(profiles_block, Mapping):
            return _error_decision(
                safe_payload, reason="profiles_not_object", gate_results=()
            )
        fingerprint_block = safe_payload.get("comparability_fingerprint")
        if fingerprint_block is None:
            return _error_decision(
                safe_payload,
                reason="comparability_fingerprint_malformed",
                gate_results=(),
            )
        try:
            fingerprint = _normalize_comparability_fingerprint(
                fingerprint_block, field_path="comparability_fingerprint"
            )
        except ReleaseDecisionError:
            return _error_decision(
                safe_payload,
                reason="comparability_fingerprint_malformed",
                gate_results=(),
            )

        normalized_profiles: dict[str, dict[str, Any]] = {}
        profile_hashes: dict[str, str] = {}
        missing_profiles: list[str] = []
        measurement_blocked: list[str] = []
        try:
            for profile_id in REQUIRED_PROFILE_IDS:
                if profile_id not in profiles_block:
                    missing_profiles.append(profile_id)
                    continue
                normalized = _normalize_profile_block(
                    profiles_block[profile_id],
                    field_path=f"profiles.{profile_id}",
                    expected_fingerprint=fingerprint,
                )
                if normalized["measurement_status"] != "MEASURED":
                    measurement_blocked.append(profile_id)
                normalized_profiles[profile_id] = normalized
                profile_hash_input = {
                    "profile_id": profile_id,
                    "measurement_status": normalized["measurement_status"],
                    "artifact": normalized["artifact"],
                    "failure_buckets": list(normalized["failure_buckets"]),
                    "fingerprint": normalized["fingerprint"],
                }
                profile_hashes[profile_id] = canonical_sha256(profile_hash_input)
        except ReleaseDecisionError as exc:
            return _error_decision(
                safe_payload,
                reason="decision_input_invalid",
                gate_results=(),
                detail=str(exc),
            )

        if missing_profiles:
            gate = GateFailure(
                gate="profile_completeness",
                reason="missing_profile",
                profile_id=missing_profiles[0],
                metric=None,
                detail_kind="missing_profiles",
            )
            return _blocked_decision(
                safe_payload,
                profile_hashes=profile_hashes,
                fingerprint=fingerprint,
                reason_codes=("missing_profile",),
                gate_results=(gate,),
            )

        if measurement_blocked:
            gate = GateFailure(
                gate="profile_measurement",
                reason="profile_not_measured",
                profile_id=measurement_blocked[0],
                metric=None,
                detail_kind="not_measured_profiles",
            )
            return _blocked_decision(
                safe_payload,
                profile_hashes=profile_hashes,
                fingerprint=fingerprint,
                reason_codes=("profile_not_measured",),
                gate_results=(gate,),
            )

        try:
            profile_fingerprints: dict[str, Mapping[str, str | None]] = {
                pid: normalized["fingerprint"]
                for pid, normalized in normalized_profiles.items()
            }
            comparable, mismatches = _evaluate_comparability(profile_fingerprints)
        except ReleaseDecisionError as exc:
            return _error_decision(
                safe_payload,
                reason="decision_input_invalid",
                gate_results=(),
                detail=str(exc),
            )
        if not comparable:
            gate = GateFailure(
                gate="comparability_fingerprint",
                reason=mismatches[0],
                profile_id=None,
                metric=None,
                detail_kind="mismatch_dimensions",
            )
            return _incomparable_decision(
                safe_payload,
                profile_hashes=profile_hashes,
                fingerprint=fingerprint,
                reason_codes=tuple(mismatches),
                gate_results=(gate,),
            )

        # Each required top-level gate must be present (and structurally a
        # mapping). Missing or malformed top-level blocks become BLOCKED if
        # the block is absent and ERROR if the block has the wrong shape.
        blocked_top_level: list[GateFailure] = []
        error_top_level: list[GateFailure] = []
        required_blocks: dict[str, Mapping[str, Any]] = {}
        for gate_name in REQUIRED_TOP_LEVEL_GATES:
            present, gate_failure = _check_required_top_level_block(
                safe_payload, gate_name, gate=gate_name
            )
            if gate_failure is None:
                required_blocks[gate_name] = safe_payload[gate_name]  # type: ignore[index]
                continue
            if gate_failure.reason.endswith("_block_invalid"):
                error_top_level.append(gate_failure)
            else:
                blocked_top_level.append(gate_failure)
        if error_top_level:
            return _error_decision(
                safe_payload,
                reason=error_top_level[0].reason,
                gate_results=tuple(error_top_level),
            )
        if blocked_top_level:
            return _blocked_decision(
                safe_payload,
                profile_hashes=profile_hashes,
                fingerprint=fingerprint,
                reason_codes=tuple(sorted({f.reason for f in blocked_top_level})),
                gate_results=tuple(blocked_top_level),
            )

        # evidence_refs: top-level must be a list of strings. If it is
        # absent we BLOCK.
        top_evidence_refs = safe_payload.get("evidence_refs")
        if top_evidence_refs is None:
            gate = GateFailure(
                gate="evidence",
                reason="evidence_missing",
                profile_id=None,
                metric=None,
                detail_kind="missing_top_level_evidence_refs",
            )
            return _blocked_decision(
                safe_payload,
                profile_hashes=profile_hashes,
                fingerprint=fingerprint,
                reason_codes=("evidence_missing",),
                gate_results=(gate,),
            )
        try:
            normalize_evidence_refs = _validate_evidence_refs(
                top_evidence_refs, field_path="evidence_refs"
            )
        except ReleaseDecisionError:
            return _error_decision(
                safe_payload,
                reason="evidence_refs_invalid",
                gate_results=(),
            )

        # Per-gate evaluation. Each evaluator returns (blocked, failed).
        blocked_eval: list[GateFailure] = []
        failed_eval: list[GateFailure] = []
        try:
            core_block = required_blocks["core_five"]
            cs_block = required_blocks["citation_safety"]
            slice_block = required_blocks["critical_slice"]
            baseline_block = required_blocks["critical_slice_baseline"]
            eff_block = required_blocks["agent_efficiency"]
            cost_block = required_blocks["cost_latency_budget"]
            fb_block = required_blocks["failure_buckets"]

            b, f = _evaluate_core_five(core_block, profiles=normalized_profiles)
            blocked_eval.extend(b)
            failed_eval.extend(f)
            b, f = _evaluate_citation_safety(cs_block, profiles=normalized_profiles)
            blocked_eval.extend(b)
            failed_eval.extend(f)
            b, f = _evaluate_critical_slice(slice_block, baseline_block)
            blocked_eval.extend(b)
            failed_eval.extend(f)
            b, f = _evaluate_agent_efficiency(eff_block)
            blocked_eval.extend(b)
            failed_eval.extend(f)
            b, f = _evaluate_cost_latency(cost_block)
            blocked_eval.extend(b)
            failed_eval.extend(f)
            b, f = _evaluate_failure_buckets(fb_block, profiles=normalized_profiles)
            blocked_eval.extend(b)
            failed_eval.extend(f)
        except ReleaseDecisionError as exc:
            return _error_decision(
                safe_payload,
                reason="decision_input_invalid",
                gate_results=(),
                detail=str(exc),
            )

        if blocked_eval:
            return _blocked_decision(
                safe_payload,
                profile_hashes=profile_hashes,
                fingerprint=fingerprint,
                reason_codes=tuple(sorted({f.reason for f in blocked_eval})),
                gate_results=tuple(blocked_eval),
            )

        if failed_eval:
            return _build_decision(
                ReleaseDecisionStatus.FAILED,
                safe_payload,
                profile_hashes=profile_hashes,
                fingerprint=fingerprint,
                gate_results=tuple(failed_eval),
                reason_codes=tuple(sorted({f.reason for f in failed_eval})),
                evidence_refs=normalize_evidence_refs,
            )

        profile_evidence_refs = _collect_evidence_refs(
            safe_payload, profiles=normalized_profiles
        )
        all_evidence_refs = tuple(sorted(set(normalize_evidence_refs) | set(profile_evidence_refs)))
        if not all_evidence_refs:
            return _blocked_decision(
                safe_payload,
                profile_hashes=profile_hashes,
                fingerprint=fingerprint,
                reason_codes=("evidence_missing",),
                gate_results=(
                    GateFailure(
                        gate="evidence",
                        reason="evidence_missing",
                        profile_id=None,
                        metric=None,
                        detail_kind="no_evidence_refs_collected",
                    ),
                ),
            )

        return _build_decision(
            ReleaseDecisionStatus.PASSED,
            safe_payload,
            profile_hashes=profile_hashes,
            fingerprint=fingerprint,
            gate_results=(),
            reason_codes=("all_gates_passed",),
            evidence_refs=all_evidence_refs,
        )
    except ReleaseDecisionError as exc:
        return _error_decision(
            safe_payload if isinstance(safe_payload, Mapping) else {},
            reason="decision_input_invalid",
            gate_results=(),
            detail=str(exc),
        )


def _build_decision(
    status: ReleaseDecisionStatus,
    payload: Mapping[str, Any],
    *,
    profile_hashes: Mapping[str, str],
    fingerprint: Mapping[str, str | None],
    gate_results: tuple[GateFailure, ...],
    reason_codes: tuple[str, ...],
    evidence_refs: tuple[str, ...],
) -> ReleaseDecision:
    canonical_input_hash = canonical_sha256(_canonical_payload(dict(payload)))
    comparability_fingerprint_hash = canonical_sha256(
        {dimension: fingerprint.get(dimension) for dimension in FINGERPRINT_DIMENSIONS}
    )
    decision_payload = {
        "canonical_input_hash": canonical_input_hash,
        "decision_engine_version": DECISION_ENGINE_VERSION,
        "closed_set_version": CLOSED_SET_VERSION,
        "status": status.value,
        "reason_codes": list(reason_codes),
        "profile_hashes": dict(profile_hashes),
        "comparability_fingerprint_hash": comparability_fingerprint_hash,
        "gate_results": [item.to_dict() for item in gate_results],
        "evidence_refs": list(evidence_refs),
    }
    decision_hash = canonical_sha256(decision_payload)
    return ReleaseDecision(
        status=status,
        reason_codes=reason_codes,
        canonical_input_hash=canonical_input_hash,
        decision_hash=decision_hash,
        profile_hashes=dict(profile_hashes),
        comparability_fingerprint_hash=comparability_fingerprint_hash,
        gate_results=gate_results,
        evidence_refs=evidence_refs,
        reproduce_command_template=REPRODUCE_COMMAND_TEMPLATE,
        decision_engine_version=DECISION_ENGINE_VERSION,
        closed_set_version=CLOSED_SET_VERSION,
    )


def _error_decision(
    payload: Any,
    *,
    reason: str,
    gate_results: tuple[GateFailure, ...],
    detail: str | None = None,
) -> ReleaseDecision:
    _validate_closed_set(reason, ERROR_REASONS)
    safe_payload = payload if isinstance(payload, Mapping) else {}
    canonical_input_hash = canonical_sha256(_canonical_payload(dict(safe_payload)))
    decision_payload = {
        "canonical_input_hash": canonical_input_hash,
        "decision_engine_version": DECISION_ENGINE_VERSION,
        "closed_set_version": CLOSED_SET_VERSION,
        "status": ReleaseDecisionStatus.ERROR.value,
        "reason_codes": [reason],
        "profile_hashes": {},
        "comparability_fingerprint_hash": canonical_sha256({}),
        "gate_results": [item.to_dict() for item in gate_results],
        "evidence_refs": [],
    }
    decision_hash = canonical_sha256(decision_payload)
    return ReleaseDecision(
        status=ReleaseDecisionStatus.ERROR,
        reason_codes=(reason,),
        canonical_input_hash=canonical_input_hash,
        decision_hash=decision_hash,
        profile_hashes={},
        comparability_fingerprint_hash=canonical_sha256({}),
        gate_results=gate_results,
        evidence_refs=(),
        reproduce_command_template=REPRODUCE_COMMAND_TEMPLATE,
        decision_engine_version=DECISION_ENGINE_VERSION,
        closed_set_version=CLOSED_SET_VERSION,
    )


def _blocked_decision(
    payload: Mapping[str, Any],
    *,
    profile_hashes: Mapping[str, str],
    fingerprint: Mapping[str, str | None],
    reason_codes: tuple[str, ...],
    gate_results: tuple[GateFailure, ...],
) -> ReleaseDecision:
    for code in reason_codes:
        _validate_closed_set(code, BLOCKED_REASONS)
    return _build_decision(
        ReleaseDecisionStatus.BLOCKED,
        payload,
        profile_hashes=profile_hashes,
        fingerprint=fingerprint,
        gate_results=gate_results,
        reason_codes=reason_codes,
        evidence_refs=(),
    )


def _incomparable_decision(
    payload: Mapping[str, Any],
    *,
    profile_hashes: Mapping[str, str],
    fingerprint: Mapping[str, str | None],
    reason_codes: tuple[str, ...],
    gate_results: tuple[GateFailure, ...],
) -> ReleaseDecision:
    for code in reason_codes:
        _validate_closed_set(code, INCOMPARABLE_REASONS)
    return _build_decision(
        ReleaseDecisionStatus.INCOMPARABLE,
        payload,
        profile_hashes=profile_hashes,
        fingerprint=fingerprint,
        gate_results=gate_results,
        reason_codes=reason_codes,
        evidence_refs=(),
    )


def is_closed_reason(code: str) -> bool:
    """Return True iff ``code`` is a known closed reason for any decision status."""
    return (
        code in PASSED_REASONS
        or code in FAILED_REASONS
        or code in BLOCKED_REASONS
        or code in INCOMPARABLE_REASONS
        or code in ERROR_REASONS
    )


def exit_code_for(decision: ReleaseDecision | ReleaseDecisionStatus | str) -> int:
    """Return the canonical exit code for a decision status."""
    if isinstance(decision, ReleaseDecision):
        return decision.exit_code
    if isinstance(decision, ReleaseDecisionStatus):
        return EXIT_CODE_BY_STATUS[decision]
    normalized = str(decision)
    if normalized not in EXIT_CODE_BY_STATUS:
        return int(ReleaseDecisionExitCode.ERROR)
    return EXIT_CODE_BY_STATUS[ReleaseDecisionStatus(normalized)]


__all__ = [
    "BLOCKED_REASONS",
    "CLOSED_SET_VERSION",
    "CITATION_SAFETY_METRIC_NAMES",
    "CORE_FIVE_METRIC_NAMES",
    "DECISION_ENGINE_VERSION",
    "DEFAULT_AGENT_EFFICIENT_PROFILE_ID",
    "ERROR_REASONS",
    "EXIT_CODE_BY_STATUS",
    "FAILED_REASONS",
    "FINGERPRINT_DIMENSIONS",
    "HIGH_RISK_FAILURE_BUCKETS",
    "INCOMPARABLE_REASONS",
    "PASSED_REASONS",
    "REPRODUCE_COMMAND_TEMPLATE",
    "REQUIRED_PROFILE_IDS",
    "REQUIRED_TOP_LEVEL_GATES",
    "ReleaseDecision",
    "ReleaseDecisionError",
    "ReleaseDecisionExitCode",
    "ReleaseDecisionStatus",
    "evaluate_release_decision",
    "exit_code_for",
    "is_closed_reason",
]
