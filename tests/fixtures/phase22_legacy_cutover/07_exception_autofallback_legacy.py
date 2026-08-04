"""Contract fixture 7: exception-driven automatic fallback to legacy."""

from __future__ import annotations

from typing import Any


def run_with_legacy_fallback(request: dict[str, Any]) -> dict[str, Any]:
    try:
        runtime = request["phase08_runtime"]
        return {"runtime": "phase08", "result": runtime()}
    except Exception:
        return {"runtime": "legacy", "reason": "new_runtime_unavailable"}