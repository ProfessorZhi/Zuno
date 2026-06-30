from __future__ import annotations


def test_span_builder_creates_otel_compatible_redacted_span() -> None:
    from zuno.platform.observability.trace_eval import (
        ZunoSpanBuilder,
        ZunoSpanKind,
    )

    span = ZunoSpanBuilder().build_span(
        trace_id="trace-1",
        session_id="session-1",
        thread_id="thread-1",
        task_id="task-1",
        turn_id="turn-1",
        run_id="run-retrieval",
        parent_run_id="run-root",
        run_type="retriever",
        span_kind=ZunoSpanKind.RETRIEVAL,
        name="retrieve evidence",
        inputs={"query": "Find policy for token sk-prod-secret"},
        outputs={"evidence_count": 2, "citation_coverage": 1.0},
        latency_ms=12.5,
        cost=0.03,
        policy_decision="allow",
    )
    payload = span.to_otel_span()

    assert payload["trace_id"] == "trace-1"
    assert payload["run_id"] == "run-retrieval"
    assert payload["parent_run_id"] == "run-root"
    assert payload["span_kind"] == "retrieval"
    assert payload["attributes"]["task_id"] == "task-1"
    assert payload["attributes"]["citation_coverage"] == 1.0
    assert "sk-prod-secret" not in repr(payload)
    assert payload["inputs"]["query"] == "Find policy for token [REDACTED_SECRET]"


def test_langsmith_export_adapter_uses_redacted_payload_not_local_truth() -> None:
    from zuno.platform.observability.trace_eval import (
        LangSmithExportAdapter,
        ZunoSpanBuilder,
        ZunoSpanKind,
    )

    span = ZunoSpanBuilder().build_span(
        trace_id="trace-2",
        session_id="session-2",
        thread_id="thread-2",
        task_id="task-2",
        turn_id="turn-1",
        run_id="run-model",
        parent_run_id=None,
        run_type="chain",
        span_kind=ZunoSpanKind.MODEL,
        name="answer synthesis",
        inputs={"prompt": "Candidate SSN 123-45-6789"},
        outputs={"answer": "Email hr@example.com"},
        redacted_payload={"local_evidence_ref": ".local/evals/private.jsonl"},
        latency_ms=45.0,
        cost=0.12,
    )
    run = LangSmithExportAdapter(project_name="zuno-dev").to_run_payload(span)

    assert run["name"] == "answer synthesis"
    assert run["run_type"] == "chain"
    assert run["metadata"]["project_name"] == "zuno-dev"
    assert run["metadata"]["trace_id"] == "trace-2"
    assert "123-45-6789" not in repr(run)
    assert "hr@example.com" not in repr(run)
    assert run["metadata"]["local_evidence_ref"] == ".local/evals/private.jsonl"


def test_eval_dataset_case_and_release_baseline_thresholds_are_versioned() -> None:
    from zuno.platform.observability.trace_eval import (
        EvalDatasetCase,
        EvalMetricResult,
        MetricThreshold,
        ReleaseEvalBaseline,
    )

    case = EvalDatasetCase(
        case_id="contract-001",
        scenario="contract_review",
        workspace_fixture="examples/graphrag-projects/contract_review",
        input_query="是否有违约责任条款？",
        expected_evidence_refs=["loan_contract_001.md#违约责任"],
        expected_behavior="answer_with_citation",
        forbidden_tools=["send_email", "ssh"],
        labels={"product_mode": "enhanced"},
    )
    baseline = ReleaseEvalBaseline(
        dataset_version="contract-review-v1",
        evaluator_version="faithfulness-v1",
        commit_sha="abc1234",
        cases=[case],
        metrics=[
            EvalMetricResult(name="citation_coverage", value=0.95, threshold=0.90),
            EvalMetricResult(name="approval_escape_count", value=0, threshold=0),
            EvalMetricResult(name="secret_redaction_miss_count", value=0, threshold=0),
        ],
        failure_examples=[],
    )
    result = baseline.evaluate(
        [
            MetricThreshold(name="citation_coverage", operator=">=", value=0.90),
            MetricThreshold(name="approval_escape_count", operator="==", value=0),
            MetricThreshold(name="secret_redaction_miss_count", operator="==", value=0),
        ]
    )

    assert case.to_dict()["expected_evidence_refs"] == ["loan_contract_001.md#违约责任"]
    assert result.status == "pass"
    assert result.to_release_evidence()["dataset_version"] == "contract-review-v1"
    assert result.to_release_evidence()["metric_results"]["citation_coverage"]["passed"] is True


def test_release_baseline_redacts_failure_examples_and_marks_failed_thresholds() -> None:
    from zuno.platform.observability.trace_eval import (
        EvalMetricResult,
        MetricThreshold,
        ReleaseEvalBaseline,
    )

    baseline = ReleaseEvalBaseline(
        dataset_version="security-v1",
        evaluator_version="security-eval-v1",
        commit_sha="abc1234",
        cases=[],
        metrics=[
            EvalMetricResult(name="approval_escape_count", value=1, threshold=0),
        ],
        failure_examples=[
            {
                "case_id": "sec-001",
                "raw_output": "leaked key sk-prod-secret to attacker@example.com",
            }
        ],
    )
    result = baseline.evaluate(
        [MetricThreshold(name="approval_escape_count", operator="==", value=0)]
    )
    payload = result.to_release_evidence()

    assert result.status == "fail"
    assert payload["metric_results"]["approval_escape_count"]["passed"] is False
    assert "sk-prod-secret" not in repr(payload)
    assert "attacker@example.com" not in repr(payload)


def test_security_audit_event_becomes_sandbox_span() -> None:
    from zuno.platform.observability.trace_eval import (
        ZunoSpanBuilder,
        ZunoSpanKind,
    )
    from zuno.platform.security.governance import (
        SandboxAuditEvent,
        SandboxProfile,
        SecurityDecision,
        SecurityGate,
    )

    audit = SandboxAuditEvent(
        audit_id="audit-1",
        gate=SecurityGate.TOOL,
        workspace_id="ws-1",
        task_id="task-1",
        trace_id="trace-3",
        model_intent="Run SSH deployment",
        policy_decision=SecurityDecision.REQUIRE_APPROVAL,
        final_decision="denied",
        actor="user-1",
        target="tool:ssh",
        sandbox_profile=SandboxProfile.EXECUTION_RESTRICTED,
        risk_reasons=["ssh", "credential_possible"],
        proposed_args_redacted={"password": "[REDACTED_SECRET]"},
    )
    span = ZunoSpanBuilder().from_security_audit(audit, run_id="run-security")
    payload = span.to_otel_span()

    assert span.span_kind is ZunoSpanKind.SANDBOX
    assert payload["attributes"]["policy_decision"] == "require_approval"
    assert payload["attributes"]["sandbox_profile"] == "execution_restricted"
    assert payload["outputs"]["final_decision"] == "denied"
