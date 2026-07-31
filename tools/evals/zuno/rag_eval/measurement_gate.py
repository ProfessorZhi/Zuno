"""Zuno PHASE22 Measurement Truth Gate.

Enforces deterministic quality gates for benchmark measurement classification:
- PREPARED
- RUNTIME_OBSERVED
- MEASURED
- BLOCKED
- FAILED
- INCOMPARABLE
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Dict, Optional


class MeasurementState(StrEnum):
    PREPARED = "PREPARED"
    RUNTIME_OBSERVED = "RUNTIME_OBSERVED"
    MEASURED = "MEASURED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    INCOMPARABLE = "INCOMPARABLE"


class MeasurementTruthGate:
    """Evaluates case inputs and execution results to determine official measurement status."""

    def evaluate(
        self,
        *,
        is_test_double: bool,
        reviewer_status: str = "pending",
        benchmark_eligible: bool = False,
        runtime_status: str = "completed",
        requested_profile: str = "",
        actual_profile: str = "",
        snapshot_ref: str = "",
        authorization_valid: bool = True,
        budget_settlement_ref: str = "",
        trace_id: str = "",
        failure_class: str = "",
        has_formal_credentials: bool = False,
    ) -> tuple[MeasurementState, str]:
        # Rule 1: Test Double is ALWAYS BLOCKED
        if is_test_double:
            return MeasurementState.BLOCKED, "not_measured_test_double_runner"

        # Rule 2: Runtime failure
        if runtime_status == "failed":
            return MeasurementState.FAILED, f"runtime_execution_failed: {failure_class or 'unknown_failure'}"

        # Rule 3: Security / Auth failed
        if not authorization_valid or runtime_status == "security_failed":
            return MeasurementState.BLOCKED, f"security_authorization_failed: {failure_class}"

        # Rule 4: Profile mismatch
        if requested_profile and actual_profile and requested_profile != actual_profile:
            return MeasurementState.INCOMPARABLE, f"profile_mismatch_{requested_profile}_vs_{actual_profile}"

        # Rule 5: Check MEASURED prerequisites
        missing_prereqs = []
        if reviewer_status != "approved":
            missing_prereqs.append("reviewer_not_approved")
        if not benchmark_eligible:
            missing_prereqs.append("not_benchmark_eligible")
        if not snapshot_ref:
            missing_prereqs.append("snapshot_ref_missing")
        if not budget_settlement_ref:
            missing_prereqs.append("budget_settlement_missing")
        if not trace_id:
            missing_prereqs.append("trace_id_missing")
        if failure_class:
            missing_prereqs.append(f"unresolved_failure:{failure_class}")
        if not has_formal_credentials:
            missing_prereqs.append("formal_credentials_missing")

        if missing_prereqs:
            # If runtime completed successfully but missing formal approval/credentials, state is RUNTIME_OBSERVED or BLOCKED
            if "reviewer_not_approved" in missing_prereqs or "formal_credentials_missing" in missing_prereqs:
                return MeasurementState.RUNTIME_OBSERVED, f"runtime_observed_pending_formal_gates: {', '.join(missing_prereqs)}"
            return MeasurementState.BLOCKED, f"measurement_blocked: {', '.join(missing_prereqs)}"

        return MeasurementState.MEASURED, ""
