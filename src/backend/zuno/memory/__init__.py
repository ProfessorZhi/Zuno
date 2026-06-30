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
    from zuno.memory.store import (
        DatabaseMemoryStore,
        DurableMemoryStore,
        InMemoryLayerStore,
        MemoryGovernanceLedgerEntry,
        MemoryStoreSnapshot,
    )


_EXPORT_TO_MODULE = {
    "DatabaseMemoryStore": "zuno.memory.store",
    "DurableMemoryStore": "zuno.memory.store",
    "ExternalKnowledgeRecord": "zuno.memory.contracts",
    "InMemoryLayerStore": "zuno.memory.store",
    "MemoryCandidate": "zuno.memory.contracts",
    "MemoryEngine": "zuno.memory.engine",
    "MemoryGovernanceLedgerEntry": "zuno.memory.store",
    "MemoryLayer": "zuno.memory.contracts",
    "MemoryProcessingPolicy": "zuno.memory.policy",
    "MemoryReviewDecision": "zuno.memory.review",
    "MemoryReviewStatus": "zuno.memory.review",
    "MemoryScope": "zuno.memory.contracts",
    "RawMemoryEvent": "zuno.memory.contracts",
    "RetentionPolicy": "zuno.memory.policy",
    "MemoryStoreSnapshot": "zuno.memory.store",
    "TaskMemorySummary": "zuno.memory.contracts",
}

__all__ = [
    "DatabaseMemoryStore",
    "DurableMemoryStore",
    "ExternalKnowledgeRecord",
    "InMemoryLayerStore",
    "MemoryCandidate",
    "MemoryEngine",
    "MemoryGovernanceLedgerEntry",
    "MemoryLayer",
    "MemoryProcessingPolicy",
    "MemoryReviewDecision",
    "MemoryReviewStatus",
    "MemoryScope",
    "RawMemoryEvent",
    "RetentionPolicy",
    "MemoryStoreSnapshot",
    "TaskMemorySummary",
]


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
