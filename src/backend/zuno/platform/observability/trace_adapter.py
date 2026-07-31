from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
import os
import random
import re
from typing import Any, Callable, Dict, List, Optional, Set
import uuid

from loguru import logger


class ObservabilityError(Exception):
    """Base exception for observability errors."""


class ObservabilityConfigError(ObservabilityError):
    """Raised when observability configuration is invalid."""


class ObservabilityDependencyError(ObservabilityError):
    """Raised when a required dependency is missing."""


class ObservabilityTraceError(ObservabilityError):
    """Raised when trace operations fail and fail_open is False."""


SENSITIVE_KEY_PATTERNS = [
    r"api_key",
    r"password",
    r"secret",
    r"authorization",
    r"\btoken\b",
    r"access_key",
    r"private_key",
    r"connection_string",
    r"cookie",
    r"set_cookie",
    r"database_url",
    r"bearer",
]

FORBIDDEN_CONTENT_KEYS = {
    "raw_document",
    "document_content",
    "prompt_content",
    "tool_result",
    "authorization_header",
    "full_database_row",
    "secret_lease",
    "approval_token",
    "desktop_token",
}

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

NODE_TYPE_TO_LANGSMITH_RUN_TYPE = {
    "RetrievalRound": "retriever",
    "BM25": "retriever",
    "Vector": "retriever",
    "Graph": "retriever",
    "Fusion": "retriever",
    "Rerank": "retriever",
    "ToolInvocation": "tool",
    "FinalSynthesis": "llm",
    "QueryRewrite": "llm",
}


def redact_sensitive_data(
    data: Any,
    *,
    max_chars: int = 512,
    redact_content: bool = True,
    seen: Optional[Set[int]] = None,
) -> Any:
    if data is None:
        return None
    if isinstance(data, (int, float, bool)):
        return data
    if isinstance(data, str):
        if len(data) > max_chars:
            return data[:max_chars] + "...[TRUNCATED]"
        return data
    if isinstance(data, Exception):
        err_msg = f"{type(data).__name__}: {str(data)}"
        if len(err_msg) > max_chars:
            return err_msg[:max_chars] + "...[TRUNCATED]"
        return err_msg

    if seen is None:
        seen = set()
    obj_id = id(data)
    if obj_id in seen:
        return "[CIRCULAR_REFERENCE]"
    seen.add(obj_id)

    try:
        if isinstance(data, (list, tuple, set)):
            res = [
                redact_sensitive_data(item, max_chars=max_chars, redact_content=redact_content, seen=seen)
                for item in data
            ]
            return tuple(res) if isinstance(data, tuple) else res

        if hasattr(data, "model_dump") and callable(getattr(data, "model_dump")):
            data = data.model_dump()
        elif hasattr(data, "dict") and callable(getattr(data, "dict")):
            data = data.dict()
        elif hasattr(data, "__dataclass_fields__"):
            import dataclasses
            data = dataclasses.asdict(data)

        if isinstance(data, dict):
            cleaned: dict[str, Any] = {}
            for key, val in data.items():
                key_str = str(key)
                is_sensitive = any(re.search(pat, key_str, re.IGNORECASE) for pat in SENSITIVE_KEY_PATTERNS)
                if is_sensitive:
                    cleaned[key_str] = "[REDACTED_SECRET]"
                elif redact_content and key_str in FORBIDDEN_CONTENT_KEYS:
                    cleaned[key_str] = "[REDACTED_CONTENT]"
                else:
                    cleaned[key_str] = redact_sensitive_data(
                        val, max_chars=max_chars, redact_content=redact_content, seen=seen
                    )
            return cleaned

        str_val = str(data)
        if len(str_val) > max_chars:
            return str_val[:max_chars] + "...[TRUNCATED]"
        return str_val
    except Exception:
        str_val = str(data)
        if len(str_val) > max_chars:
            return str_val[:max_chars] + "...[TRUNCATED]"
        return str_val
    finally:
        seen.remove(obj_id)


@dataclass
class TraceSpanHandle:
    provider: str
    external_run_id: str
    trace_id: Optional[str] = None
    parent_external_run_id: Optional[str] = None
    span_name: str = ""
    span_type: str = "generic"
    sampled: bool = True
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    correlation_refs: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.external_run_id

    def startswith(self, prefix: str) -> bool:
        return self.external_run_id.startswith(prefix)

    def to_evidence_ref(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "external_run_id": self.external_run_id,
            "trace_id": self.trace_id,
            "parent_external_run_id": self.parent_external_run_id,
            "span_name": self.span_name,
            "span_type": self.span_type,
            "sampled": self.sampled,
            "started_at": self.started_at,
            "correlation_refs": self.correlation_refs,
        }


class ObservabilityTracePort(ABC):
    @abstractmethod
    def start_span(
        self,
        span_name: str,
        *,
        span_type: str = "generic",
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str | TraceSpanHandle] = None,
        metadata: Optional[dict[str, Any]] = None,
        inputs: Optional[dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[TraceSpanHandle]:
        pass

    @abstractmethod
    def end_span(
        self,
        span_id: Optional[str | TraceSpanHandle],
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
        parent_span_id: Optional[str | TraceSpanHandle] = None,
        metadata: Optional[dict[str, Any]] = None,
        inputs: Optional[dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[TraceSpanHandle]:
        return None

    def end_span(
        self,
        span_id: Optional[str | TraceSpanHandle],
        *,
        outputs: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        pass


class InMemoryTraceAdapter(ObservabilityTracePort):
    """In-memory trace adapter prototype for ObservabilityTracePort."""

    def __init__(
        self,
        config: Optional[dict[str, Any]] = None,
        random_fn: Optional[Callable[[], float]] = None,
    ) -> None:
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
        self._random_fn = random_fn or random.random
        self._active_spans: dict[str, dict[str, Any]] = {}
        self._ended_spans: set[str] = set()

    def _should_sample(
        self,
        is_error: bool = False,
        is_eval: bool = False,
        parent_sampled: Optional[bool] = None,
    ) -> bool:
        if not self.enabled or not self.tenant_tracing_enabled:
            return False
        if parent_sampled is not None:
            return parent_sampled
        if is_eval:
            rate = self.eval_sample_rate
        elif is_error:
            rate = self.error_sample_rate
        else:
            rate = self.sample_rate

        if rate <= 0.0:
            return False
        if rate >= 1.0:
            return True
        return self._random_fn() < rate

    def start_span(
        self,
        span_name: str,
        *,
        span_type: str = "generic",
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str | TraceSpanHandle] = None,
        metadata: Optional[dict[str, Any]] = None,
        inputs: Optional[dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[TraceSpanHandle]:
        parent_id_str = parent_span_id.external_run_id if isinstance(parent_span_id, TraceSpanHandle) else parent_span_id
        parent_sampled = None
        if parent_span_id is not None:
            if isinstance(parent_span_id, TraceSpanHandle):
                parent_sampled = parent_span_id.sampled
            elif parent_id_str in self._active_spans:
                parent_sampled = self._active_spans[parent_id_str]["handle"].sampled

        if not self._should_sample(is_error=False, is_eval=(span_type == "eval"), parent_sampled=parent_sampled):
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
            cleaned_inputs = redact_sensitive_data(
                inputs or {},
                max_chars=self.max_field_chars,
                redact_content=self.metadata_only,
            )
            run_id = f"ls_{span_name}_{len(self._active_spans) + 1}_{hash(trace_id or span_name) & 0xffff}"
            handle = TraceSpanHandle(
                provider="in_memory",
                external_run_id=run_id,
                trace_id=trace_id or run_id,
                parent_external_run_id=parent_id_str,
                span_name=span_name,
                span_type=span_type,
                sampled=True,
                correlation_refs={k: v for k, v in correlation_ids.items() if v is not None},
            )
            self._active_spans[run_id] = {
                "handle": handle,
                "span_name": span_name,
                "span_type": span_type,
                "parent_span_id": parent_id_str,
                "metadata": cleaned_metadata,
                "inputs": cleaned_inputs,
                "tags": tags or [],
            }
            return handle
        except Exception as exc:
            if self.fail_open:
                return None
            raise ObservabilityTraceError(f"InMemory start_span failed: {exc}") from exc

    def end_span(
        self,
        span_id: Optional[str | TraceSpanHandle],
        *,
        outputs: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        if not span_id:
            return
        ext_id = span_id.external_run_id if isinstance(span_id, TraceSpanHandle) else span_id

        if ext_id in self._ended_spans:
            if not self.fail_open:
                raise ObservabilityTraceError(f"Span {ext_id} already ended")
            return

        if ext_id not in self._active_spans:
            if not self.fail_open:
                raise ObservabilityTraceError(f"Unknown span_id: {ext_id}")
            return

        try:
            cleaned_outputs = redact_sensitive_data(
                outputs or {},
                max_chars=self.max_field_chars,
                redact_content=self.metadata_only,
            )
            span_data = self._active_spans.pop(ext_id)
            self._ended_spans.add(ext_id)
            span_data["status"] = "error" if error else "ok"
            span_data["outputs"] = cleaned_outputs
            if error:
                span_data["error"] = redact_sensitive_data(error, max_chars=self.max_field_chars)
        except Exception as exc:
            if not self.fail_open:
                raise ObservabilityTraceError(f"InMemory end_span failed: {exc}") from exc


class LangSmithTraceAdapter(ObservabilityTracePort):
    """Real LangSmith Python SDK Trace Adapter."""

    def __init__(
        self,
        config: Optional[dict[str, Any]] = None,
        client: Optional[Any] = None,
        random_fn: Optional[Callable[[], float]] = None,
    ) -> None:
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
        self._random_fn = random_fn or random.random
        self._client = client
        self._client_initialized = client is not None
        self._active_spans: dict[str, dict[str, Any]] = {}
        self._ended_spans: set[str] = set()

    def _get_client(self) -> Any:
        if self._client_initialized:
            return self._client

        api_key = self.api_key or os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")
        if not api_key:
            err_msg = "LangSmith enabled=true but API Key is missing"
            logger.warning(err_msg)
            if not self.fail_open:
                raise ObservabilityConfigError(err_msg)
            self._client = None
            self._client_initialized = True
            return None

        try:
            from langsmith import Client as LangSmithClient
        except ImportError as exc:
            err_msg = f"LangSmith SDK import unavailable: {exc}"
            logger.error(err_msg)
            if not self.fail_open:
                raise ObservabilityDependencyError(err_msg) from exc
            self._client = None
            self._client_initialized = True
            return None

        try:
            self._client = LangSmithClient(
                api_key=api_key,
                api_url=self.endpoint,
            )
            self._client_initialized = True
            return self._client
        except Exception as exc:
            err_msg = f"Failed to initialize LangSmith Client: {exc}"
            logger.error(err_msg)
            if not self.fail_open:
                raise ObservabilityTraceError(err_msg) from exc
            self._client = None
            self._client_initialized = True
            return None

    def _should_sample(
        self,
        is_error: bool = False,
        is_eval: bool = False,
        parent_sampled: Optional[bool] = None,
    ) -> bool:
        if not self.enabled or not self.tenant_tracing_enabled:
            return False
        if parent_sampled is not None:
            return parent_sampled
        if is_eval:
            rate = self.eval_sample_rate
        elif is_error:
            rate = self.error_sample_rate
        else:
            rate = self.sample_rate

        if rate <= 0.0:
            return False
        if rate >= 1.0:
            return True
        return self._random_fn() < rate

    def start_span(
        self,
        span_name: str,
        *,
        span_type: str = "generic",
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str | TraceSpanHandle] = None,
        metadata: Optional[dict[str, Any]] = None,
        inputs: Optional[dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[TraceSpanHandle]:
        parent_id_str = parent_span_id.external_run_id if isinstance(parent_span_id, TraceSpanHandle) else parent_span_id
        parent_sampled = None
        if parent_span_id is not None:
            if isinstance(parent_span_id, TraceSpanHandle):
                parent_sampled = parent_span_id.sampled
            elif parent_id_str in self._active_spans:
                parent_sampled = self._active_spans[parent_id_str]["handle"].sampled

        if not self._should_sample(is_error=False, is_eval=(span_type == "eval"), parent_sampled=parent_sampled):
            return None

        client = self._get_client()
        if client is None:
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
            cleaned_inputs = redact_sensitive_data(
                inputs or {},
                max_chars=self.max_field_chars,
                redact_content=self.metadata_only,
            )
            cleaned_tags = redact_sensitive_data(
                tags or [span_type],
                max_chars=self.max_field_chars,
                redact_content=self.metadata_only,
            )

            external_run_id = str(uuid.uuid4())
            run_type = NODE_TYPE_TO_LANGSMITH_RUN_TYPE.get(span_type, "chain")

            run_kwargs: dict[str, Any] = {
                "id": external_run_id,
                "name": span_name,
                "run_type": run_type,
                "project_name": self.project,
                "inputs": cleaned_inputs if isinstance(cleaned_inputs, dict) else {"input": cleaned_inputs},
                "start_time": datetime.now(timezone.utc),
                "extra": {"metadata": cleaned_metadata},
                "tags": cleaned_tags if isinstance(cleaned_tags, list) else [str(cleaned_tags)],
            }
            if parent_id_str:
                run_kwargs["parent_run_id"] = parent_id_str
            if trace_id:
                run_kwargs["trace_id"] = trace_id

            client.create_run(**run_kwargs)

            handle = TraceSpanHandle(
                provider="langsmith",
                external_run_id=external_run_id,
                trace_id=trace_id or external_run_id,
                parent_external_run_id=parent_id_str,
                span_name=span_name,
                span_type=span_type,
                sampled=True,
                correlation_refs={k: v for k, v in correlation_ids.items() if v is not None},
            )
            self._active_spans[external_run_id] = {
                "handle": handle,
                "span_name": span_name,
                "span_type": span_type,
                "parent_span_id": parent_id_str,
            }
            return handle
        except Exception as exc:
            logger.error(f"LangSmith create_run failed: {exc}")
            if not self.fail_open:
                raise ObservabilityTraceError(f"LangSmith start_span failed: {exc}") from exc
            return None

    def end_span(
        self,
        span_id: Optional[str | TraceSpanHandle],
        *,
        outputs: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        if not span_id:
            return
        ext_id = span_id.external_run_id if isinstance(span_id, TraceSpanHandle) else span_id

        if ext_id in self._ended_spans:
            if not self.fail_open:
                raise ObservabilityTraceError(f"Span {ext_id} already ended")
            return

        if ext_id not in self._active_spans:
            if not self.fail_open:
                raise ObservabilityTraceError(f"Unknown span_id: {ext_id}")
            return

        client = self._get_client()
        if client is None:
            self._active_spans.pop(ext_id, None)
            self._ended_spans.add(ext_id)
            return

        try:
            cleaned_outputs = redact_sensitive_data(
                outputs or {},
                max_chars=self.max_field_chars,
                redact_content=self.metadata_only,
            )
            cleaned_meta = redact_sensitive_data(
                metadata or {},
                max_chars=self.max_field_chars,
                redact_content=self.metadata_only,
            )
            self._active_spans.pop(ext_id, None)
            self._ended_spans.add(ext_id)

            update_kwargs: dict[str, Any] = {
                "run_id": ext_id,
                "outputs": cleaned_outputs if isinstance(cleaned_outputs, dict) else {"output": cleaned_outputs},
                "end_time": datetime.now(timezone.utc),
            }
            if error:
                redacted_err = redact_sensitive_data(error, max_chars=self.max_field_chars)
                update_kwargs["error"] = str(redacted_err)
            if cleaned_meta:
                update_kwargs["extra"] = {"metadata": cleaned_meta}

            client.update_run(**update_kwargs)
        except Exception as exc:
            logger.error(f"LangSmith update_run failed: {exc}")
            if not self.fail_open:
                raise ObservabilityTraceError(f"LangSmith end_span failed: {exc}") from exc


def get_observability_adapter(
    config: Optional[dict[str, Any]] = None,
    client: Optional[Any] = None,
    random_fn: Optional[Callable[[], float]] = None,
) -> ObservabilityTracePort:
    cfg = config or {}
    if cfg.get("enabled"):
        return LangSmithTraceAdapter(cfg, client=client, random_fn=random_fn)
    return NoopTraceAdapter()


__all__ = [
    "ObservabilityError",
    "ObservabilityConfigError",
    "ObservabilityDependencyError",
    "ObservabilityTraceError",
    "TraceSpanHandle",
    "ObservabilityTracePort",
    "NoopTraceAdapter",
    "InMemoryTraceAdapter",
    "LangSmithTraceAdapter",
    "get_observability_adapter",
    "redact_sensitive_data",
    "CANONICAL_NODE_TYPES",
]
