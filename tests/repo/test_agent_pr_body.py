from __future__ import annotations

import pytest
from tools.scripts.verify_agent_pr_body import REQUIRED_SECTIONS, verify_agent_pr_body


def test_verify_agent_pr_body_valid(tmp_path) -> None:
    pr_body = tmp_path / "pr_body.md"
    pr_body.write_text(
        """## Agent Attribution

- Implementer: Antigravity

## Scope

## Current

- State active

## Evidence

- Tests passed

## Tests Run

- pytest

## Tests Not Run

- Docker

## Not Claimed

- PHASE22 completed
""",
        encoding="utf-8",
    )
    assert verify_agent_pr_body(pr_body) is True


def test_verify_agent_pr_body_missing_section(tmp_path) -> None:
    pr_body = tmp_path / "incomplete_pr_body.md"
    pr_body.write_text(
        """## Agent Attribution
- Implementer: Antigravity
""",
        encoding="utf-8",
    )
    assert verify_agent_pr_body(pr_body) is False
