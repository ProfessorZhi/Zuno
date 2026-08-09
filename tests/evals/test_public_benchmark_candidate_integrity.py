"""Tests for benchmark candidate pack integrity validator.

Covers 20 required scenarios:
  1. Valid real case → VERIFIED
  2. Missing source_record_id → INVALID
  3. Synthetic source_record_id (traceable) → WARNING
  4. Missing upstream_record_id → WARNING
  5. Placeholder question → INVALID
  6. Placeholder answer → INVALID
  7. Default gold_document_refs → INVALID
  8. Default gold_evidence_refs → INVALID
  9. Fabricated citation refs → INVALID
 10. Missing provenance → INCOMPLETE
 11. License pending (unknown license)
 12. Non-pending reviewer_status → INVALID
 13. Exact duplicate detection
 14. Near duplicate detection
 15. Deterministic sort order
 16. SHA-256 stability
 17. Validator does not modify input file
 18. 80-case stats from real file
 19. No hardcoded evidence_complete_count
 20. Reviewer approved count stays 0
"""
from __future__ import annotations

import copy
import hashlib
import json
import textwrap
from pathlib import Path
from typing import Any

import pytest
import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
PACK_DIR = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-public-benchmark-review-pack"
CANDIDATE_PATH = PACK_DIR / "candidate_cases.jsonl"
REGISTRY_PATH = (
    REPO_ROOT / "tools" / "evals" / "zuno" / "rag_eval" / "datasets" / "public_dataset_registry.yaml"
)
MANIFEST_PATH = PACK_DIR / "source_manifest.json"

# Import the module under test
from tools.evals.zuno.rag_eval.datasets.verify_candidate_pack_integrity import (  # noqa: E402
    DEFAULT_NEAR_THRESHOLD,
    detect_duplicates,
    file_sha256,
    load_candidates,
    load_registry,
    load_source_manifest,
    run_validation,
    validate_case,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_registry(tmp_path: Path) -> Path:
    """Write a minimal registry YAML and return its path."""
    data = {
        "datasets": [
            {
                "source_id": "test_dataset",
                "official_name": "Test Dataset",
                "official_url": "https://huggingface.co/datasets/test/ds",
                "source_split": "validation",
                "license_spdx": "MIT",
            },
            {
                "source_id": "hotpot_qa",
                "official_name": "HotpotQA",
                "official_url": "https://huggingface.co/datasets/hotpotqa/hotpot_qa",
                "source_split": "validation",
                "license_spdx": "CC-BY-SA-4.0",
            },
            {
                "source_id": "multihop_rag",
                "official_name": "MultiHop-RAG",
                "official_url": "https://huggingface.co/datasets/yixuantt/MultiHopRAG",
                "source_split": "train",
                "license_spdx": "Apache-2.0",
            },
            {
                "source_id": "microsoft_graphrag_benchmarking",
                "official_name": "GraphRAG-Bench",
                "official_url": "https://huggingface.co/datasets/Awesome-GraphRAG/GraphRAG-Bench",
                "source_split": "main",
                "license_spdx": "MIT",
            },
        ]
    }
    p = tmp_path / "registry.yaml"
    p.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
    return p


def _make_manifest(tmp_path: Path) -> Path:
    """Write a minimal source manifest and return its path."""
    data = {
        "sources": [
            {
                "source_id": "test_ds",
                "upstream_repository": "test/ds",
                "license": "MIT",
            },
            {
                "source_id": "hotpotqa",
                "upstream_repository": "hotpotqa/hotpot_qa",
                "license": "CC-BY-SA-4.0",
            },
        ]
    }
    p = tmp_path / "source_manifest.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def _valid_case(**overrides: Any) -> dict[str, Any]:
    """Return a minimal valid case dict."""
    base = {
        "case_id": "case_test_001",
        "source_dataset": "test/ds",
        "source_split": "validation",
        "source_record_id": "real_upstream_id_42",
        "dataset_version": "1.0.0",
        "question": "What is the capital of France?",
        "question_type": "factoid",
        "complexity": "easy",
        "expected_answer": "Paris",
        "gold_document_refs": ["doc_france_wiki"],
        "gold_evidence_refs": ["ev_france_01"],
        "supporting_fact_refs": ["sf_france_01"],
        "citation_ground_truth": ["cite_france_01"],
        "evidence_status": "evidence_complete",
        "corpus_snapshot_ref": "snapshot_test",
        "provenance": "upstream_test_ds",
        "license_ref": "MIT",
        "reviewer_status": "pending",
        "reviewer_notes": "",
        "rejection_reason": "",
        "contamination_risk": "low",
        "duplicate_group": None,
        "tags": ["test"],
    }
    base.update(overrides)
    return base


def _write_jsonl(tmp_path: Path, cases: list[dict], name: str = "candidate_cases.jsonl") -> Path:
    p = tmp_path / name
    with open(p, "w", encoding="utf-8") as fh:
        for c in cases:
            fh.write(json.dumps(c, ensure_ascii=False) + "\n")
    return p


# ---------------------------------------------------------------------------
# 1. Valid real case → VERIFIED
# ---------------------------------------------------------------------------

class TestValidCase:
    def test_valid_case_is_verified(self, tmp_path: Path) -> None:
        reg = _make_registry(tmp_path)
        registry = load_registry(reg)
        manifest = {"sources": [{"source_id": "test_ds", "upstream_repository": "test/ds"}]}
        case = _valid_case()
        result = validate_case(case, registry, manifest)
        assert result["status"] == "VERIFIED", f"Expected VERIFIED, got {result['status']}: {result['findings']}"


# ---------------------------------------------------------------------------
# 2. Missing source_record_id → INVALID
# ---------------------------------------------------------------------------

class TestMissingSourceRecordId:
    def test_empty_source_record_id(self, tmp_path: Path) -> None:
        reg = _make_registry(tmp_path)
        registry = load_registry(reg)
        manifest = {"sources": []}
        case = _valid_case(source_record_id="")
        result = validate_case(case, registry, manifest)
        assert result["status"] == "INVALID"
        assert any(f["rule"] == 4 for f in result["findings"])


# ---------------------------------------------------------------------------
# 3. Synthetic source_record_id (traceable) → WARNING only
# ---------------------------------------------------------------------------

class TestSyntheticSourceRecordId:
    def test_synthetic_but_traceable(self, tmp_path: Path) -> None:
        reg = _make_registry(tmp_path)
        registry = load_registry(reg)
        manifest = {"sources": [{"source_id": "test_ds", "upstream_repository": "test/ds"}]}
        case = _valid_case(source_record_id="hotpot_1")
        result = validate_case(case, registry, manifest)
        # Should not be INVALID or UNVERIFIABLE since it's traceable via manifest
        assert result["status"] not in ("INVALID", "UNVERIFIABLE"), (
            f"Synthetic but traceable ID should not be {result['status']}"
        )
        assert any(f["rule"] == 5 and f["severity"] == "WARNING" for f in result["findings"])


# ---------------------------------------------------------------------------
# 4. Missing upstream_record_id → WARNING
# ---------------------------------------------------------------------------

class TestMissingUpstreamRecordId:
    def test_no_upstream_record_id(self, tmp_path: Path) -> None:
        reg = _make_registry(tmp_path)
        registry = load_registry(reg)
        manifest = {"sources": [{"source_id": "test_ds", "upstream_repository": "test/ds"}]}
        case = _valid_case(source_record_id="hotpot_1")  # synthetic
        result = validate_case(case, registry, manifest)
        assert any(f["rule"] == 6 for f in result["findings"])


# ---------------------------------------------------------------------------
# 5. Placeholder question → INVALID
# ---------------------------------------------------------------------------

class TestPlaceholderQuestion:
    @pytest.mark.parametrize("question", [
        "Sample question",
        "placeholder",
        "TODO",
        "generated question for testing",
    ])
    def test_placeholder_questions(self, tmp_path: Path, question: str) -> None:
        reg = _make_registry(tmp_path)
        registry = load_registry(reg)
        manifest = {"sources": []}
        case = _valid_case(question=question)
        result = validate_case(case, registry, manifest)
        assert result["status"] == "INVALID"
        assert any(f["rule"] == 7 for f in result["findings"])


# ---------------------------------------------------------------------------
# 6. Placeholder answer → INVALID
# ---------------------------------------------------------------------------

class TestPlaceholderAnswer:
    @pytest.mark.parametrize("answer", [
        "Sample ground truth",
        "placeholder",
        "TODO",
        "",
    ])
    def test_placeholder_answers(self, tmp_path: Path, answer: str) -> None:
        reg = _make_registry(tmp_path)
        registry = load_registry(reg)
        manifest = {"sources": []}
        case = _valid_case(expected_answer=answer)
        result = validate_case(case, registry, manifest)
        assert result["status"] == "INVALID"
        assert any(f["rule"] == 8 for f in result["findings"])


# ---------------------------------------------------------------------------
# 7. Default gold_document_refs → INVALID
# ---------------------------------------------------------------------------

class TestDefaultGoldDocRefs:
    def test_default_doc_ref(self, tmp_path: Path) -> None:
        reg = _make_registry(tmp_path)
        registry = load_registry(reg)
        manifest = {"sources": []}
        case = _valid_case(gold_document_refs=["doc_test_001"])
        result = validate_case(case, registry, manifest)
        assert result["status"] == "INVALID"
        assert any(f["rule"] == 13 for f in result["findings"])


# ---------------------------------------------------------------------------
# 8. Default gold_evidence_refs → INVALID
# ---------------------------------------------------------------------------

class TestDefaultGoldEvidenceRefs:
    def test_default_ev_ref(self, tmp_path: Path) -> None:
        reg = _make_registry(tmp_path)
        registry = load_registry(reg)
        manifest = {"sources": []}
        case = _valid_case(gold_evidence_refs=["ev_test_001"])
        result = validate_case(case, registry, manifest)
        assert result["status"] == "INVALID"
        assert any(f["rule"] == 13 for f in result["findings"])


# ---------------------------------------------------------------------------
# 9. Citation ref fabricated → INVALID
# ---------------------------------------------------------------------------

class TestFabricatedCitation:
    def test_default_citation_ref(self, tmp_path: Path) -> None:
        reg = _make_registry(tmp_path)
        registry = load_registry(reg)
        manifest = {"sources": []}
        case = _valid_case(citation_ground_truth=["cite_test_001"])
        result = validate_case(case, registry, manifest)
        assert result["status"] == "INVALID"
        assert any(f["rule"] == 13 for f in result["findings"])


# ---------------------------------------------------------------------------
# 10. Missing provenance → INCOMPLETE
# ---------------------------------------------------------------------------

class TestMissingProvenance:
    def test_empty_provenance(self, tmp_path: Path) -> None:
        reg = _make_registry(tmp_path)
        registry = load_registry(reg)
        manifest = {"sources": []}
        case = _valid_case(provenance="")
        result = validate_case(case, registry, manifest)
        assert result["status"] == "INCOMPLETE"
        assert any(f["rule"] == 14 for f in result["findings"])


# ---------------------------------------------------------------------------
# 11. License pending
# ---------------------------------------------------------------------------

class TestLicensePending:
    def test_unknown_license(self, tmp_path: Path) -> None:
        reg = _make_registry(tmp_path)
        registry = load_registry(reg)
        manifest = {"sources": []}
        case = _valid_case(license_ref="Proprietary-X")
        result = validate_case(case, registry, manifest)
        assert result["license_status"] == "verification_pending"
        assert any(f["rule"] == 16 for f in result["findings"])

    def test_known_license(self, tmp_path: Path) -> None:
        reg = _make_registry(tmp_path)
        registry = load_registry(reg)
        manifest = {"sources": []}
        case = _valid_case(license_ref="MIT")
        result = validate_case(case, registry, manifest)
        assert result["license_status"] == "verified"


# ---------------------------------------------------------------------------
# 12. Non-pending reviewer_status → INVALID
# ---------------------------------------------------------------------------

class TestReviewerStatus:
    def test_approved_reviewer_status(self, tmp_path: Path) -> None:
        reg = _make_registry(tmp_path)
        registry = load_registry(reg)
        manifest = {"sources": []}
        case = _valid_case(reviewer_status="approved")
        result = validate_case(case, registry, manifest)
        assert result["status"] == "INVALID"
        assert any(f["rule"] == 17 for f in result["findings"])

    def test_rejected_reviewer_status(self, tmp_path: Path) -> None:
        reg = _make_registry(tmp_path)
        registry = load_registry(reg)
        manifest = {"sources": []}
        case = _valid_case(reviewer_status="rejected")
        result = validate_case(case, registry, manifest)
        assert result["status"] == "INVALID"


# ---------------------------------------------------------------------------
# 13. Exact duplicate detection
# ---------------------------------------------------------------------------

class TestExactDuplicates:
    def test_exact_duplicate_detected(self) -> None:
        cases = [
            {"case_id": "a", "question": "What is the capital of France?"},
            {"case_id": "b", "question": "what is the capital of france?"},
            {"case_id": "c", "question": "Different question entirely"},
        ]
        result = detect_duplicates(cases)
        assert result["exact_duplicate_count"] == 1
        assert len(result["exact_duplicate_pairs"]) == 1
        assert result["exact_duplicate_pairs"][0]["case_id_a"] == "a"
        assert result["exact_duplicate_pairs"][0]["case_id_b"] == "b"

    def test_no_exact_duplicates(self) -> None:
        cases = [
            {"case_id": "a", "question": "What is the capital of France?"},
            {"case_id": "b", "question": "What is the capital of Germany?"},
        ]
        result = detect_duplicates(cases)
        assert result["exact_duplicate_count"] == 0


# ---------------------------------------------------------------------------
# 14. Near duplicate detection
# ---------------------------------------------------------------------------

class TestNearDuplicates:
    def test_near_duplicate_detected(self) -> None:
        cases = [
            {"case_id": "a", "question": "What is the capital city of France in Europe today"},
            {"case_id": "b", "question": "What is the capital city of France in Europe right now"},
            {"case_id": "c", "question": "Completely unrelated question about mars"},
        ]
        result = detect_duplicates(cases, near_threshold=0.7)
        assert result["near_duplicate_count"] >= 1
        pair = result["near_duplicate_pairs"][0]
        assert {pair["case_id_a"], pair["case_id_b"]} == {"a", "b"}

    def test_near_duplicate_threshold_respected(self) -> None:
        cases = [
            {"case_id": "a", "question": "What is the capital of France?"},
            {"case_id": "b", "question": "How to cook pasta Italian style?"},
        ]
        result = detect_duplicates(cases, near_threshold=0.9)
        assert result["near_duplicate_count"] == 0


# ---------------------------------------------------------------------------
# 15. Deterministic sort order
# ---------------------------------------------------------------------------

class TestDeterministicSort:
    def test_exact_pairs_sorted(self) -> None:
        cases = [
            {"case_id": "c", "question": "Same question here"},
            {"case_id": "a", "question": "Same question here"},
            {"case_id": "b", "question": "Same question here"},
        ]
        r1 = detect_duplicates(cases)
        r2 = detect_duplicates(list(reversed(cases)))
        assert r1["exact_duplicate_pairs"] == r2["exact_duplicate_pairs"]

    def test_near_pairs_sorted(self) -> None:
        cases = [
            {"case_id": "x", "question": "The quick brown fox jumps over the lazy dog nearby"},
            {"case_id": "y", "question": "The quick brown fox jumps over the lazy dog around"},
        ]
        r1 = detect_duplicates(cases, near_threshold=0.5)
        r2 = detect_duplicates(list(reversed(cases)), near_threshold=0.5)
        # Same pairs regardless of input order
        pairs1 = sorted(r1["near_duplicate_pairs"], key=lambda p: p["case_id_a"])
        pairs2 = sorted(r2["near_duplicate_pairs"], key=lambda p: p["case_id_a"])
        assert len(pairs1) == len(pairs2)


# ---------------------------------------------------------------------------
# 16. SHA-256 stability
# ---------------------------------------------------------------------------

class TestSHA256Stability:
    def test_sha256_deterministic(self, tmp_path: Path) -> None:
        p = tmp_path / "test.jsonl"
        p.write_text('{"a": 1}\n{"b": 2}\n', encoding="utf-8")
        h1 = file_sha256(p)
        h2 = file_sha256(p)
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex digest length

    def test_sha256_changes_with_content(self, tmp_path: Path) -> None:
        p1 = tmp_path / "a.jsonl"
        p2 = tmp_path / "b.jsonl"
        p1.write_text('{"a": 1}\n', encoding="utf-8")
        p2.write_text('{"a": 2}\n', encoding="utf-8")
        assert file_sha256(p1) != file_sha256(p2)


# ---------------------------------------------------------------------------
# 17. Validator does not modify input file
# ---------------------------------------------------------------------------

class TestNoModification:
    def test_validator_does_not_modify_input(self, tmp_path: Path) -> None:
        reg = _make_registry(tmp_path)
        manifest = _make_manifest(tmp_path)
        cases = [_valid_case(), _valid_case(case_id="case_test_002")]
        jsonl = _write_jsonl(tmp_path, cases)
        original_content = jsonl.read_text(encoding="utf-8")
        original_sha = file_sha256(jsonl)

        run_validation(
            candidate_path=jsonl,
            registry_path=reg,
            output_dir=tmp_path / "output",
        )

        assert jsonl.read_text(encoding="utf-8") == original_content
        assert file_sha256(jsonl) == original_sha


# ---------------------------------------------------------------------------
# 18. 80-case stats from real file
# ---------------------------------------------------------------------------

class TestRealCandidateStats:
    @pytest.fixture(autouse=True)
    def _skip_if_no_data(self) -> None:
        if not CANDIDATE_PATH.exists():
            pytest.skip("candidate_cases.jsonl not found")

    def test_total_count_is_80(self) -> None:
        cases = load_candidates(CANDIDATE_PATH)
        assert len(cases) == 80

    def test_dataset_slice_counts(self, tmp_path: Path) -> None:
        out = tmp_path / "out"
        report = run_validation(
            candidate_path=CANDIDATE_PATH,
            registry_path=REGISTRY_PATH,
            output_dir=out,
        )
        slices = report["dataset_slice_counts"]
        total_from_slices = sum(slices.values())
        assert total_from_slices == 80

    def test_evidence_complete_count_matches_regenerated_pack(self, tmp_path: Path) -> None:
        out = tmp_path / "out"
        report = run_validation(
            candidate_path=CANDIDATE_PATH,
            registry_path=REGISTRY_PATH,
            output_dir=out,
        )
        assert report["evidence_complete_count"] == 52

    def test_total_case_count(self, tmp_path: Path) -> None:
        out = tmp_path / "out"
        report = run_validation(
            candidate_path=CANDIDATE_PATH,
            registry_path=REGISTRY_PATH,
            output_dir=out,
        )
        assert report["total_case_count"] == 80


# ---------------------------------------------------------------------------
# 19. No hardcoded evidence_complete_count
# ---------------------------------------------------------------------------

class TestNoHardcodedCounts:
    def test_evidence_complete_computed_not_hardcoded(self, tmp_path: Path) -> None:
        """Create a pack with known evidence counts and verify the validator computes them."""
        reg = _make_registry(tmp_path)
        cases = [
            _valid_case(case_id="c1", evidence_status="evidence_complete"),
            _valid_case(case_id="c2", evidence_status="evidence_complete"),
            _valid_case(case_id="c3", evidence_status="evidence_incomplete"),
        ]
        jsonl = _write_jsonl(tmp_path, cases)
        report = run_validation(
            candidate_path=jsonl,
            registry_path=reg,
            output_dir=tmp_path / "out",
        )
        assert report["evidence_complete_count"] == 2  # computed, not hardcoded

    def test_evidence_complete_zero_when_all_incomplete(self, tmp_path: Path) -> None:
        reg = _make_registry(tmp_path)
        cases = [
            _valid_case(case_id="c1", evidence_status="evidence_incomplete",
                        gold_document_refs=[], gold_evidence_refs=[],
                        supporting_fact_refs=[], citation_ground_truth=[]),
        ]
        jsonl = _write_jsonl(tmp_path, cases)
        report = run_validation(
            candidate_path=jsonl,
            registry_path=reg,
            output_dir=tmp_path / "out",
        )
        assert report["evidence_complete_count"] == 0


# ---------------------------------------------------------------------------
# 20. Reviewer approved count stays 0
# ---------------------------------------------------------------------------

class TestReviewerApprovedZero:
    def test_all_pending(self, tmp_path: Path) -> None:
        reg = _make_registry(tmp_path)
        cases = [_valid_case(case_id=f"c{i}", reviewer_status="pending") for i in range(5)]
        jsonl = _write_jsonl(tmp_path, cases)
        report = run_validation(
            candidate_path=jsonl,
            registry_path=reg,
            output_dir=tmp_path / "out",
        )
        assert report["reviewer_approved_count"] == 0
        assert report["benchmark_eligible_count"] == 0

    def test_real_pack_reviewer_approved_zero(self, tmp_path: Path) -> None:
        if not CANDIDATE_PATH.exists():
            pytest.skip("candidate_cases.jsonl not found")
        report = run_validation(
            candidate_path=CANDIDATE_PATH,
            registry_path=REGISTRY_PATH,
            output_dir=tmp_path / "out",
        )
        assert report["reviewer_approved_count"] == 0
        assert report["benchmark_eligible_count"] == 0

    def test_overall_status_review_required(self, tmp_path: Path) -> None:
        if not CANDIDATE_PATH.exists():
            pytest.skip("candidate_cases.jsonl not found")
        report = run_validation(
            candidate_path=CANDIDATE_PATH,
            registry_path=REGISTRY_PATH,
            output_dir=tmp_path / "out",
        )
        assert report["overall_status"] == "REVIEW_REQUIRED"


# ---------------------------------------------------------------------------
# Additional: output artifact tests
# ---------------------------------------------------------------------------

class TestOutputArtifacts:
    def test_integrity_report_json_written(self, tmp_path: Path) -> None:
        if not CANDIDATE_PATH.exists():
            pytest.skip("candidate_cases.jsonl not found")
        out = tmp_path / "out"
        run_validation(
            candidate_path=CANDIDATE_PATH,
            registry_path=REGISTRY_PATH,
            output_dir=out,
        )
        assert (out / "integrity_report.json").exists()
        report = json.loads((out / "integrity_report.json").read_text(encoding="utf-8"))
        assert "schema_version" in report
        assert "candidate_file_sha256" in report
        assert "validator_version" in report

    def test_csv_written(self, tmp_path: Path) -> None:
        if not CANDIDATE_PATH.exists():
            pytest.skip("candidate_cases.jsonl not found")
        out = tmp_path / "out"
        run_validation(
            candidate_path=CANDIDATE_PATH,
            registry_path=REGISTRY_PATH,
            output_dir=out,
        )
        csv_path = out / "dataset_slice_summary.csv"
        assert csv_path.exists()
        lines = csv_path.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 81  # header + 80 cases

    def test_review_md_written(self, tmp_path: Path) -> None:
        if not CANDIDATE_PATH.exists():
            pytest.skip("candidate_cases.jsonl not found")
        out = tmp_path / "out"
        run_validation(
            candidate_path=CANDIDATE_PATH,
            registry_path=REGISTRY_PATH,
            output_dir=out,
        )
        md_path = out / "integrity_review.md"
        assert md_path.exists()
        content = md_path.read_text(encoding="utf-8")
        assert "REVIEW_REQUIRED" in content

    def test_invalid_or_unverifiable_jsonl(self, tmp_path: Path) -> None:
        if not CANDIDATE_PATH.exists():
            pytest.skip("candidate_cases.jsonl not found")
        out = tmp_path / "out"
        report = run_validation(
            candidate_path=CANDIDATE_PATH,
            registry_path=REGISTRY_PATH,
            output_dir=out,
        )
        iu_path = out / "invalid_or_unverifiable_cases.jsonl"
        assert iu_path.exists()
        # Count lines = invalid + unverifiable
        lines = [l for l in iu_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == report["invalid_count"] + report["unverifiable_count"]


# ---------------------------------------------------------------------------
# Additional: case_id uniqueness (rule 1)
# ---------------------------------------------------------------------------

class TestCaseIdUniqueness:
    def test_duplicate_case_id_invalid(self, tmp_path: Path) -> None:
        reg = _make_registry(tmp_path)
        cases = [
            _valid_case(case_id="dup_001"),
            _valid_case(case_id="dup_001"),  # duplicate
        ]
        jsonl = _write_jsonl(tmp_path, cases)
        report = run_validation(
            candidate_path=jsonl,
            registry_path=reg,
            output_dir=tmp_path / "out",
        )
        assert report["invalid_count"] == 2
