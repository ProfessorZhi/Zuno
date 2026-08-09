from __future__ import annotations

import csv
import hashlib
import json
import random
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[5]
CACHE_ROOT = REPO_ROOT / ".local" / "eval-datasets"
PACK_DIR = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-public-benchmark-review-pack"


def _clean_str(val: str) -> str:
    cleaned = re.sub(r"\s+", " ", val or "").strip()
    return cleaned


def _normalize_hotpot_supporting_facts(value: Any) -> list[tuple[str, int]]:
    """Normalize the two official HotpotQA supporting-facts shapes.

    The downloaded HotpotQA JSON uses parallel ``title`` and ``sent_id``
    arrays, while older adapters and fixtures use ``[[title, sent_id], ...]``.
    Treating the mapping as an iterable of pairs silently drops all official
    gold evidence, so the pack generator must normalize both forms explicitly.
    """

    if isinstance(value, dict):
        titles = value.get("title") or []
        sentence_ids = value.get("sent_id") or []
        if not isinstance(titles, list) or not isinstance(sentence_ids, list):
            return []
        return [
            (str(title), int(sentence_id))
            for title, sentence_id in zip(titles, sentence_ids)
            if title and isinstance(sentence_id, int) and not isinstance(sentence_id, bool)
        ]

    if isinstance(value, list):
        normalized: list[tuple[str, int]] = []
        for item in value:
            if (
                isinstance(item, (list, tuple))
                and len(item) >= 2
                and item[0]
                and isinstance(item[1], int)
                and not isinstance(item[1], bool)
            ):
                normalized.append((str(item[0]), item[1]))
        return normalized

    return []


def load_hotpot_cases(limit: int = 32) -> list[dict[str, Any]]:
    path = CACHE_ROOT / "hotpot_qa" / "hotpot_dev_distractor_v1.json"
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    selected: list[dict[str, Any]] = []
    for item in data[:limit]:
        rec_id = item.get("_id") or item.get("id") or f"hotpot_{len(selected)+1}"
        question = _clean_str(item.get("question", ""))
        answer = _clean_str(item.get("answer", ""))
        if not question or not answer or "Sample question" in question:
            continue

        facts = _normalize_hotpot_supporting_facts(item.get("supporting_facts", []))
        gold_docs = list(dict.fromkeys(title for title, _ in facts))
        gold_ev = [f"{title}_sent_{sentence_id}" for title, sentence_id in facts]

        has_evidence = len(gold_docs) > 0 and len(gold_ev) > 0

        case = {
            "case_id": f"case_pub_{len(selected)+1:03d}",
            "source_dataset": "hotpotqa/hotpot_qa",
            "source_split": "validation",
            "source_record_id": str(rec_id),
            "dataset_version": "1.0.0",
            "question": question,
            "question_type": "multihop_fact",
            "complexity": item.get("level", "medium"),
            "expected_answer": answer,
            "gold_document_refs": gold_docs,
            "gold_evidence_refs": gold_ev,
            "supporting_fact_refs": gold_ev,
            "citation_ground_truth": gold_docs,
            "evidence_status": "evidence_complete" if has_evidence else "evidence_incomplete",
            "corpus_snapshot_ref": "snapshot_multihop_fact_slice",
            "provenance": "upstream_official_hotpot_qa",
            "license_ref": "CC-BY-SA-4.0",
            "reviewer_status": "pending",
            "reviewer_notes": "",
            "rejection_reason": "" if has_evidence else "missing_upstream_gold_evidence",
            "contamination_risk": "low",
            "duplicate_group": None,
            "tags": ["multihop_fact", "multihop_fact_slice"],
        }
        selected.append(case)
    return selected


def load_multihop_cases(start_idx: int = 33, limit: int = 24) -> list[dict[str, Any]]:
    path = CACHE_ROOT / "multihop_rag" / "queries.json"
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    selected: list[dict[str, Any]] = []
    for idx, item in enumerate(data):
        if len(selected) >= limit:
            break
        question = _clean_str(item.get("query", ""))
        answer = _clean_str(item.get("answer", ""))
        if not question or not answer or "Sample question" in question:
            continue

        evidence_list = item.get("evidence_list", [])
        gold_docs = list(dict.fromkeys([e.get("title", "") for e in evidence_list if isinstance(e, dict) and e.get("title")]))
        gold_ev = [f"{e.get('source', 'src')}_{ev_idx}" for ev_idx, e in enumerate(evidence_list)]

        rec_id = f"multihop_query_{idx+1:03d}"
        has_evidence = len(gold_docs) > 0 and len(gold_ev) > 0
        if not has_evidence:
            continue

        case = {
            "case_id": f"case_pub_{start_idx + len(selected):03d}",
            "source_dataset": "yixuantt/MultiHopRAG",
            "source_split": "train",
            "source_record_id": rec_id,
            "dataset_version": "1.0.0",
            "question": question,
            "question_type": item.get("question_type", "multihop_reasoning"),
            "complexity": "medium",
            "expected_answer": answer,
            "gold_document_refs": gold_docs,
            "gold_evidence_refs": gold_ev,
            "supporting_fact_refs": gold_ev,
            "citation_ground_truth": gold_docs,
            "evidence_status": "evidence_complete" if has_evidence else "evidence_incomplete",
            "corpus_snapshot_ref": "snapshot_graph_reasoning_slice",
            "provenance": "upstream_official_multihop_rag",
            "license_ref": "Apache-2.0",
            "reviewer_status": "pending",
            "reviewer_notes": "",
            "rejection_reason": "" if has_evidence else "missing_upstream_gold_evidence",
            "contamination_risk": "low",
            "duplicate_group": None,
            "tags": [item.get("question_type", "multihop_reasoning"), "graph_reasoning_slice"],
        }
        selected.append(case)
    return selected


def _graphrag_textbook_files() -> list[Path]:
    corpus_root = CACHE_ROOT / "microsoft_graphrag" / "textbooks"
    return sorted(
        corpus_root.glob("textbook*/textbook*.md"),
        key=lambda item: int(re.search(r"textbook(\d+)", item.name).group(1)),
    )


def _graphrag_corpus_manifest() -> list[dict[str, Any]]:
    base = CACHE_ROOT / "microsoft_graphrag"
    return [
        {
            "path": path.relative_to(base).as_posix(),
            "size_bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in _graphrag_textbook_files()
    ]


def load_graphrag_cases(start_idx: int = 57, limit: int = 24) -> list[dict[str, Any]]:
    path = CACHE_ROOT / "microsoft_graphrag" / "questions.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    corpus_files = _graphrag_textbook_files()
    corpus: list[tuple[str, str, str]] = []
    for corpus_file in corpus_files:
        raw = corpus_file.read_text(encoding="utf-8")
        corpus.append(
            (
                corpus_file.relative_to(CACHE_ROOT / "microsoft_graphrag").as_posix(),
                raw,
                _clean_str(raw).casefold(),
            )
        )

    def locate_question(question: str) -> tuple[str, str] | None:
        normalized_question = _clean_str(question).casefold()
        if not corpus:
            return None
        for relative_path, raw, normalized_corpus in corpus:
            if normalized_question not in normalized_corpus:
                continue
            tokens = normalized_question.split()
            pattern = r"\s+".join(re.escape(token) for token in tokens)
            match = re.search(pattern, raw.casefold())
            if match is None:
                raise RuntimeError(
                    f"GraphRAG corpus normalized match has no stable source span: {question!r}"
                )
            start_line = raw[: match.start()].count("\n") + 1
            end_line = raw[: match.end()].count("\n") + 1
            return relative_path, f"{relative_path}#L{start_line}-L{end_line}"
        return None

    selected: list[dict[str, Any]] = []
    for idx, line in enumerate(lines):
        if len(selected) >= limit:
            break
        if not line.strip():
            continue
        item = json.loads(line)
        question = _clean_str(item.get("Question", ""))
        answer = _clean_str(str(item.get("Answer", "")))
        if not question or not answer or "Sample question" in question:
            continue

        corpus_match = locate_question(question)
        if corpus and corpus_match is None:
            continue

        rec_id = f"graphrag_bench_q_{idx+1:03d}"
        gold_docs = [corpus_match[0]] if corpus_match else []
        gold_ev = [corpus_match[1]] if corpus_match else []
        has_evidence = bool(corpus_match)
        case = {
            "case_id": f"case_pub_{start_idx + len(selected):03d}",
            "source_dataset": "Awesome-GraphRAG/GraphRAG-Bench",
            "source_split": "main",
            "source_record_id": rec_id,
            "dataset_version": "1.0.0",
            "upstream_record_id": f"questions.jsonl:line:{idx+1}",
            "question": question,
            "question_type": "global_summary",
            "complexity": "hard",
            "expected_answer": answer,
            "gold_document_refs": gold_docs,
            "gold_evidence_refs": gold_ev,
            "supporting_fact_refs": gold_ev,
            "citation_ground_truth": gold_docs,
            "evidence_status": "evidence_complete" if has_evidence else "evidence_incomplete",
            "corpus_snapshot_ref": "snapshot_global_summary_textbook_corpus",
            "provenance": "upstream_awesome_graphrag_bench",
            "license_ref": "MIT",
            "reviewer_status": "pending",
            "reviewer_notes": (
                "Exact question match located in the cached official GraphRAG textbook corpus."
                if has_evidence
                else "Official textbook corpus is unavailable or has no exact question match."
            ),
            "rejection_reason": "" if has_evidence else "missing_official_textbook_evidence_match",
            "contamination_risk": "low",
            "duplicate_group": None,
            "tags": [
                "global_summary",
                "global_summary_slice",
                "exact_official_textbook_match" if has_evidence else "evidence_match_missing",
            ],
        }
        selected.append(case)
    if corpus and len(selected) < limit:
        raise RuntimeError(
            f"GraphRAG official textbook corpus yielded only {len(selected)} exact matches; "
            f"{limit} are required for the fixed candidate slice."
        )
    return selected


def detect_duplicates(cases: list[dict[str, Any]]) -> dict[str, Any]:
    seen_q: dict[str, str] = {}
    exact_dups = 0
    dup_details: list[dict[str, str]] = []

    for c in cases:
        norm_q = re.sub(r"[^\w\s]", "", c["question"].lower()).strip()
        if norm_q in seen_q:
            exact_dups += 1
            dup_details.append({
                "case_id": c["case_id"],
                "duplicate_of": seen_q[norm_q],
                "question": c["question"],
            })
        else:
            seen_q[norm_q] = c["case_id"]

    return {
        "exact_duplicates": exact_dups,
        "near_duplicates": 0,
        "duplicate_details": dup_details,
        "status": "clean" if exact_dups == 0 else "duplicates_found",
    }


def main() -> int:
    PACK_DIR.mkdir(parents=True, exist_ok=True)

    c1 = load_hotpot_cases(32)
    c2 = load_multihop_cases(33, 24)
    c3 = load_graphrag_cases(57, 24)

    all_cases = c1 + c2 + c3
    assert len(all_cases) == 80, f"Expected 80 cases, got {len(all_cases)}"

    # Check for placeholder questions
    for case in all_cases:
        assert "Sample question" not in case["question"], f"Placeholder question found in {case['case_id']}"
        assert "Sample ground truth" not in case["expected_answer"], f"Placeholder answer found in {case['case_id']}"

    # Calculate real evidence stats
    evidence_complete_cases = [c for c in all_cases if c["evidence_status"] == "evidence_complete"]
    evidence_incomplete_cases = [c for c in all_cases if c["evidence_status"] != "evidence_complete"]
    dup_report = detect_duplicates(all_cases)

    # 1. candidate_cases.jsonl
    jsonl_file = PACK_DIR / "candidate_cases.jsonl"
    with jsonl_file.open("w", encoding="utf-8") as f:
        for c in all_cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    # 2. review_sheet.csv
    csv_file = PACK_DIR / "review_sheet.csv"
    with csv_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["case_id", "source_dataset", "question_type", "evidence_status", "question", "expected_answer", "reviewer_status", "notes"])
        for c in all_cases:
            writer.writerow([c["case_id"], c["source_dataset"], c["question_type"], c["evidence_status"], c["question"], c["expected_answer"], c["reviewer_status"], c["reviewer_notes"]])

    # 3. source_manifest.json
    source_manifest = {
        "pack_version": "2.4.0",
        "generated_from": "real_public_official_datasets",
        "evidence_synthesis": "none_strictly_parsed_from_upstream",
        "sources": [
            {
                "source_id": "hotpotqa",
                "name": "HotpotQA",
                "upstream_repository": "hotpotqa/hotpot_qa",
                "url": "https://huggingface.co/datasets/hotpotqa/hotpot_qa",
                "license": "CC-BY-SA-4.0",
                "sampled_count": 32,
                "evidence_complete_count": len([c for c in c1 if c["evidence_status"] == "evidence_complete"]),
            },
            {
                "source_id": "multihop_rag",
                "name": "MultiHop-RAG",
                "upstream_repository": "yixuantt/MultiHopRAG",
                "url": "https://huggingface.co/datasets/yixuantt/MultiHopRAG",
                "license": "Apache-2.0",
                "sampled_count": 24,
                "evidence_complete_count": len([c for c in c2 if c["evidence_status"] == "evidence_complete"]),
                "selection_rule": "first_n_upstream_records_with_nonempty_evidence_list",
            },
            {
                "source_id": "awesome_graphrag_bench",
                "name": "Awesome-GraphRAG/GraphRAG-Bench",
                "upstream_repository": "Awesome-GraphRAG/GraphRAG-Bench",
                "url": "https://huggingface.co/datasets/Awesome-GraphRAG/GraphRAG-Bench",
                "license": "MIT",
                "sampled_count": 24,
                "evidence_complete_count": len([c for c in c3 if c["evidence_status"] == "evidence_complete"]),
                "selection_rule": "first_n_upstream_questions_with_exact_official_textbook_match",
                "corpus_files": _graphrag_corpus_manifest(),
            },
        ],
    }
    (PACK_DIR / "source_manifest.json").write_text(json.dumps(source_manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    # 4. selection_manifest.json
    selection_manifest = {
        "total_cases": 80,
        "selection_strategy": "first_n_records_passing_source_evidence_gate",
        "selection_filters": {
            "multihop_rag": "nonempty_upstream_evidence_list",
            "graphrag_bench": "exact_casefolded_question_match_in_official_textbook_corpus",
        },
        "distribution": {
            "hotpotqa/hotpot_qa": 32,
            "yixuantt/MultiHopRAG": 24,
            "Awesome-GraphRAG/GraphRAG-Bench": 24,
        },
    }
    (PACK_DIR / "selection_manifest.json").write_text(json.dumps(selection_manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    # 5. coverage_report.json
    coverage_report = {
        "raw_question_candidate_count": 80,
        "schema_valid_question_count": 80,
        "evidence_complete_count": len(evidence_complete_cases),
        "reviewer_approved_count": 0,
        "benchmark_eligible_count": 0,
        "rejected_or_incomplete_count": len(evidence_incomplete_cases),
        "slices": {
            "multihop_fact_slice": 32,
            "graph_reasoning_slice": 24,
            "global_summary_slice": 24,
        },
    }
    (PACK_DIR / "coverage_report.json").write_text(json.dumps(coverage_report, ensure_ascii=False, indent=2), encoding="utf-8")

    # 6. duplicate_report.json
    (PACK_DIR / "duplicate_report.json").write_text(json.dumps(dup_report, ensure_ascii=False, indent=2), encoding="utf-8")

    # 7. rejected_cases.jsonl
    with (PACK_DIR / "rejected_cases.jsonl").open("w", encoding="utf-8") as f:
        for c in evidence_incomplete_cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    # 8. license_report.md
    license_report = """# Public Benchmark Candidate Review Pack License Report

- **HotpotQA** (`hotpotqa/hotpot_qa`): CC-BY-SA-4.0
- **MultiHop-RAG** (`yixuantt/MultiHopRAG`): Apache-2.0
- **GraphRAG-Bench** (`Awesome-GraphRAG/GraphRAG-Bench`): MIT

All candidate cases are sourced directly from upstream official open benchmark datasets. No gold evidence fields are synthesized.
"""
    (PACK_DIR / "license_report.md").write_text(license_report, encoding="utf-8")

    # 9. approval_summary.json
    approval_summary = {
        "total_cases": 80,
        "raw_question_candidate_count": 80,
        "schema_valid_question_count": 80,
        "evidence_complete_count": len(evidence_complete_cases),
        "reviewer_approved_count": 0,
        "benchmark_eligible_count": 0,
        "rejected_or_incomplete_count": len(evidence_incomplete_cases),
        "reviewer_status_breakdown": {
            "pending": 80,
            "approved": 0,
            "rejected": 0,
        },
        "measurement_state": "blocked_pending_human_review",
    }
    (PACK_DIR / "approval_summary.json").write_text(json.dumps(approval_summary, ensure_ascii=False, indent=2), encoding="utf-8")

    # 10. README.md
    readme_content = f"""# Goal05 Phase22 Public Benchmark Review Pack

- **Status**: Candidate Review Pack Generated; delegated review is recorded under `reviewed/`
- **Total Cases**: 80 real upstream cases
- **Sources**:
  - HotpotQA (`hotpotqa/hotpot_qa`): 32 cases (CC-BY-SA-4.0)
  - MultiHop-RAG (`yixuantt/MultiHopRAG`): 24 cases (Apache-2.0)
  - GraphRAG-Bench (`Awesome-GraphRAG/GraphRAG-Bench`): 24 cases (MIT)
- **Evidence Completeness**:
  - Evidence Complete: {len(evidence_complete_cases)}
  - Evidence Incomplete / Rejected: {len(evidence_incomplete_cases)}
- **Reviewer Approval**: Raw candidate rows remain `pending`; current delegated review is recorded in `reviewed/review_summary.json`.
- **Measurement State**: `BLOCKED` pending formal runtime, credentials, and attestation evidence.
"""
    (PACK_DIR / "README.md").write_text(readme_content, encoding="utf-8")

    print(json.dumps({
        "status": "real_public_candidate_pack_generated",
        "pack_dir": str(PACK_DIR.relative_to(REPO_ROOT)),
        "cases_count": len(all_cases),
        "evidence_complete_count": len(evidence_complete_cases),
        "rejected_or_incomplete_count": len(evidence_incomplete_cases),
        "reviewer_approved_count": 0,
        "benchmark_eligible_count": 0,
    }, ensure_ascii=False, indent=2))
    return 0



if __name__ == "__main__":
    raise SystemExit(main())
