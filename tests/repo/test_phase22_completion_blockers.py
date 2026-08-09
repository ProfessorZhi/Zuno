from __future__ import annotations

import json
import shutil
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFY_PHASE22 = REPO_ROOT / "tools" / "scripts" / "verify_phase22_completion_blockers.py"


def _load_verifier():
    spec = spec_from_file_location("verify_phase22_completion_blockers", VERIFY_PHASE22)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _copy_fixture(tmp_path: Path) -> Path:
    fixture_root = tmp_path / "repo"
    paths = [
        ".agent/programs/program-manifest.yaml",
        ".agent/programs/PHASE22_fixed-benchmark-production-readiness-and-closure.md",
        ".agent/programs/closure-checklist.md",
        ".agent/programs/work-products/phase22-removal-candidates.yaml",
        "docs/status/production-readiness.md",
        "docs/evidence/goal05-phase22-blocked-benchmark/benchmark_manifest.json",
        "docs/evidence/goal05-phase22-blocked-benchmark/metrics.json",
        "docs/evidence/goal05-phase22-public-benchmark-review-pack/integrity_report.json",
        "docs/evidence/goal05-phase22-public-benchmark-review-pack/reviewed/review_summary.json",
        "docs/evidence/goal05-phase22-public-benchmark-review-pack/reviewed/reviewed_cases.jsonl",
        "docs/evidence/goal05-phase22-public-benchmark-review-pack/reviewed/review_decisions.jsonl",
        "docs/evidence/goal05-phase22-synthetic-benchmark/INVALIDATION_NOTICE.md",
    ]
    for relative in paths:
        source = REPO_ROOT / relative
        target = fixture_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return fixture_root


def test_phase22_completion_blockers_match_current_truth() -> None:
    verifier = _load_verifier()
    assert verifier.verify_phase22_completion_blockers() == []


def test_phase22_completed_fails_when_benchmark_is_blocked(tmp_path: Path) -> None:
    verifier = _load_verifier()
    fixture = _copy_fixture(tmp_path)
    manifest_path = fixture / ".agent/programs/program-manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    for phase in manifest["phases"]:
        if phase["id"] == "PHASE22":
            phase["state"] = "completed"
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    errors = verifier.verify_phase22_completion_blockers(fixture)

    assert any("PHASE22 must remain in_progress" in error for error in errors)


def test_program_archive_fails_when_benchmark_is_blocked(tmp_path: Path) -> None:
    verifier = _load_verifier()
    fixture = _copy_fixture(tmp_path)
    manifest_path = fixture / ".agent/programs/program-manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["program"]["state"] = "no-active"
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    errors = verifier.verify_phase22_completion_blockers(fixture)

    assert any("program state must remain active" in error for error in errors)


def test_production_ready_claim_fails_when_benchmark_is_blocked(tmp_path: Path) -> None:
    verifier = _load_verifier()
    fixture = _copy_fixture(tmp_path)
    readiness_path = fixture / "docs/status/production-readiness.md"
    readiness_path.write_text(
        "# Production Readiness\n\nstatus: production_ready\nquality_proven: true\n",
        encoding="utf-8",
    )

    errors = verifier.verify_phase22_completion_blockers(fixture)

    assert any("production readiness" in error and "production ready" in error for error in errors)


def test_active_removal_candidate_fails(tmp_path: Path) -> None:
    verifier = _load_verifier()
    fixture = _copy_fixture(tmp_path)
    removals_path = fixture / ".agent/programs/work-products/phase22-removal-candidates.yaml"
    removals = yaml.safe_load(removals_path.read_text(encoding="utf-8"))
    removals["mandatory_removal_candidates"][0]["current_status"] = "active_candidate"
    removals_path.write_text(yaml.safe_dump(removals, sort_keys=False), encoding="utf-8")

    errors = verifier.verify_phase22_completion_blockers(fixture)

    assert any("mandatory removal candidates remain active" in error for error in errors)


def test_measured_benchmark_must_not_use_blocked_manifest(tmp_path: Path) -> None:
    verifier = _load_verifier()
    fixture = _copy_fixture(tmp_path)
    benchmark_path = fixture / "docs/evidence/goal05-phase22-blocked-benchmark/benchmark_manifest.json"
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    benchmark["status"] = "PASSED"
    benchmark["measurement_status"] = "measured"
    benchmark["actual_case_count"] = 80
    benchmark_path.write_text(json.dumps(benchmark), encoding="utf-8")

    errors = verifier.verify_phase22_completion_blockers(fixture)

    assert any("status must be BLOCKED" in error for error in errors)


def test_blocked_benchmark_artifact_hash_mismatch_fails(tmp_path: Path) -> None:
    verifier = _load_verifier()
    fixture = _copy_fixture(tmp_path)
    benchmark_path = fixture / "docs/evidence/goal05-phase22-blocked-benchmark/benchmark_manifest.json"
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    benchmark["artifact_refs"]["metrics_json"]["sha256"] = "0" * 64
    benchmark_path.write_text(json.dumps(benchmark), encoding="utf-8")

    errors = verifier.verify_phase22_completion_blockers(fixture)

    assert any("artifact hash mismatch" in error for error in errors)


def test_review_approval_hash_mismatch_fails(tmp_path: Path) -> None:
    verifier = _load_verifier()
    fixture = _copy_fixture(tmp_path)
    summary_path = fixture / "docs/evidence/goal05-phase22-public-benchmark-review-pack/reviewed/review_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["reviewed_case_set_sha256"] = "0" * 64
    summary_path.write_text(json.dumps(summary), encoding="utf-8")

    errors = verifier.verify_phase22_completion_blockers(fixture)

    assert any("reviewed case set hash mismatch" in error for error in errors)


def test_blocked_benchmark_missing_artifact_fails(tmp_path: Path) -> None:
    verifier = _load_verifier()
    fixture = _copy_fixture(tmp_path)
    metrics_path = fixture / "docs/evidence/goal05-phase22-blocked-benchmark/metrics.json"
    metrics_path.unlink()

    errors = verifier.verify_phase22_completion_blockers(fixture)

    assert any("missing blocked benchmark artifact" in error for error in errors)


def test_missing_synthetic_invalidation_notice_fails(tmp_path: Path) -> None:
    verifier = _load_verifier()
    fixture = _copy_fixture(tmp_path)
    notice_path = fixture / "docs/evidence/goal05-phase22-synthetic-benchmark/INVALIDATION_NOTICE.md"
    notice_path.unlink()

    errors = verifier.verify_phase22_completion_blockers(fixture)

    assert any("missing required PHASE22 closure evidence" in error for error in errors)


def test_synthetic_invalidation_notice_must_preserve_runtime_boundary(tmp_path: Path) -> None:
    verifier = _load_verifier()
    fixture = _copy_fixture(tmp_path)
    notice_path = fixture / "docs/evidence/goal05-phase22-synthetic-benchmark/INVALIDATION_NOTICE.md"
    notice_path.write_text(
        "# INVALIDATION NOTICE\n\nThis benchmark is fine.\n",
        encoding="utf-8",
    )

    errors = verifier.verify_phase22_completion_blockers(fixture)

    assert any("synthetic benchmark invalidation notice missing" in error for error in errors)
