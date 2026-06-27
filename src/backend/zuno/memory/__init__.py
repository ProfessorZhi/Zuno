from __future__ import annotations

from importlib import import_module
from typing import Any


_EXPORT_TO_MODULE = {
    "ExternalKnowledgeRecord": "zuno.services.memory.layers",
    "InMemoryLayerStore": "zuno.services.memory.layers",
    "MemoryCandidate": "zuno.services.memory.layers",
    "MemoryLayer": "zuno.services.memory.layers",
    "MemoryScope": "zuno.services.memory.layers",
    "RawMemoryEvent": "zuno.services.memory.layers",
    "RetentionPolicy": "zuno.services.memory.layers",
    "TaskMemorySummary": "zuno.services.memory.layers",
}

__all__ = [
    "ExternalKnowledgeRecord",
    "InMemoryLayerStore",
    "MemoryCandidate",
    "MemoryLayer",
    "MemoryScope",
    "RawMemoryEvent",
    "RetentionPolicy",
    "TaskMemorySummary",
]


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
