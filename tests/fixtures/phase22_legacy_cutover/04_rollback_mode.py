"""Contract fixture 4: ``mode == rollback`` literal in production source."""

from __future__ import annotations

from typing import Any


def handle_rollback(request: dict[str, Any]) -> dict[str, Any]:
    if request.get("mode") == "rollback":
        return {"runtime": "legacy", "reason": "rollback branch"}
    return {"runtime": "phase08"}