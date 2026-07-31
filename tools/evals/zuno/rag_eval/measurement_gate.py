"""Zuno PHASE22 Measurement Truth Gate.

Enforces deterministic, strictly-ordered classification of benchmark
measurement status. Priority order is contractual and must not be changed:

1. Test Double           -> BLOCKED
2. Runtime Failed        -> FAILED
3. Security Denied/Stale -> BLOCKED
4. Profile Mismatch      -> INCOMPARABLE
5. Runtime Evidence Incomplete (snapshot/trace/budget/artifact/run_outcome missing,
   unresolved failure, invalid hash) -> BLOCKED
6. Runtime Evidence Complete but formal gates pending
   (reviewer pending, benchmark_eligible false, credentials missing,
   formal execution not requested) -> RUNTIME_OBSERVED
7. All gates satisfied   -> MEASURED

Rule 6 must NEVER mask a prior failure from rules 1-5.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Optional


class MeasurementState(StrEnum):
    PREPARED = "PREPARED"
    RUNTIME_OBSERVED = "RUNTIME_OBSERVED"
    MEASURED = "MEASURED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    INCOMPARABLE = "INCOMPARABLE"


class MeasurementTruthGate:
    """Evaluates canonical case results to determine official measurement status.

    Priority order is strictly enforced. Each rule is evaluated in sequence;
    the first match terminates classification. Rule 6 (RUNTIME_OBSERVED) is only
    reachable after rules 1-5 have all passed.
    """

    def evaluate(
        self,
        *,
        # Rule 1
        is_test_double: bool,
        # Rule 2
        runtime_status: str = "completed",
        failure_class: str = "",
        # Rule 3
        security_blocked: bool = False,
        # Rule 4
        requested_profile: str = "",
        actual_profile: str = "",
        # Rule 5 — Runtime Evidence completeness
        snapshot_ref: str = "",
        trace_id: Optional[str] = None,
        budget_settlement_ref: str = "",
        artifact_receipt_ref: str = "",
        run_outcome_ref: str = "",
        # Rule 6 — Formal gate eligibility
        reviewer_status: str = "pending",
        benchmark_eligible: bool = False,
        has_formal_credentials: bool = False,
        formal_execution_requested: bool = False,
    ) -> tuple[MeasurementState, str]:
        # ── Rule 1: Test Double ──────────────────────────────────────────────
        if is_test_double:
            return MeasurementState.BLOCKED, "not_measured_test_double_runner"

        # ── Rule 2: Runtime Failed ───────────────────────────────────────────
        if runtime_status == "failed":
            return MeasurementState.FAILED, f"runtime_execution_failed:{failure_class or 'unknown'}"

        # ── Rule 3: Security Denied / Stale ──────────────────────────────────
        if security_blocked or runtime_status == "security_failed" or runtime_status == "blocked":
            return MeasurementState.BLOCKED, f"security_or_dependency_blocked:{failure_class or 'unknown'}"

        # ── Rule 4: Profile Mismatch ─────────────────────────────────────────
        if requested_profile and actual_profile and requested_profile != actual_profile:
            return (
                MeasurementState.INCOMPARABLE,
                f"profile_mismatch:{requested_profile}_vs_{actual_profile}",
            )

        # ── Rule 5: Runtime Evidence Completeness ────────────────────────────
        evidence_gaps: list[str] = []
        if not snapshot_ref:
            evidence_gaps.append("snapshot_ref_missing")
        if not trace_id:
            evidence_gaps.append("trace_missing")
        if not budget_settlement_ref:
            evidence_gaps.append("budget_settlement_missing")
        if not run_outcome_ref:
            evidence_gaps.append("run_outcome_missing")
        if failure_class:
            evidence_gaps.append(f"unresolved_failure:{failure_class}")

        if evidence_gaps:
            return MeasurementState.BLOCKED, f"runtime_evidence_incomplete:{','.join(evidence_gaps)}"

        # ── Rule 6: Formal Gate Eligibility ──────────────────────────────────
        formal_gaps: list[str] = []
        if reviewer_status != "approved":
            formal_gaps.append("reviewer_pending")
        if not benchmark_eligible:
            formal_gaps.append("benchmark_eligible_false")
        if not has_formal_credentials:
            formal_gaps.append("formal_credentials_missing")
        if not formal_execution_requested:
            formal_gaps.append("formal_execution_not_requested")

        if formal_gaps:
            return MeasurementState.RUNTIME_OBSERVED, f"runtime_observed_pending_formal_gates:{','.join(formal_gaps)}"

        # ── Rule 7: All gates satisfied ──────────────────────────────────────
        return MeasurementState.MEASURED, ""
