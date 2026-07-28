from __future__ import annotations

from typing import Any

from .effect_policy import classify_tool_effect


PHASE16_DIRECT_TOOL_BYPASS_BLOCK_REASON = "PHASE16_DIRECT_TOOL_BYPASS_BLOCKED"
_READONLY_NAME_PREFIXES = (
    "get",
    "list",
    "read",
    "search",
    "lookup",
    "fetch",
    "query",
    "inspect",
    "describe",
    "retrieve",
)


class ToolBypassBlockedError(RuntimeError):
    pass


def is_legacy_direct_tool_readonly(tool_name: str) -> bool:
    normalized = _normalize_tool_name(tool_name)
    return any(normalized.startswith(prefix) for prefix in _READONLY_NAME_PREFIXES)


def ensure_legacy_direct_tool_allowed(
    *,
    tool_name: str,
    args: dict[str, Any],
    adapter_kind: str,
) -> None:
    effect_policy = classify_tool_effect(
        tool_name=tool_name,
        args=args,
        readonly=is_legacy_direct_tool_readonly(tool_name),
        adapter_kind=adapter_kind,
    )
    if not effect_policy.provider_dispatch_allowed:
        raise ToolBypassBlockedError(PHASE16_DIRECT_TOOL_BYPASS_BLOCK_REASON)


def _normalize_tool_name(tool_name: str) -> str:
    return str(tool_name or "").strip().lower().replace(".", "_").replace("-", "_")


__all__ = [
    "PHASE16_DIRECT_TOOL_BYPASS_BLOCK_REASON",
    "ToolBypassBlockedError",
    "ensure_legacy_direct_tool_allowed",
    "is_legacy_direct_tool_readonly",
]