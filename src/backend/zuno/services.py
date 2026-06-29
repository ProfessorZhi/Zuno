"""Compatibility module for legacy ``zuno.services`` imports."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path

_TARGET_PACKAGE = "zuno.platform.services"
_TARGET_PATH = Path(__file__).resolve().parent / "platform" / "services"

__path__ = [str(_TARGET_PATH)] if _TARGET_PATH.is_dir() else []

_target = import_module(_TARGET_PACKAGE)
__all__ = list(getattr(_target, "__all__", []))


def __getattr__(name: str):
    return getattr(_target, name)
