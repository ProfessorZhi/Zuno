"""Phase22 Release Decision Engine focused tests.

These tests cover the minimum high-value semantics required by the task:

* all five final statuses (PASSED, FAILED, BLOCKED, INCOMPARABLE, ERROR);
* missing profile / profile not measured;
* fingerprint mismatch;
* critical slice regression;
* safety failure;
* artifact hash mismatch / structural error;
* unknown fields and type errors including NaN / Infinity;
* deterministic replay (byte-identical output);
* CLI parse / read / write failure paths.

The tests are intentionally minimal, focused and fail-closed; we do not
modify the engine just to make a test pass.
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src" / "backend"))

from tools.evals.zuno.rag_eval.release_decision import (  # noqa: E402
    BLOCKED_REASONS,
    CORE_FIVE_METRIC_NAMES,
    DEFAULT_AGENT_EFFICIENT_PROFILE_ID,
    ERROR_REASONS,
    FAILED_REASONS,
    FINGERPRINT_DIMENSIONS,
    INCOMPARABLE_REASONS,
    PASSED_REASONS,
    REQUIRED_PROFILE_IDS,
    ReleaseDecisionStatus,
    ReleaseDecisionError,
    evaluate_release_decision,
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
        "cost_latency_budget": {"max_total_cost": 100.0, "max_p95_latency_ms": 5000},
        "failure_buckets": {},
        "evidence_refs": ["top:evidence:ref"],
        "run_id": "run-id-fixture",
    }
    payload.update(overrides)
    return payload


def test_passed_when_all_gates_satisfied():
    decision = evaluate_release_decision(_good_input())
    assert decision.status == ReleaseDecisionStatus.PASSED
    assert decision.reason_codes == ("all_gates_passed",)
    assert decision.gate_results == ()
    assert decision.evidence_refs  # non-empty
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
    payload["cost_latency_budget"] = {
        "max_total_cost": 1.0,
        "max_p95_latency_ms": 5000,
        "standard_rag": {"total_cost": 5.0, "p95_latency_ms": 200},
        "local_graphrag": {"total_cost": 0.5},
    }
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
    assert decision.reason_codes[0] == "missing_profile"


def test_blocked_on_profile_not_measured():
    payload = _good_input()
    payload["profiles"]["deep_graphrag"] = _profile_block(
        profile_id="deep_graphrag", measurement_status="BLOCKED"
    )
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.BLOCKED
    assert decision.reason_codes == ("profile_not_measured",)


def test_blocked_on_missing_evidence_refs():
    payload = _good_input()
    payload.pop("evidence_refs", None)
    for profile_id in REQUIRED_PROFILE_IDS:
        payload["profiles"][profile_id].pop("evidence_ref", None)
        payload["profiles"][profile_id].get("artifact", {}).pop("artifact_hash", None)
    payload["agent_efficiency"] = {}
    # We must remove every failing gate for the "missing_evidence_refs" path
    # to actually reach BLOCKED instead of FAILED.
    payload["core_five"] = {
        profile: {metric: 0.9 for metric in CORE_FIVE_METRIC_NAMES}
        for profile in REQUIRED_PROFILE_IDS
    }
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.BLOCKED
    assert "evidence_missing" in decision.reason_codes


def test_incomparable_on_fingerprint_mismatch():
    payload = _good_input()
    payload["profiles"]["standard_rag"]["fingerprint"] = _fingerprint(dataset_version="different-v2")
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.INCOMPARABLE
    assert any(code.endswith("_mismatch") or code == "fingerprint_dimension_missing"
               for code in decision.reason_codes)


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


def test_deterministic_replay_produces_byte_identical_decision():
    payload = _good_input()
    first = evaluate_release_decision(payload)
    second = evaluate_release_decision(payload)
    assert first == second
    assert first.decision_hash == second.decision_hash
    serialised_first = json.dumps(first.to_dict(), sort_keys=True)
    serialised_second = json.dumps(second.to_dict(), sort_keys=True)
    assert serialised_first == serialised_second


def test_reason_codes_are_closure_set():
    good_decision = evaluate_release_decision(_good_input())
    for code in good_decision.reason_codes:
        assert is_closed_reason(code)
    payload = _good_input()
    payload["profiles"]["standard_rag"]["measurement_status"] = "BLOCKED"
    blocked_decision = evaluate_release_decision(payload)
    for code in blocked_decision.reason_codes:
        assert is_closed_reason(code)
        assert code in BLOCKED_REASONS
    payload = _good_input()
    payload["profiles"]["deep_graphrag"]["fingerprint"] = _fingerprint(judge_policy="different-judge")
    incomparable_decision = evaluate_release_decision(payload)
    assert incomparable_decision.status == ReleaseDecisionStatus.INCOMPARABLE
    for code in incomparable_decision.reason_codes:
        assert is_closed_reason(code)
        assert code in INCOMPARABLE_REASONS


def test_cli_writes_evidence_pack(tmp_path: Path):
    payload = _good_input()
    input_path = tmp_path / "input.json"
    output_path = tmp_path / "output.json"
    input_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    exit_code = run_cli(input_path=input_path, output_path=output_path)
    assert exit_code == 0
    written = json.loads(output_path.read_text(encoding="utf-8"))
    assert "release_decision" in written
    decision = written["release_decision"]
    assert decision["status"] == "PASSED"
    assert decision["reason_codes"] == ["all_gates_passed"]
    assert decision["reproduce_command_template"]
    assert decision["canonical_input_hash"]
    assert decision["decision_hash"]


def test_cli_returns_blocked_when_input_missing(tmp_path: Path):
    exit_code = run_cli(
        input_path=tmp_path / "no-such.json",
        output_path=tmp_path / "out.json",
    )
    assert exit_code == 2
    written = json.loads((tmp_path / "out.json").read_text(encoding="utf-8"))
    decision = written["release_decision"]
    assert decision["status"] == "BLOCKED"
    assert decision["reason_codes"] == ["missing_input_path"]


def test_cli_returns_blocked_when_input_unreadable(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text("not really json {", encoding="utf-8")
    exit_code = run_cli(input_path=bad, output_path=tmp_path / "out.json")
    assert exit_code == 2
    written = json.loads((tmp_path / "out.json").read_text(encoding="utf-8"))
    assert written["release_decision"]["status"] == "BLOCKED"
    assert written["release_decision"]["reason_codes"] == ["input_unreadable"]


def test_cli_returns_non_zero_when_output_unwritable(tmp_path: Path):
    payload = _good_input()
    input_path = tmp_path / "input.json"
    input_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    # output_path is an existing directory, so writing to it must fail.
    output_path = tmp_path / "outdir"
    output_path.mkdir()
    exit_code = run_cli(input_path=input_path, output_path=output_path)
    assert exit_code == 3


def test_cli_does_not_emit_traceback_or_absolute_path(capsys):
    """The CLI must not print traceback or absolute paths to stdout/stderr."""
    import io

    sys_stdout = sys.stdout
    sys_stderr = sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    try:
        payload = _good_input()
        payload["unknown_field"] = "nope"
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            in_path = Path(td) / "input.json"
            out_path = Path(td) / "out.json"
            in_path.write_text(json.dumps(payload), encoding="utf-8")
            run_cli(input_path=in_path, output_path=out_path)
        out_collected = sys.stdout.getvalue()
        err_collected = sys.stderr.getvalue()
    finally:
        sys.stdout = sys_stdout
        sys.stderr = sys_stderr
    combined = out_collected + err_collected
    assert "Traceback" not in combined
    for forbidden in ("F:\\", "C:\\", "/Users", "/home", "/tmp"):
        assert forbidden not in combined, forbidden


def test_thresholds_have_fixed_closure():
    assert PASSED_REASONS == frozenset({"all_gates_passed"})
    for code in FAILED_REASONS:
        assert is_closed_reason(code)
    for code in BLOCKED_REASONS:
        assert is_closed_reason(code)
    for code in INCOMPARABLE_REASONS:
        assert is_closed_reason(code)
    for code in ERROR_REASONS:
        assert is_closed_reason(code)
