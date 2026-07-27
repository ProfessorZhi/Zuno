from __future__ import annotations

import pytest

from zuno.capability.tool_runtime.bypass_guard import (
    PHASE16_DIRECT_TOOL_BYPASS_BLOCK_REASON,
    ToolBypassBlockedError,
    ensure_legacy_direct_tool_allowed,
    is_legacy_direct_tool_readonly,
)


def test_phase16_legacy_direct_guard_allows_obvious_readonly_tool_names() -> None:
    assert is_legacy_direct_tool_readonly("read_file") is True
    ensure_legacy_direct_tool_allowed(
        tool_name="read_file",
        args={"path": "docs/architecture/README.md"},
        adapter_kind="LANGCHAIN",
    )


def test_phase16_legacy_direct_guard_blocks_write_or_unknown_tool_dispatch() -> None:
    assert is_legacy_direct_tool_readonly("send_email") is False
    with pytest.raises(ToolBypassBlockedError, match=PHASE16_DIRECT_TOOL_BYPASS_BLOCK_REASON):
        ensure_legacy_direct_tool_allowed(
            tool_name="send_email",
            args={"to": "review@example.com", "body": "hello"},
            adapter_kind="MCP",
        )