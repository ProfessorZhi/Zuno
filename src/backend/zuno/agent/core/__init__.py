"""Agent Core package surface.

After the PHASE22 backend semantic legacy cleanup the Agent Core package only
exposes the retained internal step capability (``StructuredResponseAgent``).
Retired product runtimes (``GeneralAgent`` and family) are gone; the Single
Controller Product Runtime (``zuno.agent.runtime``) owns every product run.
"""

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zuno.agent.core.agents import StructuredResponseAgent


_EXPORT_TO_MODULE = {
    "StructuredResponseAgent": ("agents", "StructuredResponseAgent"),
}

__all__ = [
    "StructuredResponseAgent",
]


def __getattr__(name: str) -> Any:
    target = _EXPORT_TO_MODULE.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    package_name, attr_name = target
    module = import_module(f"{__name__}.{package_name}")
    value = getattr(module, attr_name)
    globals()[name] = value
    return value
