from __future__ import annotations

from abc import ABC, abstractmethod
import os
import re
from typing import Any, dict, list, Optional


SENSITIVE_KEY_PATTERNS = [
    r"api_key",
    r"password",
    r"secret",
    r"authorization",
    r"token",
    r"access_key",
    r"private_key",
    r"connection_string",
]


def redact_sensitive_data(
    data: Any,
    *,
    max_chars: int = 512,
    redact_content: bool = True,
) -> Any:
    if data is None:
        return None
    if isinstance(data, (int, float, bool)):
        return data
    if isinstance(data, str):
        if len(data) > max_chars:
            return data[:max_chars] + "...[TRUNCATED]"
        return data
    if isinstance(data, list):
        return [redact_sensitive_data(item, max_chars=max_chars, redact_content=redact_content) for item in data]
    if isinstance(data, dict):
        cleaned: dict[str, Any] = {}
        for key, val in data.items():
            key_str = str(key)
            is_sensitive = any(re.search(pat, key_str, re.IGNORECASE) for pat in SENSITIVE_KEY_PATTERNS)
            if is_sensitive:
                cleaned[key_str] = "[REDACTED_SECRET]"
            else:
                cleaned[key_str] = redact_sensitive_data(val, max_chars=max_chars, redact_content=redact_content)
        return cleaned
    return str(data)[:max_chars]


class ObservabilityTracePort(ABC):
    @abstractmethod
    def start_span(
        self,
        span_name: str,
        *,
        span_type: str = "generic",
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[str]:
        pass

    @abstractmethod
    def end_span(
        self,
        span_id: Optional[str],
        *,
        outputs: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        pass


class NoopTraceAdapter(ObservabilityTracePort):
    def start_span(
        self,
        span_name: str,
        *,
        span_type: str = "generic",
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[str]:
        return None

    def end_span(
        self,
        span_id: Optional[str],
        *,
        outputs: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        pass


class LangSmithTraceAdapter(ObservabilityTracePort):
    def __init__(self, config: Optional[dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.enabled = bool(self.config.get("enabled", False))
        self.project = str(self.config.get("project", "Zuno"))
        self.endpoint = str(self.config.get("endpoint", "https://api.smith.langchain.com"))
        self.api_key = str(self.config.get("api_key", ""))
        self.sample_rate = float(self.config.get("sample_rate", 0.0))
        self.error_sample_rate = float(self.config.get("error_sample_rate", 1.0))
        self.eval_sample_rate = float(self.config.get("eval_sample_rate", 1.0))
        self.metadata_only = bool(self.config.get("metadata_only", True))
        self.max_field_chars = int(self.config.get("max_field_chars", 512))
        self.fail_open = bool(self.config.get("fail_open", True))

    def _should_sample(self, is_error: bool = False, is_eval: bool = False) -> bool:
        if not self.enabled:
            return False
        if is_eval:
            return self.eval_sample_rate > 0.0
        if is_error:
            return self.error_sample_rate > 0.0
        return self.sample_rate > 0.0

    def start_span(
        self,
        span_name: str,
        *,
        span_type: str = "generic",
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[str]:
        if not self._should_sample():
            return None
        try:
            cleaned_metadata = redact_sensitive_data(
                metadata or {},
                max_chars=self.max_field_chars,
                redact_content=self.metadata_only,
            )
            # In a real setup, calls Client().create_run(...)
            # Fail-open returns generated span id
            return f"ls_span_{span_name}_{hash(trace_id or span_name) & 0xffffffff}"
        except Exception:
            if self.fail_open:
                return None
            raise

    def end_span(
        self,
        span_id: Optional[str],
        *,
        outputs: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        if not span_id or not self.enabled:
            return
        try:
            cleaned_outputs = redact_sensitive_data(
                outputs or {},
                max_chars=self.max_field_chars,
                redact_content=self.metadata_only,
            )
            _ = cleaned_outputs
        except Exception:
            if not self.fail_open:
                raise


def get_observability_adapter(config: Optional[dict[str, Any]] = None) -> ObservabilityTracePort:
    cfg = config or {}
    if cfg.get("enabled"):
        return LangSmithTraceAdapter(cfg)
    return NoopTraceAdapter()


__all__ = [
    "ObservabilityTracePort",
    "NoopTraceAdapter",
    "LangSmithTraceAdapter",
    "get_observability_adapter",
    "redact_sensitive_data",
]
