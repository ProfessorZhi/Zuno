from __future__ import annotations

from importlib import import_module

_ZUNO_DATABASE_SESSION = import_module("zuno.database.session")

__all__ = list(getattr(_ZUNO_DATABASE_SESSION, "__all__", []))


def __getattr__(name: str):
    return getattr(_ZUNO_DATABASE_SESSION, name)
