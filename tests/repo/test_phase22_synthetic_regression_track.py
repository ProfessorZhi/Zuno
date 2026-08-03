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
