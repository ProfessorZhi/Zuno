import asyncio
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


def test_graph_index_smoke_reports_missing_persisted_runtime_and_local_artifact_stats(tmp_path):
    from tools.evals.zuno.multihop_eval.ingestion.build_corpus import build_corpus
    from tools.evals.zuno.multihop_eval.ingestion.check_graph_index_smoke import build_graph_index_smoke

    sample_root = REPO_ROOT / "tools" / "evals" / "zuno" / "multihop_eval" / "sample_data"
    questions_path = sample_root / "hotpotqa_sample.jsonl"
    corpus_path = tmp_path / "hotpotqa_corpus.jsonl"
    build_corpus(dataset="hotpotqa", input_path=questions_path, output_path=corpus_path)

    report = asyncio.run(
        build_graph_index_smoke(
            dataset="hotpotqa",
            knowledge_id="kb_eval_smoke",
            questions_path=questions_path,
            corpus_path=corpus_path,
            limit=1,
        )
    )

    assert report["execution_mode"] == "graph_index_smoke"
    assert report["graph_index_missing"] is True
    assert report["chunk_count"] >= 1
    assert report["entity_count"] >= 0
    assert report["relation_count"] >= 0
    assert report["questions"][0]["seed_entity_count"] >= 0
    assert "graph_path_empty" in report["questions"][0]["status"]


def test_graph_index_smoke_resolves_default_corpus_path():
    from tools.evals.zuno.multihop_eval.ingestion.check_graph_index_smoke import resolve_default_corpus_path

    path = resolve_default_corpus_path("hotpotqa")
    assert path.name == "dev_sample50_corpus.jsonl"
    assert "hotpotqa" in str(path)
