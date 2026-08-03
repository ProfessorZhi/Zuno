from __future__ import annotations

import json
import shutil
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFY_TRACK = REPO_ROOT / "tools" / "scripts" / "verify_phase22_synthetic_regression_track.py"


def _load_verifier():
    spec = spec_from_file_location("verify_phase22_synthetic_regression_track", VERIFY_TRACK)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _copy_fixture(tmp_path: Path) -> Path:
    fixture = tmp_path / "repo"
    paths = [
        "docs/evidence/goal05-phase22-machine-attested-synthetic-regression/track_manifest.json",
        "docs/evidence/goal05-phase22-machine-attested-synthetic-regression/readiness-report.md",
        "docs/evidence/goal05-phase22-machine-attested-synthetic-regression/pr100-file-classification.json",
        "docs/evidence/goal05-phase22-machine-attested-synthetic-regression/seed-dataset/seed_dataset_manifest.json",
        "docs/evidence/goal05-phase22-machine-attested-synthetic-regression/seed-dataset/world_model.json",
        "docs/evidence/goal05-phase22-machine-attested-synthetic-regression/candidate-dataset/candidate_dataset_manifest.json",
        "docs/evidence/goal05-phase22-machine-attested-synthetic-regression/candidate-dataset/candidate_derivation_report.json",
        "docs/evidence/goal05-phase22-machine-attested-synthetic-regression/candidate-dataset/world_model.json",
        "docs/evidence/goal05-phase22-public-benchmark-review-pack/approval_summary.json",
        "docs/evidence/goal05-phase22-public-benchmark-review-pack/integrity_report.json",
        "docs/evidence/goal05-phase22-synthetic-benchmark/INVALIDATION_NOTICE.md",
        ".agent/programs/thread-prompts/CC-A-phase22-dataset-corpus-derivation-validator.md",
        ".agent/programs/thread-prompts/CC-B-phase22-canonical-ingestion-three-indexes.md",
        ".agent/programs/thread-prompts/CC-C-phase22-four-profile-runtime-benchmark.md",
        ".agent/programs/thread-prompts/CC-D-phase22-integration-fault-security-evidence.md",
    ]
    for relative in paths:
        source = REPO_ROOT / relative
        target = fixture / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return fixture


def test_phase22_synthetic_regression_track_matches_current_truth() -> None:
    verifier = _load_verifier()
    assert verifier.verify_phase22_synthetic_regression_track() == []


def test_public_review_approval_cannot_be_reused_for_synthetic_track(tmp_path: Path) -> None:
    verifier = _load_verifier()
    fixture = _copy_fixture(tmp_path)
    approval_path = fixture / "docs/evidence/goal05-phase22-public-benchmark-review-pack/approval_summary.json"
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    approval["reviewer_approved_count"] = 80
    approval_path.write_text(json.dumps(approval), encoding="utf-8")

    verifier.REPO_ROOT = fixture
    errors = verifier.verify_phase22_synthetic_regression_track()

    assert any("reviewer_approved_count must remain 0" in error for error in errors)


def test_task_cards_must_keep_handoff_contract(tmp_path: Path) -> None:
    verifier = _load_verifier()
    fixture = _copy_fixture(tmp_path)
    card = fixture / ".agent/programs/thread-prompts/CC-A-phase22-dataset-corpus-derivation-validator.md"
    card.write_text("# bad card\n", encoding="utf-8")

    verifier.REPO_ROOT = fixture
    errors = verifier.verify_phase22_synthetic_regression_track()

    assert any("missing task-card field" in error for error in errors)


def test_pr100_invalidated_runtime_outputs_must_remain_drop(tmp_path: Path) -> None:
    verifier = _load_verifier()
    fixture = _copy_fixture(tmp_path)
    classification_path = (
        fixture
        / "docs/evidence/goal05-phase22-machine-attested-synthetic-regression/pr100-file-classification.json"
    )
    classification = json.loads(classification_path.read_text(encoding="utf-8"))
    for item in classification["files"]:
        if item["path"] == "docs/evidence/goal05-phase22-synthetic-benchmark/ingest_and_run.py":
            item["classification"] = "ACCEPT_AS_IS"
    classification_path.write_text(json.dumps(classification), encoding="utf-8")

    verifier.REPO_ROOT = fixture
    errors = verifier.verify_phase22_synthetic_regression_track()

    assert any("ingest_and_run.py must be DROP" in error for error in errors)


def test_seed_dataset_cannot_be_marked_runtime_eligible(tmp_path: Path) -> None:
    verifier = _load_verifier()
    fixture = _copy_fixture(tmp_path)
    seed_path = (
        fixture
        / "docs/evidence/goal05-phase22-machine-attested-synthetic-regression/seed-dataset/seed_dataset_manifest.json"
    )
    seed = json.loads(seed_path.read_text(encoding="utf-8"))
    seed["runtime_eligible"] = True
    seed_path.write_text(json.dumps(seed), encoding="utf-8")

    verifier.REPO_ROOT = fixture
    errors = verifier.verify_phase22_synthetic_regression_track()

    assert any("seed dataset must not be runtime eligible" in error for error in errors)


def test_candidate_dataset_cannot_be_marked_synthetic_regression_eligible_before_runtime(tmp_path: Path) -> None:
    verifier = _load_verifier()
    fixture = _copy_fixture(tmp_path)
    candidate_path = (
        fixture
        / "docs/evidence/goal05-phase22-machine-attested-synthetic-regression/candidate-dataset/candidate_dataset_manifest.json"
    )
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    candidate["synthetic_regression_eligible"] = True
    candidate_path.write_text(json.dumps(candidate), encoding="utf-8")

    verifier.REPO_ROOT = fixture
    errors = verifier.verify_phase22_synthetic_regression_track()

    assert any("candidate dataset must not be synthetic regression eligible" in error for error in errors)


def test_candidate_derivation_report_must_keep_80_valid_cases(tmp_path: Path) -> None:
    verifier = _load_verifier()
    fixture = _copy_fixture(tmp_path)
    report_path = (
        fixture
        / "docs/evidence/goal05-phase22-machine-attested-synthetic-regression/candidate-dataset/candidate_derivation_report.json"
    )
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["derivation_valid_count"] = 79
    report_path.write_text(json.dumps(report), encoding="utf-8")

    verifier.REPO_ROOT = fixture
    errors = verifier.verify_phase22_synthetic_regression_track()

    assert any("derivation_valid_count must be 80" in error for error in errors)


def test_candidate_derivation_report_must_keep_no_gold_leakage(tmp_path: Path) -> None:
    verifier = _load_verifier()
    fixture = _copy_fixture(tmp_path)
    report_path = (
        fixture
        / "docs/evidence/goal05-phase22-machine-attested-synthetic-regression/candidate-dataset/candidate_derivation_report.json"
    )
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["gold_leakage_count"] = 1
    report_path.write_text(json.dumps(report), encoding="utf-8")

    verifier.REPO_ROOT = fixture
    errors = verifier.verify_phase22_synthetic_regression_track()

    assert any("gold_leakage_count must be 0" in error for error in errors)


def test_candidate_derivation_report_must_keep_world_model_answer_derivation(tmp_path: Path) -> None:
    verifier = _load_verifier()
    fixture = _copy_fixture(tmp_path)
    report_path = (
        fixture
        / "docs/evidence/goal05-phase22-machine-attested-synthetic-regression/candidate-dataset/candidate_derivation_report.json"
    )
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["answer_derivation_valid_count"] = 79
    report_path.write_text(json.dumps(report), encoding="utf-8")

    verifier.REPO_ROOT = fixture
    errors = verifier.verify_phase22_synthetic_regression_track()

    assert any("answer_derivation_valid_count must be 80" in error for error in errors)
