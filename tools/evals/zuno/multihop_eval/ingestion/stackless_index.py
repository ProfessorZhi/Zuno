from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from tools.evals.zuno.multihop_eval.adapters.common import read_json_or_jsonl


DEFAULT_OUTPUT = Path("reports/evals/multihop/stackless_ingestion_smoke.json")


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[\w\u4e00-\u9fff]+", str(text or "").lower()))


def _score(question: str, row: dict[str, Any]) -> float:
    question_tokens = _tokenize(question)
    title_tokens = _tokenize(str(row.get("title") or ""))
    text_tokens = _tokenize(str(row.get("text") or ""))
    sentence_bonus = min(len(row.get("sentences") or []), 5) * 0.05
    return float(len(question_tokens & text_tokens) * 2 + len(question_tokens & title_tokens) * 3) + sentence_bonus


def _group_by_question(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        question_id = str(row.get("question_id") or "")
        grouped.setdefault(question_id, []).append(row)
    return grouped


def _question_text(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    return str(((rows[0].get("metadata") or {}).get("question")) or "")


def _recall_at_k(sorted_rows: list[dict[str, Any]], *, gold_ids: set[str], k: int) -> float:
    if not gold_ids:
        return 0.0
    predicted = {str(row.get("doc_id") or "") for row in sorted_rows[:k]}
    return len(predicted & gold_ids) / len(gold_ids)


def _build_single_report(*, corpus_path: Path) -> dict[str, Any]:
    rows = read_json_or_jsonl(corpus_path)
    grouped = _group_by_question(rows)
    per_question: list[dict[str, Any]] = []
    recalls = {2: [], 5: [], 10: []}

    for question_id, docs in grouped.items():
        question = _question_text(docs)
        ranked = sorted(docs, key=lambda row: (_score(question, row), len(str(row.get("text") or ""))), reverse=True)
        gold_ids = {str(row.get("doc_id") or "") for row in docs if row.get("is_gold")}
        question_metrics = {}
        for k in (2, 5, 10):
            metric = _recall_at_k(ranked, gold_ids=gold_ids, k=k)
            recalls[k].append(metric)
            question_metrics[f"Recall@{k}"] = metric
        per_question.append(
            {
                "question_id": question_id,
                "dataset": docs[0].get("dataset"),
                "question": question,
                "gold_doc_count": len(gold_ids),
                "retrieved_doc_ids_top10": [str(row.get("doc_id") or "") for row in ranked[:10]],
                "metrics": question_metrics,
            }
        )

    aggregate = {
        f"Recall@{k}": (sum(values) / len(values) if values else 0.0)
        for k, values in recalls.items()
    }
    return {
        "execution_mode": "stackless",
        "corpus_path": str(corpus_path),
        "dataset": rows[0].get("dataset") if rows else None,
        "question_count": len(per_question),
        "document_count": len(rows),
        "aggregate_metrics": aggregate,
        "questions": per_question,
        "notes": [
            "This is a stackless ingestion smoke report.",
            "It validates corpus usability for retrieval flow.",
            "It is not a real GraphRAG runtime evaluation result.",
        ],
    }


def run_stackless_smoke(*, corpus_path: Path, output_path: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    report = _build_single_report(corpus_path=corpus_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def run_stackless_smoke_many(*, corpus_paths: list[Path], output_path: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    reports = [_build_single_report(corpus_path=path) for path in corpus_paths]
    combined = {
        "execution_mode": "stackless",
        "corpora": [report["corpus_path"] for report in reports],
        "dataset_reports": reports,
        "notes": [
            "This is a stackless ingestion smoke report.",
            "It validates corpus usability for retrieval flow.",
            "It is not a real GraphRAG runtime evaluation result.",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8")
    return combined


def main() -> None:
    parser = argparse.ArgumentParser(description="Run stackless ingestion smoke over benchmark corpus.")
    parser.add_argument("--input", required=True, nargs="+", type=Path)
    parser.add_argument("--output", default=DEFAULT_OUTPUT, type=Path)
    args = parser.parse_args()
    if len(args.input) == 1:
        report = run_stackless_smoke(corpus_path=args.input[0], output_path=args.output)
        payload = {"output": str(args.output), "aggregate_metrics": report["aggregate_metrics"]}
    else:
        report = run_stackless_smoke_many(corpus_paths=list(args.input), output_path=args.output)
        payload = {
            "output": str(args.output),
            "dataset_reports": [
                {
                    "dataset": item.get("dataset"),
                    "aggregate_metrics": item.get("aggregate_metrics"),
                }
                for item in report["dataset_reports"]
            ],
        }
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
