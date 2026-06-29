from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zuno.platform.model_gateway import EchoLLMProvider, LLMProvider
    from zuno.platform.observability import (
        RedisKeys,
        build_langchain_run_config,
        build_langsmith_metadata,
        configure_langsmith,
        get_active_trace_id,
    )
    from zuno.platform.security import (
        AccessScope,
        ExecutionMode,
        normalize_access_scope,
        normalize_execution_mode,
        validate_tools_for_mode,
    )
    from zuno.platform.services.execution_policy import (
        ACCESS_SCOPE_DEFINITIONS,
        EXECUTION_MODE_DEFINITIONS,
        annotate_tool_execution_metadata,
        filter_tools_for_mode,
        get_execution_config_payload,
        get_tool_runtime_type,
    )
    from zuno.platform.storage import (
        LazyStorageClient,
        MinioClient,
        OSSClient,
        storage_client,
    )


_EXPORT_TO_MODULE = {
    "ACCESS_SCOPE_DEFINITIONS": "zuno.platform.services.execution_policy",
    "EXECUTION_MODE_DEFINITIONS": "zuno.platform.services.execution_policy",
    "AccessScope": "zuno.platform.security",
    "EchoLLMProvider": "zuno.platform.model_gateway",
    "ExecutionMode": "zuno.platform.security",
    "LLMProvider": "zuno.platform.model_gateway",
    "LazyStorageClient": "zuno.platform.storage",
    "MinioClient": "zuno.platform.storage",
    "OSSClient": "zuno.platform.storage",
    "RedisKeys": "zuno.platform.observability",
    "annotate_tool_execution_metadata": "zuno.platform.services.execution_policy",
    "build_langchain_run_config": "zuno.platform.observability",
    "build_langsmith_metadata": "zuno.platform.observability",
    "configure_langsmith": "zuno.platform.observability",
    "filter_tools_for_mode": "zuno.platform.services.execution_policy",
    "get_active_trace_id": "zuno.platform.observability",
    "get_execution_config_payload": "zuno.platform.services.execution_policy",
    "get_tool_runtime_type": "zuno.platform.services.execution_policy",
    "normalize_access_scope": "zuno.platform.security",
    "normalize_execution_mode": "zuno.platform.security",
    "storage_client": "zuno.platform.storage",
    "validate_tools_for_mode": "zuno.platform.security",
}

__all__ = [
    "ACCESS_SCOPE_DEFINITIONS",
    "EXECUTION_MODE_DEFINITIONS",
    "AccessScope",
    "EchoLLMProvider",
    "ExecutionMode",
    "LLMProvider",
    "LazyStorageClient",
    "MinioClient",
    "OSSClient",
    "RedisKeys",
    "annotate_tool_execution_metadata",
    "build_langchain_run_config",
    "build_langsmith_metadata",
    "configure_langsmith",
    "filter_tools_for_mode",
    "get_active_trace_id",
    "get_execution_config_payload",
    "get_tool_runtime_type",
    "normalize_access_scope",
    "normalize_execution_mode",
    "storage_client",
    "validate_tools_for_mode",
]


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
