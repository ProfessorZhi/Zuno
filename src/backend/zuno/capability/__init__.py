from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zuno.capability.contracts import (
        CapabilityCost,
        CapabilityHealth,
        CapabilityPermissions,
        CapabilityRecord,
        CapabilityType,
        ToolCard,
    )
    from zuno.capability.registry import CapabilityRegistry, ToolCardRegistry
    from zuno.capability.retrieval import NativeBM25Retriever, NativeBM25SearchResult
    from zuno.capability.selector import (
        CapabilitySelectionRequest,
        CapabilitySelectionResult,
        DynamicCapabilitySelector,
    )
    from zuno.capability.trace import CapabilitySelectionTrace


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
    "NativeBM25Retriever": "zuno.capability.retrieval",
    "NativeBM25SearchResult": "zuno.capability.retrieval",
    "ToolCard": "zuno.capability.contracts",
    "ToolCardRegistry": "zuno.capability.registry",
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
    "NativeBM25Retriever",
    "NativeBM25SearchResult",
    "ToolCard",
    "ToolCardRegistry",
]


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
