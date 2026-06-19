import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
SAMPLE_ROOT = REPO_ROOT / "tools" / "evals" / "zuno" / "multihop_eval" / "sample_data"


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _assert_normalized_record(record: dict, dataset: str) -> None:
    assert record["dataset"] == dataset
    assert record["id"]
    assert record["question"]
    assert record["answer"]
    assert isinstance(record["documents"], list) and record["documents"]
    assert {"doc_id", "title", "sentences", "text"} <= set(record["documents"][0])
    assert isinstance(record["gold_support"], list) and record["gold_support"]
    assert {"title", "sent_id", "text"} <= set(record["gold_support"][0])
    assert isinstance(record["gold_entities"], list)
    assert isinstance(record["gold_evidence_path"], list)
    assert isinstance(record["metadata"], dict)


def test_multihop_sample_fixtures_follow_normalized_schema():
    expected = {
        "hotpotqa_sample.jsonl": "hotpotqa",
        "twowiki_sample.jsonl": "2wikimultihopqa",
        "musique_sample.jsonl": "musique",
    }
    for file_name, dataset in expected.items():
        records = _read_jsonl(SAMPLE_ROOT / file_name)
        assert len(records) >= 1
        _assert_normalized_record(records[0], dataset)


def test_hotpotqa_adapter_normalizes_context_and_supporting_facts():
    from tools.evals.zuno.multihop_eval.adapters.hotpotqa import normalize_records

    raw = [{
        "_id": "hp_1",
        "question": "Which city links Alpha and Beta?",
        "answer": "Paris",
        "context": [["Alpha", ["Alpha starts in Paris.", "Alpha ends."]], ["Beta", ["Beta mentions Paris."]]],
        "supporting_facts": [["Alpha", 0], ["Beta", 0]],
        "type": "bridge",
        "level": "easy",
    }]

    records = normalize_records(raw)

    _assert_normalized_record(records[0], "hotpotqa")
    assert records[0]["gold_support"][0]["text"] == "Alpha starts in Paris."
    assert records[0]["metadata"]["type"] == "bridge"


def test_twowiki_adapter_normalizes_evidence_triples():
    from tools.evals.zuno.multihop_eval.adapters.twowiki import normalize_records

    raw = [{
        "_id": "tw_1",
        "question": "Who connects A and B?",
        "answer": "Ada",
        "context": [["A", ["A mentions Ada."]], ["B", ["B also mentions Ada."]]],
        "supporting_facts": [["A", 0], ["B", 0]],
        "evidences": [["A", "connected_to", "Ada"]],
        "type": "inference",
    }]

    records = normalize_records(raw)

    _assert_normalized_record(records[0], "2wikimultihopqa")
    assert records[0]["gold_entities"] == ["A", "Ada"]
    assert records[0]["gold_evidence_path"][0]["relation"] == "connected_to"


def test_musique_adapter_normalizes_paragraph_support_flags():
    from tools.evals.zuno.multihop_eval.adapters.musique import normalize_records

    raw = [{
        "id": "mu_1",
        "question": "What links the two facts?",
        "answer": "Ada",
        "paragraphs": [
            {"idx": 0, "title": "A", "paragraph_text": "A mentions Ada.", "is_supporting": True},
            {"idx": 1, "title": "B", "paragraph_text": "B is a distractor.", "is_supporting": False},
        ],
        "question_decomposition": [{"id": 1, "question": "Who is mentioned?", "answer": "Ada"}],
    }]

    records = normalize_records(raw)

    _assert_normalized_record(records[0], "musique")
    assert records[0]["gold_support"][0]["title"] == "A"
    assert records[0]["metadata"]["question_decomposition"][0]["answer"] == "Ada"


def test_downloader_rejects_unknown_dataset():
    from tools.evals.zuno.multihop_eval.download_datasets import resolve_download_plan

    try:
        resolve_download_plan(dataset="unknown", split="dev")
    except ValueError as error:
        assert "Unsupported dataset" in str(error)
    else:
        raise AssertionError("unknown dataset should be rejected")


def test_downloader_resolves_expected_dataset_sources():
    from tools.evals.zuno.multihop_eval.download_datasets import resolve_download_plan

    hotpot = resolve_download_plan(dataset="hotpotqa", split="dev")
    twowiki = resolve_download_plan(dataset="twowiki", split="dev")
    musique = resolve_download_plan(dataset="musique", split="dev")

    assert hotpot.raw_name == "hotpot_dev_distractor_v1.json"
    assert "curtis.ml.cmu.edu/datasets/hotpot" in hotpot.url
    assert twowiki.raw_name == "data_ids_april7.zip"
    assert "ms2m13252h6xubs" in twowiki.url
    assert musique.raw_name == "musique_v1.0.zip"
    assert musique.gdown_id == "1tGdADlNjWFaHLeZZGShh2IRcpO6Lv24h"
