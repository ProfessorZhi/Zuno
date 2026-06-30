import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
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


def test_real_runtime_runner_deduplicates_corpus_documents_before_chunk_build():
    from tools.evals.zuno.multihop_eval.run_real_runtime_eval import build_chunks_from_corpus

    rows = [
        {
            "dataset": "hotpotqa",
            "question_id": "q1",
            "doc_id": "shared-doc",
            "title": "Shared",
            "text": "same body",
        },
        {
            "dataset": "hotpotqa",
            "question_id": "q2",
            "doc_id": "shared-doc",
            "title": "Shared",
            "text": "same body",
        },
    ]

    chunks = build_chunks_from_corpus(corpus_rows=rows, knowledge_id="kb_1")

    assert len(chunks) == 1
    assert chunks[0].chunk_id == "shared-doc::0"
    assert chunks[0].file_id == "shared-doc"


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
            "evidence_verdict": {
                "status": "low_confidence",
                "fallback_reason": "citation_coverage_below_threshold",
            },
            "artifact_manifest": {
                "trace_id": "trace-eval-1",
            },
            "runtime_trace_events": [
                {"kind": "pre_retrieval"},
                {"kind": "post_answer"},
            ],
            "runtime_turn_ledger": {
                "stage_order": [
                    "prepare_context",
                    "capability_selection",
                    "agent_loop",
                    "knowledge_retrieval_trace",
                    "tool_trace",
                    "post_turn_commit",
                ],
                "layers_touched": ["agent", "context", "capability", "knowledge", "trace", "memory"],
                "post_turn_memory_event_ids": ["ga-1:turn"],
                "knowledge_trace": {"trace_id": "trace-eval-1"},
                "tool_trace_events": [
                    {"kind": "pre_tool"},
                    {"kind": "post_tool"},
                ],
            },
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
    assert diagnostics["evidence_verdict_status"] == "low_confidence"
    assert diagnostics["evidence_verdict_fallback_reason"] == "citation_coverage_below_threshold"
    assert diagnostics["artifact_manifest_trace_id"] == "trace-eval-1"
    assert diagnostics["runtime_trace_event_count"] == 2
    assert diagnostics["runtime_turn_stage_order"] == [
        "prepare_context",
        "capability_selection",
        "agent_loop",
        "knowledge_retrieval_trace",
        "tool_trace",
        "post_turn_commit",
    ]
    assert diagnostics["runtime_turn_layers_touched"] == ["agent", "context", "capability", "knowledge", "trace", "memory"]
    assert diagnostics["runtime_turn_post_memory_event_count"] == 1
    assert diagnostics["runtime_turn_knowledge_trace_id"] == "trace-eval-1"
    assert diagnostics["runtime_turn_tool_trace_event_count"] == 2
    assert "seed_entities not exposed by runtime metadata" not in notes


def test_real_runtime_runner_registers_project_payload_runtime_key():
    source = (
        REPO_ROOT / "tools/evals/zuno/multihop_eval/run_real_runtime_eval.py"
    ).read_text(encoding="utf-8")

    assert '"project_payload": None' in source
    assert '"domain_pack": None' not in source
