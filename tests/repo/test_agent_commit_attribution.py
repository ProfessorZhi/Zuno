from __future__ import annotations

import pytest
from tools.scripts.verify_agent_commit_attribution import (
    ALLOWED_AGENTS,
    ALLOWED_MODES,
    parse_commit_trailers,
)


def test_parse_valid_commit_trailers() -> None:
    msg = """ci: add phase22 remote verification workflow

Agent: Antigravity
Agent-Mode: Standard-Conversation
Human-Owner: ProfessorZhi
Architecture-Reviewer: ChatGPT
Work-Package: AG-PHASE22-REMOTE-VERIFICATION-HARNESS
"""
    trailers = parse_commit_trailers(msg)
    assert trailers["Agent"] == "Antigravity"
    assert trailers["Agent-Mode"] == "Standard-Conversation"
    assert trailers["Human-Owner"] == "ProfessorZhi"
    assert trailers["Architecture-Reviewer"] == "ChatGPT"
    assert trailers["Work-Package"] == "AG-PHASE22-REMOTE-VERIFICATION-HARNESS"


def test_allowed_agent_values() -> None:
    assert "Antigravity" in ALLOWED_AGENTS
    assert "Qoder" in ALLOWED_AGENTS
    assert "Codex" in ALLOWED_AGENTS
    assert "Trae" in ALLOWED_AGENTS
    assert "ChatGPT-Docs" in ALLOWED_AGENTS
    assert "Human" in ALLOWED_AGENTS


def test_allowed_mode_values() -> None:
    assert "Standard-Conversation" in ALLOWED_MODES
    assert "Expert-Team" in ALLOWED_MODES
    assert "Codex" in ALLOWED_MODES
    assert "Standard" in ALLOWED_MODES
    assert "Docs-Maintenance" in ALLOWED_MODES
    assert "Human" in ALLOWED_MODES


def test_crlf_line_endings_parsing() -> None:
    msg = "feat: test\r\n\r\nAgent: Qoder\r\nAgent-Mode: Codex\r\nHuman-Owner: Alice\r\nArchitecture-Reviewer: Bob\r\nWork-Package: WP-01\r\n"
    trailers = parse_commit_trailers(msg)
    assert trailers["Agent"] == "Qoder"
    assert trailers["Agent-Mode"] == "Codex"
