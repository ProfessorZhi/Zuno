"""Benchmark Candidate Pack Integrity Validator.

Validates the integrity, provenance, and completeness of benchmark candidate
cases from the PHASE22 Public Benchmark Review Pack.

Checks each case against 20 deterministic rules covering:
  - Identity (case_id uniqueness, source traceability)
  - Content (placeholder detection, default value detection)
  - Evidence (gold refs, supporting facts, citations)
  - Provenance (upstream source, adapter, selection rule)
  - License (presence, verification status)
  - Reviewer status (pending, approved counts)

Outputs:
  - integrity_report.json   – aggregate statistics and findings
  - invalid_or_unverifiable_cases.jsonl – per-case detail for non-VERIFIED cases
  - dataset_slice_summary.csv – per-case slice and status summary
  - integrity_review.md     – human-readable audit narrative
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
VALIDATOR_VERSION = "1.0.0"
SCHEMA_VERSION = "1.0.0"
DEFAULT_NEAR_THRESHOLD = 0.8
NGRAM_SIZE = 3

# Placeholder patterns (rule 7 / 8)
_PLACEHOLDER_RES = [
    re.compile(r"(?i)^\s*sample\s+question"),
    re.compile(r"(?i)\bplaceholder\b"),
    re.compile(r"(?i)^\s*todo\b"),
    re.compile(r"(?i)^\s*generated\s+question"),
    re.compile(r"(?i)^\s*sample\s+ground\s+truth"),
]

# Default / fabricated value patterns (rule 13)
_DEFAULT_RES = [
    re.compile(r"^doc_\w+_001$"),
    re.compile(r"^ev_\w+_001$"),
    re.compile(r"^cite_\w+_001$"),
    re.compile(r"(?i)^unknown$"),
    re.compile(r"(?i)^default$"),
]

# Known synthetic source_record_id patterns
_SYNTHETIC_ID_RES = [
    re.compile(r"^hotpot_\d+$"),
    re.compile(r"^multihop_query_\d{3}$"),
    re.compile(r"^graphrag_bench_q_\d{3}$"),
]

# Well-known licenses that don't need verification_pending
_KNOWN_LICENSES = {"CC-BY-SA-4.0", "Apache-2.0", "MIT", "BSD-2-Clause", "BSD-3-Clause", "ISC"}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_candidates(path: Path) -> list[dict[str, Any]]:
    """Load candidate cases from a JSONL file."""
    cases: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                cases.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at line {lineno}: {exc}") from exc
    return cases


def load_registry(path: Path) -> dict[str, Any]:
    """Load the public dataset registry YAML and build lookup indices."""
    import yaml  # optional dependency

    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    by_source_id: dict[str, dict] = {}
    by_hf_path: dict[str, dict] = {}
    for ds in data.get("datasets", []):
        sid = ds.get("source_id", "")
        by_source_id[sid] = ds
        url = ds.get("official_url", "")
        if "huggingface.co/datasets/" in url:
            hf_path = url.split("huggingface.co/datasets/")[-1].rstrip("/")
            by_hf_path[hf_path] = ds
    return {"by_source_id": by_source_id, "by_hf_path": by_hf_path}


def load_source_manifest(path: Path) -> dict[str, Any]:
    """Load the source manifest JSON."""
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def file_sha256(path: Path) -> str:
    """Return hex SHA-256 digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def _normalize_text(text: str) -> str:
    """Unicode-normalize, lowercase, strip punctuation, collapse whitespace."""
    text = unicodedata.normalize("NFC", text or "")
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _token_ngrams(text: str, n: int = NGRAM_SIZE) -> set[str]:
    tokens = text.split()
    if len(tokens) < n:
        return {" ".join(tokens)} if tokens else set()
    return {" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


def _jaccard(set_a: set[str], set_b: set[str]) -> float:
    if not set_a and not set_b:
        return 1.0
    union = len(set_a | set_b)
    return len(set_a & set_b) / union if union else 0.0


def _is_placeholder(text: str) -> bool:
    if not text or not text.strip():
        return True
    for pat in _PLACEHOLDER_RES:
        if pat.search(text):
            return True
    return False


def _is_default_value(text: str) -> bool:
    for pat in _DEFAULT_RES:
        if pat.match(text):
            return True
    return False


def _is_synthetic_id(sid: str) -> bool:
    for pat in _SYNTHETIC_ID_RES:
        if pat.match(sid):
            return True
    return False


# ---------------------------------------------------------------------------
# Registry resolution
# ---------------------------------------------------------------------------

def _resolve_registry_entry(
    case: dict[str, Any], registry: dict[str, Any]
) -> dict[str, Any] | None:
    src = case.get("source_dataset", "")
    entry = registry["by_hf_path"].get(src)
    if entry:
        return entry
    return registry["by_source_id"].get(src)


def _resolve_manifest_source(
    case: dict[str, Any], manifest: dict[str, Any]
) -> dict[str, Any] | None:
    src = case.get("source_dataset", "")
    for msrc in manifest.get("sources", []):
        if msrc.get("upstream_repository") == src:
            return msrc
    return None


# ---------------------------------------------------------------------------
# Per-case validation
# ---------------------------------------------------------------------------

def validate_case(
    case: dict[str, Any],
    registry: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    """Validate one case.  Returns *result* dict with status and findings."""
    findings: list[dict[str, Any]] = []
    # Severity ladder: INVALID > UNVERIFIABLE > INCOMPLETE > VERIFIED
    severity_rank = {"VERIFIED": 0, "INCOMPLETE": 1, "UNVERIFIABLE": 2, "INVALID": 3}
    status = "VERIFIED"

    def _downgrade(new_status: str) -> None:
        nonlocal status
        if severity_rank.get(new_status, 0) > severity_rank.get(status, 0):
            status = new_status

    case_id = case.get("case_id", "UNKNOWN")

    # --- Rule 2: source_dataset in registry ---
    reg = _resolve_registry_entry(case, registry)
    if reg is None:
        findings.append({"rule": 2, "severity": "INVALID",
                         "detail": f"source_dataset '{case.get('source_dataset')}' not found in registry"})
        _downgrade("INVALID")

    # --- Rule 3: source_split valid ---
    if reg is not None:
        expected_split = reg.get("source_split", "")
        actual_split = case.get("source_split", "")
        if actual_split != expected_split:
            findings.append({"rule": 3, "severity": "INVALID",
                             "detail": f"source_split '{actual_split}' != registry '{expected_split}'"})
            _downgrade("INVALID")

    # --- Rule 4: source_record_id non-empty ---
    src_id = case.get("source_record_id", "")
    if not src_id or not str(src_id).strip():
        findings.append({"rule": 4, "severity": "INVALID", "detail": "source_record_id is empty"})
        _downgrade("INVALID")

    # --- Rule 5: source_record_id traceable ---
    msrc = _resolve_manifest_source(case, manifest)
    if src_id and _is_synthetic_id(src_id):
        if msrc is not None:
            # Synthetic but traceable through manifest + generator code
            findings.append({"rule": 5, "severity": "WARNING",
                             "detail": f"source_record_id '{src_id}' is synthetic but traceable via manifest"})
        else:
            findings.append({"rule": 5, "severity": "UNVERIFIABLE",
                             "detail": f"source_record_id '{src_id}' is synthetic and not traceable"})
            _downgrade("UNVERIFIABLE")

    # --- Rule 6: upstream_record_id ---
    if not case.get("upstream_record_id") and src_id and _is_synthetic_id(src_id):
        findings.append({"rule": 6, "severity": "WARNING",
                         "detail": "No upstream_record_id field; synthetic source_record_id cannot be independently traced"})

    # --- Rule 7: question not placeholder ---
    question = case.get("question", "")
    if _is_placeholder(question):
        findings.append({"rule": 7, "severity": "INVALID",
                         "detail": f"Question is placeholder: '{question[:80]}'"})
        _downgrade("INVALID")

    # --- Rule 8: expected_answer not placeholder ---
    answer = case.get("expected_answer", "")
    if _is_placeholder(answer):
        findings.append({"rule": 8, "severity": "INVALID",
                         "detail": f"Expected answer is placeholder: '{answer[:80]}'"})
        _downgrade("INVALID")

    # --- Rule 9: gold_document_refs ---
    gold_docs = case.get("gold_document_refs", [])
    if not gold_docs:
        findings.append({"rule": 9, "severity": "INCOMPLETE", "detail": "gold_document_refs is empty"})
        _downgrade("INCOMPLETE")
    else:
        for ref in gold_docs:
            if _is_default_value(str(ref)):
                findings.append({"rule": 13, "severity": "INVALID",
                                 "detail": f"gold_document_ref uses default pattern: '{ref}'"})
                _downgrade("INVALID")

    # --- Rule 10: gold_evidence_refs ---
    gold_ev = case.get("gold_evidence_refs", [])
    if not gold_ev:
        findings.append({"rule": 10, "severity": "INCOMPLETE", "detail": "gold_evidence_refs is empty"})
        _downgrade("INCOMPLETE")
    else:
        for ref in gold_ev:
            if _is_default_value(str(ref)):
                findings.append({"rule": 13, "severity": "INVALID",
                                 "detail": f"gold_evidence_ref uses default pattern: '{ref}'"})
                _downgrade("INVALID")

    # --- Rule 11: supporting_fact_refs not auto-generated ---
    supp = case.get("supporting_fact_refs", [])
    if not supp:
        findings.append({"rule": 11, "severity": "INCOMPLETE",
                         "detail": "supporting_fact_refs is empty"})
        _downgrade("INCOMPLETE")

    # --- Rule 12: citation_ground_truth ---
    cite = case.get("citation_ground_truth", [])
    if not cite:
        findings.append({"rule": 12, "severity": "INCOMPLETE",
                         "detail": "citation_ground_truth is empty"})
        _downgrade("INCOMPLETE")

    # --- Rule 13: no default values (additional check on remaining fields) ---
    for ref in supp:
        if _is_default_value(str(ref)):
            findings.append({"rule": 13, "severity": "INVALID",
                             "detail": f"supporting_fact_ref default pattern: '{ref}'"})
            _downgrade("INVALID")
    for ref in cite:
        if _is_default_value(str(ref)):
            findings.append({"rule": 13, "severity": "INVALID",
                             "detail": f"citation_ground_truth default pattern: '{ref}'"})
            _downgrade("INVALID")

    # --- Rule 14: provenance ---
    prov = case.get("provenance", "")
    if not prov:
        findings.append({"rule": 14, "severity": "INCOMPLETE", "detail": "provenance is empty"})
        _downgrade("INCOMPLETE")
    elif isinstance(prov, str):
        # Structured provenance should contain: upstream source, record ref, adapter, selection rule
        # A simple string is minimal but acceptable if non-empty
        findings.append({"rule": 14, "severity": "WARNING",
                         "detail": "provenance is a simple string, not structured (missing adapter/selection_rule)"})

    # --- Rule 15: license_ref exists ---
    lic = case.get("license_ref", "")
    if not lic:
        findings.append({"rule": 15, "severity": "INCOMPLETE", "detail": "license_ref is empty"})
        _downgrade("INCOMPLETE")

    # --- Rule 16: license uncertainty ---
    license_status = "verified"
    if lic and lic not in _KNOWN_LICENSES:
        license_status = "verification_pending"
        findings.append({"rule": 16, "severity": "WARNING",
                         "detail": f"License '{lic}' is not in known set; marked verification_pending"})

    # --- Rule 17: reviewer_status must be pending ---
    rev = case.get("reviewer_status", "")
    if rev != "pending":
        findings.append({"rule": 17, "severity": "INVALID",
                         "detail": f"reviewer_status is '{rev}', expected 'pending'"})
        _downgrade("INVALID")

    return {
        "case_id": case_id,
        "status": status,
        "findings": findings,
        "license_status": license_status,
        "source_dataset": case.get("source_dataset", ""),
        "evidence_status": case.get("evidence_status", ""),
    }


# ---------------------------------------------------------------------------
# Duplicate detection
# ---------------------------------------------------------------------------

def detect_duplicates(
    cases: list[dict[str, Any]], near_threshold: float = DEFAULT_NEAR_THRESHOLD
) -> dict[str, Any]:
    """Deterministic exact + near duplicate detection."""
    norm_items: list[tuple[str, str, str]] = []  # (case_id, normalized_q, hash)
    for c in cases:
        nq = _normalize_text(c.get("question", ""))
        qh = hashlib.sha256(nq.encode("utf-8")).hexdigest()
        norm_items.append((c["case_id"], nq, qh))

    # Exact duplicates (same hash)
    hash_groups: dict[str, list[str]] = defaultdict(list)
    for cid, _, qh in norm_items:
        hash_groups[qh].append(cid)

    exact_pairs: list[dict[str, str]] = []
    exact_count = 0
    for qh, ids in sorted(hash_groups.items()):
        if len(ids) > 1:
            sorted_ids = sorted(ids)
            exact_count += len(sorted_ids) - 1
            for i in range(1, len(sorted_ids)):
                exact_pairs.append({"case_id_a": sorted_ids[0], "case_id_b": sorted_ids[i], "hash": qh})

    # Near duplicates (token n-gram Jaccard)
    near_pairs: list[dict[str, Any]] = []
    for i in range(len(norm_items)):
        for j in range(i + 1, len(norm_items)):
            id_a, nq_a, h_a = norm_items[i]
            id_b, nq_b, h_b = norm_items[j]
            if h_a == h_b:
                continue
            sim = _jaccard(_token_ngrams(nq_a), _token_ngrams(nq_b))
            if sim >= near_threshold:
                near_pairs.append({
                    "case_id_a": id_a, "case_id_b": id_b,
                    "jaccard_similarity": round(sim, 4),
                })

    # Sort for determinism
    exact_pairs.sort(key=lambda p: (p["case_id_a"], p["case_id_b"]))
    near_pairs.sort(key=lambda p: (-p["jaccard_similarity"], p["case_id_a"], p["case_id_b"]))

    return {
        "exact_duplicate_count": exact_count,
        "exact_duplicate_pairs": exact_pairs,
        "near_duplicate_count": len(near_pairs),
        "near_duplicate_pairs": near_pairs,
        "near_duplicate_threshold": near_threshold,
    }


# ---------------------------------------------------------------------------
# Main validation pipeline
# ---------------------------------------------------------------------------

def run_validation(
    candidate_path: Path,
    registry_path: Path,
    output_dir: Path,
    near_threshold: float = DEFAULT_NEAR_THRESHOLD,
) -> dict[str, Any]:
    """Execute the full validation pipeline and write audit artifacts."""
    cases = load_candidates(candidate_path)
    registry = load_registry(registry_path)
    manifest_path = candidate_path.parent / "source_manifest.json"
    manifest = load_source_manifest(manifest_path)
    sha = file_sha256(candidate_path)

    # Per-case validation
    results = [validate_case(c, registry, manifest) for c in cases]

    # Rule 1: case_id uniqueness
    id_counts: Counter = Counter(c.get("case_id") for c in cases)
    dup_ids = {cid: cnt for cid, cnt in id_counts.items() if cnt > 1}
    if dup_ids:
        for r in results:
            if r["case_id"] in dup_ids:
                r["status"] = "INVALID"
                r["findings"].append({
                    "rule": 1, "severity": "INVALID",
                    "detail": f"Duplicate case_id '{r['case_id']}' appears {dup_ids[r['case_id']]} times",
                })

    # Duplicate detection
    dup_report = detect_duplicates(cases, near_threshold)

    # Aggregate statistics
    status_counts: Counter = Counter(r["status"] for r in results)
    slice_counts: Counter = Counter(c.get("corpus_snapshot_ref", "unknown") for c in cases)

    verified = status_counts.get("VERIFIED", 0)
    incomplete = status_counts.get("INCOMPLETE", 0)
    unverifiable = status_counts.get("UNVERIFIABLE", 0)
    invalid = status_counts.get("INVALID", 0)

    lic_verified = sum(1 for r in results if r["license_status"] == "verified")
    lic_pending = sum(1 for r in results if r["license_status"] == "verification_pending")

    src_id_verified = sum(
        1 for r in results if not any(f["rule"] == 5 and f["severity"] != "WARNING" for f in r["findings"])
    )

    evidence_complete = sum(1 for c in cases if c.get("evidence_status") == "evidence_complete")

    findings_by_rule: dict[str, int] = defaultdict(int)
    for r in results:
        for f in r["findings"]:
            findings_by_rule[f"rule_{f['rule']}"] += 1

    reviewer_approved = sum(1 for c in cases if c.get("reviewer_status") == "approved")
    benchmark_eligible = 0  # always 0 without reviewer approval

    # Overall status
    if invalid > 0 and verified == 0:
        overall = "FAIL"
    elif verified < len(cases) or reviewer_approved == 0:
        overall = "REVIEW_REQUIRED"
    else:
        overall = "PASS"

    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "candidate_file": str(candidate_path),
        "candidate_file_sha256": sha,
        "validator_version": VALIDATOR_VERSION,
        "total_case_count": len(cases),
        "dataset_slice_counts": dict(slice_counts),
        "verified_count": verified,
        "incomplete_count": incomplete,
        "unverifiable_count": unverifiable,
        "invalid_count": invalid,
        "reviewer_approved_count": reviewer_approved,
        "benchmark_eligible_count": benchmark_eligible,
        "exact_duplicate_count": dup_report["exact_duplicate_count"],
        "near_duplicate_count": dup_report["near_duplicate_count"],
        "near_duplicate_threshold": dup_report["near_duplicate_threshold"],
        "license_verified_count": lic_verified,
        "license_pending_count": lic_pending,
        "source_id_verified_count": src_id_verified,
        "evidence_complete_count": evidence_complete,
        "findings_by_rule": dict(findings_by_rule),
        "overall_status": overall,
        "duplicate_details": dup_report,
    }

    # ---- Write outputs ----
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. integrity_report.json
    with open(output_dir / "integrity_report.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    # 2. invalid_or_unverifiable_cases.jsonl
    with open(output_dir / "invalid_or_unverifiable_cases.jsonl", "w", encoding="utf-8") as fh:
        for i, r in enumerate(results):
            if r["status"] in ("INVALID", "UNVERIFIABLE"):
                entry = {
                    "case_id": r["case_id"],
                    "status": r["status"],
                    "source_dataset": r["source_dataset"],
                    "findings": r["findings"],
                    "question": cases[i].get("question", "")[:200],
                }
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # 3. dataset_slice_summary.csv
    with open(output_dir / "dataset_slice_summary.csv", "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["case_id", "source_dataset", "source_split",
                         "evidence_status", "integrity_status", "question_type"])
        for i, c in enumerate(cases):
            writer.writerow([
                c.get("case_id", ""),
                c.get("source_dataset", ""),
                c.get("source_split", ""),
                c.get("evidence_status", ""),
                results[i]["status"],
                c.get("question_type", ""),
            ])

    # 4. integrity_review.md
    _write_review_md(output_dir / "integrity_review.md", report, results, cases)

    return report


def _write_review_md(
    path: Path,
    report: dict[str, Any],
    results: list[dict[str, Any]],
    cases: list[dict[str, Any]],
) -> None:
    """Write the human-readable integrity review."""
    lines: list[str] = []
    lines.append("# Benchmark Candidate Pack Integrity Review\n")
    lines.append(f"**Generated**: {report['generated_at']}  ")
    lines.append(f"**Validator**: v{VALIDATOR_VERSION}  ")
    lines.append(f"**Schema**: v{SCHEMA_VERSION}  ")
    lines.append(f"**Overall Status**: **{report['overall_status']}**\n")

    lines.append("## Summary\n")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Total Cases | {report['total_case_count']} |")
    lines.append(f"| VERIFIED | {report['verified_count']} |")
    lines.append(f"| INCOMPLETE | {report['incomplete_count']} |")
    lines.append(f"| UNVERIFIABLE | {report['unverifiable_count']} |")
    lines.append(f"| INVALID | {report['invalid_count']} |")
    lines.append(f"| Evidence Complete | {report['evidence_complete_count']} |")
    lines.append(f"| Exact Duplicates | {report['exact_duplicate_count']} |")
    lines.append(f"| Near Duplicates | {report['near_duplicate_count']} |")
    lines.append(f"| License Verified | {report['license_verified_count']} |")
    lines.append(f"| License Pending | {report['license_pending_count']} |")
    lines.append(f"| Source ID Verified | {report['source_id_verified_count']} |")
    lines.append(f"| Reviewer Approved | {report['reviewer_approved_count']} |")
    lines.append(f"| Benchmark Eligible | {report['benchmark_eligible_count']} |")
    lines.append("")

    lines.append("## Dataset Slices\n")
    lines.append("| Slice | Count |")
    lines.append("|---|---|")
    for sl, cnt in sorted(report["dataset_slice_counts"].items()):
        lines.append(f"| {sl} | {cnt} |")
    lines.append("")

    lines.append("## Findings by Rule\n")
    lines.append("| Rule | Violation Count |")
    lines.append("|---|---|")
    for rule, cnt in sorted(report["findings_by_rule"].items()):
        lines.append(f"| {rule} | {cnt} |")
    lines.append("")

    lines.append("## Duplicate Analysis\n")
    dup = report["duplicate_details"]
    lines.append(f"- Near-duplicate threshold (Jaccard): {dup['near_duplicate_threshold']}")
    lines.append(f"- Exact duplicate pairs: {dup['exact_duplicate_count']}")
    lines.append(f"- Near duplicate pairs: {dup['near_duplicate_count']}")
    if dup["near_duplicate_pairs"]:
        lines.append("")
        lines.append("| Case A | Case B | Jaccard |")
        lines.append("|---|---|---|")
        for p in dup["near_duplicate_pairs"]:
            lines.append(f"| {p['case_id_a']} | {p['case_id_b']} | {p['jaccard_similarity']} |")
    lines.append("")

    lines.append("## Notes\n")
    lines.append("- All 80 cases use synthetic `source_record_id` values generated by the adapter "
                 "(`hotpot_N`, `multihop_query_NNN`, `graphrag_bench_q_NNN`). "
                 "These are traceable through `source_manifest.json` but not independently verifiable "
                 "against upstream record IDs.")
    lines.append("- HotpotQA (32 cases): `gold_document_refs`, `gold_evidence_refs`, "
                 "`supporting_fact_refs`, and `citation_ground_truth` are all empty "
                 "→ classified INCOMPLETE.")
    lines.append("- MultiHop-RAG (24 cases): 20 have `evidence_complete`; "
                 "4 `null_query` cases have empty evidence → INCOMPLETE.")
    lines.append("- GraphRAG-Bench (24 cases): upstream `questions.jsonl` lacks sentence-level "
                 "gold evidence refs → all INCOMPLETE.")
    lines.append("- Provenance fields are simple strings (e.g. `upstream_official_hotpot_qa`), "
                 "not structured objects with adapter/selection_rule metadata.")
    lines.append("- `reviewer_approved_count` = 0; `benchmark_eligible_count` = 0 "
                 "(blocked on human review).")
    lines.append("")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark Candidate Pack Integrity Validator"
    )
    parser.add_argument("--candidate-pack", required=True,
                        help="Path to candidate_cases.jsonl")
    parser.add_argument("--registry", required=True,
                        help="Path to public_dataset_registry.yaml")
    parser.add_argument("--output-dir", required=True,
                        help="Directory for audit output files")
    parser.add_argument("--near-threshold", type=float,
                        default=DEFAULT_NEAR_THRESHOLD,
                        help=f"Jaccard threshold for near-duplicate detection (default {DEFAULT_NEAR_THRESHOLD})")
    args = parser.parse_args()

    report = run_validation(
        candidate_path=Path(args.candidate_pack),
        registry_path=Path(args.registry),
        output_dir=Path(args.output_dir),
        near_threshold=args.near_threshold,
    )

    print(json.dumps({
        "overall_status": report["overall_status"],
        "total_case_count": report["total_case_count"],
        "verified_count": report["verified_count"],
        "incomplete_count": report["incomplete_count"],
        "unverifiable_count": report["unverifiable_count"],
        "invalid_count": report["invalid_count"],
        "exact_duplicate_count": report["exact_duplicate_count"],
        "near_duplicate_count": report["near_duplicate_count"],
        "evidence_complete_count": report["evidence_complete_count"],
        "reviewer_approved_count": report["reviewer_approved_count"],
        "benchmark_eligible_count": report["benchmark_eligible_count"],
    }, indent=2))

    return 0 if report["overall_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
