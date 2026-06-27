import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
SAMPLE_ROOT = REPO_ROOT / "tools" / "evals" / "zuno" / "multihop_eval" / "sample_data"


def test_corpus_builder_converts_normalized_rows_to_document_rows(tmp_path):
    from tools.evals.zuno.multihop_eval.ingestion.build_corpus import build_corpus

    output = tmp_path / "hotpotqa_corpus.jsonl"
    result = build_corpus(
        dataset="hotpotqa",
        input_path=SAMPLE_ROOT / "hotpotqa_sample.jsonl",
        output_path=output,
    )

    rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert result["corpus_rows"] == len(rows)
    assert result["question_count"] == 1
    assert result["gold_doc_count"] >= 1
    assert rows[0]["question_id"]
    assert {"dataset", "question_id", "doc_id", "title", "text", "sentences", "is_gold", "gold_sent_ids", "metadata"} <= set(rows[0])


def test_corpus_builder_maps_gold_support_back_to_document():
    from tools.evals.zuno.multihop_eval.adapters.common import read_json_or_jsonl
    from tools.evals.zuno.multihop_eval.ingestion.build_corpus import build_corpus_rows

    records = read_json_or_jsonl(SAMPLE_ROOT / "twowiki_sample.jsonl")
    rows = build_corpus_rows(records, dataset="twowiki")

    gold_rows = [row for row in rows if row["is_gold"]]
    assert gold_rows
    assert any(row["gold_sent_ids"] for row in gold_rows)
    assert all(row["question_id"] == rows[0]["question_id"] for row in rows)


def test_corpus_builder_summary_counts_questions_and_gold_docs():
    from tools.evals.zuno.multihop_eval.ingestion.build_corpus import summarize_corpus

    rows = [
        {"question_id": "q1", "is_gold": True},
        {"question_id": "q1", "is_gold": False},
        {"question_id": "q2", "is_gold": True},
    ]
    summary = summarize_corpus(rows)
    assert summary == {"corpus_rows": 3, "question_count": 2, "gold_doc_count": 2}
