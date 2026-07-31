from __future__ import annotations

import pytest

from zuno.platform.settings import app_settings
from zuno.platform.observability.trace_adapter import (
    InMemoryTraceAdapter,
    LangSmithTraceAdapter,
    NoopTraceAdapter,
    ObservabilityConfigError,
    get_observability_adapter,
)


def test_factory_disabled_returns_noop() -> None:
    adapter = get_observability_adapter({"enabled": False})
    assert isinstance(adapter, NoopTraceAdapter)

    adapter_empty = get_observability_adapter({})
    assert isinstance(adapter_empty, NoopTraceAdapter)


def test_factory_enabled_returns_langsmith_adapter() -> None:
    adapter = get_observability_adapter({
        "enabled": True,
        "api_key": "sk-test-key",
        "sample_rate": 1.0,
    })
    assert isinstance(adapter, LangSmithTraceAdapter)


def test_in_memory_trace_adapter_explicit_instantiation() -> None:
    in_mem = InMemoryTraceAdapter({
        "enabled": True,
        "sample_rate": 1.0,
    })
    handle = in_mem.start_span("TestSpan")
    assert handle is not None
    assert handle.provider == "in_memory"
    in_mem.end_span(handle, outputs={"ok": True})


def test_config_missing_api_key_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGCHAIN_API_KEY", raising=False)

    adapter = LangSmithTraceAdapter({
        "enabled": True,
        "api_key": "",
        "sample_rate": 1.0,
        "fail_open": False,
    })
    with pytest.raises(ObservabilityConfigError) as exc_info:
        adapter.start_span("AgentRun")
    assert "API Key is missing" in str(exc_info.value)


def test_config_missing_api_key_fail_open(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGCHAIN_API_KEY", raising=False)

    adapter = LangSmithTraceAdapter({
        "enabled": True,
        "api_key": "",
        "fail_open": True,
        "sample_rate": 1.0,
    })
    # Fail open returns None gracefully without exception or fake trace
    handle = adapter.start_span("AgentRun")
    assert handle is None
