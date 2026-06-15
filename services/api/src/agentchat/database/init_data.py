from __future__ import annotations

from importlib import import_module

_ZUNO_DATABASE_INIT_DATA = import_module("zuno.database.init_data")

__all__ = list(getattr(_ZUNO_DATABASE_INIT_DATA, "__all__", []))


def __getattr__(name: str):
    return getattr(_ZUNO_DATABASE_INIT_DATA, name)
