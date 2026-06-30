from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zuno.memory.contracts import (
        ExternalKnowledgeRecord,
        MemoryCandidate,
        MemoryLayer,
        MemoryProcessingPolicy,
        MemoryReviewDecision,
        MemoryReviewStatus,
        MemoryScope,
        RawMemoryEvent,
        TaskMemorySummary,
    )
    from zuno.memory.engine import MemoryEngine
    from zuno.memory.policy import RetentionPolicy
    from zuno.memory.store import InMemoryLayerStore


_EXPORT_TO_MODULE = {
    "ExternalKnowledgeRecord": "zuno.memory.contracts",
    "InMemoryLayerStore": "zuno.memory.store",
    "MemoryCandidate": "zuno.memory.contracts",
    "MemoryEngine": "zuno.memory.engine",
    "MemoryLayer": "zuno.memory.contracts",
    "MemoryProcessingPolicy": "zuno.memory.policy",
    "MemoryReviewDecision": "zuno.memory.review",
    "MemoryReviewStatus": "zuno.memory.review",
    "MemoryScope": "zuno.memory.contracts",
    "RawMemoryEvent": "zuno.memory.contracts",
    "RetentionPolicy": "zuno.memory.policy",
    "TaskMemorySummary": "zuno.memory.contracts",
}

__all__ = [
    "ExternalKnowledgeRecord",
    "InMemoryLayerStore",
    "MemoryCandidate",
    "MemoryEngine",
    "MemoryLayer",
    "MemoryProcessingPolicy",
    "MemoryReviewDecision",
    "MemoryReviewStatus",
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
