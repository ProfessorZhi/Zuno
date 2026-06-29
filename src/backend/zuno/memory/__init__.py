from __future__ import annotations

from importlib import import_module
from typing import Any


_EXPORT_TO_MODULE = {
    "ExternalKnowledgeRecord": "zuno.memory.contracts",
    "InMemoryLayerStore": "zuno.memory.store",
    "MemoryCandidate": "zuno.memory.contracts",
    "MemoryLayer": "zuno.memory.contracts",
    "MemoryScope": "zuno.memory.contracts",
    "RawMemoryEvent": "zuno.memory.contracts",
    "RetentionPolicy": "zuno.memory.policy",
    "TaskMemorySummary": "zuno.memory.contracts",
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
