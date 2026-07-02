from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Iterable


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def _norm(value: Any) -> str:
    return str(value or "").lower()


def _context_text(context: dict[str, Any]) -> str:
    return _norm(
        "\n".join(
            str(context.get(key, ""))
            for key in ["content", "text", "source", "file_path", "metadata"]
        )
    )


def _context_source_text(context: dict[str, Any]) -> str:
    return _norm(
        "\n".join(
            str(context.get(key, ""))
            for key in ["source", "file_path", "file_name", "metadata"]
            if context.get(key)
        )
    )


def _source_matches_context(evidence: dict[str, Any], context: dict[str, Any]) -> bool:
    source_text = _context_source_text(context)
    doc_id = _norm(evidence.get("doc_id"))
    file_contains = _norm(evidence.get("file_contains"))
    if doc_id and doc_id in source_text:
        return True
    return bool(file_contains and file_contains in source_text)


def _evidence_matches_context(
    evidence: dict[str, Any],
    context: dict[str, Any],
    *,
    allow_document_match: bool = False,
) -> bool:
    if allow_document_match and _source_matches_context(evidence, context):
        return True
    text = _context_text(context)
    source_text = _context_source_text(context)
    file_contains = _norm(evidence.get("file_contains"))
    text_contains = _norm(evidence.get("text_contains"))
    file_ok = not file_contains or not source_text or file_contains in source_text
    text_ok = not text_contains or text_contains in text
    return file_ok and text_ok


def _is_context_relevant(
    context: dict[str, Any],
    gold_evidence: Iterable[dict[str, Any]],
    *,
    allow_document_match: bool = False,
) -> bool:
    return any(
        _evidence_matches_context(
            evidence,
            context,
            allow_document_match=allow_document_match,
        )
        for evidence in gold_evidence
    )


def _retrieval_metrics(sample: dict[str, Any], contexts: list[dict[str, Any]], k: int) -> dict[str, float]:
    gold = list(sample.get("gold_evidence") or [])
    top_contexts = contexts[:k]
    if not gold:
        return {
            "retrieval_recall": 1.0,
            "hit_rate": 1.0,
            "context_precision": 1.0,
            "mrr": 1.0,
            "ndcg": 1.0,
        }

    matched_gold = [
        evidence
        for evidence in gold
        if any(
            _evidence_matches_context(
                evidence,
                context,
                allow_document_match=True,
            )
            for context in top_contexts
        )
    ]
    relevant_flags = [
        _is_context_relevant(context, gold, allow_document_match=True)
        for context in top_contexts
    ]
    first_relevant_rank = next((idx + 1 for idx, flag in enumerate(relevant_flags) if flag), None)
    dcg = sum((1 / math.log2(idx + 2)) for idx, flag in enumerate(relevant_flags) if flag)
    ideal_relevant = sum(1 for flag in relevant_flags if flag)
    idcg = sum(1 / math.log2(idx + 2) for idx in range(ideal_relevant))

    return {
        "retrieval_recall": len(matched_gold) / len(gold),
        "hit_rate": 1.0 if matched_gold else 0.0,
        "context_precision": sum(1 for flag in relevant_flags if flag) / max(len(top_contexts), 1),
        "mrr": (1 / first_relevant_rank) if first_relevant_rank else 0.0,
        "ndcg": (dcg / idcg) if idcg else 0.0,
    }


def _citation_accuracy(sample: dict[str, Any], answer_row: dict[str, Any] | None) -> float | None:
    if not sample.get("required_citations"):
        return None
    citations = list((answer_row or {}).get("citations") or [])
    if not citations:
        return 0.0
    gold = list(sample.get("gold_evidence") or [])
    supported = sum(1 for citation in citations if _is_context_relevant(citation, gold))
    return supported / len(citations)


def _source_span_matches(citation: dict[str, Any], evidence: dict[str, Any]) -> bool:
    if not _evidence_matches_context(evidence, citation):
        return False
    expected_span = str(evidence.get("source_span") or "").strip().lower()
    actual_span = str(citation.get("source_span") or citation.get("source_ref") or "").strip().lower()
    if expected_span:
        return expected_span == actual_span or expected_span in actual_span or actual_span in expected_span

    expected_page = evidence.get("page_number")
    if expected_page in (None, ""):
        return True
    actual_page = citation.get("page_number") or citation.get("page") or citation.get("page_index")
    try:
        return int(expected_page) == int(actual_page)
    except (TypeError, ValueError):
        return False


def _source_span_accuracy(sample: dict[str, Any], answer_row: dict[str, Any] | None) -> float | None:
    if not sample.get("required_citations"):
        return None
    gold = list(sample.get("gold_evidence") or [])
    if not any(evidence.get("page_number") not in (None, "") or evidence.get("source_span") for evidence in gold):
        return _citation_accuracy(sample, answer_row)
    citations = list((answer_row or {}).get("citations") or [])
    if not citations:
        return 0.0
    supported = sum(
        1
        for citation in citations
        if any(_source_span_matches(citation, evidence) for evidence in gold)
    )
    return supported / len(citations)


def _unsupported_claim_rate(answer_row: dict[str, Any] | None, judge_row: dict[str, Any] | None) -> float | None:
    for row in (answer_row or {}, judge_row or {}):
        explicit = row.get("unsupported_claim_rate") or row.get("unsupported_claims_rate")
        if explicit is not None:
            return float(explicit)
    answer = answer_row or {}
    unsupported = answer.get("unsupported_claims")
    if isinstance(unsupported, int):
        unsupported_count = unsupported
    elif isinstance(unsupported, list):
        unsupported_count = len(unsupported)
    else:
        return None
    claim_count = answer.get("claim_count") or answer.get("claims_count")
    try:
        total = int(claim_count)
    except (TypeError, ValueError):
        total = 0
    if total <= 0:
        return None
    return unsupported_count / total


def _mean(values: Iterable[float | None]) -> float | None:
    usable = [value for value in values if value is not None]
    if not usable:
        return None
    return sum(usable) / len(usable)


def compute_metrics(
    *,
    dataset_path: Path,
    retrieval_results_path: Path,
    answers_path: Path | None = None,
    judge_results_path: Path | None = None,
    k: int = 5,
) -> dict[str, Any]:
    samples = _read_jsonl(dataset_path)
    retrieval_rows = {row["id"]: row for row in _read_jsonl(retrieval_results_path)}
    answer_rows = {row["id"]: row for row in _read_jsonl(answers_path)} if answers_path else {}
    judge_rows = {row["id"]: row for row in _read_jsonl(judge_results_path)} if judge_results_path else {}

    per_sample: list[dict[str, Any]] = []
    for sample in samples:
        sample_id = sample["id"]
        retrieval_row = retrieval_rows.get(sample_id, {})
        contexts = list(retrieval_row.get("contexts") or retrieval_row.get("documents") or [])
        retrieval = _retrieval_metrics(sample, contexts, k)
        citation_accuracy = _citation_accuracy(sample, answer_rows.get(sample_id))
        source_span_accuracy = _source_span_accuracy(sample, answer_rows.get(sample_id))
        judge = judge_rows.get(sample_id, {})
        unsupported_claim_rate = _unsupported_claim_rate(answer_rows.get(sample_id), judge)
        per_sample.append(
            {
                "id": sample_id,
                **retrieval,
                "faithfulness": judge.get("faithfulness"),
                "answer_correctness": judge.get("answer_correctness"),
                "citation_accuracy": citation_accuracy,
                "source_span_accuracy": source_span_accuracy,
                "unsupported_claim_rate": unsupported_claim_rate,
                "retrieved_contexts": len(contexts),
            }
        )

    aggregate = {
        "sample_count": len(per_sample),
        "retrieval_recall_at_k": _mean(row["retrieval_recall"] for row in per_sample),
        "hit_rate_at_k": _mean(row["hit_rate"] for row in per_sample),
        "context_precision_at_k": _mean(row["context_precision"] for row in per_sample),
        "mrr_at_k": _mean(row["mrr"] for row in per_sample),
        "ndcg_at_k": _mean(row["ndcg"] for row in per_sample),
        "faithfulness": _mean(row["faithfulness"] for row in per_sample),
        "answer_correctness": _mean(row["answer_correctness"] for row in per_sample),
        "citation_accuracy": _mean(row["citation_accuracy"] for row in per_sample),
        "source_span_accuracy": _mean(row["source_span_accuracy"] for row in per_sample),
        "unsupported_claim_rate": _mean(row["unsupported_claim_rate"] for row in per_sample),
    }
    return {
        "k": k,
        "aggregate": aggregate,
        "per_sample": per_sample,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute Zuno RAG evaluation metrics.")
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--retrieval-results", required=True, type=Path)
    parser.add_argument("--answers", type=Path)
    parser.add_argument("--judge-results", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()

    metrics = compute_metrics(
        dataset_path=args.dataset,
        retrieval_results_path=args.retrieval_results,
        answers_path=args.answers,
        judge_results_path=args.judge_results,
        k=args.k,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
