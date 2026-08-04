"""Contract fixture 14: ``try/except ImportError`` legacy fallback."""

from __future__ import annotations

try:
    from zuno.core.legacy_runner import run  # type: ignore[import-not-found]
except Exception:
    def run(*args, **kwargs):
        return {"runtime": "legacy_fallback"}