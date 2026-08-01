"""Phase22 Release Decision Engine focused tests.

The test suite is intentionally compact and high-value.  Each new "final
narrow fix" review-driven requirement is covered by a single minimal test:

* Citation/Safety completeness (one missing metric blocks PASSED).
* Critical Slice Baseline completeness (one missing baseline slice blocks).
* Cost/Latency completeness (one missing profile metric blocks; one bad
  numeric shape produces ERROR).
* Failure Bucket taxonomy + shape (one bad shape produces ERROR; one
  unknown non-empty bucket produces FAILED).
* Profile Fingerprint completeness (a missing profile fingerprint blocks).
* Artifact Hash completeness (a missing artifact hash blocks).
* Status exit-code mapping and CLI ReleaseDecisionError -> ERROR 4.
* Determinism + path privacy between two tmp dirs.
* Closure-set invariants for reason codes and required gates.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src" / "backend"))

from tools.evals.zuno.rag_eval.release_decision import (  # noqa: E402
    BLOCKED_REASONS,
    CORE_FIVE_METRIC_NAMES,
    CITATION_SAFETY_METRIC_NAMES,
    DEFAULT_AGENT_EFFICIENT_PROFILE_ID,
    ERROR_REASONS,
    EXIT_CODE_BY_STATUS,
    FAILED_REASONS,
    FINGERPRINT_DIMENSIONS,
    FAILURE_BUCKET_TAXONOMY,
    INCOMPARABLE_REASONS,
    PASSED_REASONS,
    REQUIRED_PROFILE_IDS,
    REQUIRED_TOP_LEVEL_GATES,
    ReleaseDecisionError,
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
    block: dict = {
        "profile_id": profile_id,
        "measurement_status": measurement_status,
        "artifact": {"artifact_hash": artifact_hash, "manifest_hash": "manifest:profile"},
        "failure_buckets": list(failure_buckets),
        "evidence_ref": evidence_ref,
        "evaluation": {"ok": True},
        "fingerprint": fingerprint,
    }
    return block


def _good_core_five():
    return {
        profile: {metric: 0.9 for metric in CORE_FIVE_METRIC_NAMES}
        for profile in REQUIRED_PROFILE_IDS
    }


def _good_citation_safety():
    """Good citation/safety values: 0.9 = accuracy/abstention, low rates."""
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
# Status -> exit code contract
# --------------------------------------------------------------------------


def test_exit_code_map_matches_status():
    assert EXIT_CODE_BY_STATUS[ReleaseDecisionStatus.PASSED] == 0
    assert EXIT_CODE_BY_STATUS[ReleaseDecisionStatus.FAILED] == 1
    assert EXIT_CODE_BY_STATUS[ReleaseDecisionStatus.BLOCKED] == 2
    assert EXIT_CODE_BY_STATUS[ReleaseDecisionStatus.INCOMPARABLE] == 3
    assert EXIT_CODE_BY_STATUS[ReleaseDecisionStatus.ERROR] == 4


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


def test_failed_when_core_five_below_threshold():
    payload = _good_input()
    payload["core_five"]["standard_rag"]["faithfulness"] = 0.2
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.FAILED
    assert "core_five_metric_below_threshold" in decision.reason_codes


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


def test_incomparable_emits_only_actual_dimension_mismatch():
    payload = _good_input()
    payload["profiles"]["standard_rag"]["fingerprint"] = _fingerprint(
        dataset_version="different-v2"
    )
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.INCOMPARABLE
    assert "dataset_version_mismatch" in decision.reason_codes
    assert "fingerprint_dimension_missing" not in decision.reason_codes
    assert decision.gate_results[0].reason == "dataset_version_mismatch"


def test_error_on_unknown_top_level_field():
    payload = _good_input()
    payload["unknown_field"] = "nope"
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.ERROR
    assert decision.reason_codes == ("unknown_top_level_field",)


# --------------------------------------------------------------------------
# Review-driven focused tests (one minimal test per requirement)
# --------------------------------------------------------------------------


def test_missing_citation_safety_metric_blocks_passed():
    payload = _good_input()
    cs = _good_citation_safety()
    cs["standard_rag"].pop("abstention_correctness")
    payload["citation_safety"] = cs
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.BLOCKED
    assert "citation_safety_metric_missing" in decision.reason_codes


def test_citation_safety_bad_score_is_error():
    payload = _good_input()
    cs = _good_citation_safety()
    cs["standard_rag"]["citation_accuracy"] = 1.5  # out of [0,1]
    payload["citation_safety"] = cs
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.ERROR


def test_missing_critical_slice_baseline_blocks_passed():
    payload = _good_input()
    baseline = {profile: {"multi_hop": 0.7, "citation_required": 0.7} for profile in REQUIRED_PROFILE_IDS}
    del baseline["deep_graphrag"]["citation_required"]
    payload["critical_slice_baseline"] = baseline
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.BLOCKED
    assert "critical_slice_baseline_metric_missing" in decision.reason_codes


def test_critical_slice_regression_failed_not_floor_blocked():
    """If the baseline exists but the current value is below it, the decision
    is FAILED (threshold violation), not BLOCKED. Floor fallback (0.5) has
    been removed."""
    payload = _good_input()
    payload["critical_slice"]["standard_rag"]["multi_hop"] = 0.4
    payload["critical_slice_baseline"]["standard_rag"]["multi_hop"] = 0.8
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.FAILED
    assert "critical_slice_regression" in decision.reason_codes


def test_missing_cost_latency_metric_blocks_passed():
    payload = _good_input()
    del payload["cost_latency_budget"]["deep_graphrag"]
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.BLOCKED
    assert "cost_latency_metric_missing" in decision.reason_codes


def test_cost_latency_nan_is_error():
    payload = _good_input()
    payload["cost_latency_budget"]["deep_graphrag"]["total_cost"] = float("nan")
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.ERROR


def test_failure_bucket_bad_shape_is_error():
    payload = _good_input()
    payload["failure_buckets"]["deep_graphrag"] = "not-a-list"
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.ERROR


def test_unknown_non_empty_failure_bucket_failed():
    payload = _good_input()
    payload["failure_buckets"]["deep_graphrag"] = ["made_up_bucket_xyz"]
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.FAILED
    assert "unknown_failure_bucket" in decision.reason_codes


def test_high_risk_failure_bucket_failed():
    payload = _good_input()
    payload["failure_buckets"]["deep_graphrag"] = ["citation_binding_miss"]
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.FAILED
    assert "high_risk_failure_bucket_present" in decision.reason_codes


def test_missing_profile_fingerprint_blocks_passed():
    payload = _good_input()
    del payload["profiles"]["local_graphrag"]["fingerprint"]
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.BLOCKED
    assert "profile_fingerprint_missing" in decision.reason_codes


def test_missing_artifact_hash_blocks_passed():
    payload = _good_input()
    del payload["profiles"]["local_graphrag"]["artifact"]["artifact_hash"]
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.BLOCKED
    assert "profile_artifact_hash_missing" in decision.reason_codes


def test_artifact_hash_bad_shape_is_error():
    payload = _good_input()
    payload["profiles"]["local_graphrag"]["artifact"]["artifact_hash"] = 42
    decision = evaluate_release_decision(payload)
    assert decision.status == ReleaseDecisionStatus.ERROR


# --------------------------------------------------------------------------
# Determinism + path privacy
# --------------------------------------------------------------------------


def test_deterministic_replay_byte_identical():
    payload = _good_input()
    a = evaluate_release_decision(payload)
    b = evaluate_release_decision(payload)
    assert a == b
    assert a.decision_hash == b.decision_hash
    assert json.dumps(a.to_dict(), sort_keys=True) == json.dumps(b.to_dict(), sort_keys=True)


def test_evidence_pack_contains_no_local_path_or_user_name():
    payload = _good_input()
    decision = evaluate_release_decision(payload)
    serialised = json.dumps(decision.to_dict(), ensure_ascii=False)
    for forbidden in ("/Users", "/home", "/tmp", "Alice", "Bob"):
        assert forbidden not in serialised


def test_two_tmpdir_byte_identical_evidence_pack(tmp_path: Path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()
    payload_text = json.dumps(_good_input(), ensure_ascii=False)
    in_a = a / "input.json"
    in_b = b / "input.json"
    in_a.write_text(payload_text, encoding="utf-8")
    in_b.write_text(payload_text, encoding="utf-8")
    out_a = a / "out.json"
    out_b = b / "out.json"
    code_a = run_cli(input_path=in_a, output_path=out_a)
    code_b = run_cli(input_path=in_b, output_path=out_b)
    assert code_a == 0
    assert code_b == 0
    assert out_a.read_bytes() == out_b.read_bytes()


# --------------------------------------------------------------------------
# CLI Exit Code Contract
# --------------------------------------------------------------------------


def _cli_run(payload, tmp_path):
    in_p = tmp_path / "in.json"
    out_p = tmp_path / "out.json"
    in_p.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    code = run_cli(input_path=in_p, output_path=out_p)
    pack = json.loads(out_p.read_text(encoding="utf-8"))
    return code, pack


def test_cli_zero_for_passed(tmp_path: Path):
    code, pack = _cli_run(_good_input(), tmp_path)
    assert code == 0
    assert pack["release_decision"]["status"] == "PASSED"
    assert pack["release_decision"]["exit_code"] == 0


def test_cli_one_for_failed(tmp_path: Path):
    payload = _good_input()
    payload["citation_safety"]["standard_rag"]["contradicted_claim_rate"] = 1.0
    code, pack = _cli_run(payload, tmp_path)
    assert code == 1
    assert pack["release_decision"]["status"] == "FAILED"
    assert pack["release_decision"]["exit_code"] == 1


def test_cli_two_for_blocked(tmp_path: Path):
    payload = _good_input()
    del payload["profiles"]["local_graphrag"]
    code, pack = _cli_run(payload, tmp_path)
    assert code == 2
    assert pack["release_decision"]["status"] == "BLOCKED"
    assert pack["release_decision"]["exit_code"] == 2


def test_cli_three_for_incomparable(tmp_path: Path):
    payload = _good_input()
    payload["profiles"]["standard_rag"]["fingerprint"] = _fingerprint(
        dataset_version="different-v2"
    )
    code, pack = _cli_run(payload, tmp_path)
    assert code == 3
    assert pack["release_decision"]["status"] == "INCOMPARABLE"
    assert pack["release_decision"]["exit_code"] == 3


def test_cli_four_for_engine_error(tmp_path: Path):
    payload = _good_input()
    payload["unknown_field"] = "nope"
    code, pack = _cli_run(payload, tmp_path)
    assert code == 4
    assert pack["release_decision"]["status"] == "ERROR"
    assert pack["release_decision"]["exit_code"] == 4


def test_cli_four_for_output_unwritable(tmp_path: Path):
    payload = _good_input()
    in_p = tmp_path / "in.json"
    in_p.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    out_p = tmp_path / "outdir"
    out_p.mkdir()
    code = run_cli(input_path=in_p, output_path=out_p)
    assert code == 4


def test_cli_engine_raises_maps_to_error_not_blocked(monkeypatch, tmp_path: Path):
    """If ``evaluate_release_decision`` itself raises, the CLI emits an
    ERROR decision with exit code 4 -- never a BLOCKED status carrying the
    ERROR-only reason ``decision_input_valid``."""
    from tools.evals.zuno.rag_eval import run_phase22_release_decision as cli_module

    def _raise(_payload):
        raise ReleaseDecisionError("engine tripped")

    monkeypatch.setattr(cli_module, "evaluate_release_decision", _raise)
    in_p = tmp_path / "in.json"
    out_p = tmp_path / "out.json"
    in_p.write_text("{}", encoding="utf-8")
    code = cli_module.run_cli(input_path=in_p, output_path=out_p)
    assert code == 4
    pack = json.loads(out_p.read_text(encoding="utf-8"))
    assert pack["release_decision"]["status"] == "ERROR"
    assert pack["release_decision"]["reason_codes"] == ["decision_input_invalid"]


# --------------------------------------------------------------------------
# Closure-set invariants
# --------------------------------------------------------------------------


def test_required_top_level_gates_match_spec():
    assert set(REQUIRED_TOP_LEVEL_GATES) == {
        "core_five",
        "citation_safety",
        "critical_slice",
        "critical_slice_baseline",
        "agent_efficiency",
        "cost_latency_budget",
        "failure_buckets",
    }


def test_reason_code_closure_invariant():
    assert PASSED_REASONS == frozenset({"all_gates_passed"})
    for code in FAILED_REASONS:
        assert is_closed_reason(code)
    for code in BLOCKED_REASONS:
        assert is_closed_reason(code)
    for code in INCOMPARABLE_REASONS:
        assert is_closed_reason(code)
    for code in ERROR_REASONS:
        assert is_closed_reason(code)
    assert "high_risk_failure_bucket_present" in FAILED_REASONS
    assert "unknown_failure_bucket" in FAILED_REASONS
    assert "citation_safety_metric_missing" in BLOCKED_REASONS
    assert "critical_slice_baseline_metric_missing" in BLOCKED_REASONS
    assert "cost_latency_metric_missing" in BLOCKED_REASONS
    assert "profile_fingerprint_missing" in BLOCKED_REASONS
    assert "artifact_hash_missing" in BLOCKED_REASONS


def test_failure_bucket_taxonomy_is_closed_set():
    taxonomy = FAILURE_BUCKET_TAXONOMY
    assert isinstance(taxonomy, frozenset)
    assert "doc_miss" in taxonomy
    assert "citation_binding_miss" in taxonomy
    assert "answer_unfaithful" in taxonomy
