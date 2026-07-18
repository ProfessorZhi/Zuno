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
        "zuno.memory.store": {
            "DatabaseMemoryStore",
            "DurableMemoryStore",
            "InMemoryLayerStore",
            "MemoryGovernanceLedgerEntry",
            "MemoryStoreSnapshot",
        },
        "zuno.memory.policy": {"MemoryProcessingPolicy", "RetentionPolicy"},
        "zuno.memory.review": {
            "ExternalKnowledgeRecord",
            "MemoryCandidate",
            "MemoryReviewDecision",
            "MemoryReviewStatus",
        },
        "zuno.memory.retrieval": {
            "DeterministicSemanticMemoryAdapter",
            "InMemoryLayerStore",
            "MemoryCandidate",
            "MemoryScope",
            "SemanticMemorySearchResult",
        },
        "zuno.memory.rendering": {"RawMemoryEvent", "TaskMemorySummary"},
        "zuno.memory.engine": {
            "InMemoryLayerStore",
            "MEMORY_TAXONOMY",
            "DeterministicSemanticMemoryAdapter",
            "MemoryEngine",
            "MemoryEvalBaselineResult",
            "MemoryEvalPolicy",
            "MemoryPrivacyDeleteReport",
            "MemoryTaxonomyEntry",
            "DatabaseMemoryStore",
            "DurableMemoryStore",
            "RawMemoryEvent",
            "SemanticMemorySearchResult",
            "TaskMemorySummary",
        },
        "zuno.memory.runtime_batch": {
            "CandidateStatus",
            "CompressionDecision",
            "CompressionLevel",
            "ConflictRecord",
            "ConsolidationRecord",
            "ContextPackVersion",
            "FreshnessRecord",
            "LongTermMemoryKind",
            "MemoryCandidateRecord",
            "MemoryEnvelope",
            "MemoryLifecycleRecord",
            "MemoryReadinessEvidence",
            "MemoryRuntimeBatch",
            "MemorySafetyRecord",
            "MemoryStorageRecord",
            "MemoryTraceRecord",
            "MemoryVersionRecord",
            "ModelMemoryRouting",
            "PrivacyDeleteRecord",
            "ProjectionPublicationRecord",
            "ReflexionGovernanceRecord",
            "RehydrationRecord",
            "RetrievalGateRecord",
            "SessionSummaryRecord",
            "StateMachineRecord",
            "VersionStatus",
        },
    }

    for module_name, exports in expected_exports.items():
        module = importlib.import_module(module_name)
        assert set(module.__all__) == exports


def test_memory_layer_modules_reuse_legacy_foundation_objects() -> None:
    from zuno.memory.contracts import MemoryLayer, MemoryScope, RawMemoryEvent
    from zuno.memory.policy import MemoryProcessingPolicy, RetentionPolicy
    from zuno.memory.review import MemoryReviewDecision
    from zuno.memory.store import DatabaseMemoryStore, DurableMemoryStore, InMemoryLayerStore
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
    assert issubclass(DurableMemoryStore, LegacyStore)
    assert issubclass(DatabaseMemoryStore, LegacyStore)


def test_memory_package_facade_points_at_layer_modules() -> None:
    import zuno.memory as memory
    from zuno.memory.contracts import MemoryLayer
    from zuno.memory.policy import RetentionPolicy
    from zuno.memory.store import InMemoryLayerStore
    from zuno.memory.engine import MemoryEngine
    from zuno.memory.runtime_batch import MemoryRuntimeBatch

    assert memory.MemoryLayer is MemoryLayer
    assert memory.RetentionPolicy is RetentionPolicy
    assert memory.InMemoryLayerStore is InMemoryLayerStore
    assert memory.MemoryEngine is MemoryEngine
    assert memory.MemoryRuntimeBatch is MemoryRuntimeBatch
