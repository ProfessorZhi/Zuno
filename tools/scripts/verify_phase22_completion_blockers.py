from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
PROGRAM_ID = "zuno-canonical-architecture-runtime-realization-v1"
PROGRAM_ROOT = Path(".agent/programs")
ARCHIVE_ROOT = Path("docs/history/programs") / PROGRAM_ID

PROGRAM_MANIFEST = PROGRAM_ROOT / "program-manifest.yaml"
PHASE22_FILE = PROGRAM_ROOT / "PHASE22_fixed-benchmark-production-readiness-and-closure.md"
CLOSURE_CHECKLIST = PROGRAM_ROOT / "closure-checklist.md"
REMOVAL_CANDIDATES = PROGRAM_ROOT / "work-products/phase22-removal-candidates.yaml"
PRODUCTION_READINESS = Path("docs/status/production-readiness.md")
FINAL_VERIFICATION_REPORT = Path("docs/evidence/goal05-phase22-verification-report.md")
BENCHMARK_MANIFEST = Path(
    "docs/evidence/goal05-phase22-blocked-benchmark/benchmark_manifest.json"
)
REVIEW_INTEGRITY_REPORT = Path(
    "docs/evidence/goal05-phase22-public-benchmark-review-pack/integrity_report.json"
)
REVIEW_APPROVAL_SUMMARY = Path(
    "docs/evidence/goal05-phase22-public-benchmark-review-pack/reviewed/review_summary.json"
)
SYNTHETIC_INVALIDATION_NOTICE = Path(
    "docs/evidence/goal05-phase22-synthetic-benchmark/INVALIDATION_NOTICE.md"
)


def _read_text(repo_root: Path, relative_path: Path) -> str:
    return (repo_root / relative_path).read_text(encoding="utf-8")


def _read_yaml(repo_root: Path, relative_path: Path) -> Any:
    return yaml.safe_load(_read_text(repo_root, relative_path))


def _read_json(repo_root: Path, relative_path: Path) -> Any:
    return json.loads(_read_text(repo_root, relative_path))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes().replace(b"\r\n", b"\n"))
    return digest.hexdigest()


def _program_file(repo_root: Path, active_path: Path) -> Path:
    """Resolve an active file or its immutable archived copy."""
    active = repo_root / active_path
    if active.exists():
        return active_path
    return ARCHIVE_ROOT / active_path.relative_to(PROGRAM_ROOT)


def _require_file(repo_root: Path, relative_path: Path, errors: list[str]) -> bool:
    if not (repo_root / relative_path).exists():
        errors.append(f"missing required PHASE22 closure evidence: {relative_path.as_posix()}")
        return False
    return True


def _phase_state(manifest: dict[str, Any], phase_id: str) -> str | None:
    for phase in manifest.get("phases", []):
        if phase.get("id") == phase_id:
            return phase.get("state")
    return None


def _is_benchmark_blocked(benchmark: dict[str, Any], approval: dict[str, Any]) -> bool:
    return (
        benchmark.get("status") == "BLOCKED"
        or benchmark.get("measurement_status") == "blocked_not_measured"
        or benchmark.get("actual_case_count") == 0
        or benchmark.get("benchmark_eligible_case_count") == 0
        or approval.get("overall_status") != "PASS"
        or approval.get("benchmark_eligible_count", 0) < approval.get("total_cases", 0)
    )


def _claims_production_ready(text: str) -> bool:
    positive_claims = [
        "status: production_ready",
        "production_ready: true",
        "quality_proven: true",
        "production readiness completed",
        "production ready established",
        "22/22 completed",
        "phase01-phase22 completed",
        "phase01–phase22 completed",
        "生产可用已建立",
        "生产就绪已建立",
    ]
    negative_markers = ["不得", "不能", "不代表", "未建立", "not ", "not_", "not-"]
    for line in text.splitlines():
        lowered = line.lower()
        if any(marker in lowered for marker in negative_markers):
            continue
        if any(claim in lowered for claim in positive_claims):
            return True
    return False


def _verify_blocked_benchmark_artifacts(
    repo_root: Path, benchmark: dict[str, Any], errors: list[str]
) -> None:
    artifact_refs = benchmark.get("artifact_refs")
    if not isinstance(artifact_refs, dict):
        errors.append("blocked benchmark manifest artifact_refs must be an object")
        return

    benchmark_dir = repo_root / BENCHMARK_MANIFEST.parent
    for artifact_name, artifact_meta in sorted(artifact_refs.items()):
        if not isinstance(artifact_meta, dict):
            errors.append(f"blocked benchmark artifact {artifact_name!r} metadata must be an object")
            continue
        relative_path = artifact_meta.get("path")
        expected_sha = artifact_meta.get("sha256")
        if not isinstance(relative_path, str) or not relative_path:
            errors.append(f"blocked benchmark artifact {artifact_name!r} missing path")
            continue
        if not isinstance(expected_sha, str) or len(expected_sha) != 64:
            errors.append(f"blocked benchmark artifact {artifact_name!r} missing sha256")
            continue
        artifact_path = benchmark_dir / relative_path
        if not artifact_path.exists():
            errors.append(f"missing blocked benchmark artifact: {artifact_name} -> {relative_path}")
            continue
        actual_sha = _sha256_file(artifact_path)
        if actual_sha != expected_sha:
            errors.append(
                f"blocked benchmark artifact hash mismatch: {artifact_name} "
                f"expected {expected_sha} got {actual_sha}"
            )


def _resolve_repo_relative_file(
    repo_root: Path, raw_path: Any, label: str, errors: list[str]
) -> Path | None:
    if not isinstance(raw_path, str) or not raw_path.strip():
        errors.append(f"review approval {label} path must be a non-empty relative path")
        return None
    path = Path(raw_path)
    if path.is_absolute():
        errors.append(f"review approval {label} path must be relative")
        return None
    resolved = (repo_root / path).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError:
        errors.append(f"review approval {label} path escapes repository root")
        return None
    if not resolved.exists():
        errors.append(f"missing review approval {label}: {raw_path}")
        return None
    return resolved


def _read_jsonl_objects(path: Path, label: str, errors: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        errors.append(f"review approval {label} is not readable")
        return rows
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            errors.append(f"review approval {label} contains invalid JSON at line {line_number}")
            continue
        if not isinstance(value, dict):
            errors.append(f"review approval {label} line {line_number} must be an object")
            continue
        rows.append(value)
    return rows


def _verify_review_approval_summary(
    repo_root: Path, summary: dict[str, Any], errors: list[str]
) -> None:
    candidate_path = _resolve_repo_relative_file(
        repo_root, summary.get("source_candidate_pack"), "candidate pack", errors
    )
    reviewed_path = _resolve_repo_relative_file(
        repo_root, summary.get("reviewed_case_set"), "reviewed case set", errors
    )
    decisions_path = _resolve_repo_relative_file(
        repo_root, summary.get("review_decisions"), "review decisions", errors
    )
    if candidate_path is not None and summary.get("source_candidate_pack_sha256") != _sha256_file(candidate_path):
        errors.append("review approval candidate pack hash mismatch")
    if reviewed_path is not None and summary.get("reviewed_case_set_sha256") != _sha256_file(reviewed_path):
        errors.append("review approval reviewed case set hash mismatch")
    if decisions_path is not None and summary.get("review_decisions_sha256") != _sha256_file(decisions_path):
        errors.append("review approval decision ledger hash mismatch")
    if reviewed_path is None or decisions_path is None:
        return

    reviewed = _read_jsonl_objects(reviewed_path, "reviewed case set", errors)
    decisions = _read_jsonl_objects(decisions_path, "review decisions", errors)
    if len(reviewed) != summary.get("total_cases"):
        errors.append("reviewed case set count does not match review summary")
    if len(decisions) != summary.get("total_cases"):
        errors.append("review decision count does not match review summary")

    approved = sum(
        1
        for case in reviewed
        if case.get("reviewer_status") == "approved" and case.get("benchmark_eligible") is True
    )
    rejected = sum(1 for case in reviewed if case.get("reviewer_status") == "rejected")
    pending = sum(1 for case in reviewed if case.get("reviewer_status") == "pending")
    if approved != summary.get("reviewer_approved_count"):
        errors.append("reviewed case approved count does not match review summary")
    if approved != summary.get("benchmark_eligible_count"):
        errors.append("reviewed case eligible count does not match review summary")
    if rejected != summary.get("rejected_or_incomplete_count"):
        errors.append("reviewed case rejected count does not match review summary")
    if pending:
        errors.append("reviewed case set must not contain pending decisions")


def _verify_synthetic_invalidation_notice(repo_root: Path, errors: list[str]) -> None:
    if not _require_file(repo_root, SYNTHETIC_INVALIDATION_NOTICE, errors):
        return
    text = _read_text(repo_root, SYNTHETIC_INVALIDATION_NOTICE)
    required_phrases = [
        "d7566624",
        "INVALIDATED",
        "non-canonical simulation",
        "in-process deterministic\nsubstring matching",
        "Port reachable",
        "Index Ready",
        "canonical_runtime_not_executed",
        "SUCCESS_REAL_INGESTION",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            errors.append(
                "synthetic benchmark invalidation notice missing required truth phrase: "
                f"{phrase!r}"
            )


def _closure_fields(manifest: dict[str, Any]) -> tuple[list[Any], list[Any], dict[str, Any]]:
    engineering = manifest.get("program", {}).get("engineering_closure", {})
    if not isinstance(engineering, dict):
        return [], [], {}
    repository = engineering.get("repository_owned_blockers", [])
    external = engineering.get("external_qualification_blockers", [])
    return (
        repository if isinstance(repository, list) else ["invalid_repository_owned_blockers_field"],
        external if isinstance(external, list) else ["invalid_external_qualification_blockers_field"],
        engineering,
    )


def verify_phase22_completion_blockers(repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    resolved_program = {
        "manifest": _program_file(repo_root, PROGRAM_MANIFEST),
        "phase22": _program_file(repo_root, PHASE22_FILE),
        "checklist": _program_file(repo_root, CLOSURE_CHECKLIST),
        "removals": _program_file(repo_root, REMOVAL_CANDIDATES),
    }
    required_files = [
        *resolved_program.values(),
        PRODUCTION_READINESS,
        BENCHMARK_MANIFEST,
        REVIEW_INTEGRITY_REPORT,
        REVIEW_APPROVAL_SUMMARY,
        SYNTHETIC_INVALIDATION_NOTICE,
    ]
    for relative_path in required_files:
        _require_file(repo_root, relative_path, errors)
    if errors:
        return errors

    manifest = _read_yaml(repo_root, resolved_program["manifest"])
    benchmark = _read_json(repo_root, BENCHMARK_MANIFEST)
    review_integrity = _read_json(repo_root, REVIEW_INTEGRITY_REPORT)
    review_approval = _read_json(repo_root, REVIEW_APPROVAL_SUMMARY)
    removals = _read_yaml(repo_root, resolved_program["removals"])
    phase22_text = _read_text(repo_root, resolved_program["phase22"])
    closure_text = _read_text(repo_root, resolved_program["checklist"])
    readiness_text = _read_text(repo_root, PRODUCTION_READINESS)
    _verify_review_approval_summary(repo_root, review_approval, errors)
    _verify_blocked_benchmark_artifacts(repo_root, benchmark, errors)
    _verify_synthetic_invalidation_notice(repo_root, errors)

    program_state = manifest.get("program", {}).get("state")
    phase22_state = _phase_state(manifest, "PHASE22")
    benchmark_blocked = _is_benchmark_blocked(benchmark, review_approval)
    repository_blockers, external_blockers, engineering = _closure_fields(manifest)

    if not benchmark_blocked:
        errors.append("PHASE22 blocked benchmark evidence no longer records the external qualification block")
    if benchmark.get("status") != "BLOCKED":
        errors.append(f"blocked benchmark manifest status must be BLOCKED, got {benchmark.get('status')!r}")
    if benchmark.get("measurement_status") != "blocked_not_measured":
        errors.append(
            "blocked benchmark manifest measurement_status must be blocked_not_measured, "
            f"got {benchmark.get('measurement_status')!r}"
        )
    if benchmark.get("actual_case_count") != 0:
        errors.append(
            f"blocked benchmark actual_case_count must remain 0, got {benchmark.get('actual_case_count')!r}"
        )
    if benchmark_blocked and not external_blockers:
        errors.append("external qualification blockers must remain visible when benchmark measurement is blocked")

    if phase22_state == "completed":
        if program_state not in {"completed", "archived", "no-active"}:
            errors.append(f"completed PHASE22 requires completed/archived program state, got {program_state!r}")
        if engineering.get("status") != "completed":
            errors.append("completed PHASE22 requires engineering_closure.status: completed")
        if engineering.get("decision") != "archive_allowed":
            errors.append("completed PHASE22 requires engineering_closure.decision: archive_allowed")
        if repository_blockers:
            errors.append(
                "PHASE22 cannot complete with repository-owned blockers: "
                + ", ".join(str(item) for item in repository_blockers)
            )
        for label, text in [("PHASE22 file", phase22_text), ("production readiness", readiness_text)]:
            if _claims_production_ready(text):
                errors.append(f"{label} appears to claim production ready or quality proven")
        for phrase in [
            "status: completed",
            "engineering_closure: completed",
            "measurement: blocked_external",
            "quality: not_yet_proven",
            "production_readiness: not_established",
        ]:
            if phrase not in phase22_text:
                errors.append(f"PHASE22 final status missing phrase: {phrase}")
        for phrase in [
            "[x] PHASE22",
            "[x] `.agent/programs/` 恢复",
            "repository_owned_blockers: 0",
            "external_qualification_blockers",
        ]:
            if phrase not in closure_text:
                errors.append(f"final closure checklist missing phrase: {phrase}")
        for phrase in [
            "engineering_closure: completed",
            "measurement: blocked_external",
            "quality: not_yet_proven",
            "production_readiness: not_established",
        ]:
            if phrase not in readiness_text:
                errors.append(f"production-readiness.md missing final PHASE22 phrase: {phrase}")
    elif phase22_state == "in_progress":
        if program_state != "active":
            errors.append(f"in-progress PHASE22 requires active program state, got {program_state!r}")
        if "PHASE22 remains `in_progress`" not in phase22_text:
            errors.append("in-progress PHASE22 file must explicitly say PHASE22 remains `in_progress`")
    else:
        errors.append(f"PHASE22 manifest state must be in_progress or completed, got {phase22_state!r}")

    if review_integrity.get("invalid_count") != 0 or review_integrity.get("unverifiable_count") != 0:
        errors.append("public benchmark candidate integrity must have zero invalid or unverifiable cases")

    total_cases = review_approval.get("total_cases")
    approved_count = review_approval.get("reviewer_approved_count")
    eligible_count = review_approval.get("benchmark_eligible_count")
    rejected_count = review_approval.get("rejected_or_incomplete_count")
    if not isinstance(total_cases, int) or total_cases <= 0:
        errors.append("public benchmark review total_cases must be a positive integer")
    if not isinstance(approved_count, int) or not 0 <= approved_count <= (total_cases or 0):
        errors.append("public benchmark review reviewer_approved_count is out of range")
    if not isinstance(eligible_count, int) or not 0 <= eligible_count <= (total_cases or 0):
        errors.append("public benchmark review benchmark_eligible_count is out of range")
    if approved_count != eligible_count:
        errors.append("reviewer_approved_count and benchmark_eligible_count must match")
    if isinstance(rejected_count, int) and isinstance(total_cases, int) and approved_count + rejected_count != total_cases:
        errors.append("approved plus rejected review counts must equal total_cases")
    if review_approval.get("overall_status") not in {"REVIEW_REQUIRED", "REVIEW_PARTIAL", "PASS"}:
        errors.append("public benchmark review overall_status must be REVIEW_REQUIRED, REVIEW_PARTIAL, or PASS")

    active_removals = [
        candidate.get("path", "<unknown>")
        for candidate in removals.get("mandatory_removal_candidates", [])
        if candidate.get("current_status") == "active_candidate"
    ]
    if active_removals:
        errors.append("repository-owned mandatory removal blockers remain: " + ", ".join(active_removals))

    return errors


def main() -> int:
    errors = verify_phase22_completion_blockers()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PHASE22 completion blocker classification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
