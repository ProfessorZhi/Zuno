"""Contract fixture 5: ``shadow`` mode with ``legacy`` as primary."""

from __future__ import annotations

from typing import Any


def handle_shadow(request: dict[str, Any]) -> dict[str, Any]:
    mode = request.get("mode")
    if mode == "shadow":
        return {"runtime": "legacy", "shadow_match": False}
    return {"runtime": "phase08"}