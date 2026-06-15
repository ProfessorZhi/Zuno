from __future__ import annotations

from importlib import import_module

_ZUNO_DATABASE_METADATA = import_module("zuno.database.metadata")

__all__ = list(getattr(_ZUNO_DATABASE_METADATA, "__all__", []))


def __getattr__(name: str):
    return getattr(_ZUNO_DATABASE_METADATA, name)
