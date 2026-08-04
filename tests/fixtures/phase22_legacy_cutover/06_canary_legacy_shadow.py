"""Contract fixture 6: ``canary`` mode with ``legacy`` as shadow."""

from __future__ import annotations

from typing import Any


def handle_canary(request: dict[str, Any]) -> dict[str, Any]:
    mode = request.get("mode")
    if mode == "canary":
        return {
            "runtime": "phase08",
            "shadow_match": False,
            "shadow_runtime": "legacy",
        }
    return {"runtime": "phase08"}