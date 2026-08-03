"""PHASE22 GAP-C1/C2/C3 four-profile benchmark harness (DeepSeek2 / CC-C
hardening).

Truth boundary: the four profiles only run on a REAL activated snapshot.
Until then every profile reports ``NOT_RUN_DEPENDENCY_BLOCKED`` — there is
no fabricated ``RUNTIME_OBSERVED`` state and no placeholder runtime
masquerading as measurement.

Formal runtime owners (reused, never rebuilt):
* standard_rag  -> ``RagHandler.retrieve_ranked_documents``
* local_graphrag -> ``GraphRetriever.retrieve`` (Neo4j neighbor traversal)
* deep_graphrag -> ``GraphRetriever.retrieve`` (multi-hop paths)
* agentic_graphrag -> ``build_agent_graph`` + ``UnifiedAgentRuntimeService``
  (fixed AgentRunGraph + dynamic Plan DAG + StepExecutionGraph)
If an owner is missing the harness reports
``PROFILE_RUNTIME_OWNER_MISSING:<profile>`` — it never substitutes a
second runtime.

Gold isolation: runtime requests, prompts, traces, retrieval contexts,
tool arguments, planner inputs, step inputs and final synthesis inputs are
scanned for forbidden gold fields.  With zero traces the scan reports
``trace_gold_isolation_status = NOT_RUN_DEPENDENCY_BLOCKED`` — scanning
zero traces is never reported as a pass.

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

from tools.evals.zuno.rag_eval.measurement_gate import MeasurementState  # noqa: E402
from tools.evals.zuno.rag_eval.release_decision import (  # noqa: E402
    FINGERPRINT_DIMENSIONS,
    REQUIRED_PROFILE_IDS,
    ReleaseDecisionStatus,
    evaluate_release_decision,
)
from tools.evals.zuno.synthetic_benchmark.dataset_contract import load_jsonl, sha256_json  # noqa: E402
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

# Scanned gold-isolation surfaces (Task H).
GOLD_SCAN_SURFACES = (
    "runtime_request",
    "prompt",
    "trace",
    "retrieval_context",
    "tool_arguments",
    "planner_input",
    "step_input",
    "final_synthesis_input",
)

FORMAL_RUNTIME_OWNERS: dict[str, dict[str, Any]] = {
    "standard_rag": {
        "owners": [("zuno.platform.services.rag.handler", "RagHandler", "retrieve_ranked_documents")],
        "entry_api": "retrieve_ranked_documents",
    },
    "local_graphrag": {
        "owners": [("zuno.platform.services.graphrag.retriever", "GraphRetriever", "retrieve")],
        "entry_api": "retrieve (entity resolution + neighbor traversal)",
    },
    "deep_graphrag": {
        "owners": [("zuno.platform.services.graphrag.retriever", "GraphRetriever", "retrieve")],
        "entry_api": "retrieve (multi-hop path traversal)",
    },
    "agentic_graphrag": {
        "owners": [
            ("zuno.agent.runtime.graph", "build_agent_graph", None),
            ("zuno.agent.runtime.service", "UnifiedAgentRuntimeService", "start"),
        ],
        "entry_api": "start (fixed AgentRunGraph + dynamic Plan DAG + StepExecutionGraph)",
    },
}


# ---------------------------------------------------------------------------
# Formal runtime owner resolution (Task G)
# ---------------------------------------------------------------------------


def resolve_profile_runtime_owners() -> dict[str, dict[str, Any]]:
    """Resolve the formal owner of every profile without executing it.

    Returns per-profile availability; a missing owner is reported as
    ``PROFILE_RUNTIME_OWNER_MISSING`` and blocks that profile — a second
    product runtime is never built here.
    """
    resolution: dict[str, dict[str, Any]] = {}
    for profile_id in REQUIRED_PROFILES:
        spec = FORMAL_RUNTIME_OWNERS[profile_id]
        owner_labels: list[str] = []
        missing_detail: list[str] = []
        try:
            for module_name, class_name, method_name in spec["owners"]:
                owner_labels.append(f"{module_name}.{class_name}")
                module = __import__(module_name, fromlist=[class_name])
                owner = getattr(module, class_name)
                if method_name is not None:
                    method = getattr(owner, method_name, None)
                    if method is None:
                        raise AttributeError(f"{module_name}.{class_name}.{method_name} missing")
            resolution[profile_id] = {
                "owner": " + ".join(owner_labels),
                "entry_api": spec["entry_api"],
                "status": "OWNER_AVAILABLE",
            }
        except Exception as exc:  # noqa: BLE001
            resolution[profile_id] = {
                "owner": " + ".join(owner_labels) or spec["entry_api"],
                "entry_api": spec["entry_api"],
                "status": f"PROFILE_RUNTIME_OWNER_MISSING:{profile_id}",
                "detail": str(exc)[:200],
            }
    return resolution


# ---------------------------------------------------------------------------
# Gold isolation scan (Task H)
# ---------------------------------------------------------------------------


def scan_gold_isolation(
    requests: list[dict[str, Any]],
    trace_files: list[Path] | None = None,
) -> dict[str, Any]:
    """Scan every available gold-isolation surface.

    With no trace files the trace-level status is
    ``NOT_RUN_DEPENDENCY_BLOCKED`` — zero scanned traces never reads as a
    pass.
    """
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
        "surfaces": list(GOLD_SCAN_SURFACES),
        "request_scan_count": len(requests),
        "request_forbidden_field_count": len(request_forbidden),
        "request_forbidden_fields": sorted(set(request_forbidden))[:20],
        "trace_scan_file_count": len(scanned_files),
        "trace_scan_files": scanned_files,
        "trace_forbidden_field_count": len(trace_forbidden),
        "trace_forbidden_fields": sorted(set(trace_forbidden))[:20],
        "trace_gold_isolation_status": (
            "NOT_RUN_DEPENDENCY_BLOCKED" if not scanned_files else "SCANNED"
        ),
        "forbidden_field_count": len(request_forbidden) + len(trace_forbidden),
        # A full pass requires every surface to have been scanned; zero
        # trace files can never read as a complete gold-isolation pass.
        "scan_passed": not request_forbidden and not trace_forbidden and bool(scanned_files),
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
# Blocked evidence (snapshot not activated) — Task F
# ---------------------------------------------------------------------------


def build_blocked_profile_evidence(
    *,
    requests: list[dict[str, Any]],
    dataset_hash: str,
    corpus_hash: str,
    knowledge_version_id: str | None,
    snapshot_id: str | None,
    block_reason: str,
    owner_resolution: dict[str, dict[str, Any]],
    blocked_at: str,
) -> dict[str, Any]:
    per_profile: dict[str, dict[str, Any]] = {}
    for profile_id in REQUIRED_PROFILES:
        owner = owner_resolution.get(profile_id, {})
        reason_codes = [block_reason]
        if owner.get("status", "").startswith("PROFILE_RUNTIME_OWNER_MISSING"):
            reason_codes.append(owner["status"])
        per_profile[profile_id] = {
            "profile_id": profile_id,
            "profile_run_id": None,
            "case_id": None,
            "snapshot_id": None,
            "knowledge_version_id": None,
            "trace_ref": None,
            "retrieval_evidence_ref": None,
            "citation_evidence_ref": None,
            "usage_ref": None,
            "latency": None,
            "run_outcome_ref": None,
            "runtime_fingerprint": None,
            "artifact_hash": None,
            "measurement_status": MeasurementState.BLOCKED.value,
            "measurement_reason": ",".join(reason_codes),
            "runtime_owner": owner.get("status", "OWNER_UNAVAILABLE"),
            "is_test_double": False,
        }
    return {
        "schema_version": "1.0.0",
        "track_id": "machine_attested_synthetic_regression",
        "evidence_kind": "four_profile_runtime",
        "worker": "deepseek2-cc-b34c",
        "status": "FOUR_PROFILE_RUNTIME_NOT_RUN_DEPENDENCY_BLOCKED",
        "block_reason": block_reason,
        "blocked_at": blocked_at,
        "dataset_hash": dataset_hash,
        "corpus_hash": corpus_hash,
        "knowledge_version_id": knowledge_version_id,
        "snapshot_id": snapshot_id,
        "request_count": len(requests),
        "profile_count": len(REQUIRED_PROFILES),
        "profiles": list(REQUIRED_PROFILES),
        "per_profile": per_profile,
        "profile_run_ids": [],
        "runtime_metrics_ref": None,
        "metrics_computed": False,
        "runtime_owner_resolution": owner_resolution,
    }


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
    parser.add_argument("--dependency-pr", default="112")
    parser.add_argument("--dependency-head-sha", default="ce495af2a39c01379878a9e2c1bb58d876456b1e")
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
    owner_resolution = resolve_profile_runtime_owners()

    missing_owners = [
        profile_id
        for profile_id, info in owner_resolution.items()
        if info.get("status", "").startswith("PROFILE_RUNTIME_OWNER_MISSING")
    ]

    if knowledge_version_id is None or snapshot_id is None or missing_owners:
        block_reasons: list[str] = []
        if knowledge_version_id is None:
            block_reasons.append(KNOWLEDGE_VERSION_DEPENDENCY_BLOCK_REASON)
        elif snapshot_id is None:
            block_reasons.append(SNAPSHOT_DEPENDENCY_BLOCK_REASON)
        for profile_id in missing_owners:
            block_reasons.append(f"PROFILE_RUNTIME_OWNER_MISSING:{profile_id}")
        block_reason = ",".join(block_reasons)

        blocked_evidence = build_blocked_profile_evidence(
            requests=requests,
            dataset_hash=dataset_hash,
            corpus_hash=corpus_hash,
            knowledge_version_id=knowledge_version_id,
            snapshot_id=snapshot_id,
            block_reason=block_reason,
            owner_resolution=owner_resolution,
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
        # A real activated snapshot is present and every formal runtime
        # owner resolves. Execution is the coordinator's next step: this
        # harness would dispatch the 320 requests through the formal owners
        # (RagHandler / GraphRetriever / UnifiedAgentRuntimeService) and
        # the measurement gate. No placeholder runtime is used.
        evidence = {
            "schema_version": "1.0.0",
            "track_id": "machine_attested_synthetic_regression",
            "evidence_kind": "four_profile_runtime",
            "worker": "deepseek2-cc-b34c",
            "status": "FOUR_PROFILE_RUNTIME_READY_FOR_MEASUREMENT",
            "dataset_hash": dataset_hash,
            "corpus_hash": corpus_hash,
            "knowledge_version_id": knowledge_version_id,
            "snapshot_id": snapshot_id,
            "request_count": len(requests),
            "per_profile": {
                profile_id: {
                    "profile_id": profile_id,
                    "profile_run_id": None,
                    "measurement_status": MeasurementState.PREPARED.value,
                    "measurement_reason": "awaiting_measurement_dispatch",
                }
                for profile_id in REQUIRED_PROFILES
            },
            "profile_run_ids": [],
            "runtime_metrics_ref": None,
            "metrics_computed": False,
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
                "dependency_accepted": False,
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
            "trace_gold_isolation_status": gold_scan["trace_gold_isolation_status"],
            "runtime_owner_resolution": owner_resolution,
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


if __name__ == "__main__":
    raise SystemExit(main())
