"""Evaluation import surface for the active zuno runtime."""

from __future__ import annotations

from pathlib import Path
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

_EVALS_ROOT = Path(__file__).resolve().parents[4] / "tools" / "evals" / "zuno"
if _EVALS_ROOT.exists():
    __path__.append(str(_EVALS_ROOT))

__all__: list[str] = []
