from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from tools.evals.zuno.rag_eval.profile_runners import (
    AgenticGraphRAGProfileRunner,
    BenchmarkCaseInput,
    DeepGraphRAGProfileRunner,
    LocalGraphRAGProfileRunner,
    StandardRAGProfileRunner,
)
from zuno.platform.observability.trace_adapter import NoopTraceAdapter


REPO_ROOT = Path(__file__).resolve().parents[4]
CANDIDATE_PACK_FILE = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-public-benchmark-review-pack" / "candidate_cases.jsonl"
SMOKE_OUTPUT_DIR = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-profile-contract-smoke"
LEGACY_DRY_RUN_DIR = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-dry-run-output"


def load_subset_candidates() -> list[dict[str, Any]]:
    lines = CANDIDATE_PACK_FILE.read_text(encoding="utf-8").splitlines()
    cases = [json.loads(line) for line in lines if line.strip()]
    
    # Pick 2 per slice
    by_slice: dict[str, list[dict[str, Any]]] = {}
    for c in cases:
        ref = c.get("corpus_snapshot_ref", "default")
        by_slice.setdefault(ref, []).append(c)

    subset: list[dict[str, Any]] = []
    for slice_ref, items in by_slice.items():
        subset.extend(items[:2])
    return subset


def run_contract_smoke() -> dict[str, Any]:
    SMOKE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LEGACY_DRY_RUN_DIR.mkdir(parents=True, exist_ok=True)

    candidates = load_subset_candidates()
    assert len(candidates) >= 6, f"Expected at least 6 candidate cases, got {len(candidates)}"

    trace_adapter = NoopTraceAdapter()
    runners = {
        "standard_rag": StandardRAGProfileRunner(trace_adapter),
        "graphrag_local": LocalGraphRAGProfileRunner(trace_adapter),
        "graphrag_global": DeepGraphRAGProfileRunner(trace_adapter),
        "agentic_graphrag": AgenticGraphRAGProfileRunner(trace_adapter),
    }

    results_by_profile: dict[str, list[dict[str, Any]]] = {}

    for c in candidates:
        case_in = BenchmarkCaseInput(
            case_id=c["case_id"],
            question=c["question"],
            question_type=c["question_type"],
            gold_document_refs=tuple(c.get("gold_document_refs", ())),
            gold_evidence_refs=tuple(c.get("gold_evidence_refs", ())),
            corpus_snapshot_ref=c["corpus_snapshot_ref"],
        )
        for pname, runner in runners.items():
            res = runner.run_case(case_in)
            results_by_profile.setdefault(pname, []).append({
                "case_id": res.case_id,
                "profile_name": res.profile_name,
                "status": res.status,
                "is_test_double": res.is_test_double,
                "measurement_state": res.measurement_state,
                "blocked_reason": res.blocked_reason,
                "answer": res.answer,
                "standard_floor_preserved": res.standard_floor_preserved,
                "retrieved_doc_count": len(res.retrieved_doc_refs),
            })

    case_ids = [c["case_id"] for c in candidates]
    case_set_hash = hashlib.sha256(json.dumps(case_ids, sort_keys=True).encode("utf-8")).hexdigest()

    manifest = {
        "benchmark_type": "profile_contract_smoke_run",
        "runner_type": "deterministic_test_doubles",
        "measurement_state": "MEASUREMENT_BLOCKED",
        "blocked_reason": "not_measured_test_double_runner",
        "status": "CONTRACT_SMOKE_COMPLETED",
        "reviewer_approved_count": 0,
        "benchmark_eligible_count": 0,
        "candidate_cases_evaluated": len(candidates),
        "case_set_hash": case_set_hash,
        "profiles_evaluated": list(runners.keys()),
        "langsmith_tracing": "noop_disabled",
        "paid_llm_invoked": False,
        "reproduce_command": "python -m tools.evals.zuno.rag_eval.run_dry_run_benchmark",
    }

    (SMOKE_OUTPUT_DIR / "smoke_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (SMOKE_OUTPUT_DIR / "smoke_results.json").write_text(json.dumps(results_by_profile, ensure_ascii=False, indent=2), encoding="utf-8")

    report = {
        "status": "CONTRACT_SMOKE_COMPLETED",
        "output_dir": str(SMOKE_OUTPUT_DIR.relative_to(REPO_ROOT)),
        "candidates_count": len(candidates),
        "measurement_state": "MEASUREMENT_BLOCKED",
        "blocked_reason": "not_measured_test_double_runner",
        "runner_type": "test_double",
    }
    (SMOKE_OUTPUT_DIR / "smoke_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    readme = """# Goal05 Phase22 Profile Contract Smoke Output

- **Status**: `CONTRACT_SMOKE_COMPLETED`
- **Measurement State**: `MEASUREMENT_BLOCKED`
- **Blocked Reason**: `not_measured_test_double_runner`
- **Runner Type**: `deterministic_test_doubles`
- **Purpose**: Contract smoke testing and schema validation only. This is NOT a formal benchmark measurement run.
"""
    (SMOKE_OUTPUT_DIR / "README.md").write_text(readme, encoding="utf-8")

    # Mark legacy dry run output files as superseded / not formal evidence
    legacy_manifest = {
        "status": "superseded",
        "note": "Superseded by Profile Contract Smoke Run; test doubles were used.",
        "measurement_state": "MEASUREMENT_BLOCKED",
        "blocked_reason": "not_measured_test_double_runner",
    }
    (LEGACY_DRY_RUN_DIR / "dry_run_manifest.json").write_text(json.dumps(legacy_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (LEGACY_DRY_RUN_DIR / "dry_run_report.json").write_text(json.dumps(legacy_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (LEGACY_DRY_RUN_DIR / "README.md").write_text("# Legacy Dry Run Output (Superseded)\n\nThis directory contains superseded contract smoke outputs. Formal benchmark measurement was NOT performed.\n", encoding="utf-8")

    return report


def main() -> int:
    report = run_contract_smoke()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

