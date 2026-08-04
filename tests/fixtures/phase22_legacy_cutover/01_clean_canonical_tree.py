"""Contract fixture 1: clean canonical tree.

A production-clean Python module that uses only canonical imports, has no
legacy runtime hooks, and represents the expected post-PHASE22 baseline.
"""

from __future__ import annotations

from typing import Any

from zuno.agent.runtime import UnifiedAgentRuntimeService


def handle_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Canonical new_default request handler."""
    runtime = UnifiedAgentRuntimeService.from_canonical(payload)
    return runtime.execute(payload)