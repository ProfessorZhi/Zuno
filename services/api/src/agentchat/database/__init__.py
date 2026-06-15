from __future__ import annotations

from importlib import import_module
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

_ZUNO_DATABASE = import_module("zuno.database")

__all__ = list(getattr(_ZUNO_DATABASE, "__all__", []))


def __getattr__(name: str):
    return getattr(_ZUNO_DATABASE, name)
