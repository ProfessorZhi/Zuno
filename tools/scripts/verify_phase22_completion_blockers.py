from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]

PROGRAM_MANIFEST = Path(".agent/programs/program-manifest.yaml")
PHASE22_FILE = Path(".agent/programs/PHASE22_fixed-benchmark-production-readiness-and-closure.md")
CLOSURE_CHECKLIST = Path(".agent/programs/closure-checklist.md")
PRODUCTION_READINESS = Path("docs/status/production-readiness.md")
BENCHMARK_MANIFEST = Path(
    "docs/evidence/goal05-phase22-blocked-benchmark/benchmark_manifest.json"
)
REVIEW_INTEGRITY_REPORT = Path(
    "docs/evidence/goal05-phase22-public-benchmark-review-pack/integrity_report.json"
)
REMOVAL_CANDIDATES = Path(".agent/programs/work-products/phase22-removal-candidates.yaml")


def _read_text(repo_root: Path, relative_path: Path) -> str:
    return (repo_root / relative_path).read_text(encoding="utf-8")


def _read_yaml(repo_root: Path, relative_path: Path) -> Any:
    return yaml.safe_load(_read_text(repo_root, relative_path))


def _read_json(repo_root: Path, relative_path: Path) -> Any:
    return json.loads(_read_text(repo_root, relative_path))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    content = path.read_bytes().replace(b"\r\n", b"\n")
    digest.update(content)
    return digest.hexdigest()


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


def _is_benchmark_blocked(benchmark: dict[str, Any], review: dict[str, Any]) -> bool:
    return (
        benchmark.get("status") == "BLOCKED"
        or benchmark.get("measurement_status") == "blocked_not_measured"
        or benchmark.get("actual_case_count") == 0
        or benchmark.get("benchmark_eligible_case_count") == 0
        or review.get("overall_status") == "REVIEW_REQUIRED"
        or review.get("reviewer_approved_count") == 0
        or review.get("benchmark_eligible_count") == 0
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
    repo_root: Path,
    benchmark: dict[str, Any],
    errors: list[str],
) -> None:
    artifact_refs = benchmark.get("artifact_refs")
    if not isinstance(artifact_refs, dict):
        errors.append("blocked benchmark manifest artifact_refs must be an object")
        return

    benchmark_dir = repo_root / BENCHMARK_MANIFEST.parent
    for artifact_name, artifact_meta in sorted(artifact_refs.items()):
        if not isinstance(artifact_meta, dict):
            errors.append(
                f"blocked benchmark artifact {artifact_name!r} metadata must be an object"
            )
            continue
        relative_path = artifact_meta.get("path")
        expected_sha = artifact_meta.get("sha256")
        if not isinstance(relative_path, str) or not relative_path:
            errors.append(
                f"blocked benchmark artifact {artifact_name!r} missing path"
            )
            continue
        if not isinstance(expected_sha, str) or len(expected_sha) != 64:
            errors.append(
                f"blocked benchmark artifact {artifact_name!r} missing sha256"
            )
            continue
        artifact_path = benchmark_dir / relative_path
        if not artifact_path.exists():
            errors.append(
                f"missing blocked benchmark artifact: {artifact_name} -> {relative_path}"
            )
            continue
        actual_sha = _sha256_file(artifact_path)
        if actual_sha != expected_sha:
            errors.append(
                f"blocked benchmark artifact hash mismatch: {artifact_name} "
                f"expected {expected_sha} got {actual_sha}"
            )


def verify_phase22_completion_blockers(repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    required_files = [
        PROGRAM_MANIFEST,
        PHASE22_FILE,
        CLOSURE_CHECKLIST,
        PRODUCTION_READINESS,
        BENCHMARK_MANIFEST,
        REVIEW_INTEGRITY_REPORT,
        REMOVAL_CANDIDATES,
    ]
    for relative_path in required_files:
        _require_file(repo_root, relative_path, errors)
    if errors:
        return errors

    manifest = _read_yaml(repo_root, PROGRAM_MANIFEST)
    benchmark = _read_json(repo_root, BENCHMARK_MANIFEST)
    review = _read_json(repo_root, REVIEW_INTEGRITY_REPORT)
    removals = _read_yaml(repo_root, REMOVAL_CANDIDATES)
    phase22_text = _read_text(repo_root, PHASE22_FILE)
    closure_text = _read_text(repo_root, CLOSURE_CHECKLIST)
    readiness_text = _read_text(repo_root, PRODUCTION_READINESS)

    program_state = manifest.get("program", {}).get("state")
    current_phase = manifest.get("program", {}).get("current_phase")
    phase22_state = _phase_state(manifest, "PHASE22")
    benchmark_blocked = _is_benchmark_blocked(benchmark, review)

    if current_phase != "PHASE22":
        errors.append(f"program current_phase must remain PHASE22 while closure is open, got {current_phase!r}")

    if benchmark_blocked:
        if program_state != "active":
            errors.append(
                f"program state must remain active while PHASE22 benchmark/review is blocked, got {program_state!r}"
            )
        if phase22_state != "in_progress":
            errors.append(
                f"PHASE22 must remain in_progress while benchmark/review is blocked, got {phase22_state!r}"
            )
        for label, text in [
            ("PHASE22 file", phase22_text),
            ("production readiness", readiness_text),
        ]:
            if _claims_production_ready(text):
                errors.append(
                    f"{label} appears to claim production ready or quality proven while benchmark/review is blocked"
                )

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
    _verify_blocked_benchmark_artifacts(repo_root, benchmark, errors)
    if review.get("overall_status") != "REVIEW_REQUIRED":
        errors.append(
            f"public benchmark review pack must remain REVIEW_REQUIRED until human review, got {review.get('overall_status')!r}"
        )
    for field in ["reviewer_approved_count", "benchmark_eligible_count"]:
        if review.get(field) != 0:
            errors.append(f"public benchmark review {field} must remain 0 until approval, got {review.get(field)!r}")

    active_removals = [
        candidate.get("path", "<unknown>")
        for candidate in removals.get("mandatory_removal_candidates", [])
        if candidate.get("current_status") == "active_candidate"
    ]
    if active_removals:
        errors.append(
            "PHASE22 mandatory removal candidates remain active: "
            + ", ".join(active_removals)
        )

    if "PHASE22 remains `in_progress`" not in phase22_text:
        errors.append("PHASE22 file must explicitly say PHASE22 remains `in_progress`")
    if "[ ] PHASE22" not in closure_text:
        errors.append("closure checklist must keep PHASE22 unchecked")
    if "[ ] `.agent/programs/` 恢复 no-active" not in closure_text:
        errors.append("closure checklist must keep the no-active reset unchecked")
    if "不能声明 quality proven、22/22 completed 或 production ready" not in readiness_text:
        errors.append(
            "production-readiness.md must keep the explicit no quality-proven / no 22/22 / no production-ready boundary"
        )

    return errors


def main() -> int:
    errors = verify_phase22_completion_blockers()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PHASE22 completion blocker gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
