from __future__ import annotations

from importlib import import_module
from typing import Any

from .layers import (
    ExternalKnowledgeRecord,
    InMemoryLayerStore,
    MemoryCandidate,
    MemoryLayer,
    MemoryProcessingPolicy,
    MemoryReviewDecision,
    MemoryReviewStatus,
    MemoryScope,
    RawMemoryEvent,
    RetentionPolicy,
    TaskMemorySummary,
)

__all__ = [
    "ExternalKnowledgeRecord",
    "InMemoryLayerStore",
    "MemoryCandidate",
    "MemoryLayer",
    "MemoryProcessingPolicy",
    "MemoryReviewDecision",
    "MemoryReviewStatus",
    "MemoryScope",
    "RawMemoryEvent",
    "RetentionPolicy",
    "TaskMemorySummary",
    "client",
]


def __getattr__(name: str) -> Any:
    if name == "client":
        module = import_module("zuno.services.memory.client")
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
