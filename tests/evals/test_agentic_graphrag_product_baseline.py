from __future__ import annotations

import json

from zuno.agent.contracts import RetrievalProfile, ScenarioSummary, TraceSummary
from zuno.agent.product_baseline import run_workspace_product_e2e_scenario


def test_launchable_agentic_graphrag_product_baseline_generates_shareable_summaries(
    tmp_path,
) -> None:
    result = run_workspace_product_e2e_scenario(output_dir=tmp_path)

    scenario = result.scenario_summary
    trace = result.trace_summary

    assert isinstance(scenario, ScenarioSummary)
    assert isinstance(trace, TraceSummary)
    assert result.scenario_fixture_path.exists()
    assert result.trace_fixture_path.exists()

    fixture = json.loads(result.scenario_fixture_path.read_text(encoding="utf-8"))
    assert fixture["scenario_summary"]["user_question"] == scenario.user_question
    assert fixture["trace_summary"]["trace_id"] == trace.trace_id

    assert scenario.user_question.startswith("Compare renewal")
    assert scenario.selected_skill == "contract_review"
    assert set(scenario.retrieval_profiles.values()) == {"standard", "deep"}
    assert scenario.retrieval_decision.requested_profile is RetrievalProfile.DEEP
    assert scenario.retrieval_decision.effective_profile is RetrievalProfile.DEEP
    assert scenario.retrieval_decision.citation_coverage >= 1.0
    assert "retrieve" in scenario.plan_summary.lower()
    assert scenario.reflection_verdict["decision"] == "finish"
    assert scenario.reflection_verdict["citation_coverage"] >= 1.0
    assert scenario.replan_event["trigger"] == "retrieval_empty"
    assert scenario.replan_event["trajectory_changed"] is True
    assert scenario.artifact_content_excerpt
    assert len(scenario.artifact_content_excerpt) < 600
    assert scenario.citations
    assert scenario.citation_lineage
    assert scenario.citation_lineage[0]["parse_job_id"].startswith("parse_")
    assert scenario.citation_lineage[0]["source_sha256"]

    metrics = scenario.metrics_summary
    assert metrics["latency_ms"] >= 0
    assert metrics["cost_estimate"] == 0.0
    assert metrics["token_count"] >= 0
    assert metrics["evidence_count"] >= 1
    assert metrics["citation_coverage"] >= 1.0
    assert metrics["retrieval_profile_evidence"] == {
        "standard": True,
        "deep": True,
        "deep_without_graph": True,
    }
    assert metrics["native_formats"] == {
        "text/plain": "indexed",
        "text/markdown": "indexed",
        "text/csv": "indexed",
        "application/json": "indexed",
        "text/html": "indexed",
        "text/x-python": "indexed",
    }
    blocked_evidence = metrics["blocked_parser_evidence"]
    assert set(blocked_evidence) == {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "image/png",
    }
    for evidence in blocked_evidence.values():
        assert evidence["status"] == "blocked"
        assert evidence["index_job_created"] is False
        assert evidence["blocked_reason"]
        assert evidence["dependency_probe"]["external_dependency_status"] == "target_blocked"
    assert metrics["binary_source_object"]["bytes_verified"] is True
    assert metrics["binary_source_object"]["storage_uri"].startswith("file:")
    assert metrics["dead_letter"]["status"] == "dead_letter"
    assert metrics["reconciler_findings"]
    assert metrics["reflexion_candidate"]["review_status"] == "pending"

    assert scenario.feedback_result["durable_status"] == "persisted"
    assert scenario.feedback_result["dataset_candidate"] is True
    assert scenario.restart_rehydrate_result == {
        "task": "available",
        "artifact": "available",
        "feedback": "available",
        "cited_answer": "available",
    }
    for status in ["queued", "parsing", "parsed", "indexing", "indexed", "blocked"]:
        assert status in scenario.file_status_timeline
    assert scenario.parser_dependency_probe is not None
    assert scenario.parser_dependency_probe.status == "target_blocked"
    assert scenario.blocked_reason
    assert scenario.worker_event["parse_worker_status"] == "succeeded"
    assert scenario.worker_event["index_worker_status"] == "succeeded"
    assert scenario.index_status == "indexed_with_blocked_inputs_no_fake_index"

    event_types = [event.event_type for event in trace.events]
    assert "strategy_selected" in event_types
    assert "skill_selected" in event_types
    assert "plan_created" in event_types
    assert "retrieval" in event_types
    assert "reflection_completed" in event_types
    assert "replan_created" in event_types
    assert "reflexion_candidate_created" in event_types
    assert "answer_finalized" in event_types
    assert "feedback_received" in event_types
    assert {metric.name for metric in trace.metrics} >= {
        "citation_coverage",
        "evidence_count",
        "latency_ms",
        "cost_estimate",
    }
    assert trace.cost_summary.model_id == "local-runtime"
