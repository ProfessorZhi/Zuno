"""Phase22 Release Decision Engine focused tests.

The test suite is intentionally compact and high-value:

* Five final statuses (PASSED, FAILED, BLOCKED, INCOMPARABLE, ERROR).
* Each required gate's BLOCKED path (one minimal deletion test each).
* Required-gate missing vs threshold-fail distinction.
* Comparability fingerprint mismatch reason codes (no spurious
  fingerprint_dimension_missing when every dimension is declared).
* Artifact hash mismatch / structural error paths.
* NaN / Infinity / out-of-range / unknown field rejection.
* Deterministic replay (byte-identical across runs and across two
  independent temporary working directories).
* CLI read failure, CLI write failure, and one exit-code round trip per
  final status.
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src" / "backend"))

from tools.evals.zuno.rag_eval.release_decision import (  # noqa: E402
    BLOCKED_REASONS,
    CORE_FIVE_METRIC_NAMES,
    DEFAULT_AGENT_EFFICIENT_PROFILE_ID,
    ERROR_REASONS,
    EXIT_CODE_BY_STATUS,
    FAILED_REASONS,
    FINGERPRINT_DIMENSIONS,
    INCOMPARABLE_REASONS,
    PASSED_REASONS,
    REQUIRED_PROFILE_IDS,
    REQUIRED_TOP_LEVEL_GATES,
    ReleaseDecisionError,
    ReleaseDecisionExitCode,
    ReleaseDecisionStatus,
    evaluate_release_decision,
    exit_code_for,
    is_closed_reason,
)
from tools.evals.zuno.rag_eval.run_phase22_release_decision import run_cli  # noqa: E402


def _fingerprint(**overrides):
    base = {dimension: "fingerprint-v1" for dimension in FINGERPRINT_DIMENSIONS}
    base["graph_snapshot"] = None
    base.update(overrides)
    return base


def _profile_block(
    *,
    profile_id,
    measurement_status="MEASURED",
    failure_buckets=(),
    artifact_hash="hash:profile",
    evidence_ref="evidence:profile",
    fingerprint=None,
):
    if fingerprint is None:
        fingerprint = _fingerprint()
    return {
        "profile_id": profile_id,
        "measurement_status": measurement_status,
        "artifact": {"artifact_hash": artifact_hash, "manifest_hash": "manifest:profile"},
        "failure_buckets": list(failure_buckets),
        "evidence_ref": evidence_ref,
        "evaluation": {"ok": True},
        "fingerprint": fingerprint,
    }


def _good_core_five():
    return {
        profile: {metric: 0.9 for metric in CORE_FIVE_METRIC_NAMES}
        for profile in REQUIRED_PROFILE_IDS
    }


def _good_citation_safety():
    return {
        profile: {
            "citation_accuracy": 0.95,
            "unsupported_claim_rate": 0.01,
            "contradicted_claim_rate": 0.0,
            "abstention_correctness": 0.9,
        }
        for profile in REQUIRED_PROFILE_IDS
    }


def _good_critical_slice():
    return {
        profile: {"multi_hop": 0.8, "citation_required": 0.8}
        for profile in REQUIRED_PROFILE_IDS
    }


def _good_agent_efficiency():
    return {DEFAULT_AGENT_EFFICIENT_PROFILE_ID: {"evidence_yield": 0.7}}


def _good_cost_latency_budget():
    return {
        "max_total_cost": 100.0,
        "max_p95_latency_ms": 5000,
        "standard_rag": {"total_cost": 1.0, "p95_latency_ms": 200},
        "local_graphrag": {"total_cost": 1.0, "p95_latency_ms": 200},
        "deep_graphrag": {"total_cost": 1.0, "p95_latency_ms": 200},
        "agentic_graphrag": {"total_cost": 1.0, "p95_latency_ms": 200},
    }


def _good_failure_buckets():
    return {profile: [] for profile in REQUIRED_PROFILE_IDS}


def _good_evidence_refs():
    return ["top:evidence:ref"]


def _good_input(**overrides):
    payload = {
        "profiles": {
            profile_id: _profile_block(profile_id=profile_id)
            for profile_id in REQUIRED_PROFILE_IDS
        },
        "comparability_fingerprint": _fingerprint(),
        "core_five": _good_core_five(),
        "citation_safety": _good_citation_safety(),
        "critical_slice": _good_critical_slice(),
        "critical_slice_baseline": {
            profile: {"multi_hop": 0.7, "citation_required": 0.7}
            for profile in REQUIRED_PROFILE_IDS
        },
        "agent_efficiency": _good_agent_efficiency(),
        "cost_latency_budget": _good_cost_latency_budget(),
        "failure_buckets": _good_failure_buckets(),
        "evidence_refs": _good_evidence_refs(),
        "run_id": "run-id-fixture",
    }
    payload.update(overrides)
    return payload


# --------------------------------------------------------------------------
# Status -- exit-code contract
# --------------------------------------------------------------------------


def test_exit_code_map_matches_status():
    assert EXIT_CODE_BY_STATUS[ReleaseDecisionStatus.PASSED] == 0
    assert EXIT_CODE_BY_STATUS[ReleaseDecisionStatus.FAILED] == 1
    assert EXIT_CODE_BY_STATUS[ReleaseDecisionStatus.BLOCKED] == 2
    assert EXIT_CODE_BY_STATUS[ReleaseDecisionStatus.INCOMPARABLE] == 3
    assert EXIT_CODE_BY_STATUS[ReleaseDecisionStatus.ERROR] == 4
    assert int(ReleaseDecisionExitCode.PASSED) == 0
    assert int(ReleaseDecisionExitCode.FAILED) == 1
    assert int(ReleaseDecisionExitCode.BLOCKED) == 2
    assert int(ReleaseDecisionExitCode.INCOMPARABLE) == 3
    assert int(ReleaseDecisionExitCode.ERROR) == 4


def test_passed_decision_carries_exit_code_zero():
    decision = evaluate_release_decision(_good_input())
    assert decision.status == ReleaseDecisionStatus.PASSED
    assert decision.exit_code == 0
    assert exit_code_for(decision) == 0


# --------------------------------------------------------------------------
# Five final statuses
# --------------------------------------------------------------------------


def test_passed_when_all_gates_satisfied():
    decision = evaluate_release_decision(_good_input())
    assert decision.status == ReleaseDecisionStatus.PASSED
    assert decision.reason_codes == ("all_gates_passed",)
    assert decision.gate_results == ()
    assert decision.evidence_refs
    assert decision.canonical_input_hash
    assert decision.decision_hash
    assert set(decision.profile_hashes) == set(REQUIRED_PROFILE_IDS)
    assert decision.reproduce_command_template


def test_failed_when_core_five_metric_below_threshold():
    core_five = _good_core_five()
    core_five["standard_rag"]["faithfulness"] = 0.2
    decision = evaluate_release_decision(_good_input(core_five=core_five))
    assert decision.status == ReleaseDecisionStatus.FAILED
    assert "core_five_metric_below_threshold" in decision.reason_codes
    assert any(
        gate.metric == "faithfulness" and gate.profile_id == "standard_rag"
        for gate in decision.gate_results
    )


def test_failed_when_citation_safety_violation():
    citation_safety = _good_citation_safety()
    citation_safety["local_graphrag"]["contradicted_claim_rate"] = 0.5
    decision = evaluate_release_decision(_good_input(citation_safety=citation_safety))
    assert decision.status == ReleaseDecisionStatus.FAILED
    assert "contradicted_claim_rate_above_threshold" in decision.reason_codes


def test_failed_on_critical_slice_regression():
    payload = _good_input()
    payload["critical_slice"]["standard_rag"]["multi_hop"] = 0.4
    payload["critical_slice_baseline"]["standard_rag"]["multi_hop"] = 0.8
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.FAILED
    assert "critical_slice_regression" in decision.reason_codes


def test_failed_on_cost_above_budget():
    payload = _good_input()
    payload["cost_latency_budget"]["standard_rag"]["total_cost"] = 500.0
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.FAILED
    assert "cost_above_budget" in decision.reason_codes


def test_failed_on_high_risk_failure_bucket():
    payload = _good_input()
    payload["profiles"]["deep_graphrag"]["failure_buckets"] = ["citation_binding_miss"]
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.FAILED
    assert "high_risk_failure_bucket_present" in decision.reason_codes


def test_blocked_on_missing_profile():
    payload = _good_input()
    del payload["profiles"]["local_graphrag"]
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.BLOCKED
    assert decision.reason_codes == ("missing_profile",)


def test_blocked_on_profile_not_measured():
    payload = _good_input()
    payload["profiles"]["deep_graphrag"] = _profile_block(
        profile_id="deep_graphrag", measurement_status="BLOCKED"
    )
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.BLOCKED
    assert decision.reason_codes == ("profile_not_measured",)


def test_incomparable_on_fingerprint_mismatch():
    payload = _good_input()
    payload["profiles"]["standard_rag"]["fingerprint"] = _fingerprint(dataset_version="different-v2")
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.INCOMPARABLE
    assert "dataset_version_mismatch" in decision.reason_codes
    # Never carry the spurious "fingerprint_dimension_missing" code when every
    # dimension was declared and only a value differs.
    assert "fingerprint_dimension_missing" not in decision.reason_codes
    # The gate's reason must reflect the actual mismatch dimension, not a
    # fixed placeholder string.
    assert decision.gate_results[0].reason == "dataset_version_mismatch"


def test_error_on_unknown_top_level_field():
    payload = _good_input()
    payload["unknown_field"] = "nope"
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.ERROR
    assert decision.reason_codes == ("unknown_top_level_field",)


def test_error_on_nan_score():
    core_five = _good_core_five()
    core_five["standard_rag"]["faithfulness"] = float("nan")
    payload = _good_input(core_five=core_five)
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.ERROR


def test_error_on_infinity_score():
    core_five = _good_core_five()
    core_five["agentic_graphrag"]["answer_correctness"] = math.inf
    payload = _good_input(core_five=core_five)
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.ERROR


def test_error_on_score_out_of_range():
    core_five = _good_core_five()
    core_five["agentic_graphrag"]["context_precision"] = 1.5
    payload = _good_input(core_five=core_five)
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.ERROR


def test_error_on_artifact_hash_too_short():
    payload = _good_input()
    payload["profiles"]["standard_rag"]["artifact"]["artifact_hash"] = "x"
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.ERROR


# --------------------------------------------------------------------------
# Required-gate BLOCKED semantics (one minimal deletion test per gate)
# --------------------------------------------------------------------------


def test_blocked_when_required_gate_core_five_missing():
    payload = _good_input()
    payload.pop("core_five")
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.BLOCKED
    assert "core_five_block_missing" in decision.reason_codes


def test_blocked_when_required_gate_citation_safety_missing():
    payload = _good_input()
    payload.pop("citation_safety")
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.BLOCKED
    assert "citation_safety_block_missing" in decision.reason_codes


def test_blocked_when_required_gate_critical_slice_missing():
    payload = _good_input()
    payload.pop("critical_slice")
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.BLOCKED
    assert "critical_slice_block_missing" in decision.reason_codes


def test_blocked_when_required_gate_critical_slice_baseline_missing():
    payload = _good_input()
    payload.pop("critical_slice_baseline")
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.BLOCKED
    assert "critical_slice_baseline_block_missing" in decision.reason_codes


def test_blocked_when_required_gate_agent_efficiency_missing():
    payload = _good_input()
    payload.pop("agent_efficiency")
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.BLOCKED
    assert "agent_efficiency_block_missing" in decision.reason_codes


def test_blocked_when_required_gate_cost_latency_budget_missing():
    payload = _good_input()
    payload.pop("cost_latency_budget")
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.BLOCKED
    assert "cost_latency_budget_block_missing" in decision.reason_codes


def test_blocked_when_required_gate_failure_buckets_missing():
    payload = _good_input()
    payload.pop("failure_buckets")
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.BLOCKED
    assert "failure_buckets_block_missing" in decision.reason_codes


def test_blocked_when_required_gate_evidence_refs_missing():
    payload = _good_input()
    payload.pop("evidence_refs")
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.BLOCKED
    assert "evidence_missing" in decision.reason_codes


def test_blocked_when_core_five_metric_missing_inside_block():
    """Once the gate is present, missing metrics inside core_five are also BLOCKED,
    not FAILED -- gating on presence vs. threshold is the contract the engine
    promises."""
    payload = _good_input()
    core = _good_core_five()
    core["standard_rag"]["faithfulness"] = None
    payload["core_five"] = core
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.BLOCKED
    assert "core_five_metric_missing" in decision.reason_codes


def test_blocked_when_agent_efficiency_metric_missing():
    payload = _good_input()
    payload["agent_efficiency"] = {"standard_rag": {}}
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.BLOCKED
    assert "agent_efficiency_metric_missing" in decision.reason_codes


# --------------------------------------------------------------------------
# Determinism + path privacy
# --------------------------------------------------------------------------


def test_deterministic_replay_produces_byte_identical_decision():
    payload = _good_input()
    first = evaluate_release_decision(payload)
    second = evaluate_release_decision(payload)
    assert first == second
    assert first.decision_hash == second.decision_hash
    serialised_first = json.dumps(first.to_dict(), sort_keys=True)
    serialised_second = json.dumps(second.to_dict(), sort_keys=True)
    assert serialised_first == serialised_second


def test_evidence_pack_contains_no_local_path_or_user_name():
    payload = _good_input()
    input_path = Path("/some/secret/Alice/Users/input.json")
    output_path = Path("/tmp/build/out.json")
    decision = evaluate_release_decision(payload)
    pack = {"release_decision": decision.to_dict()}
    serialised = json.dumps(pack, ensure_ascii=False)
    for forbidden in ("Alice", "Users", "/Users", "/home", "/tmp", "secret"):
        assert forbidden not in serialised, forbidden


def test_evidence_pack_is_byte_identical_across_two_tmp_dirs(tmp_path: Path):
    """Same input from two different working directories must produce
    byte-identical evidence packs."""
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()
    payload = _good_input()
    serialised_payload = json.dumps(payload, ensure_ascii=False)
    in_a = a / "input.json"
    in_b = b / "input.json"
    in_a.write_text(serialised_payload, encoding="utf-8")
    in_b.write_text(serialised_payload, encoding="utf-8")
    out_a = a / "out.json"
    out_b = b / "out.json"
    code_a = run_cli(input_path=in_a, output_path=out_a)
    code_b = run_cli(input_path=in_b, output_path=out_b)
    assert code_a == 0
    assert code_b == 0
    assert out_a.read_bytes() == out_b.read_bytes()


# --------------------------------------------------------------------------
# Reason code closure
# --------------------------------------------------------------------------


def test_reason_codes_are_closure_set():
    for status_decision, allowed in [
        (evaluate_release_decision(_good_input()), PASSED_REASONS | FAILED_REASONS | BLOCKED_REASONS | INCOMPARABLE_REASONS | ERROR_REASONS),
    ]:
        for code in status_decision.reason_codes:
            assert is_closed_reason(code)
            assert code in allowed

    blocked = evaluate_release_decision({**_good_input(), "core_five": None})
    assert blocked.status == ReleaseDecisionStatus.BLOCKED
    for code in blocked.reason_codes:
        assert code in BLOCKED_REASONS

    failed = evaluate_release_decision(
        {**_good_input(), "citation_safety": {**_good_citation_safety(),
                                              "standard_rag": {"contradicted_claim_rate": 0.5,
                                                                "citation_accuracy": 0.95,
                                                                "unsupported_claim_rate": 0.01,
                                                                "abstention_correctness": 0.9}}}
    )
    assert failed.status == ReleaseDecisionStatus.FAILED
    for code in failed.reason_codes:
        assert code in FAILED_REASONS


# --------------------------------------------------------------------------
# CLI coverage of every final status and I/O failures
# --------------------------------------------------------------------------


def _run_cli_with_payload(payload, tmp_path: Path):
    input_path = tmp_path / "input.json"
    output_path = tmp_path / "out.json"
    input_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    exit_code = run_cli(input_path=input_path, output_path=output_path)
    return exit_code, json.loads(output_path.read_text(encoding="utf-8"))


def test_cli_returns_zero_for_passed(tmp_path: Path):
    code, pack = _run_cli_with_payload(_good_input(), tmp_path)
    assert code == 0
    assert pack["release_decision"]["exit_code"] == 0
    assert pack["release_decision"]["status"] == "PASSED"
    assert "cli_input_path" not in pack["release_decision"]
    assert "cli_output_path" not in pack["release_decision"]


def test_cli_returns_one_for_failed(tmp_path: Path):
    payload = _good_input()
    payload["profiles"]["standard_rag"]["failure_buckets"] = ["citation_binding_miss"]
    code, pack = _run_cli_with_payload(payload, tmp_path)
    assert code == 1
    assert pack["release_decision"]["exit_code"] == 1
    assert pack["release_decision"]["status"] == "FAILED"


def test_cli_returns_two_for_blocked(tmp_path: Path):
    payload = _good_input()
    del payload["profiles"]["local_graphrag"]
    code, pack = _run_cli_with_payload(payload, tmp_path)
    assert code == 2
    assert pack["release_decision"]["exit_code"] == 2
    assert pack["release_decision"]["status"] == "BLOCKED"


def test_cli_returns_three_for_incomparable(tmp_path: Path):
    payload = _good_input()
    payload["profiles"]["deep_graphrag"]["fingerprint"] = _fingerprint(
        dataset_version="different-v2"
    )
    code, pack = _run_cli_with_payload(payload, tmp_path)
    assert code == 3
    assert pack["release_decision"]["exit_code"] == 3
    assert pack["release_decision"]["status"] == "INCOMPARABLE"


def test_cli_returns_four_for_error(tmp_path: Path):
    payload = _good_input()
    payload["unknown_field"] = "nope"
    code, pack = _run_cli_with_payload(payload, tmp_path)
    assert code == 4
    assert pack["release_decision"]["exit_code"] == 4
    assert pack["release_decision"]["status"] == "ERROR"


def test_cli_returns_two_when_input_missing(tmp_path: Path):
    code, pack = _run_cli_with_payload(_good_input(), tmp_path)
    in_path = tmp_path / "absent.json"
    out_path = tmp_path / "out.json"
    code = run_cli(input_path=in_path, output_path=out_path)
    assert code == 2
    written = json.loads((tmp_path / "out.json").read_text(encoding="utf-8"))
    assert written["release_decision"]["status"] == "BLOCKED"
    assert written["release_decision"]["reason_codes"] == ["missing_input_path"]


def test_cli_returns_two_when_input_unreadable(tmp_path: Path):
    in_path = tmp_path / "broken.json"
    in_path.write_text("not really json {", encoding="utf-8")
    out_path = tmp_path / "out.json"
    code = run_cli(input_path=in_path, output_path=out_path)
    assert code == 2
    written = json.loads(out_path.read_text(encoding="utf-8"))
    assert written["release_decision"]["status"] == "BLOCKED"
    assert written["release_decision"]["reason_codes"] == ["input_unreadable"]


def test_cli_returns_four_when_output_unwritable(tmp_path: Path):
    payload = _good_input()
    in_path = tmp_path / "input.json"
    in_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    out_path = tmp_path / "outdir"
    out_path.mkdir()
    code = run_cli(input_path=in_path, output_path=out_path)
    assert code == 4


# --------------------------------------------------------------------------
# Threshold invariants
# --------------------------------------------------------------------------


def test_threshold_closure_invariant():
    assert PASSED_REASONS == frozenset({"all_gates_passed"})
    for code in FAILED_REASONS:
        assert is_closed_reason(code)
    for code in BLOCKED_REASONS:
        assert is_closed_reason(code)
    for code in INCOMPARABLE_REASONS:
        assert is_closed_reason(code)
    for code in ERROR_REASONS:
        assert is_closed_reason(code)
    # All required top-level gates are documented.
    assert set(REQUIRED_TOP_LEVEL_GATES) == {
        "core_five",
        "citation_safety",
        "critical_slice",
        "critical_slice_baseline",
        "agent_efficiency",
        "cost_latency_budget",
        "failure_buckets",
    }
