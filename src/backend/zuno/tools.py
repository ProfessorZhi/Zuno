"""Compatibility module for legacy ``zuno.tools`` imports."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path

_TARGET_PACKAGE = "zuno.capability.tools"
_TARGET_PATH = Path(__file__).resolve().parent / "capability" / "tools"

__path__ = [str(_TARGET_PATH)] if _TARGET_PATH.is_dir() else []

_target = import_module(_TARGET_PACKAGE)
__all__ = list(getattr(_target, "__all__", []))

for _name in __all__:
    globals()[_name] = getattr(_target, _name)


def __getattr__(name: str):
    return getattr(_target, name)
