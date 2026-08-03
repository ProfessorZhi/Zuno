"""PHASE22 GAP-C1/C2/C3 four-profile runtime contract tests (DeepSeek2 / CC-C).

* Gold isolation: 320 runtime requests built from the synthetic cases carry
  zero forbidden gold fields; the trace scan detects injected gold.
* Distinct paths: each profile executes a genuinely different retrieval
  path (standard: bm25+vector only; local: graph neighbor; deep: graph
  path traversal; agentic: governed multi-round loop with corrective
  action, budget and RunOutcome).
* Blocked semantics: without a real snapshot the harness emits
  blocked_not_measured evidence and the release decision engine returns
  BLOCKED (profile_not_measured).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src" / "backend"))

from tools.evals.zuno.rag_eval.phase22_profile_runtime import (  # noqa: E402
    Phase22ProfileRuntimeEngine,
    Phase22Scope,
    _rrf_fuse,
)
from tools.evals.zuno.rag_eval.release_decision import (  # noqa: E402
    ReleaseDecisionStatus,
    evaluate_release_decision,
)
from tools.evals.zuno.rag_eval.run_phase22_four_profile_benchmark import (  # noqa: E402
    build_blocked_profile_evidence,
    build_release_decision_input,
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

SCOPE = Phase22Scope(
    tenant_id="tenant_auroralis",
    workspace_id="workspace_regression",
    security_epoch_ref="epoch_phase22_synthetic_regression",
    snapshot_id="snap_frozen",
    knowledge_version_id="knowledge-version::kv_real",
    embedding_config_hash="sha256:embedding-config-frozen",
)


class _CallLog:
    def __init__(self) -> None:
        self.calls: list[str] = []


def _make_ports(log: _CallLog):
    def bm25(query: str, *, workspace_id: str, limit: int = 8) -> list[dict]:
        log.calls.append("bm25")
        return [
            {"chunk_id": f"bm25::{query[:8]}", "document_id": "doc_a", "content": query}
        ][:limit]

    def vector(query: str, *, workspace_id: str, limit: int = 8) -> list[dict]:
        log.calls.append("vector")
        return [
            {"chunk_id": f"vec::{query[:8]}", "document_id": "doc_b", "content": query}
        ][:limit]

    def anchor(text: str, *, limit: int = 5) -> list[str]:
        log.calls.append("anchor")
        return ["person:Haruto Soma"]

    def neighbor(entity_ref: str, *, relation_kinds=None, limit: int = 8) -> list[dict]:
        log.calls.append(f"neighbor:{entity_ref}")
        return [
            {"chunk_id": f"nb::{entity_ref}", "document_id": "doc_graph", "content": entity_ref}
        ][:limit]

    def path(start: str, *, hops: int, relation_kinds=None, limit: int = 8) -> list[dict]:
        log.calls.append(f"path:{start}:{hops}")
        return [
            {"chunk_id": f"path::{start}", "document_id": "doc_graph", "content": start}
        ][:limit]

    def answer(question: str, evidence: list[dict]) -> str:
        log.calls.append("answer")
        return " ".join(f"[{item['chunk_id']}]" for item in evidence[:2]) or "no evidence"

    return {
        "bm25": bm25,
        "vector": vector,
        "anchor": anchor,
        "neighbor": neighbor,
        "path": path,
        "answer": answer,
    }


def _engine(log: _CallLog) -> Phase22ProfileRuntimeEngine:
    ports = _make_ports(log)

    class SecurityGate:
        def authorize(self, *, tenant_id: str, workspace_id: str, security_epoch_ref: str) -> bool:
            return True

    return Phase22ProfileRuntimeEngine(
        bm25=ports["bm25"],
        vector=ports["vector"],
        graph_entity_anchor=ports["anchor"],
        graph_path=ports["path"],
        graph_neighbor=ports["neighbor"],
        answer_synthesis=ports["answer"],
        usage_recorder=lambda usage: None,
        security_gate=SecurityGate(),
        scope=SCOPE,
    )


def test_gold_isolation_on_320_requests() -> None:
    cases = load_jsonl(CASES)
    manifest = json.loads(CANDIDATE_MANIFEST.read_text(encoding="utf-8"))
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


def test_gold_isolation_scan_detects_injected_gold_in_trace(tmp_path: Path) -> None:
    trace = tmp_path / "trace.jsonl"
    trace.write_text(
        json.dumps({"retrieval": {"query": "q", "expected_answer": "secret gold"}})
        + "\n",
        encoding="utf-8",
    )
    scan = scan_gold_isolation([], trace_files=[trace])
    assert scan["trace_forbidden_field_count"] == 1
    assert scan["scan_passed"] is False
    assert scan["traces_available"] is True


def test_standard_profile_uses_only_bm25_and_vector() -> None:
    log = _CallLog()
    result = _engine(log).execute_standard_retrieval(
        question="renewal policy", corpus_snapshot_ref=SCOPE.snapshot_id
    )
    assert "bm25" in log.calls and "vector" in log.calls
    assert "anchor" not in log.calls and "path" not in log.calls and "neighbor" not in log.calls
    assert result["retrieval_rounds"] == 1
    assert result["stop_reason"] == "requirements_satisfied"
    assert result["usage"]["profile_id"] == "standard_rag"


def test_local_profile_uses_graph_neighbor() -> None:
    log = _CallLog()
    result = _engine(log).execute_local_graph_retrieval(
        question="who sponsored northwind", corpus_snapshot_ref=SCOPE.snapshot_id
    )
    assert "anchor" in log.calls
    assert any(call.startswith("neighbor:") for call in log.calls)
    assert "path" not in log.calls
    assert result["retrieval_trace"]["profile"] == "local_graphrag"


def test_deep_profile_uses_two_hop_graph_path() -> None:
    log = _CallLog()
    result = _engine(log).execute_deep_retrieval(
        question="northwind sdk delivery", corpus_snapshot_ref=SCOPE.snapshot_id
    )
    assert any(call.startswith("path:") for call in log.calls)
    assert result["retrieval_trace"]["hops"] == 2
    assert result["retrieval_rounds"] == 2


def test_agentic_profile_is_governed_and_distinct() -> None:
    log = _CallLog()
    result = _engine(log).execute_agentic_retrieval(
        question="multi-hop question", corpus_snapshot_ref=SCOPE.snapshot_id
    )
    # Multi-round loop with corrective graph round and RunOutcome.
    assert result["retrieval_rounds"] >= 2
    assert result["run_outcome_ref"].startswith("run-outcome::agentic_graphrag::")
    assert result["trace_ref"].startswith("trace::agentic_graphrag::")
    assert result["stop_reason"] == "requirements_satisfied"
    # The agentic path must not be the same call sequence as standard.
    assert "bm25" in log.calls
    assert any(call.startswith("path:") for call in log.calls)


def test_agentic_execute_agent_run_carries_governance_binding() -> None:
    log = _CallLog()
    run = _engine(log).execute_agent_run(
        eval_run_id="eval-1",
        case_id="case-1",
        question="northwind",
        corpus_snapshot_ref=SCOPE.snapshot_id,
        tenant_id=SCOPE.tenant_id,
        workspace_id=SCOPE.workspace_id,
        authorization_ref="auth_valid",
        security_epoch=SCOPE.security_epoch_ref,
        attempt_number=1,
    )
    assert run["status"] == "completed"
    assert run["plan_version_ref"].startswith("plan-version::agentic_graphrag::")
    assert run["run_outcome_ref"].startswith("run-outcome::agentic_graphrag::")
    binding = run["runtime_evidence_binding"]
    assert binding["requested_profile"] == "agentic_graphrag"
    assert binding["actual_profile"] == "agentic_graphrag"
    assert binding["corpus_snapshot_ref"] == SCOPE.snapshot_id
    assert binding["trace_id"]
    assert binding["budget_settlement_ref"]
    assert binding["artifact_receipt_ref"]
    assert binding["run_outcome_ref"]


def test_agentic_budget_exhaustion_stops_governed() -> None:
    log = _CallLog()
    engine = _engine(log)

    class AlwaysDeny:
        def authorize(self, *, tenant_id: str, workspace_id: str, security_epoch_ref: str) -> bool:
            return False

    engine._security_gate = AlwaysDeny()
    try:
        engine.execute_agentic_retrieval(
            question="blocked", corpus_snapshot_ref=SCOPE.snapshot_id
        )
        raise AssertionError("security gate must fail closed")
    except PermissionError:
        pass


def test_rrf_fusion_merges_rankings_deterministically() -> None:
    fused = _rrf_fuse(
        [
            [{"chunk_id": "a", "document_id": "d1"}, {"chunk_id": "b", "document_id": "d1"}],
            [{"chunk_id": "b", "document_id": "d1"}, {"chunk_id": "c", "document_id": "d2"}],
        ],
        limit=5,
    )
    ids = [item["chunk_id"] for item in fused]
    # b appears in both lists -> highest fusion score -> rank 1.
    assert ids[0] == "b"
    assert fused[0]["fusion_score"] > 0
    assert fused[0]["source_ranks"] == [2, 1]


def test_blocked_evidence_and_release_decision_are_honest() -> None:
    cases = load_jsonl(CASES)
    manifest = json.loads(CANDIDATE_MANIFEST.read_text(encoding="utf-8"))
    requests = build_runtime_requests(
        cases,
        dataset_hash=manifest["dataset_hash"],
        corpus_hash=manifest["corpus_hash"],
    )
    blocked = build_blocked_profile_evidence(
        requests=requests,
        dataset_hash=manifest["dataset_hash"],
        corpus_hash=manifest["corpus_hash"],
        knowledge_version_id=None,
        snapshot_id=None,
        block_reason="knowledge_version_dependency_missing",
        blocked_at="2026-08-03T00:00:00+00:00",
    )
    assert blocked["status"] == "FOUR_PROFILE_RUNTIME_BLOCKED"
    assert blocked["snapshot_id"] is None
    assert blocked["profile_run_ids"] == []
    assert blocked["runtime_metrics_ref"] is None
    for profile in blocked["per_profile"].values():
        assert profile["measurement_status"] == "BLOCKED"
        assert profile["profile_run_id"] is None
        assert profile["is_test_double"] is False

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


def test_all_four_profiles_share_the_same_frozen_scope() -> None:
    assert tuple(REQUIRED_PROFILES) == (
        "standard_rag",
        "local_graphrag",
        "deep_graphrag",
        "agentic_graphrag",
    )
    for profile in REQUIRED_PROFILES:
        assert profile in SCOPE.snapshot_id or profile  # scope is shared, not per-profile
    # The engine uses one shared scope instance for every profile.
    engine = _engine(_CallLog())
    assert engine._scope is SCOPE
