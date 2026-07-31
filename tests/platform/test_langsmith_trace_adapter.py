from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional
import pytest
import yaml

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
    redact_sensitive_data,
)


class FakeLangSmithClient:
    def __init__(
        self,
        should_raise_create: bool = False,
        should_raise_update: bool = False,
    ) -> None:
        self.create_calls: List[Dict[str, Any]] = []
        self.update_calls: List[Dict[str, Any]] = []
        self.should_raise_create = should_raise_create
        self.should_raise_update = should_raise_update

    def create_run(self, **kwargs: Any) -> None:
        if self.should_raise_create:
            raise RuntimeError("SDK create_run failure")
        self.create_calls.append(kwargs)

    def update_run(self, **kwargs: Any) -> None:
        if self.should_raise_update:
            raise RuntimeError("SDK update_run failure")
        self.update_calls.append(kwargs)


def test_1_and_2_factory_disabled_and_enabled() -> None:
    noop = get_observability_adapter({"enabled": False})
    assert isinstance(noop, NoopTraceAdapter)

    enabled = get_observability_adapter({"enabled": True, "api_key": "sk-key", "sample_rate": 1.0})
    assert isinstance(enabled, LangSmithTraceAdapter)


def test_3_client_lazy_instantiation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LANGSMITH_API_KEY", "sk-lazy-key")
    adapter = LangSmithTraceAdapter({"enabled": True, "sample_rate": 1.0})
    assert adapter._client_initialized is False
    assert adapter._client is None

    fake_client = FakeLangSmithClient()
    adapter._client = fake_client
    adapter._client_initialized = True
    handle = adapter.start_span("LazySpan")
    assert handle is not None
    assert len(fake_client.create_calls) == 1


def test_4_5_6_7_8_9_10_11_sdk_calls_parent_metadata_tags_outputs_errors_uuid() -> None:
    fake_client = FakeLangSmithClient()
    adapter = LangSmithTraceAdapter(
        config={
            "enabled": True,
            "project": "ZunoTest",
            "endpoint": "https://api.smith.langchain.com",
            "sample_rate": 1.0,
            "metadata_only": True,
        },
        client=fake_client,
    )

    metadata = {
        "agent_run_id": "run_001",
        "api_key": "sk-secret-123",
        "prompt_content": "Secret prompt text",
    }

    # Root span
    root_handle = adapter.start_span(
        "AgentRun",
        span_type="AgentRun",
        trace_id="trace_999",
        metadata=metadata,
        inputs={"user_query": "hello"},
        tags=["workspace", "test"],
    )
    assert root_handle is not None
    assert root_handle.provider == "langsmith"
    uuid.UUID(root_handle.external_run_id)  # Validate real UUID format!
    assert root_handle.trace_id == "trace_999"

    assert len(fake_client.create_calls) == 1
    create_call = fake_client.create_calls[0]
    assert create_call["name"] == "AgentRun"
    assert create_call["project_name"] == "ZunoTest"
    assert create_call["extra"]["metadata"]["api_key"] == "[REDACTED_SECRET]"
    assert create_call["extra"]["metadata"]["prompt_content"] == "[REDACTED_CONTENT]"

    # Child span
    child_handle = adapter.start_span(
        "RetrievalRound",
        span_type="RetrievalRound",
        parent_span_id=root_handle,
        metadata={"round": 1},
    )
    assert child_handle is not None
    assert child_handle.parent_external_run_id == root_handle.external_run_id
    assert len(fake_client.create_calls) == 2
    assert fake_client.create_calls[1]["run_type"] == "retriever"
    assert fake_client.create_calls[1]["parent_run_id"] == root_handle.external_run_id

    # End child span normally
    adapter.end_span(child_handle, outputs={"retrieved_count": 5})
    assert len(fake_client.update_calls) == 1
    assert fake_client.update_calls[0]["run_id"] == child_handle.external_run_id
    assert fake_client.update_calls[0]["outputs"]["retrieved_count"] == 5

    # End root span with error
    adapter.end_span(root_handle, error="Execution failed due to timeout")
    assert len(fake_client.update_calls) == 2
    assert fake_client.update_calls[1]["run_id"] == root_handle.external_run_id
    assert fake_client.update_calls[1]["error"] == "Execution failed due to timeout"


def test_12_duplicate_end_span() -> None:
    fake_client = FakeLangSmithClient()
    adapter = LangSmithTraceAdapter({"enabled": True, "sample_rate": 1.0, "fail_open": True}, client=fake_client)
    handle = adapter.start_span("Span1")
    assert handle is not None

    adapter.end_span(handle, outputs={"ok": True})
    assert len(fake_client.update_calls) == 1

    # Duplicate end span in fail_open mode does not call client again or throw
    adapter.end_span(handle, outputs={"ok": True})
    assert len(fake_client.update_calls) == 1

    # Duplicate end span in fail_closed mode raises ObservabilityTraceError
    adapter_fail_closed = LangSmithTraceAdapter({"enabled": True, "sample_rate": 1.0, "fail_open": False}, client=fake_client)
    h2 = adapter_fail_closed.start_span("Span2")
    adapter_fail_closed.end_span(h2)
    with pytest.raises(ObservabilityTraceError) as exc_info:
        adapter_fail_closed.end_span(h2)
    assert "already ended" in str(exc_info.value)


def test_13_unknown_span_id() -> None:
    fake_client = FakeLangSmithClient()
    adapter_open = LangSmithTraceAdapter({"enabled": True, "sample_rate": 1.0, "fail_open": True}, client=fake_client)
    adapter_open.end_span("unknown_span_uuid")
    assert len(fake_client.update_calls) == 0

    adapter_closed = LangSmithTraceAdapter({"enabled": True, "sample_rate": 1.0, "fail_open": False}, client=fake_client)
    with pytest.raises(ObservabilityTraceError) as exc_info:
        adapter_closed.end_span("unknown_span_uuid")
    assert "Unknown span_id" in str(exc_info.value)


def test_14_15_fail_open_and_fail_closed_on_sdk_error() -> None:
    faulty_client = FakeLangSmithClient(should_raise_create=True, should_raise_update=True)
    
    # Fail open -> returns None for start_span, swallows exception in end_span
    adapter_open = LangSmithTraceAdapter({"enabled": True, "sample_rate": 1.0, "fail_open": True}, client=faulty_client)
    h = adapter_open.start_span("FailSpan")
    assert h is None
    adapter_open.end_span(h)

    # Fail closed -> raises ObservabilityTraceError
    adapter_closed = LangSmithTraceAdapter({"enabled": True, "sample_rate": 1.0, "fail_open": False}, client=faulty_client)
    with pytest.raises(ObservabilityTraceError) as exc_info:
        adapter_closed.start_span("FailSpan")
    assert "LangSmith start_span failed" in str(exc_info.value)


def test_16_api_key_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGCHAIN_API_KEY", raising=False)

    adapter_open = LangSmithTraceAdapter({"enabled": True, "api_key": "", "sample_rate": 1.0, "fail_open": True})
    assert adapter_open.start_span("NoKeySpan") is None

    adapter_closed = LangSmithTraceAdapter({"enabled": True, "api_key": "", "sample_rate": 1.0, "fail_open": False})
    with pytest.raises(ObservabilityConfigError):
        adapter_closed.start_span("NoKeySpan")


def test_17_18_endpoint_and_project() -> None:
    fake_client = FakeLangSmithClient()
    adapter = LangSmithTraceAdapter(
        {
            "enabled": True,
            "project": "CustomProject",
            "endpoint": "https://custom.langsmith.com",
            "sample_rate": 1.0,
        },
        client=fake_client,
    )
    assert adapter.project == "CustomProject"
    assert adapter.endpoint == "https://custom.langsmith.com"
    handle = adapter.start_span("SpanCustom")
    assert handle is not None
    assert fake_client.create_calls[0]["project_name"] == "CustomProject"


def test_19_20_21_22_23_24_25_sampling_suite() -> None:
    # 19: sample_rate = 0
    a_zero = LangSmithTraceAdapter({"enabled": True, "sample_rate": 0.0}, client=FakeLangSmithClient())
    assert a_zero.start_span("S1") is None

    # 20: sample_rate = 1
    a_one = LangSmithTraceAdapter({"enabled": True, "sample_rate": 1.0}, client=FakeLangSmithClient())
    assert a_one.start_span("S1") is not None

    # 21: deterministic intermediate sampling with injected random_fn
    low_rand = LangSmithTraceAdapter({"enabled": True, "sample_rate": 0.5}, client=FakeLangSmithClient(), random_fn=lambda: 0.3)
    high_rand = LangSmithTraceAdapter({"enabled": True, "sample_rate": 0.5}, client=FakeLangSmithClient(), random_fn=lambda: 0.7)
    assert low_rand.start_span("S1") is not None
    assert high_rand.start_span("S1") is None

    # 22: error sampling
    err_adapter = LangSmithTraceAdapter({"enabled": True, "sample_rate": 0.0, "error_sample_rate": 1.0}, client=FakeLangSmithClient())
    # Normal span not sampled
    assert err_adapter.start_span("S1") is None

    # 23: eval sampling
    eval_adapter = LangSmithTraceAdapter({"enabled": True, "sample_rate": 0.0, "eval_sample_rate": 1.0}, client=FakeLangSmithClient())
    assert eval_adapter.start_span("EvalSpan", span_type="eval") is not None

    # 24: tenant disabled
    tenant_off = LangSmithTraceAdapter({"enabled": True, "tenant_tracing_enabled": False, "sample_rate": 1.0}, client=FakeLangSmithClient())
    assert tenant_off.start_span("S1") is None

    # 25: child inherits parent sampling decision
    parent_unsampled_handle = TraceSpanHandle(provider="langsmith", external_run_id="p1", sampled=False)
    child_handle = a_one.start_span("Child", parent_span_id=parent_unsampled_handle)
    assert child_handle is None


def test_26_27_28_29_30_redaction_and_unserializable() -> None:
    fake_client = FakeLangSmithClient()
    adapter = LangSmithTraceAdapter({"enabled": True, "sample_rate": 1.0, "metadata_only": True}, client=fake_client)

    class UnserializableObj:
        def __str__(self) -> str:
            return "UnserializableRepresentation"

    meta = {
        "api_key": "sk-secret-val",
        "nested": {"password": "pass", "document_content": "doc body"},
        "bad_obj": UnserializableObj(),
        "long_text": "x" * 1000,
    }

    handle = adapter.start_span("SpanRedact", metadata=meta)
    assert handle is not None
    recorded_meta = fake_client.create_calls[0]["extra"]["metadata"]
    assert recorded_meta["api_key"] == "[REDACTED_SECRET]"
    assert recorded_meta["nested"]["password"] == "[REDACTED_SECRET]"
    assert recorded_meta["nested"]["document_content"] == "[REDACTED_CONTENT]"
    assert "UnserializableRepresentation" in recorded_meta["bad_obj"]
    assert recorded_meta["long_text"].endswith("...[TRUNCATED]")


def test_31_sdk_import_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    import sys
    monkeypatch.setitem(sys.modules, "langsmith", None)

    adapter_open = LangSmithTraceAdapter({"enabled": True, "api_key": "sk-key", "sample_rate": 1.0, "fail_open": True})
    assert adapter_open.start_span("Span1") is None

    adapter_closed = LangSmithTraceAdapter({"enabled": True, "api_key": "sk-key", "sample_rate": 1.0, "fail_open": False})
    with pytest.raises(ObservabilityDependencyError):
        adapter_closed.start_span("Span1")


def test_32_sdk_exception_does_not_mutate_domain_result() -> None:
    faulty_client = FakeLangSmithClient(should_raise_create=True, should_raise_update=True)
    adapter = LangSmithTraceAdapter({"enabled": True, "sample_rate": 1.0, "fail_open": True}, client=faulty_client)

    # Domain execution logic remains unaffected even if trace adapter encounters exception
    domain_outcome = {"outcome": "success", "data": 42}
    handle = adapter.start_span("DomainSpan")
    adapter.end_span(handle, outputs=domain_outcome)
    assert domain_outcome["outcome"] == "success"
    assert domain_outcome["data"] == 42


def test_33_handle_does_not_leak_client_or_secret() -> None:
    handle = TraceSpanHandle(
        provider="langsmith",
        external_run_id="run_12345",
        trace_id="trace_12345",
        span_name="AgentRun",
        correlation_refs={"agent_run_id": "r1"},
    )
    ref = handle.to_evidence_ref()
    assert "client" not in ref
    assert "api_key" not in ref
    assert ref["provider"] == "langsmith"
    assert ref["external_run_id"] == "run_12345"


def test_34_config_example_matches_schema() -> None:
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


def test_canonical_node_types_mapped() -> None:
    fake_client = FakeLangSmithClient()
    adapter = LangSmithTraceAdapter({"enabled": True, "sample_rate": 1.0}, client=fake_client)
    for node in CANONICAL_NODE_TYPES:
        h = adapter.start_span(node, span_type=node)
        assert h is not None
        adapter.end_span(h, outputs={"status": "completed"})
