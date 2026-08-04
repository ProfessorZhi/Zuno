"""Contract fixture 2: ``_fallback_to_legacy`` in production source.

This file mirrors the live cutover-controller signature that the verifier
must detect. It deliberately declares ``_fallback_to_legacy`` so that the
AST stage picks it up.
"""

from __future__ import annotations

from typing import Any


def _fallback_to_legacy(request: dict[str, Any], exc: Exception) -> dict[str, Any]:
    """Production helper that always falls back to a legacy runner."""
    return {"runtime": "legacy", "reason": type(exc).__name__}