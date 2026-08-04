"""Contract fixture 8: product API still reaches ``GeneralAgent``.

A representative controller file whose dispatch path names the legacy
``GeneralAgent`` runtime explicitly.
"""

from __future__ import annotations

from typing import Any


def product_runtime(request: dict[str, Any]) -> dict[str, Any]:
    """Public product runtime that resolves to ``GeneralAgent``."""
    agent = request.get("agent") or "GeneralAgent"
    return {"runtime": agent, "request": request}