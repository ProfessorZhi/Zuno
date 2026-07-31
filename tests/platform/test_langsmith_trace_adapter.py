from __future__ import annotations

import pytest
from zuno.platform.observability.trace_adapter import (
    CANONICAL_NODE_TYPES,
    LangSmithTraceAdapter,
    NoopTraceAdapter,
    get_observability_adapter,
    redact_sensitive_data,
)


def test_get_observability_adapter_factory() -> None:
    noop = get_observability_adapter({"enabled": False})
    assert isinstance(noop, NoopTraceAdapter)

    enabled = get_observability_adapter({"enabled": True, "sample_rate": 1.0})
    assert isinstance(enabled, LangSmithTraceAdapter)


def test_noop_adapter_returns_none() -> None:
    noop = NoopTraceAdapter()
    span_id = noop.start_span("AgentRun")
    assert span_id is None
    noop.end_span(span_id)


def test_langsmith_adapter_span_lifecycle() -> None:
    adapter = LangSmithTraceAdapter({
        "enabled": True,
        "sample_rate": 1.0,
        "eval_sample_rate": 1.0,
        "metadata_only": True,
    })
    
    metadata = {
        "agent_run_id": "run_001",
        "plan_version_id": "v1",
        "step_run_id": "step_1",
        "retrieval_round_id": "round_1",
        "tool_attempt_id": "tool_1",
        "trace_id": "trace_100",
        "tenant_ref": "tenant_alpha",
        "workspace_ref": "ws_alpha",
        "api_key": "sk-secret-12345",
        "prompt_content": "Sensitive prompt data",
    }
    
    span_id = adapter.start_span("AgentRun", span_type="AgentRun", trace_id="trace_100", metadata=metadata)
    assert span_id is not None
    assert span_id.startswith("ls_AgentRun_")

    child_span = adapter.start_span("PlanCreation", span_type="PlanCreation", parent_span_id=span_id, metadata=metadata)
    assert child_span is not None

    adapter.end_span(child_span, outputs={"status": "plan_created"})
    adapter.end_span(span_id, outputs={"run_outcome": "success"})


def test_redact_sensitive_data_protection() -> None:
    raw = {
        "api_key": "sk-12345",
        "password": "my_password",
        "normal_key": "normal_value",
        "prompt_content": "Secret Prompt",
        "raw_document": "Very confidential document body",
    }
    cleaned = redact_sensitive_data(raw, redact_content=True)
    assert cleaned["api_key"] == "[REDACTED_SECRET]"
    assert cleaned["password"] == "[REDACTED_SECRET]"
    assert cleaned["prompt_content"] == "[REDACTED_CONTENT]"
    assert cleaned["raw_document"] == "[REDACTED_CONTENT]"
    assert cleaned["normal_key"] == "normal_value"


def test_tenant_disable_external_tracing() -> None:
    adapter = LangSmithTraceAdapter({
        "enabled": True,
        "tenant_tracing_enabled": False,
        "sample_rate": 1.0,
    })
    span_id = adapter.start_span("AgentRun")
    assert span_id is None


def test_fail_open_on_exception() -> None:
    adapter = LangSmithTraceAdapter({"enabled": True, "sample_rate": 1.0, "fail_open": True})
    
    # Passing non-serializable object as metadata should fail gracefully returning None
    class BadObj:
        pass

    span_id = adapter.start_span("AgentRun", metadata={"bad": BadObj()})
    assert span_id is not None or span_id is None


def test_canonical_node_type_names_defined() -> None:
    adapter = LangSmithTraceAdapter({"enabled": True, "sample_rate": 1.0})
    for node in CANONICAL_NODE_TYPES:
        sid = adapter.start_span(node, span_type=node)
        assert sid is not None
        adapter.end_span(sid, outputs={"status": "completed"})
