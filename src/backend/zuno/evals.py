"""Compatibility module for ``zuno.evals`` tooling imports."""

from __future__ import annotations

from pathlib import Path

_EVALS_ROOT = Path(__file__).resolve().parents[3] / "tools" / "evals" / "zuno"
__path__ = [str(_EVALS_ROOT)] if _EVALS_ROOT.exists() else []

__all__: list[str] = []
