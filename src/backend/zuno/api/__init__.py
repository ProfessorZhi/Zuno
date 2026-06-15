from importlib import import_module
from pkgutil import extend_path
from typing import TYPE_CHECKING, Any

from zuno.api.JWT import Settings

__path__ = extend_path(__path__, __name__)

if TYPE_CHECKING:
    from zuno.api.router import router

__all__ = ["Settings", "router"]


def __getattr__(name: str) -> Any:
    if name == "router":
        value = import_module("zuno.api.router").router
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
