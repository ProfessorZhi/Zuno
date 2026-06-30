from __future__ import annotations

import importlib


def test_memory_layer_modules_expose_target_boundaries() -> None:
    expected_exports = {
        "zuno.memory.contracts": {
            "ExternalKnowledgeRecord",
            "MemoryCandidate",
            "MemoryLayer",
            "MemoryProcessingPolicy",
            "MemoryReviewDecision",
            "MemoryReviewStatus",
            "MemoryScope",
            "RawMemoryEvent",
            "TaskMemorySummary",
        },
        "zuno.memory.store": {"InMemoryLayerStore"},
        "zuno.memory.policy": {"MemoryProcessingPolicy", "RetentionPolicy"},
        "zuno.memory.review": {
            "ExternalKnowledgeRecord",
            "MemoryCandidate",
            "MemoryReviewDecision",
            "MemoryReviewStatus",
        },
        "zuno.memory.retrieval": {"InMemoryLayerStore", "MemoryCandidate", "MemoryScope"},
        "zuno.memory.rendering": {"RawMemoryEvent", "TaskMemorySummary"},
        "zuno.memory.engine": {
            "InMemoryLayerStore",
            "MEMORY_TAXONOMY",
            "MemoryEngine",
            "MemoryEvalPolicy",
            "MemoryTaxonomyEntry",
            "RawMemoryEvent",
            "TaskMemorySummary",
        },
    }

    for module_name, exports in expected_exports.items():
        module = importlib.import_module(module_name)
        assert set(module.__all__) == exports


def test_memory_layer_modules_reuse_legacy_foundation_objects() -> None:
    from zuno.memory.contracts import MemoryLayer, MemoryScope, RawMemoryEvent
    from zuno.memory.policy import MemoryProcessingPolicy, RetentionPolicy
    from zuno.memory.review import MemoryReviewDecision
    from zuno.memory.store import InMemoryLayerStore
    from zuno.services.memory.layers import (
        InMemoryLayerStore as LegacyStore,
        MemoryLayer as LegacyLayer,
        MemoryScope as LegacyScope,
        RawMemoryEvent as LegacyRawEvent,
        MemoryProcessingPolicy as LegacyProcessingPolicy,
        MemoryReviewDecision as LegacyReviewDecision,
        RetentionPolicy as LegacyPolicy,
    )

    assert MemoryLayer is LegacyLayer
    assert MemoryScope is LegacyScope
    assert RawMemoryEvent is LegacyRawEvent
    assert MemoryProcessingPolicy is LegacyProcessingPolicy
    assert MemoryReviewDecision is LegacyReviewDecision
    assert RetentionPolicy is LegacyPolicy
    assert InMemoryLayerStore is LegacyStore


def test_memory_package_facade_points_at_layer_modules() -> None:
    import zuno.memory as memory
    from zuno.memory.contracts import MemoryLayer
    from zuno.memory.policy import RetentionPolicy
    from zuno.memory.store import InMemoryLayerStore
    from zuno.memory.engine import MemoryEngine

    assert memory.MemoryLayer is MemoryLayer
    assert memory.RetentionPolicy is RetentionPolicy
    assert memory.InMemoryLayerStore is InMemoryLayerStore
    assert memory.MemoryEngine is MemoryEngine
