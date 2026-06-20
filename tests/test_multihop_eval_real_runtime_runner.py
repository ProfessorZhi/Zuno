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


def test_real_runtime_runner_extracts_route_diagnostics_from_runtime_payload():
    from tools.evals.zuno.multihop_eval.run_real_runtime_eval import extract_route_diagnostics

    runtime_result = {
        "metadata": {
            "route_policy": "auto",
            "requested_mode": "local_graphrag",
            "resolved_mode": "hybrid_rag",
            "internal_route": "standard_rag",
            "seed_entities": ["Scott Derrickson", "Ed Wood"],
            "seed_entities_with_source": [
                {"value": "Scott Derrickson", "source": "query"},
                {"value": "Ed Wood", "source": "baseline_title"},
            ],
            "graph_worthy": True,
            "retriever_runs": [
                {"source": "vector"},
                {"source": "graph"},
            ],
            "rounds": [{"round": 1}, {"round": 2}],
        },
        "first_pass_result": {
            "graph_result": {
                "documents": [{"chunk_id": "c1"}],
                "paths": ["A -> B", "B -> C"],
            },
            "community_result": {
                "used_communities": ["community-0"],
                "follow_up_questions": ["follow-up"],
            },
        },
    }

    diagnostics, notes = extract_route_diagnostics(
        runtime_result=runtime_result,
        fallback=True,
        fallback_reason="graph_result_empty",
    )

    assert diagnostics["requested_mode"] == "local_graphrag"
    assert diagnostics["resolved_mode"] == "hybrid_rag"
    assert diagnostics["internal_route"] == "standard_rag"
    assert diagnostics["route_policy"] == "auto"
    assert diagnostics["retriever_used"] == ["vector", "graph"]
    assert diagnostics["graph_worthy"] is True
    assert diagnostics["graph_result_count"] == 1
    assert diagnostics["graph_path_count"] == 2
    assert diagnostics["seed_entities_with_source"][1]["source"] == "baseline_title"
    assert diagnostics["community_report_count"] == 1
    assert diagnostics["drift_followup_count"] == 1
    assert diagnostics["seed_entities"] == ["Scott Derrickson", "Ed Wood"]
    assert diagnostics["seed_entity_count"] == 2
    assert "seed_entities not exposed by runtime metadata" not in notes
