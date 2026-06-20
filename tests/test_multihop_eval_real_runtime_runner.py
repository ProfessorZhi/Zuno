import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


def test_real_runtime_runner_resolves_public_modes():
    from tools.evals.zuno.multihop_eval.run_real_runtime_eval import resolve_runtime_mode

    assert resolve_runtime_mode("baseline_rag") == "rag"
    assert resolve_runtime_mode("local_graphrag") == "local_graphrag"
    assert resolve_runtime_mode("deep_graphrag") == "rag_graph_deep"


def test_real_runtime_runner_loads_named_eval_profile(tmp_path):
    from tools.evals.zuno.multihop_eval.run_real_runtime_eval import resolve_eval_profile

    profile_file = tmp_path / "profiles.json"
    profile_file.write_text(
        json.dumps({"retrieval_only_text_multihop": {"conversation_model": "deepseek-v4-flash"}}),
        encoding="utf-8",
    )

    payload = resolve_eval_profile(
        profile_file=profile_file,
        profile_name="retrieval_only_text_multihop",
    )

    assert payload["conversation_model"] == "deepseek-v4-flash"
    assert payload["profile_name"] == "retrieval_only_text_multihop"


def test_real_runtime_runner_builds_gold_doc_ids_from_titles():
    from tools.evals.zuno.multihop_eval.run_real_runtime_eval import build_gold_doc_ids

    record = {
        "documents": [
            {"doc_id": "doc-a", "title": "Alpha"},
            {"doc_id": "doc-b", "title": "Beta"},
        ],
        "gold_support": [
            {"title": "Alpha"},
            {"title": "Beta"},
            {"title": "Alpha"},
        ],
    }

    assert build_gold_doc_ids(record) == ["doc-a", "doc-b"]
