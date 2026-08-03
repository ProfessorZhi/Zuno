"""PHASE22 GAP-C1/C2/C3 four-profile runtime truth contract tests
(DeepSeek2 / CC-C hardening).

* Gold isolation: 320 runtime requests from the synthetic cases carry zero
  forbidden gold fields; the trace scan detects injected gold; with zero
  trace files the trace status is NOT_RUN_DEPENDENCY_BLOCKED and never a
  pass.
* No false runtime evidence: without a real snapshot every profile is
  BLOCKED (NOT_RUN_DEPENDENCY_BLOCKED), profile_run_ids stay empty and no
  RUNTIME_OBSERVED state is fabricated.
* Formal runtime owners: the four profiles resolve to the formal owners
  (RagHandler / GraphRetriever / build_agent_graph) — no placeholder
  runtime is built; a missing owner reports PROFILE_RUNTIME_OWNER_MISSING.
* Release decision on blocked profiles is BLOCKED (profile_not_measured).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src" / "backend"))

from tools.evals.zuno.rag_eval.release_decision import (  # noqa: E402
    ReleaseDecisionStatus,
    evaluate_release_decision,
)
from tools.evals.zuno.rag_eval.run_phase22_four_profile_benchmark import (  # noqa: E402
    GOLD_SCAN_SURFACES,
    build_blocked_profile_evidence,
    build_release_decision_input,
    resolve_profile_runtime_owners,
    scan_gold_isolation,
)
from tools.evals.zuno.synthetic_benchmark.dataset_contract import load_jsonl  # noqa: E402
from tools.evals.zuno.synthetic_benchmark.runtime_request_contract import (  # noqa: E402
    GOLD_RUNTIME_FORBIDDEN_FIELDS_EXTENDED,
    REQUIRED_PROFILES,
    build_runtime_requests,
    validate_runtime_isolation,
)

TRACK_DIR = ROOT / "docs" / "evidence" / "goal05-phase22-machine-attested-synthetic-regression"
CASES = TRACK_DIR / "candidate-dataset" / "synthetic_cases.jsonl"
CANDIDATE_MANIFEST = TRACK_DIR / "candidate-dataset" / "candidate_dataset_manifest.json"


def _load() -> tuple[list[dict], dict]:
    cases = load_jsonl(CASES)
    manifest = json.loads(CANDIDATE_MANIFEST.read_text(encoding="utf-8"))
    return cases, manifest


def test_gold_isolation_on_320_requests() -> None:
    cases, manifest = _load()
    requests = build_runtime_requests(
        cases,
        dataset_hash=manifest["dataset_hash"],
        corpus_hash=manifest["corpus_hash"],
    )
    validation = validate_runtime_isolation(requests)
    assert validation.passed
    assert validation.case_count == 80
    assert validation.request_count == 320
    assert validation.forbidden_field_count == 0
    assert not (GOLD_RUNTIME_FORBIDDEN_FIELDS_EXTENDED & set(requests[0]))
    assert "derivation_spec" not in requests[0]
    assert "expected_answer" not in requests[0]
    assert "world_model" not in requests[0]


def test_gold_isolation_scan_surfaces_are_covered() -> None:
    for surface in (
        "runtime_request",
        "prompt",
        "trace",
        "retrieval_context",
        "tool_arguments",
        "planner_input",
        "step_input",
        "final_synthesis_input",
    ):
        assert surface in GOLD_SCAN_SURFACES


def test_gold_isolation_scan_detects_injected_gold_in_trace(tmp_path: Path) -> None:
    trace = tmp_path / "trace.jsonl"
    trace.write_text(
        json.dumps(
            {
                "prompt": {"text": "answer the question"},
                "retrieval_context": [{"content": "evidence"}],
                "tool_arguments": {"expected_answer": "secret gold"},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    scan = scan_gold_isolation([], trace_files=[trace])
    assert scan["trace_forbidden_field_count"] == 1
    assert scan["trace_gold_isolation_status"] == "SCANNED"
    assert scan["scan_passed"] is False
    assert scan["traces_available"] is True


def test_gold_isolation_scan_with_zero_traces_is_not_a_pass() -> None:
    scan = scan_gold_isolation([{"request_id": "r1", "question": "q"}])
    assert scan["trace_scan_file_count"] == 0
    assert scan["trace_gold_isolation_status"] == "NOT_RUN_DEPENDENCY_BLOCKED"
    assert scan["scan_passed"] is False
    assert scan["traces_available"] is False


def test_formal_runtime_owners_resolve() -> None:
    resolution = resolve_profile_runtime_owners()
    for profile_id in REQUIRED_PROFILES:
        status = resolution[profile_id]["status"]
        assert status == "OWNER_AVAILABLE", (
            f"{profile_id} owner missing: {status} — must not be substituted "
            "with a placeholder runtime"
        )
        assert resolution[profile_id]["entry_api"]


def test_blocked_evidence_never_fabricates_runtime_observed() -> None:
    cases, manifest = _load()
    requests = build_runtime_requests(
        cases,
        dataset_hash=manifest["dataset_hash"],
        corpus_hash=manifest["corpus_hash"],
    )
    owner_resolution = resolve_profile_runtime_owners()
    blocked = build_blocked_profile_evidence(
        requests=requests,
        dataset_hash=manifest["dataset_hash"],
        corpus_hash=manifest["corpus_hash"],
        knowledge_version_id=None,
        snapshot_id=None,
        block_reason="knowledge_version_dependency_missing",
        owner_resolution=owner_resolution,
        blocked_at="2026-08-03T00:00:00+00:00",
    )
    assert blocked["status"] == "FOUR_PROFILE_RUNTIME_NOT_RUN_DEPENDENCY_BLOCKED"
    assert blocked["snapshot_id"] is None
    assert blocked["profile_run_ids"] == []
    assert blocked["runtime_metrics_ref"] is None
    for profile in blocked["per_profile"].values():
        assert profile["measurement_status"] == "BLOCKED"
        assert profile["profile_run_id"] is None
        assert profile["trace_ref"] is None
        assert profile["run_outcome_ref"] is None
        assert profile["artifact_hash"] is None
        assert profile["is_test_double"] is False
        # No fabricated RUNTIME_OBSERVED anywhere.
        assert profile["measurement_status"] != "RUNTIME_OBSERVED"


def test_blocked_evidence_reports_owner_missing() -> None:
    cases, manifest = _load()
    requests = build_runtime_requests(
        cases,
        dataset_hash=manifest["dataset_hash"],
        corpus_hash=manifest["corpus_hash"],
    )
    owner_resolution = {
        "standard_rag": {"status": "PROFILE_RUNTIME_OWNER_MISSING:standard_rag"},
        "local_graphrag": {"status": "OWNER_AVAILABLE"},
        "deep_graphrag": {"status": "OWNER_AVAILABLE"},
        "agentic_graphrag": {"status": "OWNER_AVAILABLE"},
    }
    blocked = build_blocked_profile_evidence(
        requests=requests,
        dataset_hash=manifest["dataset_hash"],
        corpus_hash=manifest["corpus_hash"],
        knowledge_version_id=None,
        snapshot_id=None,
        block_reason="knowledge_version_dependency_missing",
        owner_resolution=owner_resolution,
        blocked_at="2026-08-03T00:00:00+00:00",
    )
    assert "PROFILE_RUNTIME_OWNER_MISSING:standard_rag" in blocked["per_profile"]["standard_rag"]["measurement_reason"]


def test_blocked_release_decision_is_honest() -> None:
    cases, manifest = _load()
    requests = build_runtime_requests(
        cases,
        dataset_hash=manifest["dataset_hash"],
        corpus_hash=manifest["corpus_hash"],
    )
    owner_resolution = resolve_profile_runtime_owners()
    blocked = build_blocked_profile_evidence(
        requests=requests,
        dataset_hash=manifest["dataset_hash"],
        corpus_hash=manifest["corpus_hash"],
        knowledge_version_id=None,
        snapshot_id=None,
        block_reason="knowledge_version_dependency_missing",
        owner_resolution=owner_resolution,
        blocked_at="2026-08-03T00:00:00+00:00",
    )
    decision = evaluate_release_decision(
        build_release_decision_input(
            blocked_evidence=blocked,
            dataset_hash=manifest["dataset_hash"],
            corpus_hash=manifest["corpus_hash"],
            snapshot_id=None,
            knowledge_version_id=None,
        )
    )
    assert decision.status == ReleaseDecisionStatus.BLOCKED
    assert "profile_not_measured" in decision.reason_codes
    assert decision.decision_hash


def test_all_four_profiles_share_frozen_contract() -> None:
    assert tuple(REQUIRED_PROFILES) == (
        "standard_rag",
        "local_graphrag",
        "deep_graphrag",
        "agentic_graphrag",
    )
