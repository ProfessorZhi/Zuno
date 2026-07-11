from __future__ import annotations

import json

import pytest

from zuno.agent.product_baseline import run_workspace_product_e2e_scenario
from zuno.platform.observability.product_benchmark import (
    build_agentic_graphrag_regression_summary,
)


def test_agentic_graphrag_regression_summary_consumes_phase12_e2e_output(tmp_path) -> None:
    e2e = run_workspace_product_e2e_scenario(output_dir=tmp_path / "scenario")

    summary = build_agentic_graphrag_regression_summary(
        scenario=e2e.scenario_summary,
        trace=e2e.trace_summary,
        output_dir=tmp_path,
        commit_sha="phase13-local",
    )

    assert summary.conversation.task_id == "task_phase12_product"
    assert summary.conversation.selected_knowledge_spaces == [
        "ks_phase12_standard",
        "ks_phase12_deep",
    ]
    assert summary.conversation.retrieval_profiles == {
        "ks_phase12_standard": "standard",
        "ks_phase12_deep": "deep",
    }
    assert summary.conversation.selected_skill == "contract_review"

    stage_names = {stage.stage_name for stage in summary.stages}
    assert {
        "file_upload",
        "object_store_write",
        "input_gate",
        "parse_queue",
        "parse_worker",
        "document_ir",
        "index_queue",
        "index_worker",
        "retrieval",
        "rerank",
        "graph_expand",
        "tool_call",
        "planning",
        "reflection",
        "replan",
        "answer",
        "output_gate",
        "artifact",
        "feedback",
    } <= stage_names
    assert all(stage.model_id == "local-runtime" for stage in summary.stages)

    assert summary.ingestion.files_uploaded == 10
    assert summary.ingestion.files_indexed == 6
    assert summary.ingestion.files_failed == 0
    assert summary.ingestion.files_blocked == 4
    assert summary.ingestion.dependency_status == "target_blocked"
    assert summary.ingestion.dead_letter_count == 1
    assert summary.ingestion.reconciler_findings
    assert summary.ingestion.binary_bytes_processed > 0

    assert summary.retrieval.retrieval_rounds >= 3
    assert summary.retrieval.evidence_count >= 1
    assert summary.retrieval.citation_count >= 1
    assert summary.retrieval.citation_coverage >= 1.0
    assert "deep_without_graph" in summary.retrieval.retrievers_used

    assert summary.planning.plan_step_count >= 1
    assert summary.planning.skill_selected == "contract_review"
    assert summary.planning.replan_count == 1
    assert summary.planning.reflection_count >= 1
    assert summary.planning.reflexion_count == 1
    assert summary.planning.replan_reason == "retrieval_empty"

    assert summary.security.input_blocks == 0
    assert summary.security.output_dlp_blocks == 0
    assert summary.cost.model_id == "local-runtime"
    assert summary.cost.cost_estimate == 0.0

    assert {report.baseline_label for report in summary.baseline_comparison} == {
        "basic_rag",
        "static_graphrag",
        "agentic_graphrag",
    }
    assert summary.answers["pdf_office_ocr_no_fake_index"] is True
    assert summary.answers["binary_sha256_traceability"] is True
    assert summary.answers["agentic_replan_changed_trajectory"] is True

    assert summary.release_evidence["status"] == "pass"
    assert summary.release_evidence["metric_results"]["citation_coverage"]["passed"] is True
    assert summary.release_evidence["metric_results"]["blocked_fake_index_count"]["passed"] is True
    assert summary.summary_path is not None
    payload = json.loads(summary.summary_path.read_text(encoding="utf-8"))
    assert payload["conversation"]["task_id"] == "task_phase12_product"
    assert payload["answers"]["pdf_office_ocr_no_fake_index"] is True


def test_agentic_graphrag_regression_summary_rejects_missing_required_stage(tmp_path) -> None:
    e2e = run_workspace_product_e2e_scenario(output_dir=tmp_path / "scenario")

    with pytest.raises(ValueError, match="missing required stage metrics"):
        build_agentic_graphrag_regression_summary(
            scenario=e2e.scenario_summary,
            trace=e2e.trace_summary,
            required_stage_names=["file_upload", "nonexistent_stage"],
        )
