from importlib import import_module
from typing import TYPE_CHECKING, Any

from zuno.api.JWT import Settings

if TYPE_CHECKING:
    from zuno.api.router import router

__all__ = ["Settings", "router"]


def __getattr__(name: str) -> Any:
    if name == "router":
        value = import_module("zuno.api.router").router
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
