from __future__ import annotations

from importlib import import_module
from typing import Any


_EXPORT_TO_MODULE = {
    "CapabilityCost": "zuno.capability.contracts",
    "CapabilityHealth": "zuno.capability.contracts",
    "CapabilityPermissions": "zuno.capability.contracts",
    "CapabilityRecord": "zuno.capability.contracts",
    "CapabilityRegistry": "zuno.capability.registry",
    "CapabilitySelectionRequest": "zuno.capability.selector",
    "CapabilitySelectionResult": "zuno.capability.selector",
    "CapabilitySelectionTrace": "zuno.capability.trace",
    "CapabilityType": "zuno.capability.contracts",
    "DynamicCapabilitySelector": "zuno.capability.selector",
}

__all__ = [
    "CapabilityCost",
    "CapabilityHealth",
    "CapabilityPermissions",
    "CapabilityRecord",
    "CapabilityRegistry",
    "CapabilitySelectionRequest",
    "CapabilitySelectionResult",
    "CapabilitySelectionTrace",
    "CapabilityType",
    "DynamicCapabilitySelector",
]


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
