from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from tools.evals.zuno.multihop_eval.adapters.common import read_json_or_jsonl, write_jsonl


def _normalize_dataset_name(dataset: str) -> str:
    normalized = str(dataset or "").strip().lower()
    if normalized in {"twowiki", "2wiki"}:
        return "2wikimultihopqa"
    return normalized


def _build_gold_map(record: dict[str, Any]) -> dict[str, list[int]]:
    by_title: dict[str, list[int]] = defaultdict(list)
    for item in record.get("gold_support") or []:
        title = str(item.get("title") or "").strip()
        if not title:
            continue
        try:
            sent_id = int(item.get("sent_id"))
        except (TypeError, ValueError):
            continue
        by_title[title].append(sent_id)
    for title in list(by_title.keys()):
        by_title[title] = sorted(set(by_title[title]))
    return by_title


def build_corpus_rows(records: list[dict[str, Any]], *, dataset: str) -> list[dict[str, Any]]:
    dataset_name = _normalize_dataset_name(dataset)
    rows: list[dict[str, Any]] = []
    for record in records:
        question_id = str(record.get("id") or "").strip()
        if not question_id:
            continue
        question = str(record.get("question") or "")
        answer = str(record.get("answer") or "")
        gold_map = _build_gold_map(record)
        for document in record.get("documents") or []:
            title = str(document.get("title") or "")
            gold_sent_ids = gold_map.get(title, [])
            rows.append(
                {
                    "dataset": dataset_name,
                    "question_id": question_id,
                    "doc_id": str(document.get("doc_id") or title or ""),
                    "title": title,
                    "text": str(document.get("text") or ""),
                    "sentences": list(document.get("sentences") or []),
                    "is_gold": bool(gold_sent_ids),
                    "gold_sent_ids": gold_sent_ids,
                    "metadata": {
                        "answer": answer,
                        "question": question,
                        "source": "multihop_eval",
                    },
                }
            )
    return rows


def summarize_corpus(rows: list[dict[str, Any]]) -> dict[str, int]:
    question_ids = {str(row.get("question_id") or "") for row in rows if row.get("question_id")}
    gold_docs = sum(1 for row in rows if row.get("is_gold"))
    return {
        "corpus_rows": len(rows),
        "question_count": len(question_ids),
        "gold_doc_count": gold_docs,
    }


def build_corpus(*, dataset: str, input_path: Path, output_path: Path) -> dict[str, Any]:
    records = read_json_or_jsonl(input_path)
    rows = build_corpus_rows(records, dataset=dataset)
    write_jsonl(output_path, rows)
    summary = summarize_corpus(rows)
    return {
        "dataset": _normalize_dataset_name(dataset),
        "input": str(input_path),
        "output": str(output_path),
        **summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build benchmark corpus documents from normalized multihop JSONL.")
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    summary = build_corpus(dataset=args.dataset, input_path=args.input, output_path=args.output)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
