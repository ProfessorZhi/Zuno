from agentchat.api.v1.mcp_server import _build_mcp_summary


def test_build_mcp_summary_uses_deterministic_tool_preview():
    summary = _build_mcp_summary(
        "qa-mcp",
        {
            "qa-mcp": [
                {"name": "qa_ping"},
                {"name": "qa_echo"},
                {"name": "qa_health"},
                {"name": "qa_extra"},
            ]
        },
    )

    assert summary.mcp_as_tool_name == "qa-mcp"
    assert "qa_ping" in summary.description
    assert "qa_echo" in summary.description
    assert "qa_health" in summary.description
    assert "qa_extra" not in summary.description
