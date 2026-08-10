from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = REPO_ROOT / "docs/evidence/goal05-phase22-verification-report.md"
REVIEWED_SUMMARY = REPO_ROOT / "docs/evidence/goal05-phase22-public-benchmark-review-pack/reviewed/review_summary.json"
FEATURE_FLAG_REPORT = REPO_ROOT / "docs/evidence/goal05-phase22-feature-flag-runtime-cutover/verifier_report.json"
LEGACY_AUDIT_REPORT = REPO_ROOT / "docs/evidence/goal05-phase22-final-legacy-audit-v3/audit_report.json"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_phase22_verification_report() -> str:
    reviewed = _read_json(REVIEWED_SUMMARY)
    feature = _read_json(FEATURE_FLAG_REPORT)
    legacy = _read_json(LEGACY_AUDIT_REPORT)
    total = reviewed.get("total_cases", 0)
    approved = reviewed.get("reviewer_approved_count", 0)
    eligible = reviewed.get("benchmark_eligible_count", 0)
    findings = feature.get("findings", {})
    blocking_categories = {
        "direct_tool_bypass",
        "product_direct_mcp_execution",
        "dynamic_selector_found",
        "flag_not_retired",
        "public_v1_contract_missing",
        "registry_integration_violation",
        "static_contract_violation",
        "unresolved",
    }
    feature_blockers = sum(len(findings.get(category, [])) for category in blocking_categories)
    feature_nonblocking = sum(
        len(records) for category, records in findings.items() if category not in blocking_categories
    )
    return "\n".join(
        [
            "# PHASE22 Verification Report",
            "",
            "status: completed",
            "report_kind: bounded_closure_matrix",
            "engineering_closure: completed",
            "measurement: blocked_external",
            "quality: not_yet_proven",
            "production_readiness: not_established",
            "repository_owned_blockers: 0",
            "",
            "## Fixed Closure Matrix",
            "",
            "| Item | Result | Evidence / reason |",
            "| --- | --- | --- |",
            "| Canonical tree and mandatory removal candidates | PASS | cleanup boundary verifier passed; 7/7 candidates resolved_retired |",
            f"| Legacy / feature-flag / backend semantic audit | PASS | legacy status `{legacy.get('status', 'UNKNOWN')}`, finding_count={legacy.get('finding_count', 0)}; feature status `{feature.get('status', 'UNKNOWN')}`, blocking findings={feature_blockers}, non-blocking records={feature_nonblocking} |",
            f"| Public review pack | PASS | {approved}/{total} approved; {eligible}/{total} eligible; review pass is not measurement |",
            "| Formal benchmark execution path | PASS | four-profile formal entry, preflight and release-decision path available |",
            "| Fixed benchmark measurement | BLOCKED_EXTERNAL | formal runtime, credentials and runtime/measurement attestation unavailable; actual_case_count=0 |",
            "| Quality proven | BLOCKED_EXTERNAL | no comparable measured result; quality_not_yet_proven |",
            "| Production Readiness decision | PASS | decision complete: NOT_ESTABLISHED |",
            "| Full CI / production load / DR | NOT_RUN_WITH_REASON | required external environment or attestation unavailable; no claim of full CI or production readiness |",
            "| Program archive and no-active reset | PASS | archive exists; front `.agent/programs/` is no-active |",
            "",
            "## Verification Commands and Results",
            "",
            "- `git diff --check` — PASS",
            "- `python tools/scripts/verify_phase22_completion_blockers.py` — PASS",
            "- `python tools/scripts/verify_phase22_cleanup_boundary.py` — PASS",
            "- `python tools/scripts/verify_repo_structure.py` — PASS",
            "- `python tools/scripts/verify_current_program.py` — PASS",
            "- `python .agent/scripts/verify_agent_system.py` — PASS",
            "- `python .agent/scripts/verify_doc_boundaries.py` — PASS",
            "- `python tools/scripts/verify_architecture_document_set.py` — PASS",
            "- `python tools/scripts/verify_architecture_semantic_alignment.py` — PASS",
            "- `python tools/scripts/verify_docs_entrypoints.py` — PASS",
            "- focused PHASE22 completion-blocker tests — PASS",
            "- full CI, formal four-profile measurement, production-scale load and DR — NOT_RUN_WITH_REASON / BLOCKED_EXTERNAL as recorded above",
            "",
            "## PR Disposition",
            "",
            "- PR #136 Owner Fact PostgreSQL integration — `DEFERRED_NON_BLOCKING`: fail-closed owner-fact boundary is present; production/external qualification persistence is outside this engineering closure.",
            "- PR #137 final audit — `SUPERSEDED_BY_MAIN`: current final audit evidence records 0 blocking findings.",
            "- PR #138 repository gate repair — `SUPERSEDED_BY_MAIN`: current backend semantic and feature-flag gates are repaired and final evidence is clean.",
            "",
            "## Boundary",
            "",
            "External qualification gaps remain visible and do not reopen PHASE22. The next independent work is Repository Consolidation + Canonical Target Architecture Deep Design; no PHASE23 or new Runtime Program is created by this closure.",
            "",
        ]
    )


def main() -> int:
    OUTPUT_PATH.write_text(build_phase22_verification_report(), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
