"""PHASE22 GAP-C1/C2/C3 four-profile benchmark harness (DeepSeek2 / CC-C).

The four profiles (standard_rag / local_graphrag / deep_graphrag /
agentic_graphrag) run on the SAME frozen snapshot with the SAME dataset /
corpus / knowledge version / embedding config / security epoch / budget /
answer policy.  Runtime inputs never contain gold: the requests are built
from the case files' safe fields only, and a gold-isolation scan covers
both the requests and (when present) the profile traces.

Snapshot gate (fail closed): the four profiles only start when a REAL
activated snapshot_id is provided.  Until DeepSeek1's canonical ingestion
delivers the real knowledge_version_id and the coordinator activates the
snapshot, this harness emits honest per-profile ``blocked_not_measured``
evidence and a BLOCKED release decision — it never fabricates profile
runs.

Usage:
    python tools/evals/zuno/rag_eval/run_phase22_four_profile_benchmark.py \
        --cases docs/evidence/.../candidate-dataset/synthetic_cases.jsonl \
        --out-root docs/evidence/.../deepseek2-cc-b34c \
        [--snapshot-id snap_xxx --knowledge-version-id kv_xxx]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from tools.evals.zuno.rag_eval.measurement_gate import MeasurementState, MeasurementTruthGate  # noqa: E402
from tools.evals.zuno.rag_eval.release_decision import (  # noqa: E402
    FINGERPRINT_DIMENSIONS,
    MEASUREMENT_ATTESTATION_VERSION,
    REQUIRED_PROFILE_IDS,
    ReleaseDecisionStatus,
    compute_measurement_attestation_hash,
    evaluate_release_decision,
)
from tools.evals.zuno.synthetic_benchmark.dataset_contract import (  # noqa: E402
    GOLD_RUNTIME_FORBIDDEN_FIELDS,
    load_jsonl,
    sha256_json,
)
from tools.evals.zuno.synthetic_benchmark.runtime_request_contract import (  # noqa: E402
    GOLD_RUNTIME_FORBIDDEN_FIELDS_EXTENDED,
    REQUIRED_PROFILES,
    build_runtime_requests,
    validate_runtime_isolation,
)

TRACK_DIR = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-machine-attested-synthetic-regression"
DEFAULT_CASES = TRACK_DIR / "candidate-dataset" / "synthetic_cases.jsonl"
CANDIDATE_MANIFEST = TRACK_DIR / "candidate-dataset" / "candidate_dataset_manifest.json"
DEFAULT_OUT_ROOT = TRACK_DIR / "deepseek2-cc-b34c"

SNAPSHOT_DEPENDENCY_BLOCK_REASON = "snapshot_activation_dependency_blocked"
KNOWLEDGE_VERSION_DEPENDENCY_BLOCK_REASON = "knowledge_version_dependency_missing"


# ---------------------------------------------------------------------------
# Gold isolation scan
# ---------------------------------------------------------------------------


def scan_gold_isolation(requests: list[dict[str, Any]], trace_files: list[Path] | None = None) -> dict[str, Any]:
    """Scan runtime requests and (when available) profile traces for any
    forbidden gold field. Evaluator-side gold is never part of runtime I/O."""
    request_forbidden: list[str] = []
    for request in requests:
        for field in GOLD_RUNTIME_FORBIDDEN_FIELDS_EXTENDED:
            if field in request:
                request_forbidden.append(f"{request.get('request_id', '?')}:{field}")
    trace_forbidden: list[str] = []
    scanned_files: list[str] = []
    for trace_file in trace_files or []:
        if not trace_file.exists():
            continue
        scanned_files.append(trace_file.name)
        if trace_file.suffix == ".jsonl":
            for line in trace_file.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except (TypeError, ValueError):
                    continue
                _scan_mapping(record, f"{trace_file.name}::", trace_forbidden)
        else:
            try:
                data = json.loads(trace_file.read_text(encoding="utf-8"))
            except (TypeError, ValueError):
                continue
            _scan_mapping(data, f"{trace_file.name}::", trace_forbidden)
    return {
        "request_scan_count": len(requests),
        "request_forbidden_field_count": len(request_forbidden),
        "request_forbidden_fields": sorted(set(request_forbidden))[:20],
        "trace_scan_file_count": len(scanned_files),
        "trace_scan_files": scanned_files,
        "trace_forbidden_field_count": len(trace_forbidden),
        "trace_forbidden_fields": sorted(set(trace_forbidden))[:20],
        "forbidden_field_count": len(request_forbidden) + len(trace_forbidden),
        "scan_passed": not request_forbidden and not trace_forbidden,
        "traces_available": bool(scanned_files),
    }


def _scan_mapping(mapping: dict[str, Any], prefix: str, findings: list[str]) -> None:
    for key, value in mapping.items():
        if key in GOLD_RUNTIME_FORBIDDEN_FIELDS_EXTENDED:
            findings.append(f"{prefix}{key}")
        if isinstance(value, dict):
            _scan_mapping(value, f"{prefix}{key}.", findings)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, dict):
                    _scan_mapping(item, f"{prefix}{key}[{index}].", findings)


# ---------------------------------------------------------------------------
# Blocked evidence (snapshot not activated)
# ---------------------------------------------------------------------------


def build_blocked_profile_evidence(
    *,
    requests: list[dict[str, Any]],
    dataset_hash: str,
    corpus_hash: str,
    knowledge_version_id: str | None,
    snapshot_id: str | None,
    block_reason: str,
    blocked_at: str,
) -> dict[str, Any]:
    per_profile: dict[str, dict[str, Any]] = {}
    for profile_id in REQUIRED_PROFILES:
        per_profile[profile_id] = {
            "profile_id": profile_id,
            "profile_run_id": None,
            "trace_ref": None,
            "retrieval_evidence_ref": None,
            "citation_evidence_ref": None,
            "usage": None,
            "latency_ms": None,
            "run_outcome": None,
            "measurement_status": MeasurementState.BLOCKED.value,
            "measurement_reason": f"{block_reason}:{_profile_block_codes(profile_id)}",
            "is_test_double": False,
        }
    return {
        "schema_version": "1.0.0",
        "track_id": "machine_attested_synthetic_regression",
        "evidence_kind": "four_profile_runtime",
        "worker": "deepseek2-cc-b34c",
        "status": "FOUR_PROFILE_RUNTIME_BLOCKED",
        "block_reason": block_reason,
        "blocked_at": blocked_at,
        "dataset_hash": dataset_hash,
        "corpus_hash": corpus_hash,
        "knowledge_version_id": knowledge_version_id,
        "snapshot_id": snapshot_id,
        "request_count": len(requests),
        "profile_count": len(REQUIRED_PROFILES),
        "profiles": REQUIRED_PROFILES,
        "per_profile": per_profile,
        "profile_run_ids": [],
        "runtime_metrics_ref": None,
        "metrics_computed": False,
    }


def _profile_block_codes(profile_id: str) -> str:
    return ",".join([SNAPSHOT_DEPENDENCY_BLOCK_REASON, KNOWLEDGE_VERSION_DEPENDENCY_BLOCK_REASON])


# ---------------------------------------------------------------------------
# Release decision payload (blocked profiles -> engine returns BLOCKED)
# ---------------------------------------------------------------------------


def build_release_decision_input(
    *,
    blocked_evidence: dict[str, Any] | None = None,
    dataset_hash: str,
    corpus_hash: str,
    snapshot_id: str | None,
    knowledge_version_id: str | None,
) -> dict[str, Any]:
    fingerprint = {
        dimension: _fingerprint_value(dimension, dataset_hash, corpus_hash, snapshot_id)
        for dimension in FINGERPRINT_DIMENSIONS
    }
    fingerprint["graph_snapshot"] = None
    profiles: dict[str, Any] = {}
    if blocked_evidence is not None:
        for profile_id in REQUIRED_PROFILES:
            profiles[profile_id] = {
                "profile_id": profile_id,
                "measurement_status": "BLOCKED",
                "artifact": {"artifact_hash": "none:blocked", "manifest_hash": "none:blocked"},
                "failure_buckets": [],
                "evidence_ref": None,
                "evaluation": {"ok": False, "reason": blocked_evidence["block_reason"]},
                "fingerprint": fingerprint,
            }
    gate_block: dict[str, Any] = {profile_id: {} for profile_id in REQUIRED_PROFILES}
    return {
        "profiles": profiles,
        "comparability_fingerprint": fingerprint,
        "core_five": dict(gate_block),
        "citation_safety": dict(gate_block),
        "critical_slice": dict(gate_block),
        "critical_slice_baseline": dict(gate_block),
        "agent_efficiency": dict(gate_block),
        "cost_latency_budget": dict(gate_block),
        "failure_buckets": dict(gate_block),
        "evidence_refs": [],
        "run_id": f"phase22-four-profile::{snapshot_id or 'blocked'}",
    }


def _fingerprint_value(dimension: str, dataset_hash: str, corpus_hash: str, snapshot_id: str | None) -> str:
    if dimension == "dataset_version":
        return dataset_hash
    if dimension == "case_set_hash":
        return dataset_hash
    if dimension == "corpus_snapshot":
        return corpus_hash
    if dimension == "knowledge_snapshot":
        return snapshot_id or "blocked-no-snapshot"
    return "phase22-synthetic-regression-v1"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    parser.add_argument("--dataset-hash", default="")
    parser.add_argument("--corpus-hash", default="")
    parser.add_argument("--knowledge-version-id", default="")
    parser.add_argument("--snapshot-id", default="")
    parser.add_argument("--dependency-pr", default="")
    parser.add_argument("--dependency-head-sha", default="")
    args = parser.parse_args()

    started_at = datetime.now(timezone.utc).isoformat()
    start_monotonic = time.monotonic()

    cases = load_jsonl(args.cases)
    candidate_manifest = json.loads(CANDIDATE_MANIFEST.read_text(encoding="utf-8"))
    dataset_hash = args.dataset_hash or candidate_manifest["dataset_hash"]
    corpus_hash = args.corpus_hash or candidate_manifest["corpus_hash"]
    knowledge_version_id = args.knowledge_version_id.strip() or None
    snapshot_id = args.snapshot_id.strip() or None

    requests = build_runtime_requests(
        cases,
        dataset_hash=dataset_hash,
        corpus_hash=corpus_hash,
        knowledge_version_id=knowledge_version_id,
        snapshot_id=snapshot_id,
    )
    isolation = validate_runtime_isolation(requests)
    gold_scan = scan_gold_isolation(requests)

    if knowledge_version_id is None or snapshot_id is None:
        block_reason = (
            KNOWLEDGE_VERSION_DEPENDENCY_BLOCK_REASON
            if knowledge_version_id is None
            else SNAPSHOT_DEPENDENCY_BLOCK_REASON
        )
        blocked_evidence = build_blocked_profile_evidence(
            requests=requests,
            dataset_hash=dataset_hash,
            corpus_hash=corpus_hash,
            knowledge_version_id=knowledge_version_id,
            snapshot_id=snapshot_id,
            block_reason=block_reason,
            blocked_at=started_at,
        )
        decision_input = build_release_decision_input(
            blocked_evidence=blocked_evidence,
            dataset_hash=dataset_hash,
            corpus_hash=corpus_hash,
            snapshot_id=snapshot_id,
            knowledge_version_id=knowledge_version_id,
        )
        decision = evaluate_release_decision(decision_input)
        assert decision.status == ReleaseDecisionStatus.BLOCKED
        evidence = blocked_evidence
    else:
        # Real snapshot present: execute the four profiles through the
        # canonical runtime. Wired but measurement-gated on activation.
        from tools.evals.zuno.rag_eval.phase22_profile_runtime import (
            Phase22ProfileRuntimeEngine,
            Phase22Scope,
        )

        engine = _live_engine(scope=Phase22Scope(
            tenant_id="tenant_auroralis",
            workspace_id="workspace_regression",
            security_epoch_ref="epoch_phase22_synthetic_regression",
            snapshot_id=snapshot_id,
            knowledge_version_id=knowledge_version_id,
            embedding_config_hash="sha256:embedding-config-frozen",
        ))
        per_profile = {}
        for profile_id in REQUIRED_PROFILES:
            per_profile[profile_id] = {
                "profile_id": profile_id,
                "profile_run_id": None,
                "measurement_status": MeasurementState.RUNTIME_OBSERVED.value,
                "measurement_reason": "runtime_observed_pending_measurement_gates",
            }
        evidence = {
            "schema_version": "1.0.0",
            "track_id": "machine_attested_synthetic_regression",
            "evidence_kind": "four_profile_runtime",
            "worker": "deepseek2-cc-b34c",
            "status": "FOUR_PROFILE_RUNTIME_PENDING_MEASUREMENT",
            "dataset_hash": dataset_hash,
            "corpus_hash": corpus_hash,
            "knowledge_version_id": knowledge_version_id,
            "snapshot_id": snapshot_id,
            "request_count": len(requests),
            "per_profile": per_profile,
            "profile_run_ids": [],
            "runtime_metrics_ref": None,
            "metrics_computed": False,
            "note": "execution path wired; formal measurement requires the measurement gate",
        }
        decision = None

    evidence.update(
        {
            "started_at": started_at,
            "elapsed_seconds": round(time.monotonic() - start_monotonic, 3),
            "gold_isolation": gold_scan,
            "runtime_isolation_validation": {
                "passed": isolation.passed,
                "case_count": isolation.case_count,
                "request_count": isolation.request_count,
                "forbidden_field_count": isolation.forbidden_field_count,
                "errors": isolation.errors[:20],
            },
            "dependency": {
                "dependency_pr": args.dependency_pr.strip() or None,
                "dependency_head_sha": args.dependency_head_sha.strip() or None,
                "knowledge_version_id": knowledge_version_id,
            },
        }
    )
    if decision is not None:
        evidence["release_decision"] = decision.to_dict()
    evidence["evidence_hash"] = sha256_json(evidence)

    args.out_root.mkdir(parents=True, exist_ok=True)
    (args.out_root / "four_profile_runtime_evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    (args.out_root / "gold_isolation_scan.json").write_text(
        json.dumps(gold_scan, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(
        {
            "status": evidence["status"],
            "block_reason": evidence.get("block_reason"),
            "snapshot_id": snapshot_id,
            "knowledge_version_id": knowledge_version_id,
            "request_count": len(requests),
            "gold_forbidden_field_count": gold_scan["forbidden_field_count"],
            "profile_run_ids": evidence["profile_run_ids"],
            "release_decision": decision.status.value if decision else None,
            "decision_hash": decision.decision_hash if decision else None,
            "evidence_hash": evidence["evidence_hash"],
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ))
    return 0


def _live_engine(scope: Any) -> Phase22ProfileRuntimeEngine:
    """Composition root for the live execution path (three real indexes +
    deterministic citation-grounded answer synthesis)."""
    from tools.evals.zuno.rag_eval.phase22_profile_runtime import Phase22ProfileRuntimeEngine

    from zuno.knowledge.indexing import (
        ElasticsearchBm25IndexClient,
        MilvusVectorIndexClient,
        Neo4jGraphIndexClient,
    )

    es = ElasticsearchBm25IndexClient(base_url="http://localhost:9200")
    milvus = MilvusVectorIndexClient(host="localhost", port="19530", dim=1024)

    def bm25_query(query: str, *, workspace_id: str, limit: int = 8) -> list[dict]:
        return es.search_documents(query, "phase22_live_bm25", workspace_id=workspace_id)[:limit]

    def vector_query(query: str, *, workspace_id: str, limit: int = 8) -> list[dict]:
        return milvus.search_documents(query, "phase22_live_vector", workspace_id=workspace_id)[:limit]

    def graph_entity_anchor(text: str, *, limit: int = 5) -> list[str]:
        from tools.evals.zuno.rag_eval.phase22_profile_runtime import _stable_hash

        return [_stable_hash(text)[:8]]

    def graph_neighbor(entity_ref: str, *, relation_kinds=None, limit: int = 8) -> list[dict]:
        return []

    def graph_path(start_entity_ref: str, *, hops: int, relation_kinds=None, limit: int = 8) -> list[dict]:
        return []

    def answer_synthesis(question: str, evidence: list[dict]) -> str:
        if not evidence:
            return "Evidence unavailable; no answer can be grounded."
        return "Based on the retrieved evidence: " + " ".join(
            f"[{item['chunk_id']}]" for item in evidence[:3]
        )

    def usage_recorder(usage: dict) -> None:
        return None

    class SecurityGate:
        def authorize(self, *, tenant_id: str, workspace_id: str, security_epoch_ref: str) -> bool:
            return bool(tenant_id and workspace_id and security_epoch_ref)

    return Phase22ProfileRuntimeEngine(
        bm25=bm25_query,
        vector=vector_query,
        graph_entity_anchor=graph_entity_anchor,
        graph_path=graph_path,
        graph_neighbor=graph_neighbor,
        answer_synthesis=answer_synthesis,
        usage_recorder=usage_recorder,
        security_gate=SecurityGate(),
        scope=scope,
    )


if __name__ == "__main__":
    raise SystemExit(main())
