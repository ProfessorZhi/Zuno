from __future__ import annotations

from abc import ABC, abstractmethod
import os
import re
from typing import Any, Dict, List, Optional


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

CANONICAL_NODE_TYPES = [
    "AgentRun",
    "PlanCreation",
    "PlanValidation",
    "StepExecution",
    "RetrievalRound",
    "QueryRewrite",
    "BM25",
    "Vector",
    "Graph",
    "Fusion",
    "Rerank",
    "EvidenceAcceptance",
    "ToolInvocation",
    "StepAcceptance",
    "Replan",
    "FinalSynthesis",
    "CitationValidation",
    "FinalGate",
    "RunOutcome",
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
            elif redact_content and key_str in ("raw_document", "prompt_content", "tool_result", "document_content"):
                cleaned[key_str] = "[REDACTED_CONTENT]"
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


class InMemoryTraceAdapter(ObservabilityTracePort):
    """In-memory trace prototype adapter for ObservabilityTracePort.

    NOTE:
    - LangSmith SDK integration (langsmith.Client) = NOT IMPLEMENTED
    - Canonical runtime trace wiring = NOT IMPLEMENTED
    - This adapter stores spans in-memory for testing port contracts and redaction logic.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.enabled = bool(self.config.get("enabled", False))
        self.tenant_tracing_enabled = bool(self.config.get("tenant_tracing_enabled", True))
        self.project = str(self.config.get("project", "Zuno"))
        self.endpoint = str(self.config.get("endpoint", "https://api.smith.langchain.com"))
        self.api_key = str(self.config.get("api_key", ""))
        self.sample_rate = float(self.config.get("sample_rate", 0.0))
        self.error_sample_rate = float(self.config.get("error_sample_rate", 1.0))
        self.eval_sample_rate = float(self.config.get("eval_sample_rate", 1.0))
        self.metadata_only = bool(self.config.get("metadata_only", True))
        self.include_prompt_content = bool(self.config.get("include_prompt_content", False))
        self.include_document_content = bool(self.config.get("include_document_content", False))
        self.include_tool_content = bool(self.config.get("include_tool_content", False))
        self.max_field_chars = int(self.config.get("max_field_chars", 512))
        self.fail_open = bool(self.config.get("fail_open", True))
        self._active_spans: dict[str, dict[str, Any]] = {}

    def _should_sample(self, is_error: bool = False, is_eval: bool = False) -> bool:
        if not self.enabled or not self.tenant_tracing_enabled:
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
        if not self._should_sample(is_error=False, is_eval=(span_type == "eval")):
            return None
        try:
            meta = metadata or {}
            correlation_ids = {
                "agent_run_id": meta.get("agent_run_id"),
                "plan_version_id": meta.get("plan_version_id"),
                "step_run_id": meta.get("step_run_id"),
                "retrieval_round_id": meta.get("retrieval_round_id"),
                "tool_attempt_id": meta.get("tool_attempt_id"),
                "trace_id": trace_id or meta.get("trace_id"),
                "tenant_ref": meta.get("tenant_ref", "default_tenant"),
                "workspace_ref": meta.get("workspace_ref", "default_workspace"),
            }
            cleaned_metadata = redact_sensitive_data(
                {**meta, **correlation_ids},
                max_chars=self.max_field_chars,
                redact_content=self.metadata_only,
            )
            span_id = f"ls_{span_name}_{len(self._active_spans) + 1}_{hash(trace_id or span_name) & 0xffff}"
            self._active_spans[span_id] = {
                "span_name": span_name,
                "span_type": span_type,
                "parent_span_id": parent_span_id,
                "metadata": cleaned_metadata,
            }
            return span_id
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
        if not span_id or span_id not in self._active_spans:
            return
        try:
            cleaned_outputs = redact_sensitive_data(
                outputs or {},
                max_chars=self.max_field_chars,
                redact_content=self.metadata_only,
            )
            span_data = self._active_spans.pop(span_id, {})
            span_data["status"] = "error" if error else "ok"
            span_data["outputs"] = cleaned_outputs
            if error:
                span_data["error"] = str(error)
        except Exception:
            if not self.fail_open:
                raise


# Alias for backward compatibility while clearly documenting prototype status
LangSmithTraceAdapter = InMemoryTraceAdapter


def get_observability_adapter(config: Optional[dict[str, Any]] = None) -> ObservabilityTracePort:
    cfg = config or {}
    if cfg.get("enabled"):
        return InMemoryTraceAdapter(cfg)
    return NoopTraceAdapter()


__all__ = [
    "ObservabilityTracePort",
    "NoopTraceAdapter",
    "InMemoryTraceAdapter",
    "LangSmithTraceAdapter",
    "get_observability_adapter",
    "redact_sensitive_data",
    "CANONICAL_NODE_TYPES",
]
