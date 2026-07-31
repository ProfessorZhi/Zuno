from __future__ import annotations

from unittest.mock import MagicMock, create_autospec
import uuid
from typing import Any, Dict, List, Optional
import pytest
import yaml

from langsmith import Client
from zuno.platform.settings import resolve_app_config_path
from zuno.platform.observability.trace_adapter import (
    CANONICAL_NODE_TYPES,
    InMemoryTraceAdapter,
    LangSmithTraceAdapter,
    NoopTraceAdapter,
    ObservabilityConfigError,
    ObservabilityDependencyError,
    ObservabilityTraceError,
    TraceSpanHandle,
    get_observability_adapter,
    is_valid_uuid,
    redact_sensitive_data,
)


def create_autospec_client() -> MagicMock:
    """Create an autospec mock for langsmith.Client verifying method signatures."""
    mock_client = create_autospec(Client, instance=True)
    create_calls: List[Dict[str, Any]] = []
    update_calls: List[Dict[str, Any]] = []

    def mock_create_run(**kwargs: Any) -> None:
        create_calls.append(kwargs)

    def mock_update_run(**kwargs: Any) -> None:
        update_calls.append(kwargs)

    mock_client.create_run.side_effect = mock_create_run
    mock_client.update_run.side_effect = mock_update_run
    mock_client.create_calls = create_calls
    mock_client.update_calls = update_calls
    return mock_client


def test_1_autospec_client_signature_validation() -> None:
    client = create_autospec_client()
    adapter = LangSmithTraceAdapter({"enabled": True, "sample_rate": 1.0}, client=client)

    handle = adapter.start_span("TestSpan", metadata={"k": "v"})
    assert handle is not None
    assert len(client.create_calls) == 1
    # Verify autospec accepts parameters matching official Client.create_run signature
    assert "name" in client.create_calls[0]
    assert "run_type" in client.create_calls[0]

    adapter.end_span(handle, outputs={"ok": True})
    assert len(client.update_calls) == 1
    assert "run_id" in client.update_calls[0]


def test_2_zuno_trace_id_not_used_directly_if_not_uuid() -> None:
    client = create_autospec_client()
    adapter = LangSmithTraceAdapter({"enabled": True, "sample_rate": 1.0}, client=client)

    # String trace_id that is NOT a valid UUID
    non_uuid_trace_id = "zuno_trace_12345_non_uuid"
    handle = adapter.start_span("SpanNonUUID", trace_id=non_uuid_trace_id)
    assert handle is not None

    create_call = client.create_calls[0]
    # LangSmith create_run call MUST NOT receive non-UUID string as trace_id
    assert "trace_id" not in create_call
    # Non-UUID Zuno trace_id MUST be saved to metadata.zuno_trace_id
    assert create_call["extra"]["metadata"]["zuno_trace_id"] == non_uuid_trace_id

    # Valid UUID string SHOULD be passed as trace_id
    valid_uuid_trace_id = str(uuid.uuid4())
    handle2 = adapter.start_span("SpanUUID", trace_id=valid_uuid_trace_id)
    assert handle2 is not None
    assert client.create_calls[1]["trace_id"] == valid_uuid_trace_id


def test_3_end_span_delivery_failure_and_retry_semantics() -> None:
    client = create_autospec_client()
    adapter_closed = LangSmithTraceAdapter({"enabled": True, "sample_rate": 1.0, "fail_open": False}, client=client)

    handle = adapter_closed.start_span("SpanRetry")
    assert handle is not None

    # Simulate SDK update_run raising error on first call
    client.update_run.side_effect = RuntimeError("Network error")
    with pytest.raises(ObservabilityTraceError):
        adapter_closed.end_span(handle, outputs={"res": "fail"})

    # Delivery failure recorded
    assert adapter_closed.delivery_failures > 0
    # Span was NOT moved to _ended_spans on failure!
    assert handle.external_run_id not in adapter_closed._ended_spans


def test_4_error_summary_run_emitted_for_unsampled_trace_when_error_sampled() -> None:
    client = create_autospec_client()
    # sample_rate = 0, but error_sample_rate = 1.0
    adapter = LangSmithTraceAdapter({
        "enabled": True,
        "sample_rate": 0.0,
        "error_sample_rate": 1.0,
    }, client=client)

    # start_span for unsampled trace returns None
    handle = adapter.start_span("UnsampledSpan")
    assert handle is None
    assert len(client.create_calls) == 0

    # end_span called with None handle and error triggers Error Summary Run creation!
    adapter.end_span(None, error="Database connection failed password=secret")
    assert len(client.create_calls) == 1
    create_call = client.create_calls[0]
    assert create_call["name"] == "UnsampledTrace:ErrorSummary"
    assert "secret" not in create_call["error"]
    assert "[REDACTED_SECRET]" in create_call["error"]


def test_5_content_switches_respected_in_adapter() -> None:
    client = create_autospec_client()
    adapter = LangSmithTraceAdapter({
        "enabled": True,
        "sample_rate": 1.0,
        "metadata_only": False,  # metadata_only=False MUST NOT bypass content switches!
        "include_prompt_content": False,
        "include_document_content": False,
        "include_tool_content": False,
    }, client=client)

    inputs = {
        "prompt_content": "User prompt text",
        "document_content": "Document body",
        "tool_result": "Tool output",
        "normal_key": "Normal input",
    }

    handle = adapter.start_span("SpanSwitches", inputs=inputs)
    assert handle is not None

    created_inputs = client.create_calls[0]["inputs"]
    assert created_inputs["prompt_content"] == "[REDACTED_CONTENT]"
    assert created_inputs["document_content"] == "[REDACTED_CONTENT]"
    assert created_inputs["tool_result"] == "[REDACTED_CONTENT]"
    assert created_inputs["normal_key"] == "Normal input"


def test_6_canonical_node_types_mapped() -> None:
    client = create_autospec_client()
    adapter = LangSmithTraceAdapter({"enabled": True, "sample_rate": 1.0}, client=client)
    for node in CANONICAL_NODE_TYPES:
        h = adapter.start_span(node, span_type=node)
        assert h is not None
        adapter.end_span(h, outputs={"status": "completed"})


def test_7_config_example_schema_consistency() -> None:
    config_path = resolve_app_config_path("src/backend/zuno/platform/config/config.example.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        cfg_data = yaml.safe_load(f)

    assert "langsmith" in cfg_data
    ls_cfg = cfg_data["langsmith"]
    expected_keys = {
        "enabled",
        "project",
        "endpoint",
        "api_key",
        "sample_rate",
        "error_sample_rate",
        "eval_sample_rate",
        "include_prompt_content",
        "include_document_content",
        "include_tool_content",
        "metadata_only",
        "max_field_chars",
        "fail_open",
    }
    assert expected_keys.issubset(set(ls_cfg.keys()))
