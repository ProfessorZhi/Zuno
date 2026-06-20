import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
SAMPLE_ROOT = REPO_ROOT / "tools" / "evals" / "zuno" / "multihop_eval" / "sample_data"


def test_stackless_index_reports_recall_metrics_from_corpus(tmp_path):
    from tools.evals.zuno.multihop_eval.ingestion.build_corpus import build_corpus
    from tools.evals.zuno.multihop_eval.ingestion.stackless_index import run_stackless_smoke

    corpus_path = tmp_path / "musique_corpus.jsonl"
    build_corpus(
        dataset="musique",
        input_path=SAMPLE_ROOT / "musique_sample.jsonl",
        output_path=corpus_path,
    )
    report_path = tmp_path / "stackless_smoke.json"
    report = run_stackless_smoke(corpus_path=corpus_path, output_path=report_path)

    assert report["execution_mode"] == "stackless"
    assert report["question_count"] >= 1
    assert {"Recall@2", "Recall@5", "Recall@10"} <= set(report["aggregate_metrics"])
    assert report_path.exists()


def test_stackless_index_uses_question_metadata_for_scoring(tmp_path):
    from tools.evals.zuno.multihop_eval.ingestion.stackless_index import run_stackless_smoke

    corpus_path = tmp_path / "corpus.jsonl"
    corpus_path.write_text(
        "\n".join(
            [
                '{"dataset":"hotpotqa","question_id":"q1","doc_id":"d1","title":"alpha","text":"alpha beta answer","sentences":["alpha beta answer"],"is_gold":true,"gold_sent_ids":[0],"metadata":{"question":"alpha answer?","answer":"yes","source":"multihop_eval"}}',
                '{"dataset":"hotpotqa","question_id":"q1","doc_id":"d2","title":"noise","text":"zzz zzz","sentences":["zzz zzz"],"is_gold":false,"gold_sent_ids":[],"metadata":{"question":"alpha answer?","answer":"yes","source":"multihop_eval"}}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    report = run_stackless_smoke(corpus_path=corpus_path, output_path=tmp_path / "report.json")
    assert report["questions"][0]["retrieved_doc_ids_top10"][0] == "d1"


def test_stackless_index_can_merge_multiple_corpora_into_one_report(tmp_path):
    from tools.evals.zuno.multihop_eval.ingestion.build_corpus import build_corpus
    from tools.evals.zuno.multihop_eval.ingestion.stackless_index import run_stackless_smoke_many

    corpus_a = tmp_path / "hotpotqa_corpus.jsonl"
    corpus_b = tmp_path / "twowiki_corpus.jsonl"
    build_corpus(dataset="hotpotqa", input_path=SAMPLE_ROOT / "hotpotqa_sample.jsonl", output_path=corpus_a)
    build_corpus(dataset="twowiki", input_path=SAMPLE_ROOT / "twowiki_sample.jsonl", output_path=corpus_b)

    report = run_stackless_smoke_many(
        corpus_paths=[corpus_a, corpus_b],
        output_path=tmp_path / "stackless_ingestion_smoke.json",
    )

    assert report["execution_mode"] == "stackless"
    assert len(report["dataset_reports"]) == 2
